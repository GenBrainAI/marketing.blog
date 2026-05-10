---
title: "SSRF Protection in AI Agent Tools"
slug: "ssrf-protection-ai-agents"
date: 2026-05-10
category: technical
cluster: "security-compliance"
tags: [ssrf, url-allowlisting, network-security, ai-agents, input-validation, security]
description: "Protect AI agent tools from SSRF attacks with URL allowlisting, internal network blocking, DNS rebinding prevention, and response validation."
relatedPosts: [automated-security-auditing, path-traversal-defense, nats-auth-hardening]
---

# SSRF Protection in AI Agent Tools

Server-Side Request Forgery (SSRF) is uniquely dangerous in AI agent platforms. Agents frequently need to fetch external resources -- pulling data from APIs, downloading files, checking URLs provided in tasks -- but each outbound request is a potential vector for attacking internal infrastructure. When our AI CSO agent ran its first [automated security audit](/blog/automated-security-auditing), it identified four HIGH-severity SSRF vulnerabilities: unrestricted URL fetching in agent tools, accessible cloud metadata endpoints, internal service enumeration through error messages, and DNS rebinding susceptibility.

This post details the SSRF attack surface specific to AI agents, demonstrates the vulnerabilities found, and provides the defense implementation that blocks these attacks while maintaining agent functionality.

## Why SSRF Is Amplified in AI Agent Platforms

Traditional SSRF affects a single web application. In a multi-agent platform, the threat model is worse:

1. **Agent tools accept URLs from untrusted sources**: Tasks, messages from other agents, and user inputs all may contain URLs
2. **Agents run inside the trusted network perimeter**: They can reach internal services, metadata endpoints, and other agents
3. **Cloud metadata access**: Agents on AWS/GCP/Azure can reach `169.254.169.254` for IAM credentials
4. **Lateral movement**: SSRF in one agent can probe and attack other agents' [NATS endpoints](/blog/nats-jetstream-ai-agents)
5. **Automated exploitation**: Unlike manual attacks, a compromised agent can rapidly scan internal networks

## Real Vulnerabilities Found

### Vulnerability 1: Unrestricted URL Fetching in WebSearch Tool

```python
# VULNERABLE: Agent tool fetches any URL without validation
class WebFetchTool:
    """MCP tool for agents to fetch web content."""

    async def fetch(self, url: str) -> str:
        """Fetch content from a URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
```

**Attack**: A malicious task instructs the agent to fetch `http://169.254.169.254/latest/meta-data/iam/security-credentials/agent-role`, exposing AWS IAM temporary credentials with access to production resources.

### Vulnerability 2: Internal Service Discovery via Error Messages

```python
# VULNERABLE: Error messages reveal internal network topology
async def fetch_with_retry(url: str) -> str:
    try:
        response = await session.get(url, timeout=5)
        return await response.text()
    except aiohttp.ClientConnectorError as e:
        # Leaks internal IP/port information
        raise ToolError(f"Failed to connect: {e}")
    except asyncio.TimeoutError:
        # Distinguishes "exists but slow" from "doesn't exist"
        raise ToolError(f"Timeout connecting to {url}")
```

**Attack**: By observing different error types (connection refused vs. timeout vs. success), an attacker maps the internal network topology through the agent.

### Vulnerability 3: DNS Rebinding Attack

```python
# VULNERABLE: Validates hostname at resolution time, but DNS can change
def is_safe_url(url: str) -> bool:
    hostname = urlparse(url).hostname
    ip = socket.gethostbyname(hostname)
    return not is_internal_ip(ip)

async def fetch(url: str) -> str:
    if not is_safe_url(url):
        raise SecurityError("Internal URLs not allowed")
    # Time-of-check/time-of-use gap: DNS may resolve differently now
    return await session.get(url)
```

**Attack**: Attacker controls DNS for `evil.com`. First resolution returns `1.2.3.4` (passes validation). By the time the actual request fires, DNS now returns `10.0.0.1` (internal service).

## The Fix: Comprehensive SSRF Protection Layer

We implemented a multi-layer SSRF protection system:

```python
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional, Set
import asyncio
import aiohttp
from aiohttp import TCPConnector

class SSRFProtector:
    """Comprehensive SSRF protection for AI agent HTTP requests."""

    # Blocked IP ranges (RFC 1918, link-local, metadata endpoints)
    BLOCKED_NETWORKS = [
        ipaddress.ip_network("10.0.0.0/8"),        # Private
        ipaddress.ip_network("172.16.0.0/12"),      # Private
        ipaddress.ip_network("192.168.0.0/16"),     # Private
        ipaddress.ip_network("127.0.0.0/8"),        # Loopback
        ipaddress.ip_network("169.254.0.0/16"),     # Link-local (metadata!)
        ipaddress.ip_network("100.64.0.0/10"),      # Shared address space
        ipaddress.ip_network("0.0.0.0/8"),          # Current network
        ipaddress.ip_network("224.0.0.0/4"),        # Multicast
        ipaddress.ip_network("240.0.0.0/4"),        # Reserved
        ipaddress.ip_network("::1/128"),            # IPv6 loopback
        ipaddress.ip_network("fc00::/7"),           # IPv6 unique local
        ipaddress.ip_network("fe80::/10"),          # IPv6 link-local
        ipaddress.ip_network("::ffff:0:0/96"),      # IPv4-mapped IPv6
    ]

    # Allowed URL schemes
    ALLOWED_SCHEMES = {"http", "https"}

    # Blocked ports (common internal services)
    BLOCKED_PORTS = {
        25, 465, 587,    # SMTP
        6379,            # Redis
        5432,            # PostgreSQL
        3306,            # MySQL
        27017,           # MongoDB
        9200, 9300,      # Elasticsearch
        2379, 2380,      # etcd
        4222,            # NATS
        7687,            # Neo4j Bolt
        8500, 8600,      # Consul
    }

    # Domain allowlist for agent tools (if strict mode)
    ALLOWED_DOMAINS: Optional[Set[str]] = None  # Set to restrict

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        if strict_mode:
            self.ALLOWED_DOMAINS = set()

    def validate_url(self, url: str) -> str:
        """
        Validate a URL against SSRF protections.
        Returns the validated URL or raises SecurityError.
        """
        # Step 1: Parse and validate scheme
        parsed = urlparse(url)

        if parsed.scheme not in self.ALLOWED_SCHEMES:
            raise SSRFError(f"Scheme '{parsed.scheme}' not allowed")

        if not parsed.hostname:
            raise SSRFError("No hostname in URL")

        # Step 2: Check for IP address in hostname
        hostname = parsed.hostname.lower()

        # Block raw IP addresses (force DNS resolution through our resolver)
        try:
            ip = ipaddress.ip_address(hostname)
            if self._is_blocked_ip(ip):
                raise SSRFError("Access to internal IP addresses is blocked")
        except ValueError:
            pass  # Not an IP, it's a hostname - continue

        # Step 3: Domain allowlist (if strict mode)
        if self.ALLOWED_DOMAINS is not None:
            if hostname not in self.ALLOWED_DOMAINS:
                raise SSRFError(
                    f"Domain '{hostname}' not in allowlist"
                )

        # Step 4: Port validation
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if port in self.BLOCKED_PORTS:
            raise SSRFError(f"Port {port} is blocked")

        # Step 5: Check for URL tricks
        if '@' in parsed.netloc:
            raise SSRFError("Credentials in URL not allowed")

        if '\\' in url:
            raise SSRFError("Backslashes in URL not allowed")

        # Detect unicode/homograph tricks
        try:
            hostname.encode('ascii')
        except UnicodeEncodeError:
            raise SSRFError("Non-ASCII characters in hostname not allowed")

        return url

    def _is_blocked_ip(self, ip: ipaddress._BaseAddress) -> bool:
        """Check if an IP address is in a blocked range."""
        return any(ip in network for network in self.BLOCKED_NETWORKS)

    async def resolve_and_validate(self, hostname: str) -> list:
        """
        Resolve hostname and validate all returned IPs.
        Prevents DNS rebinding by pinning resolved addresses.
        """
        try:
            # Use getaddrinfo for IPv4 and IPv6
            loop = asyncio.get_event_loop()
            results = await loop.getaddrinfo(
                hostname, None,
                family=socket.AF_UNSPEC,
                type=socket.SOCK_STREAM
            )
        except socket.gaierror:
            raise SSRFError(f"DNS resolution failed for {hostname}")

        validated_ips = []
        for family, type_, proto, canonname, sockaddr in results:
            ip = ipaddress.ip_address(sockaddr[0])
            if self._is_blocked_ip(ip):
                raise SSRFError(
                    f"DNS resolution for {hostname} returned "
                    f"blocked IP {ip}"
                )
            validated_ips.append(sockaddr[0])

        if not validated_ips:
            raise SSRFError(f"No valid IPs for {hostname}")

        return validated_ips
```

## DNS-Pinning HTTP Client

To prevent DNS rebinding (TOCTOU attacks), we pin the resolved IP and connect directly:

```python
class SSRFSafeHTTPClient:
    """HTTP client with SSRF protections and DNS pinning."""

    def __init__(self, protector: SSRFProtector):
        self.protector = protector
        self.max_response_size = 10 * 1024 * 1024  # 10 MB
        self.timeout = aiohttp.ClientTimeout(total=30, connect=5)

    async def fetch(self, url: str) -> dict:
        """Safely fetch a URL with full SSRF protection."""
        # Step 1: Validate URL structure
        validated_url = self.protector.validate_url(url)
        parsed = urlparse(validated_url)

        # Step 2: Resolve DNS and validate IPs (pin the result)
        resolved_ips = await self.protector.resolve_and_validate(
            parsed.hostname
        )

        # Step 3: Create connector that uses pinned IP
        # This prevents DNS rebinding between validation and request
        connector = TCPConnector(
            ssl=parsed.scheme == "https",
            # Force connection to validated IP
            resolver=PinnedResolver(parsed.hostname, resolved_ips)
        )

        # Step 4: Make request with safety limits
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout
        ) as session:
            async with session.get(
                validated_url,
                allow_redirects=False,  # Handle redirects manually
                max_redirects=0
            ) as response:
                # Step 5: Validate response
                content_length = response.content_length
                if content_length and content_length > self.max_response_size:
                    raise SSRFError("Response too large")

                # Read with size limit
                body = await response.content.read(self.max_response_size + 1)
                if len(body) > self.max_response_size:
                    raise SSRFError("Response exceeded size limit")

                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": body.decode('utf-8', errors='replace'),
                    "url": str(response.url)
                }

    async def fetch_with_redirect_handling(
        self, url: str, max_redirects: int = 3
    ) -> dict:
        """Fetch with safe redirect following (re-validates each hop)."""
        current_url = url
        for _ in range(max_redirects):
            result = await self.fetch(current_url)

            if result["status"] in (301, 302, 303, 307, 308):
                location = result["headers"].get("Location")
                if not location:
                    break

                # CRITICAL: Validate redirect target against SSRF rules
                # Redirects are a common SSRF bypass technique
                current_url = location
                continue

            return result

        raise SSRFError("Too many redirects")


class PinnedResolver:
    """DNS resolver that returns pre-validated IPs."""

    def __init__(self, hostname: str, pinned_ips: list):
        self.hostname = hostname
        self.pinned_ips = pinned_ips

    async def resolve(self, host: str, port: int = 0, family: int = 0):
        """Return pinned IPs instead of performing DNS lookup."""
        if host == self.hostname:
            return [
                {"hostname": host, "host": ip, "port": port,
                 "family": socket.AF_INET, "proto": 0, "flags": 0}
                for ip in self.pinned_ips
            ]
        raise SSRFError(f"Unexpected hostname in resolution: {host}")
```

## Domain Allowlisting for Agent Tools

For maximum security, agent tools operate with explicit domain allowlists based on their function:

```python
# Per-agent-tool URL allowlists
TOOL_ALLOWLISTS = {
    "web_search": {
        # Search engine APIs
        "api.search.brave.com",
        "www.googleapis.com",
        "api.bing.microsoft.com",
    },
    "github_integration": {
        "api.github.com",
        "raw.githubusercontent.com",
        "github.com",
    },
    "documentation_fetch": {
        "docs.python.org",
        "developer.mozilla.org",
        "docs.aws.amazon.com",
        "cloud.google.com",
    },
    "webhook_delivery": {
        # Customer-configured webhook URLs (validated at config time)
        # Loaded from tenant configuration
    }
}

class ToolAwareSSRFProtector(SSRFProtector):
    """SSRF protector with per-tool domain allowlists."""

    def __init__(self, tool_name: str):
        super().__init__(strict_mode=True)
        self.ALLOWED_DOMAINS = TOOL_ALLOWLISTS.get(tool_name, set())

    def add_tenant_domains(self, domains: list):
        """Add tenant-configured domains (validated at config time)."""
        for domain in domains:
            # Validate domain format
            if self._is_valid_domain(domain):
                self.ALLOWED_DOMAINS.add(domain.lower())
```

## Response Sanitization

Even after validating the request, response content needs sanitization to prevent information leakage:

```python
class ResponseSanitizer:
    """Sanitize HTTP responses to prevent information leakage."""

    # Patterns that indicate internal service responses
    INTERNAL_INDICATORS = [
        r"amazonaws\.com.*metadata",
        r"computeMetadata",
        r"kube-system",
        r"internal\..*\.svc\.cluster\.local",
        r"X-Forwarded-For.*10\.\d+\.\d+\.\d+",
    ]

    def sanitize(self, response: dict) -> dict:
        """Remove or flag internal information from responses."""
        import re

        body = response.get("body", "")

        for pattern in self.INTERNAL_INDICATORS:
            if re.search(pattern, body, re.IGNORECASE):
                raise SSRFError(
                    "Response contains internal infrastructure information. "
                    "This may indicate an SSRF bypass attempt."
                )

        # Strip sensitive headers
        headers = response.get("headers", {})
        sensitive_headers = [
            "X-Real-IP", "X-Forwarded-For", "X-Internal-Request",
            "Server", "X-Powered-By"
        ]
        for header in sensitive_headers:
            headers.pop(header, None)

        response["headers"] = headers
        return response
```

## Monitoring and Alerting

We monitor for SSRF attempts through our [NATS messaging layer](/blog/nats-jetstream-ai-agents):

```python
class SSRFMonitor:
    """Monitor and alert on SSRF attempt patterns."""

    async def log_blocked_request(self, event: dict):
        """Log blocked SSRF attempt for security analysis."""
        await self.nats.publish(
            "security.ssrf.blocked",
            json.dumps({
                "agent": event["agent_name"],
                "url": event["attempted_url"],
                "reason": event["block_reason"],
                "source_task": event["task_id"],
                "timestamp": datetime.utcnow().isoformat()
            })
        )

        # Alert if pattern suggests active exploitation
        recent_blocks = await self.count_recent_blocks(
            agent=event["agent_name"],
            window=timedelta(minutes=5)
        )
        if recent_blocks > 10:
            await self.nats.publish(
                "security.findings.high",
                json.dumps({
                    "severity": "HIGH",
                    "title": "Potential SSRF exploitation attempt",
                    "agent": event["agent_name"],
                    "details": f"{recent_blocks} blocked requests in 5 minutes"
                })
            )
```

## Integration with Platform Security

SSRF protection integrates with [AI-powered security reviews](/blog/ai-security-reviews) at the CI/CD level. Our CSO agent verifies that new [MCP tool integrations](/blog/mcp-tool-integration) include SSRF protection before deployment, preventing regression.

For the complete security posture, SSRF protection works alongside [path traversal defense](/blog/path-traversal-defense) (for local file access) and [NATS authentication hardening](/blog/nats-auth-hardening) (for internal service access).

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

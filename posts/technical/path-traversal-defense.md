---
title: "Path Traversal Defense in AI Agent Platforms"
slug: "path-traversal-defense"
date: 2026-05-10
category: technical
cluster: "security-compliance"
tags: [path-traversal, sandbox, workspace-isolation, security, chroot, ai-agents]
description: "Implement path traversal defense for AI agent workspaces using sandboxed environments, chroot-like isolation, and symlink attack prevention."
relatedPosts: [automated-security-auditing, ssrf-protection-ai-agents, preventing-cypher-injection]
---

# Path Traversal Defense in AI Agent Platforms

AI agents that interact with file systems face a fundamental security challenge: how do you grant an agent legitimate file access within its workspace while preventing it from reading `/etc/shadow`, traversing to other agents' workspaces, or following symlinks to sensitive system files? At agent.ceo, our AI CSO agent's [automated security audit](/blog/automated-security-auditing) uncovered three HIGH-severity path traversal vulnerabilities -- workspace escape via `../` sequences, symlink following to host filesystem, and unrestricted glob patterns that could enumerate directory structures outside the sandbox.

This post details the attack vectors, our defense architecture, and the implementation patterns that provide chroot-like isolation for autonomous AI agents.

## The Attack Surface

In a multi-agent platform, each agent operates within a designated workspace. The agent might need to:

- Read and write files for task execution
- Access configuration files within its workspace
- Create temporary files during processing
- Read input files provided by other agents or users

Each of these legitimate operations becomes an attack vector if path validation is insufficient.

### Vulnerability 1: Classic Path Traversal

```python
# VULNERABLE: Direct path concatenation without validation
class AgentWorkspace:
    def __init__(self, agent_id: str):
        self.base_path = f"/workspaces/{agent_id}"

    def read_file(self, filename: str) -> str:
        """Read a file from the agent's workspace."""
        filepath = os.path.join(self.base_path, filename)
        with open(filepath, 'r') as f:
            return f.read()
```

**Attack**: An agent (or compromised input) requests `filename = "../../etc/passwd"`:

```python
# os.path.join("/workspaces/agent-1", "../../etc/passwd")
# Results in: "/etc/passwd" -- outside the workspace!
```

### Vulnerability 2: Symlink Following

```python
# Even with basic path checking, symlinks bypass validation
workspace.read_file("reports/latest")
# Where "reports/latest" is a symlink -> /etc/shadow
```

An attacker who can create files in the workspace (e.g., through a file upload or another compromised agent) can plant symlinks that point outside the sandbox.

### Vulnerability 3: Null Byte Injection (in older systems)

```python
# In systems with C-based path handling
filename = "report.pdf\x00../../etc/passwd"
# Path validation sees "report.pdf" but file open follows the full path
```

## Defense Architecture: Layered Workspace Isolation

We implement defense in depth with four layers:

```
Layer 4: Application-level path validation
Layer 3: Linux namespace isolation (mount namespace)
Layer 2: Filesystem-level restrictions (chroot-like)
Layer 1: Kernel-level enforcement (seccomp, AppArmor)
```

### Layer 1: Kernel-Level Enforcement

Each agent container runs with a restrictive seccomp profile and AppArmor policy:

```json
{
  "comment": "Agent workspace seccomp profile",
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", "stat", "fstat"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "names": ["openat"],
      "action": "SCMP_ACT_ALLOW",
      "args": [
        {
          "index": 1,
          "value": 0,
          "op": "SCMP_CMP_EQ",
          "comment": "Only allow openat with AT_FDCWD"
        }
      ]
    },
    {
      "names": ["symlink", "symlinkat", "link", "linkat"],
      "action": "SCMP_ACT_ERRNO",
      "comment": "Prevent symlink creation entirely"
    },
    {
      "names": ["mount", "umount2", "pivot_root", "chroot"],
      "action": "SCMP_ACT_ERRNO",
      "comment": "Prevent filesystem manipulation"
    }
  ]
}
```

The corresponding AppArmor profile:

```
# /etc/apparmor.d/agent-workspace
profile agent-workspace {
  # Allow read/write only within workspace
  /workspaces/{agent_id}/** rw,
  /workspaces/{agent_id}/ r,

  # Deny traversal targets explicitly
  deny /etc/** rwklx,
  deny /proc/** rwklx,
  deny /sys/** rwklx,
  deny /workspaces/*/  r,  # Other agent workspaces

  # Deny symlink following outside workspace
  deny link /workspaces/{agent_id}/** -> /**,

  # Allow specific system libraries (read-only)
  /usr/lib/** r,
  /lib/** r,
}
```

### Layer 2: Mount Namespace Isolation

Each agent's workspace uses a dedicated mount namespace that limits the filesystem view:

```yaml
# Kubernetes pod security context for agent workspace
apiVersion: v1
kind: Pod
metadata:
  name: agent-workspace-cso
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    fsGroup: 10001
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/agent-workspace.json
  containers:
  - name: agent
    image: agent-runtime:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
    volumeMounts:
    - name: workspace
      mountPath: /workspace
      # Agent sees only its own workspace at /workspace
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: workspace
    persistentVolumeClaim:
      claimName: agent-cso-workspace
  - name: tmp
    emptyDir:
      medium: Memory
      sizeLimit: 100Mi
```

### Layer 3: Application-Level Path Validation

Even with kernel-level protection, we implement strict path validation at the application layer:

```python
import os
from pathlib import Path, PurePosixPath
from typing import Optional

class SecureWorkspace:
    """Sandboxed workspace with path traversal prevention."""

    def __init__(self, agent_id: str, base_path: str = "/workspace"):
        self.agent_id = agent_id
        self.base_path = Path(base_path).resolve()

        # Verify base path exists and is a directory
        if not self.base_path.is_dir():
            raise SecurityError(f"Workspace not found: {self.base_path}")

    def _resolve_safe_path(self, user_path: str) -> Path:
        """
        Resolve a user-provided path safely within the workspace.
        Raises SecurityError if the path would escape the sandbox.
        """
        # Step 1: Reject obviously malicious input
        if '\x00' in user_path:
            raise SecurityError("Null bytes not allowed in paths")

        if user_path.startswith('/'):
            raise SecurityError("Absolute paths not allowed")

        # Step 2: Normalize without resolving symlinks first
        normalized = PurePosixPath(user_path)

        # Check for traversal in the logical path
        try:
            normalized.relative_to('.')
        except ValueError:
            raise SecurityError(f"Path traversal detected: {user_path}")

        # Step 3: Construct the full path
        candidate = self.base_path / normalized

        # Step 4: Resolve symlinks and verify containment
        try:
            resolved = candidate.resolve(strict=False)
        except (OSError, ValueError) as e:
            raise SecurityError(f"Path resolution failed: {e}")

        # Step 5: Verify the resolved path is within workspace
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise SecurityError(
                f"Path escapes workspace: {user_path} "
                f"resolves to {resolved}, outside {self.base_path}"
            )

        # Step 6: Check that no component is a symlink pointing outside
        current = self.base_path
        for part in normalized.parts:
            current = current / part
            if current.is_symlink():
                link_target = current.resolve()
                try:
                    link_target.relative_to(self.base_path)
                except ValueError:
                    raise SecurityError(
                        f"Symlink escape detected: {current} -> {link_target}"
                    )

        return resolved

    def read_file(self, path: str) -> str:
        """Safely read a file within the workspace."""
        safe_path = self._resolve_safe_path(path)

        if not safe_path.is_file():
            raise FileNotFoundError(f"Not a file: {path}")

        # Size limit to prevent memory exhaustion
        if safe_path.stat().st_size > 10 * 1024 * 1024:  # 10 MB
            raise SecurityError("File exceeds maximum size (10 MB)")

        return safe_path.read_text()

    def write_file(self, path: str, content: str) -> None:
        """Safely write a file within the workspace."""
        safe_path = self._resolve_safe_path(path)

        # Prevent writing to existing symlinks
        if safe_path.exists() and safe_path.is_symlink():
            raise SecurityError("Cannot write to symlink")

        # Create parent directories if needed (within sandbox)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content)

    def list_directory(self, path: str = ".") -> list:
        """Safely list directory contents within workspace."""
        safe_path = self._resolve_safe_path(path)

        if not safe_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        entries = []
        for entry in safe_path.iterdir():
            # Mark symlinks but don't follow them for listing
            entry_info = {
                "name": entry.name,
                "is_file": entry.is_file(),
                "is_dir": entry.is_dir(),
                "is_symlink": entry.is_symlink(),
                "size": entry.stat().st_size if entry.is_file() else None
            }
            entries.append(entry_info)

        return entries
```

### Layer 4: Glob and Wildcard Restrictions

Unrestricted glob patterns can be used for directory enumeration:

```python
class SecureGlob:
    """Restricted glob that prevents workspace escape."""

    MAX_RESULTS = 1000
    MAX_DEPTH = 5

    def __init__(self, workspace: SecureWorkspace):
        self.workspace = workspace

    def glob(self, pattern: str) -> list:
        """Execute a glob pattern within workspace boundaries."""
        # Reject patterns that could traverse
        if '..' in pattern:
            raise SecurityError("Traversal in glob pattern")

        if pattern.startswith('/'):
            raise SecurityError("Absolute glob patterns not allowed")

        # Limit recursion depth
        depth = pattern.count('/') + pattern.count('**') * self.MAX_DEPTH
        if depth > self.MAX_DEPTH:
            raise SecurityError(f"Glob depth exceeds limit ({self.MAX_DEPTH})")

        # Execute within sandbox
        results = []
        for match in self.workspace.base_path.glob(pattern):
            # Verify each result is within workspace
            try:
                match.resolve().relative_to(self.workspace.base_path)
                results.append(str(match.relative_to(self.workspace.base_path)))
            except ValueError:
                continue  # Skip matches that resolve outside workspace

            if len(results) >= self.MAX_RESULTS:
                break

        return results
```

## Testing the Defenses

We maintain a comprehensive test suite for path traversal prevention:

```python
import pytest

class TestPathTraversalDefense:
    """Verify workspace isolation against traversal attacks."""

    TRAVERSAL_PAYLOADS = [
        "../etc/passwd",
        "../../etc/shadow",
        "....//....//etc/passwd",
        "..%2f..%2fetc%2fpasswd",
        "%2e%2e/%2e%2e/etc/passwd",
        "..\\..\\etc\\passwd",
        "....\\\\....\\\\etc\\passwd",
        "/etc/passwd",
        "workspace/../../../etc/passwd",
        "reports/./../../etc/passwd",
    ]

    SYMLINK_ATTACKS = [
        ("malicious_link", "/etc/passwd"),
        ("nested/deep/link", "/etc/shadow"),
        ("innocent.txt", "/workspaces/other-agent/secrets"),
    ]

    @pytest.fixture
    def workspace(self, tmp_path):
        ws = SecureWorkspace("test-agent", str(tmp_path))
        (tmp_path / "legitimate.txt").write_text("safe content")
        return ws

    @pytest.mark.parametrize("payload", TRAVERSAL_PAYLOADS)
    def test_traversal_blocked(self, workspace, payload):
        with pytest.raises(SecurityError):
            workspace.read_file(payload)

    @pytest.mark.parametrize("link_name,target", SYMLINK_ATTACKS)
    def test_symlink_escape_blocked(self, workspace, link_name, target, tmp_path):
        # Create malicious symlink
        link_path = tmp_path / link_name
        link_path.parent.mkdir(parents=True, exist_ok=True)
        link_path.symlink_to(target)

        with pytest.raises(SecurityError):
            workspace.read_file(link_name)

    def test_legitimate_access_works(self, workspace):
        content = workspace.read_file("legitimate.txt")
        assert content == "safe content"
```

## Deployment in Kubernetes

For organizations running [AI agents on Kubernetes](/blog/kubernetes-ai-agents), workspace isolation integrates with Pod Security Standards:

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: agent-workspace-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities: ["ALL"]
  volumes: ["persistentVolumeClaim", "emptyDir"]
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: MustRunAsNonRoot
  fsGroup:
    rule: RunAsAny
  readOnlyRootFilesystem: true
  allowedHostPaths: []  # No host path access
```

## Key Takeaways

1. **Never trust path input**: Always resolve and validate paths before any file operation
2. **Layer defenses**: Combine kernel enforcement (seccomp, AppArmor), namespace isolation, and application validation
3. **Block symlinks**: Either prevent symlink creation entirely or validate link targets before following
4. **Limit scope**: Agents get read-only root filesystem with writable workspace only
5. **Test adversarially**: Maintain a payload library and test every file operation against it

Path traversal defense is one pillar of the broader security posture for [AI agent platforms](/blog/what-are-ai-agents). Combined with [SSRF protection](/blog/ssrf-protection-ai-agents) and proper [credential management](/blog/credential-management-multi-cloud), it ensures that autonomous agents operate safely within their designated boundaries.

> GenBrain AI is the company behind agent.ceo, building the next generation of autonomous agent orchestration.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*

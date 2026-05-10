---
title: "2FA/MFA Implementation for AI Platforms"
slug: "2fa-mfa-ai-platforms"
date: 2026-05-10
category: technical
cluster: "security-compliance"
tags: [2fa, mfa, totp, webauthn, passkeys, authentication, security]
description: "Implement TOTP, backup codes, and WebAuthn/passkeys for AI agent platforms. Covers RFC 6238 compliance, bcrypt hashing, and phishing resistance."
relatedPosts: [automated-security-auditing, credential-management-multi-cloud, nats-auth-hardening]
---

# 2FA/MFA Implementation for AI Platforms

When your platform orchestrates autonomous AI agents that manage infrastructure, deploy code, and handle sensitive data, single-factor authentication is not enough. A compromised password grants an attacker control over an entire fleet of AI agents -- the blast radius is orders of magnitude greater than a compromised individual account. At agent.ceo, we are implementing multi-factor authentication that covers human operators, API access, and critical agent operations, building on TOTP (RFC 6238), bcrypt-hashed backup codes, and a WebAuthn/passkeys roadmap for phishing-resistant authentication.

This post covers our implementation architecture, the specific cryptographic choices we made, and how MFA integrates with an [AI agent platform](/blog/what-are-ai-agents).

## Why MFA Matters More for AI Platforms

In a traditional SaaS application, a compromised account affects one user's data. In an AI agent platform like agent.ceo, a compromised operator account can:

- Issue commands to any AI agent in the fleet
- Modify agent configurations and permissions
- Access credentials stored for multi-cloud operations
- Alter [knowledge graph](/blog/wiki-knowledge-graphs) data that agents rely on
- Deploy malicious code through [AI-powered DevOps](/blog/ai-powered-devops) pipelines

The force multiplication effect of AI agents means authentication security must be proportionally stronger.

## TOTP Implementation (RFC 6238)

We implement Time-based One-Time Passwords following RFC 6238 with specific hardening for AI platform use cases:

```python
import hmac
import hashlib
import struct
import time
import secrets
import base64
from dataclasses import dataclass
from typing import Optional

@dataclass
class TOTPConfig:
    """TOTP configuration following RFC 6238."""
    digits: int = 6
    period: int = 30  # seconds
    algorithm: str = "SHA1"  # RFC 6238 default, SHA256 for new enrollments
    issuer: str = "agent.ceo"
    skew: int = 1  # Allow 1 period of clock drift

class TOTPProvider:
    """RFC 6238 compliant TOTP implementation."""

    def __init__(self, config: TOTPConfig = TOTPConfig()):
        self.config = config

    def generate_secret(self) -> str:
        """Generate a cryptographically secure TOTP secret."""
        # 20 bytes (160 bits) for SHA1, 32 bytes (256 bits) for SHA256
        secret_length = 32 if self.config.algorithm == "SHA256" else 20
        secret_bytes = secrets.token_bytes(secret_length)
        return base64.b32encode(secret_bytes).decode('ascii').rstrip('=')

    def compute_totp(self, secret: str, timestamp: Optional[int] = None) -> str:
        """Compute TOTP value for a given timestamp."""
        if timestamp is None:
            timestamp = int(time.time())

        # Step 1: Compute time step (T)
        time_step = timestamp // self.config.period

        # Step 2: Convert to 8-byte big-endian
        time_bytes = struct.pack('>Q', time_step)

        # Step 3: Compute HMAC
        secret_bytes = base64.b32decode(secret + '=' * (-len(secret) % 8))
        hash_algo = getattr(hashlib, self.config.algorithm.lower())
        hmac_result = hmac.new(secret_bytes, time_bytes, hash_algo).digest()

        # Step 4: Dynamic truncation (RFC 4226 Section 5.4)
        offset = hmac_result[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_result[offset:offset + 4])[0]
        truncated &= 0x7FFFFFFF  # Clear sign bit

        # Step 5: Compute OTP value
        otp = truncated % (10 ** self.config.digits)
        return str(otp).zfill(self.config.digits)

    def verify_totp(self, secret: str, token: str, used_tokens: set) -> bool:
        """
        Verify a TOTP token with clock skew tolerance and replay prevention.
        """
        if not token or len(token) != self.config.digits:
            return False

        # Replay prevention: reject previously used tokens
        current_time = int(time.time())
        current_step = current_time // self.config.period

        if f"{current_step}:{token}" in used_tokens:
            return False

        # Check current period and allowed skew windows
        for offset in range(-self.config.skew, self.config.skew + 1):
            check_time = current_time + (offset * self.config.period)
            expected = self.compute_totp(secret, check_time)

            if hmac.compare_digest(expected, token):
                # Mark token as used to prevent replay
                used_tokens.add(f"{current_step + offset}:{token}")
                return True

        return False

    def generate_provisioning_uri(self, secret: str, account: str) -> str:
        """Generate otpauth:// URI for QR code enrollment."""
        params = (
            f"otpauth://totp/{self.config.issuer}:{account}"
            f"?secret={secret}"
            f"&issuer={self.config.issuer}"
            f"&algorithm={self.config.algorithm}"
            f"&digits={self.config.digits}"
            f"&period={self.config.period}"
        )
        return params
```

## Backup Codes: Bcrypt-Hashed Recovery

Backup codes provide account recovery when TOTP devices are lost. We generate them securely and store only bcrypt hashes:

```python
import bcrypt
import secrets
import string

class BackupCodeProvider:
    """Generate and verify backup recovery codes."""

    CODE_LENGTH = 10
    CODE_COUNT = 10
    BCRYPT_ROUNDS = 12

    def generate_backup_codes(self) -> tuple[list[str], list[str]]:
        """
        Generate backup codes. Returns (plaintext_codes, hashed_codes).
        Plaintext codes shown to user once; only hashes are stored.
        """
        alphabet = string.ascii_lowercase + string.digits
        # Remove ambiguous characters (0, o, l, 1)
        alphabet = alphabet.replace('0', '').replace('o', '')
        alphabet = alphabet.replace('l', '').replace('1', '')

        plaintext_codes = []
        hashed_codes = []

        for _ in range(self.CODE_COUNT):
            # Generate cryptographically random code
            code = ''.join(
                secrets.choice(alphabet) for _ in range(self.CODE_LENGTH)
            )
            # Format as xxxxx-xxxxx for readability
            formatted = f"{code[:5]}-{code[5:]}"
            plaintext_codes.append(formatted)

            # Hash with bcrypt for storage
            code_hash = bcrypt.hashpw(
                code.encode('utf-8'),
                bcrypt.gensalt(rounds=self.BCRYPT_ROUNDS)
            )
            hashed_codes.append(code_hash.decode('utf-8'))

        return plaintext_codes, hashed_codes

    def verify_backup_code(
        self, submitted_code: str, stored_hashes: list[str]
    ) -> tuple[bool, Optional[int]]:
        """
        Verify a backup code against stored hashes.
        Returns (is_valid, index_to_invalidate).
        Each code can only be used once.
        """
        # Normalize: remove formatting dashes
        normalized = submitted_code.replace('-', '').lower().strip()

        for index, stored_hash in enumerate(stored_hashes):
            if stored_hash is None:
                continue  # Already used

            if bcrypt.checkpw(
                normalized.encode('utf-8'),
                stored_hash.encode('utf-8')
            ):
                return True, index

        return False, None
```

## MFA Enrollment Flow

The enrollment process integrates with the agent.ceo platform:

```python
from enum import Enum
from datetime import datetime, timedelta

class MFAState(Enum):
    NOT_ENROLLED = "not_enrolled"
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    LOCKED = "locked"

class MFAEnrollmentService:
    """Manage MFA enrollment lifecycle."""

    MAX_VERIFICATION_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(minutes=15)

    def __init__(self, totp_provider, backup_provider, user_store):
        self.totp = totp_provider
        self.backup = backup_provider
        self.store = user_store

    async def begin_enrollment(self, user_id: str) -> dict:
        """Start MFA enrollment for a user."""
        # Generate TOTP secret
        secret = self.totp.generate_secret()

        # Store temporarily (encrypted) until verified
        await self.store.save_pending_mfa(user_id, {
            "secret": encrypt(secret),
            "state": MFAState.PENDING_VERIFICATION,
            "created_at": datetime.utcnow(),
            "attempts": 0
        })

        # Generate provisioning URI for QR code
        user = await self.store.get_user(user_id)
        uri = self.totp.generate_provisioning_uri(secret, user.email)

        return {
            "provisioning_uri": uri,
            "secret": secret,  # Also show for manual entry
            "message": "Scan QR code with authenticator app, then verify"
        }

    async def verify_enrollment(self, user_id: str, token: str) -> dict:
        """Verify TOTP token to complete enrollment."""
        pending = await self.store.get_pending_mfa(user_id)

        if not pending:
            raise ValueError("No pending MFA enrollment")

        if pending["attempts"] >= self.MAX_VERIFICATION_ATTEMPTS:
            await self.store.delete_pending_mfa(user_id)
            raise SecurityError("Too many failed attempts. Restart enrollment.")

        secret = decrypt(pending["secret"])

        if self.totp.verify_totp(secret, token, set()):
            # Enrollment verified - generate backup codes
            plaintext_codes, hashed_codes = self.backup.generate_backup_codes()

            # Activate MFA
            await self.store.activate_mfa(user_id, {
                "totp_secret": encrypt(secret),
                "backup_codes": hashed_codes,
                "state": MFAState.ACTIVE,
                "enrolled_at": datetime.utcnow()
            })

            await self.store.delete_pending_mfa(user_id)

            return {
                "status": "enrolled",
                "backup_codes": plaintext_codes,
                "message": "Save these backup codes securely. They will not be shown again."
            }
        else:
            pending["attempts"] += 1
            await self.store.save_pending_mfa(user_id, pending)
            raise ValueError("Invalid token. Please try again.")
```

## MFA for Critical Agent Operations

Beyond human login, we enforce MFA for high-risk agent operations -- a concept we call "step-up authentication":

```python
class StepUpAuthPolicy:
    """Require additional authentication for critical operations."""

    CRITICAL_OPERATIONS = {
        "agent.deploy_to_production": "totp",
        "agent.modify_credentials": "totp",
        "agent.access_other_workspace": "totp",
        "admin.modify_agent_permissions": "totp",
        "admin.rotate_master_keys": "webauthn",  # Highest security
        "admin.delete_agent": "totp",
        "billing.modify_payment": "totp",
    }

    async def authorize_operation(
        self, user_id: str, operation: str, mfa_token: Optional[str]
    ) -> bool:
        """Check if operation requires step-up auth and verify."""
        required_method = self.CRITICAL_OPERATIONS.get(operation)

        if not required_method:
            return True  # Operation doesn't require MFA

        if not mfa_token:
            raise MFARequiredError(
                f"Operation '{operation}' requires {required_method} verification"
            )

        user_mfa = await self.store.get_mfa_config(user_id)

        if required_method == "totp":
            return self.totp.verify_totp(
                decrypt(user_mfa["totp_secret"]),
                mfa_token,
                user_mfa["used_tokens"]
            )
        elif required_method == "webauthn":
            return await self.verify_webauthn(user_id, mfa_token)

        return False
```

## WebAuthn/Passkeys Roadmap

Our roadmap includes WebAuthn support for phishing-resistant authentication. Here is the planned architecture:

```python
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement
)

class WebAuthnProvider:
    """WebAuthn/passkey authentication provider (roadmap)."""

    RP_ID = "agent.ceo"
    RP_NAME = "agent.ceo"
    ORIGIN = "https://app.agent.ceo"

    async def begin_registration(self, user_id: str) -> dict:
        """Generate WebAuthn registration challenge."""
        user = await self.store.get_user(user_id)

        options = generate_registration_options(
            rp_id=self.RP_ID,
            rp_name=self.RP_NAME,
            user_id=user_id.encode(),
            user_name=user.email,
            user_display_name=user.display_name,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED
            ),
            # Exclude already-registered credentials
            exclude_credentials=await self.get_existing_credentials(user_id)
        )

        # Store challenge for verification
        await self.store.save_challenge(user_id, options.challenge)

        return options

    async def complete_registration(self, user_id: str, response: dict) -> bool:
        """Verify WebAuthn registration response."""
        challenge = await self.store.get_challenge(user_id)

        verification = verify_registration_response(
            credential=response,
            expected_challenge=challenge,
            expected_rp_id=self.RP_ID,
            expected_origin=self.ORIGIN
        )

        # Store credential for future authentication
        await self.store.save_credential(user_id, {
            "credential_id": verification.credential_id,
            "public_key": verification.credential_public_key,
            "sign_count": verification.sign_count,
            "registered_at": datetime.utcnow()
        })

        return True
```

## Rate Limiting and Brute Force Protection

MFA verification endpoints need aggressive rate limiting:

```python
from datetime import datetime, timedelta
from collections import defaultdict

class MFARateLimiter:
    """Prevent brute force attacks against MFA verification."""

    MAX_ATTEMPTS = 5
    WINDOW = timedelta(minutes=5)
    LOCKOUT = timedelta(minutes=30)
    PROGRESSIVE_DELAY = [0, 1, 2, 4, 8]  # seconds

    def __init__(self):
        self.attempts = defaultdict(list)
        self.lockouts = {}

    async def check_rate_limit(self, user_id: str) -> None:
        """Check if user is rate limited. Raises if locked out."""
        # Check lockout
        if user_id in self.lockouts:
            lockout_until = self.lockouts[user_id]
            if datetime.utcnow() < lockout_until:
                remaining = (lockout_until - datetime.utcnow()).seconds
                raise RateLimitError(
                    f"Account locked. Try again in {remaining} seconds."
                )
            else:
                del self.lockouts[user_id]

        # Clean old attempts outside window
        cutoff = datetime.utcnow() - self.WINDOW
        self.attempts[user_id] = [
            t for t in self.attempts[user_id] if t > cutoff
        ]

        # Check attempt count
        attempt_count = len(self.attempts[user_id])
        if attempt_count >= self.MAX_ATTEMPTS:
            self.lockouts[user_id] = datetime.utcnow() + self.LOCKOUT
            await self.alert_security(user_id, attempt_count)
            raise RateLimitError("Too many failed attempts. Account locked.")

        # Apply progressive delay
        if attempt_count < len(self.PROGRESSIVE_DELAY):
            delay = self.PROGRESSIVE_DELAY[attempt_count]
            if delay > 0:
                await asyncio.sleep(delay)

    async def record_attempt(self, user_id: str, success: bool):
        """Record an MFA verification attempt."""
        if not success:
            self.attempts[user_id].append(datetime.utcnow())
        else:
            # Reset on success
            self.attempts[user_id] = []
```

## Integration with Agent Platform Architecture

MFA integrates with the broader [agent.ceo architecture](/blog/architecture-agent-ceo) through the [API gateway](/blog/api-gateway-ai-agents):

```yaml
# API gateway MFA enforcement rules
mfa_policy:
  # All admin endpoints require MFA
  - path_prefix: "/api/v1/admin/"
    require: "totp"
    session_validity: "15m"

  # Agent management requires MFA
  - path_prefix: "/api/v1/agents/*/config"
    methods: ["PUT", "DELETE"]
    require: "totp"

  # Credential operations require strongest factor
  - path_prefix: "/api/v1/credentials/"
    methods: ["POST", "PUT", "DELETE"]
    require: "webauthn"
    fallback: "totp"

  # Read operations don't require step-up
  - path_prefix: "/api/v1/"
    methods: ["GET"]
    require: "session"  # Standard session auth sufficient
```

## SOC 2 Compliance Mapping

Our MFA implementation maps directly to SOC 2 requirements:

- **CC6.1**: Logical and physical access controls -- MFA enforces multi-factor verification
- **CC6.2**: Registration and authorization -- enrollment flow with verification
- **CC6.3**: Role-based access -- step-up auth for privileged operations
- **CC6.6**: System boundaries -- MFA at all entry points to the platform

This is part of our broader SOC 2 preparation, alongside the [automated security auditing](/blog/automated-security-auditing) performed by our CSO agent and our [credential management](/blog/credential-management-multi-cloud) practices.

> agent.ceo offers both SaaS and enterprise private installation options for organizations of any size.

## Try agent.ceo

**SaaS** — Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise** — For private installation on your own infrastructure, contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo).

---
*agent.ceo is built by [GenBrain AI](https://genbrain.ai) — a GenAI-first autonomous agent orchestration platform. General inquiries: hello@agent.ceo | Security: security@agent.ceo*

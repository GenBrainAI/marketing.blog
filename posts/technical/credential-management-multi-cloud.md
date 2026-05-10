---
title: "Credential Management for Multi-Cloud AI Agents"
slug: "credential-management-multi-cloud"
date: 2026-05-10
category: technical
cluster: "security-compliance"
tags: [credential-management, multi-cloud, iam, least-privilege, secret-rotation, aws, gcp, azure]
description: "Manage credentials for AI agents across AWS, GCP, and Azure with least-privilege IAM, automatic rotation, encrypted storage, and scoped access."
relatedPosts: [automated-security-auditing, nats-auth-hardening, 2fa-mfa-ai-platforms]
---

# Credential Management for Multi-Cloud AI Agents

AI agents that operate across cloud providers need credentials -- API keys, IAM roles, service account tokens, OAuth tokens -- to interact with infrastructure, deploy resources, and manage services. The challenge: how do you grant agents the access they need while maintaining least-privilege, enforcing automatic rotation, and preventing credential theft from becoming a catastrophic breach? At agent.ceo, our agents access AWS, GCP, and Azure with scoped credentials that rotate automatically, are stored encrypted, and are audited continuously by our [AI CSO agent](/blog/automated-security-auditing).

This post details our credential management architecture, the implementation patterns for each cloud provider, and how we maintain SOC 2 compliance across a multi-cloud AI agent fleet.

## The Problem: Credential Sprawl in Multi-Agent Systems

A typical agent.ceo deployment includes 10+ specialized agents, each needing access to different cloud resources:

| Agent | AWS Access | GCP Access | Azure Access |
|-------|-----------|------------|--------------|
| DevOps Agent | ECS, ECR, CloudWatch | GKE, Cloud Build | AKS |
| CSO Agent | GuardDuty, SecurityHub | Security Command Center | Sentinel |
| Data Agent | S3, Athena | BigQuery, GCS | Blob Storage |
| Marketing Agent | SES | -- | -- |
| CTO Agent | All (elevated) | All (elevated) | All (elevated) |

Without proper management, this creates dozens of credentials with varying lifetimes, scopes, and rotation schedules -- a security nightmare.

## Architecture: Centralized Credential Vault

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional
import asyncio

class CredentialType(Enum):
    AWS_IAM_ROLE = "aws_iam_role"
    AWS_ACCESS_KEY = "aws_access_key"
    GCP_SERVICE_ACCOUNT = "gcp_service_account"
    GCP_WORKLOAD_IDENTITY = "gcp_workload_identity"
    AZURE_MANAGED_IDENTITY = "azure_managed_identity"
    AZURE_SERVICE_PRINCIPAL = "azure_service_principal"
    OAUTH_TOKEN = "oauth_token"
    API_KEY = "api_key"

class CredentialScope:
    """Define the minimum permissions an agent needs."""

    def __init__(self, agent_name: str, cloud: str, permissions: list):
        self.agent_name = agent_name
        self.cloud = cloud
        self.permissions = permissions
        self.max_duration = timedelta(hours=1)  # Short-lived by default

# Per-agent credential scopes (least privilege)
AGENT_CREDENTIAL_SCOPES = {
    "devops-agent": [
        CredentialScope(
            agent_name="devops-agent",
            cloud="aws",
            permissions=[
                "ecs:UpdateService",
                "ecs:DescribeServices",
                "ecr:GetAuthorizationToken",
                "ecr:BatchGetImage",
                "cloudwatch:PutMetricData",
                "cloudwatch:GetMetricData",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
            ]
        ),
        CredentialScope(
            agent_name="devops-agent",
            cloud="gcp",
            permissions=[
                "container.clusters.get",
                "container.deployments.create",
                "container.deployments.update",
                "cloudbuild.builds.create",
            ]
        ),
    ],
    "cso-agent": [
        CredentialScope(
            agent_name="cso-agent",
            cloud="aws",
            permissions=[
                "guardduty:GetFindings",
                "guardduty:ListFindings",
                "securityhub:GetFindings",
                "securityhub:BatchGetSecurityControls",
                # READ-ONLY: CSO cannot modify resources
            ]
        ),
    ],
}
```

## AWS: Assumed Roles with Session Policies

For AWS, we use IAM role assumption with session policies that further restrict permissions per-agent:

```python
import boto3
from botocore.config import Config

class AWSCredentialProvider:
    """Provide scoped, short-lived AWS credentials to agents."""

    def __init__(self, vault_client, audit_logger):
        self.vault = vault_client
        self.audit = audit_logger
        self.sts_client = boto3.client('sts')

    async def get_agent_credentials(
        self, agent_name: str, scope: CredentialScope
    ) -> dict:
        """
        Generate short-lived AWS credentials for an agent
        using role assumption with session policy.
        """
        # Base role for the agent (defined in AWS IAM)
        role_arn = f"arn:aws:iam::123456789012:role/agent-{agent_name}"

        # Session policy restricts the role's permissions further
        session_policy = self._build_session_policy(scope)

        response = self.sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=f"{agent_name}-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}",
            DurationSeconds=3600,  # 1 hour max
            Policy=json.dumps(session_policy),
            Tags=[
                {"Key": "agent", "Value": agent_name},
                {"Key": "purpose", "Value": "automated-operation"},
                {"Key": "rotated_at", "Value": datetime.utcnow().isoformat()}
            ]
        )

        credentials = {
            "access_key_id": response["Credentials"]["AccessKeyId"],
            "secret_access_key": response["Credentials"]["SecretAccessKey"],
            "session_token": response["Credentials"]["SessionToken"],
            "expiration": response["Credentials"]["Expiration"].isoformat()
        }

        # Audit credential issuance
        await self.audit.log(
            event="credential_issued",
            agent=agent_name,
            cloud="aws",
            role=role_arn,
            expiration=credentials["expiration"],
            permissions=scope.permissions
        )

        return credentials

    def _build_session_policy(self, scope: CredentialScope) -> dict:
        """Build an IAM session policy from scope definition."""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": scope.permissions,
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "aws:RequestedRegion": ["us-east-1", "us-west-2"]
                        },
                        # Prevent privilege escalation
                        "BoolIfExists": {
                            "aws:MultiFactorAuthPresent": "true"
                        }
                    }
                },
                {
                    "Effect": "Deny",
                    "Action": [
                        "iam:*",
                        "organizations:*",
                        "sts:AssumeRole",  # Prevent role chaining
                    ],
                    "Resource": "*"
                }
            ]
        }
```

## GCP: Workload Identity Federation

For GCP, we use Workload Identity Federation to eliminate long-lived service account keys entirely:

```python
from google.auth import credentials
from google.auth.transport.requests import Request
from google.cloud import iam_credentials_v1

class GCPCredentialProvider:
    """Provide scoped GCP credentials via Workload Identity Federation."""

    def __init__(self, project_id: str, workload_pool: str):
        self.project_id = project_id
        self.workload_pool = workload_pool
        self.iam_client = iam_credentials_v1.IAMCredentialsClient()

    async def get_agent_credentials(
        self, agent_name: str, scope: CredentialScope
    ) -> dict:
        """
        Generate short-lived GCP access token for an agent.
        Uses Workload Identity - no persistent keys.
        """
        # Service account per agent (least privilege)
        service_account = (
            f"agent-{agent_name}@{self.project_id}.iam.gserviceaccount.com"
        )

        # Generate short-lived access token
        response = self.iam_client.generate_access_token(
            name=f"projects/-/serviceAccounts/{service_account}",
            scope=self._permissions_to_oauth_scopes(scope.permissions),
            lifetime={"seconds": 3600}  # 1 hour
        )

        return {
            "access_token": response.access_token,
            "expiration": response.expire_time.isoformat(),
            "service_account": service_account
        }

    def _permissions_to_oauth_scopes(self, permissions: list) -> list:
        """Map granular permissions to OAuth scopes."""
        scope_map = {
            "container.": "https://www.googleapis.com/auth/cloud-platform",
            "cloudbuild.": "https://www.googleapis.com/auth/cloud-platform",
            "bigquery.": "https://www.googleapis.com/auth/bigquery",
            "storage.": "https://www.googleapis.com/auth/devstorage.read_write",
        }

        scopes = set()
        for perm in permissions:
            for prefix, oauth_scope in scope_map.items():
                if perm.startswith(prefix):
                    scopes.add(oauth_scope)
                    break

        return list(scopes)
```

## Azure: Managed Identity with Conditional Access

```python
from azure.identity import ManagedIdentityCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient

class AzureCredentialProvider:
    """Provide scoped Azure credentials to agents."""

    def __init__(self, tenant_id: str, vault_url: str):
        self.tenant_id = tenant_id
        self.vault_url = vault_url

    async def get_agent_credentials(
        self, agent_name: str, scope: CredentialScope
    ) -> dict:
        """
        Get Azure credentials for an agent using Managed Identity
        when running in Azure, or Key Vault for cross-cloud.
        """
        # Prefer Managed Identity (no secrets to manage)
        try:
            credential = ManagedIdentityCredential(
                client_id=f"agent-{agent_name}-identity"
            )
            token = credential.get_token(
                *self._permissions_to_scopes(scope.permissions)
            )
            return {
                "access_token": token.token,
                "expiration": datetime.fromtimestamp(token.expires_on).isoformat(),
                "method": "managed_identity"
            }
        except Exception:
            # Fall back to Key Vault stored credentials (cross-cloud)
            return await self._get_from_key_vault(agent_name, scope)

    async def _get_from_key_vault(self, agent_name: str, scope) -> dict:
        """Retrieve credentials from Azure Key Vault."""
        vault_credential = ManagedIdentityCredential()
        client = SecretClient(
            vault_url=self.vault_url,
            credential=vault_credential
        )

        secret = client.get_secret(f"agent-{agent_name}-credential")
        return json.loads(secret.value)
```

## Encrypted Storage Layer

All credentials at rest are encrypted with envelope encryption:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import os

class CredentialStore:
    """Encrypted credential storage with envelope encryption."""

    def __init__(self, master_key_provider):
        self.master_key_provider = master_key_provider

    def encrypt_credential(self, credential: dict) -> dict:
        """Encrypt a credential using envelope encryption."""
        # Generate a unique data encryption key (DEK) per credential
        dek = Fernet.generate_key()
        fernet = Fernet(dek)

        # Encrypt the credential with DEK
        plaintext = json.dumps(credential).encode('utf-8')
        encrypted_data = fernet.encrypt(plaintext)

        # Encrypt the DEK with the master key (KEK)
        master_key = self.master_key_provider.get_current_key()
        kek_fernet = Fernet(master_key)
        encrypted_dek = kek_fernet.encrypt(dek)

        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode(),
            "key_version": self.master_key_provider.current_version,
            "algorithm": "Fernet/AES-128-CBC-HMAC-SHA256",
            "encrypted_at": datetime.utcnow().isoformat()
        }

    def decrypt_credential(self, stored: dict) -> dict:
        """Decrypt a credential from storage."""
        # Get the correct master key version
        master_key = self.master_key_provider.get_key(
            version=stored["key_version"]
        )
        kek_fernet = Fernet(master_key)

        # Decrypt the DEK
        encrypted_dek = base64.b64decode(stored["encrypted_dek"])
        dek = kek_fernet.decrypt(encrypted_dek)

        # Decrypt the credential
        fernet = Fernet(dek)
        encrypted_data = base64.b64decode(stored["encrypted_data"])
        plaintext = fernet.decrypt(encrypted_data)

        return json.loads(plaintext.decode('utf-8'))
```

## Automatic Rotation Orchestration

Credentials rotate automatically based on type and risk level:

```python
class CredentialRotationOrchestrator:
    """Orchestrate credential rotation across all cloud providers."""

    ROTATION_SCHEDULES = {
        CredentialType.AWS_IAM_ROLE: timedelta(hours=1),      # Session-based
        CredentialType.AWS_ACCESS_KEY: timedelta(days=1),      # Daily
        CredentialType.GCP_SERVICE_ACCOUNT: timedelta(hours=1),# Token-based
        CredentialType.GCP_WORKLOAD_IDENTITY: timedelta(hours=1),
        CredentialType.AZURE_MANAGED_IDENTITY: timedelta(hours=1),
        CredentialType.OAUTH_TOKEN: timedelta(hours=4),        # Per provider
        CredentialType.API_KEY: timedelta(days=7),             # Weekly
    }

    async def run_rotation_cycle(self):
        """Check and rotate all credentials that are due."""
        all_credentials = await self.store.list_all_credentials()

        for cred in all_credentials:
            schedule = self.ROTATION_SCHEDULES[cred.type]
            time_since_rotation = datetime.utcnow() - cred.last_rotated

            if time_since_rotation >= schedule:
                try:
                    await self.rotate_credential(cred)
                    await self.audit.log(
                        event="credential_rotated",
                        credential_id=cred.id,
                        agent=cred.agent_name,
                        cloud=cred.cloud,
                        old_age=str(time_since_rotation)
                    )
                except RotationError as e:
                    await self.alert(
                        severity="HIGH",
                        message=f"Credential rotation failed: {e}",
                        credential=cred.id
                    )

    async def rotate_credential(self, cred):
        """Rotate a specific credential with zero-downtime."""
        provider = self.get_provider(cred.cloud)

        # Phase 1: Generate new credential
        new_cred = await provider.generate_new_credential(cred)

        # Phase 2: Distribute to agent (both old and new valid)
        await self.distribute_to_agent(cred.agent_name, new_cred)

        # Phase 3: Verify agent is using new credential
        verified = await self.verify_agent_using_new(
            cred.agent_name, new_cred, timeout=timedelta(minutes=5)
        )

        if verified:
            # Phase 4: Revoke old credential
            await provider.revoke_credential(cred)
            await self.store.update_credential(cred.id, new_cred)
        else:
            # Rollback
            await provider.revoke_credential(new_cred)
            raise RotationError(
                f"Agent {cred.agent_name} did not adopt new credential"
            )
```

## Audit Trail and Compliance

Every credential operation is logged for SOC 2 compliance:

```python
class CredentialAuditLogger:
    """Immutable audit log for all credential operations."""

    async def log(self, **event):
        """Log a credential event to immutable audit trail."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": str(uuid.uuid4()),
            **event,
            # Integrity hash for tamper detection
            "integrity_hash": self._compute_hash(event)
        }

        # Write to append-only audit log
        await self.audit_store.append(entry)

        # Publish to security monitoring
        await self.nats.publish(
            "security.audit.credentials",
            json.dumps(entry)
        )

    # SOC 2 CC6.1 evidence: all credential access logged
    # SOC 2 CC6.2: credential lifecycle from issuance to revocation
    # SOC 2 CC7.2: continuous monitoring of credential usage
```

## Integration with Platform Architecture

Credential management integrates with the [agent.ceo platform](/blog/architecture-agent-ceo) at multiple levels:

- **Agent startup**: Agents receive scoped credentials via the [MCP tool system](/blog/mcp-tool-integration)
- **Runtime requests**: Short-lived tokens issued on-demand with per-request audit
- **Cross-agent isolation**: No agent can access another agent's credentials
- **Monitoring**: The CSO agent continuously verifies credential hygiene

For organizations deploying [SaaS AI agent platforms](/blog/saas-platform-ai-agents), this credential architecture ensures tenant isolation at the cloud IAM layer, not just the application layer.

## Key Takeaways

1. **Eliminate long-lived credentials**: Use role assumption, workload identity, and managed identity
2. **Scope aggressively**: Each agent gets only the permissions it needs, with session policies as a second constraint
3. **Rotate automatically**: Credentials should rotate on hours/days, never months
4. **Encrypt at rest**: Envelope encryption with separate DEK per credential
5. **Audit everything**: Every credential issuance, use, and rotation is logged immutably

## Try agent.ceo

Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

---
title: "Enterprise Security: Air-Gapped AI Agent Deployments"
slug: "enterprise-air-gapped-deployments"
date: 2026-05-10
category: marketing
cluster: "saas-vs-enterprise"
tags: [enterprise, air-gap, security, compliance, on-premises, isolated-networks]
description: "Deploy agent.ceo in fully air-gapped environments. Complete network isolation for defense, healthcare, and financial services."
relatedPosts: [private-installation-guide, saas-vs-enterprise-deployment, tco-saas-vs-self-hosted]
---

# Enterprise Security: Air-Gapped AI Agent Deployments

Some organizations cannot tolerate any outbound network connectivity from their AI infrastructure. Defense contractors, classified government programs, healthcare systems handling PHI, and financial institutions with strict data sovereignty requirements all share a common constraint: their AI agent orchestration must run in a fully air-gapped environment with zero external network dependencies.

agent.ceo supports air-gapped deployment as a first-class configuration. GenBrain AI is the company behind agent.ceo, a GenAI-first autonomous agent orchestration platform that can run entirely within an isolated network boundary — no internet access required.

## What "Air-Gapped" Means for AI Agents

An air-gapped deployment of agent.ceo means:

- **Zero outbound network traffic.** No telemetry, no update checks, no external API calls.
- **No dependency on external LLM APIs.** Language models run locally within your network.
- **All container images sourced from internal registry.** No pulls from public registries at runtime.
- **NATS messaging contained entirely within cluster.** No federation with external NATS clusters.
- **Knowledge graph fully local.** Neo4j data never leaves your network boundary.

This is not a "mostly isolated" deployment with exceptions — it is complete network severance.

## Architecture: Air-Gapped Configuration

| Component | Standard Enterprise | Air-Gapped Enterprise |
|-----------|-------------------|----------------------|
| LLM Access | External API (OpenAI, Anthropic) | Local model serving (vLLM, TGI, Ollama) |
| Container Images | Pull from agent.ceo registry | Pre-loaded to internal registry |
| Updates | Helm upgrade from remote repo | Offline bundle transfer |
| Monitoring | Optional external export | Internal-only observability |
| Authentication | Firebase Auth | On-prem OIDC (Keycloak, AD FS) |
| Certificate Authority | Public CA or Let's Encrypt | Internal CA |
| Time Sync | Public NTP | Internal NTP or GPS-disciplined clock |

## Local LLM Integration

The most significant architectural difference in an air-gapped deployment is LLM inference. Without access to external APIs, you need local model serving infrastructure.

### Supported Local Model Serving Options

| Platform | Models Supported | GPU Requirements |
|----------|-----------------|-----------------|
| vLLM | Llama 3, Mistral, Mixtral, CodeLlama | NVIDIA A100/H100 recommended |
| Text Generation Inference (TGI) | Same as vLLM | NVIDIA A100/H100 recommended |
| Ollama | Smaller models for dev/test | Consumer GPUs sufficient |

### Hardware Sizing for Local Inference

For production-grade agent orchestration with local models:

| Workload | Model Size | GPU Memory | Recommended Hardware |
|----------|-----------|-----------|---------------------|
| 5-10 concurrent agents | 70B parameters | 80 GB | 1x NVIDIA A100 80GB |
| 20-50 concurrent agents | 70B parameters | 320 GB | 4x NVIDIA A100 80GB |
| 50+ concurrent agents | 70B parameters | 640 GB+ | 8x NVIDIA A100 or 4x H100 |

The agent.ceo platform abstracts the model serving layer — agents interact with a unified inference API regardless of whether the backend is a cloud API or a local vLLM instance. See our [architecture documentation](/blog/architecture-agent-ceo) for details on how this abstraction works.

## Deployment Process for Air-Gapped Environments

### Phase 1: Offline Bundle Preparation

GenBrain AI provides an offline deployment bundle containing:

1. **Container images** — All platform images exported as OCI-compliant tarballs
2. **Helm charts** — Packaged charts with air-gap-specific values templates
3. **Validation tools** — Offline health check and integration test suite
4. **Documentation** — Full deployment runbook (no external links required)

The bundle is delivered via encrypted physical media or secure file transfer to your network's ingestion point.

### Phase 2: Internal Registry Population

```
# Load images into your internal registry
for image in ./images/*.tar; do
  skopeo copy oci-archive:$image docker://your-registry.internal/agent-ceo/$(basename $image .tar)
done
```

### Phase 3: Platform Deployment

The Helm values file for air-gapped deployments includes:

```yaml
global:
  airgap: true
  imageRegistry: your-registry.internal/agent-ceo
  
llm:
  provider: local
  endpoint: http://vllm.internal:8000/v1
  model: meta-llama/Llama-3-70B-Instruct

auth:
  provider: oidc
  issuer: https://keycloak.internal/realms/agent-ceo
  
nats:
  externalAccess: false
  
telemetry:
  enabled: false
  externalExport: false
```

### Phase 4: Validation Without Network

The offline validation suite confirms:

- All pods running with images from internal registry
- LLM inference functional via local endpoint
- NATS messaging operational between agents
- Neo4j knowledge graph persistence verified
- Authentication flow complete through internal OIDC
- No DNS resolution attempts to external domains
- No outbound connection attempts detected

## Security Controls

Air-gapped deployments include all standard agent.ceo security features plus additional isolation guarantees:

### Standard Security (All Deployments)

- 2FA/MFA enforcement
- Per-agent scoped credential access
- Encrypted credential storage (AES-256-GCM)
- Role-based access control
- Audit logging for all agent actions

### Air-Gap-Specific Security

- **Network policy enforcement**: Kubernetes NetworkPolicies prevent any pod from establishing outbound connections
- **Egress deny-all**: Default-deny egress rules at the namespace level
- **Image signature verification**: All images verified against GenBrain AI's signing key before admission
- **Binary attestation**: Supply chain verification for all deployed artifacts
- **Runtime security**: Falco or equivalent for anomaly detection

For more on our security architecture, see our [enterprise security overview](/blog/enterprise-ai-agents-security) and [credential management documentation](/blog/credential-management-multi-cloud).

## Update Process

Air-gapped environments cannot pull updates from the internet. Instead:

1. **GenBrain AI publishes release bundles** on a monthly cadence (or more frequently for critical patches)
2. **Your team transfers the bundle** to the isolated network via approved media
3. **Staged rollout** — deploy to a staging environment first, validate, then promote to production
4. **Rollback capability** — previous image versions remain in your internal registry

Critical security patches follow an expedited process. Contact [security@agent.ceo](mailto:security@agent.ceo) to establish your organization's vulnerability notification channel.

## Compliance Frameworks

Air-gapped agent.ceo deployments help satisfy requirements across multiple compliance frameworks:

| Framework | Relevant Controls | How Air-Gap Helps |
|-----------|------------------|-------------------|
| FedRAMP High | SC-7, AC-4 | Complete boundary protection |
| HIPAA | 164.312(e) | PHI never traverses public networks |
| PCI DSS | 1.3, 1.4 | No unauthorized outbound connections |
| ITAR | 120.17 | Technical data isolation |
| CMMC Level 3 | SC.3.177 | Controlled information flow |

## Real-World Use Cases

### Defense: Classified Agent Workflows

A defense contractor runs agent.ceo on a classified network with no internet connectivity. Agents assist with document analysis, requirements tracing, and test plan generation — all within the classification boundary.

### Healthcare: PHI-Processing Agents

A health system deploys agents that process patient records for clinical decision support. The air-gapped deployment ensures PHI never leaves the hospital network, satisfying HIPAA requirements without complex BAA negotiations for external services.

### Financial Services: Trading Floor Agents

A trading firm uses agent.ceo for automated code review and deployment validation. The air-gapped deployment prevents any risk of proprietary algorithm exposure through AI service provider logs.

## Getting Started

Air-gapped deployments require planning and coordination with our engineering team. The typical engagement timeline:

| Week | Activity |
|------|----------|
| 1-2 | Architecture review and hardware sizing |
| 3-4 | Offline bundle preparation and delivery |
| 5-6 | Deployment and validation |
| 7-8 | Agent development and testing |

To begin the conversation, reach out to [enterprise@agent.ceo](mailto:enterprise@agent.ceo) with your compliance framework, target environment (cloud or on-prem), and estimated agent count. Our team will schedule a technical architecture session within 48 hours.

For organizations that are still evaluating whether they need a full air-gap versus standard enterprise deployment, our [deployment comparison guide](/blog/saas-vs-enterprise-deployment) walks through the decision framework. You can also explore the [total cost of ownership analysis](/blog/tco-saas-vs-self-hosted) to understand the investment required.

## Try agent.ceo

**SaaS**: Get started with 1 free agent-week at [agent.ceo](https://agent.ceo).

**Enterprise**: Contact [enterprise@agent.ceo](mailto:enterprise@agent.ceo) for private deployment options.

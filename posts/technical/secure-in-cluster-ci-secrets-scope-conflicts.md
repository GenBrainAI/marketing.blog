---
title: "Tutorial: Securing Your In-Cluster CI Pipeline — Secrets, Scopes, and Config Conflicts"
slug: "secure-in-cluster-ci-secrets-scope-conflicts"
date: 2026-11-12
category: technical
cluster: "tutorials"
tags: [security, cloud-build, mcp, secrets, ci-cd, tutorial]
description: "Two production incidents reveal three security patterns every in-cluster CI pipeline needs: excluding secrets from build tarballs, eliminating dual-scope tool registrations, and replacing hard exits with graceful shutdowns."
relatedPosts:
  - /blog/in-cluster-deploy-cloud-build-api-gke
  - /blog/crash-resilient-mcp-wrapper-startup-race
  - /blog/mcp-stdio-foreground-exec-background-stdin-devnull
  - /blog/image-pinning-latest-tag-customer-agent-drift
  - /blog/outer-loop-shell-script-keeps-agents-alive
---

# Securing Your In-Cluster CI Pipeline: Secrets, Scopes, and Config Conflicts

Two incidents. Same week. Neither triggered an alert. Both leaked credentials or killed agent tooling in ways that were completely invisible until someone went looking.

The first: our deploy pipeline was uploading `.env` files, PEM keys, and service account credentials to GCS inside every build tarball. The second: a dual-scope MCP registration was silently bypassing crash recovery, causing agent tools to vanish mid-session with no error and no way to bring them back.

This tutorial walks through both incidents and extracts three security patterns that apply to any in-cluster CI pipeline -- not just ours.

## Incident 1: Secrets in the Build Tarball

Our in-cluster deploy pipeline (`cluster_build.py`) packages the source into a tarball, uploads it to a GCS staging bucket, and submits it to Cloud Build. The script had an `EXCLUDE_PATTERNS` list to keep junk out of the tarball:

```python
EXCLUDE_PATTERNS = [
    '.git',
    'node_modules',
    '__pycache__',
    '.pyc',
]
```

This list was written to save bandwidth, not for security. Every file not in the list went into the tarball and sat in a GCS bucket accessible to anyone with the right IAM role. That included:
- `.env` and `.env.production` files containing API keys
- `*.pem` and `*.key` files -- TLS certificates and private keys
- `credentials.json` -- service account credentials
- `service-account*.json` -- GCP service account key files
- `.secrets.baseline` -- the detect-secrets baseline (which lists where secrets live in the codebase)
- The `.claude/` directory -- Claude Code configuration that can contain API keys

None of these belong in a GCS bucket. But because the exclude list was built to skip large directories rather than protect sensitive files, they shipped with every build.

### The Fix: Glob Patterns and fnmatch

The expanded exclusion list:

```python
EXCLUDE_PATTERNS = [
    '.git',
    'node_modules',
    '__pycache__',
    '.pyc',
    # Sensitive files — never include in build tarballs
    '.env*',
    '*.pem',
    '*.key',
    'credentials.json',
    'service-account*.json',
    '.secrets.baseline',
    '.claude',
]
```

But adding patterns was not enough. The original `should_exclude()` function used simple string matching:

```python
# BEFORE: broken for glob patterns
def should_exclude(path):
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path:
            return True
    return False
```

This works for exact names like `.git` and `node_modules`. It does not work for `*.pem` or `.env*`. The string `*.pem` is not a substring of `server.pem`. You need glob matching.

The fix switched to `fnmatch`:

```python
import fnmatch

def should_exclude(path):
    basename = os.path.basename(path)
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(basename, pattern):
            return True
        if fnmatch.fnmatch(path, pattern):
            return True
    return False
```

Matching against both the basename and the full path catches files regardless of directory depth. A `credentials.json` three directories deep gets excluded just like one at the root.

## Pattern 1: Exclude Sensitive Files from Build Context

The build context -- whether it is a Docker build context, a Cloud Build tarball, or a CI artifact upload -- should never contain credentials. This applies regardless of whether the credentials end up in the final image.

Rules:
- **Use glob patterns, not exact filenames.** `*.pem` catches `server.pem`, `ca-bundle.pem`, and `tls-2026.pem`. A hardcoded list of known filenames misses the one someone adds next month.
- **Use proper glob matching.** Python's `fnmatch`, Docker's `.dockerignore`, and GCloud's `.gcloudignore` all support glob syntax. Simple `in` or `==` string checks do not expand wildcards.
- **Exclude the detection tools too.** `.secrets.baseline` tells an attacker exactly which files contain secrets. Tool configuration directories (`.claude/`, `.vscode/`) may contain tokens.
- **Treat the exclusion list as a security control.** Review it during security audits. Test it -- write a test that creates a file matching each sensitive pattern and asserts it does not appear in the built tarball.

## Incident 2: Dual-Scope MCP Registration

Our agent-hub MCP server provides the tools agents use to communicate: `send_to_agent`, `get_agent_inbox`, `complete_task_unverified`. If it dies, the agent is deaf and mute.

We had built a [crash-resilient wrapper](/blog/crash-resilient-mcp-wrapper-startup-race) that handles restarts and exponential backoff. The wrapper was registered at the user scope:

```bash
claude mcp add -s user agent-hub /path/to/mcp_wrapper.sh
```

But `configure_mcp.py` also wrote a `.claude.json` file at the local scope, registering the same server as a direct Python invocation:

```json
{
  "mcpServers": {
    "agent-hub": {
      "command": "python",
      "args": ["-m", "mcp_servers.agent_hub_mcp"]
    }
  }
}
```

Two registrations. Same server name. Different scopes. Different code paths. One had crash recovery. One did not.

Claude Code resolves MCP server names by scope priority. Sometimes it picked the wrapper. Sometimes the direct invocation. When it picked the direct invocation and the process died -- NATS disconnect, memory spike, `ConnectionResetError` -- the tools vanished permanently. No retry. No recovery. No error message.

### The Fix: Four Changes

**1. `configure_mcp.py` -- prefer the wrapper.** When the wrapper exists and is executable, register it as the MCP command instead of the direct Python invocation:

```python
wrapper_path = os.path.expanduser("~/mcp_wrapper.sh")
if os.path.isfile(wrapper_path) and os.access(wrapper_path, os.X_OK):
    mcp_config["command"] = wrapper_path
    mcp_config["args"] = []
```

**2. `entrypoint_unified.sh` -- clean up conflicts.** At startup, remove any conflicting user-scope registrations and clean up stale entries left by prior versions. One registration. One scope. One code path.

**3. `memory_watchdog.py` -- graceful shutdown.** The memory watchdog was using `os._exit()` to terminate when memory limits were hit. This skips all Python cleanup: `atexit` handlers, `finally` blocks, open file handle flushing, and network connection teardown. The fix: raise `SystemExit` instead, letting Python run its cleanup stack.

**4. `agent_hub_mcp.py` -- catch `ConnectionResetError`.** The server was catching `BrokenPipeError` (client hung up) but not `ConnectionResetError` (client connection was forcibly reset). Both indicate client disconnection and should trigger the same graceful shutdown path.

## Pattern 2: One Registration Scope Per Tool

MCP servers, LSP servers, and other tool registrations can exist at multiple scopes: user, project, workspace, local. When the same name appears in multiple scopes, the runtime picks one based on priority rules that may not be obvious -- and if only one scope has crash recovery, you have a coin-flip chance of running without it.

The fix is structural:
- **Choose one scope as authoritative.** For agent infrastructure, that is usually the local project scope -- it is version-controlled and reproducible.
- **Clean up conflicting scopes at startup.** The entrypoint script should remove stale registrations from other scopes before the agent session begins.
- **Point every scope to the same executable.** If you cannot prevent dual registration (some tools auto-register), at least ensure both entries invoke the crash-resilient wrapper rather than the raw binary.

## Pattern 3: Graceful Shutdown vs. Hard Exit

`os._exit()` terminates the process immediately -- no `atexit` handlers, no `finally` blocks, no file flushing, no socket cleanup. In agent infrastructure, hard exits cause:
- **Stale PID files** that make the next process think a previous instance is still running.
- **Dangling network connections** that hold NATS subscriptions or database connections open until the server-side timeout fires (often 30-60 seconds).
- **Zombie processes** when the watchdog kills a child but the child's children (grandchild processes) are not in the same process group.

`SystemExit` is the correct alternative. Python runs cleanup in order: `finally` blocks unwind, `atexit` handlers fire, file buffers flush, context managers exit. The process still terminates -- cleanly.

The same principle applies to error handling. `BrokenPipeError` and `ConnectionResetError` are two faces of the same event: the client is gone. Catching one but not the other means half your disconnections cause unhandled exceptions instead of clean shutdowns.

## Putting It Together

These three patterns share a theme: the thing that breaks your pipeline is never the thing you built defenses for. You excluded `.git` because it was big, not because it was secret -- and missed the `.env` next to it. You built crash recovery and then registered a second code path that bypassed it.

Security in CI pipelines is about closing the gaps between the tools you already have:

1. Your exclude list needs glob matching, not string matching.
2. Your tool registrations need exactly one scope, not two.
3. Your shutdown path needs cleanup, not a hard kill.

None of these are hard fixes. The hard part is finding them before they cause an incident -- and that takes the habit of asking: "What happens when this goes wrong in a way I did not plan for?"

---

*GenBrain AI runs a fleet of autonomous agents in production on GKE. Both incidents described here were real. The fixes are in production. If you are building agent infrastructure or in-cluster CI pipelines, [agent.ceo](https://agent.ceo) is where we share what we learn.*

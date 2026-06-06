---
title: "Level-Triggered vs Edge-Triggered: Why Our Agent Hot-Looped on Stale Inbox Items"
slug: "level-triggered-edge-triggered-agent-pending-work"
date: 2026-10-13
category: technical
cluster: "architecture-deep-dives"
tags: [edge-triggered, level-triggered, hot-loop, fingerprint-ledger, wrapper, deep-dive]
description: "Our CEO agent restarted every 2 seconds for hours because its wrapper kept re-detecting the same stale inbox items. The fix came from hardware interrupt design: stop checking whether work exists, start checking whether new work appeared."
relatedPosts:
  - /blog/outer-loop-shell-script-keeps-agents-alive
  - /blog/ceo-relaunch-loop-strategy-inbox-flood
  - /blog/detect-break-agent-retry-loops-production
  - /blog/ralph-loop-one-task-per-session-anti-drift
  - /blog/prompt-watchdog-daemon-keeps-agents-working
---

# Level-Triggered vs Edge-Triggered: Why Our Agent Hot-Looped on Stale Inbox Items

The CEO agent was restarting every two seconds. Not crashing. Not erroring. Cleanly exiting, immediately restarting, cleanly exiting, immediately restarting. A perfect, unbreakable loop burning tokens and compute while accomplishing nothing.

The wrapper script was doing exactly what it was told: check for pending work after each session, and if there's work, restart fast so the agent picks it up. The problem wasn't the logic. The problem was the *trigger model*. We were level-triggered when we needed to be edge-triggered.

This is a deep dive into a concept borrowed from hardware interrupt design that turned out to be the exact framing we needed to fix a production hot-loop in our agent fleet.

## The wrapper's job

Every agent in our fleet runs inside a [wrapper script](/blog/outer-loop-shell-script-keeps-agents-alive) that manages the agent lifecycle. When the agent exits cleanly (finished its work, nothing left to do), the wrapper calls a `check_pending_work()` function before deciding what to do next.

`check_pending_work()` looks in two places: the agent's inbox directory (`agent_inbox/pending/tasks/`) for files representing incoming messages, and the TMS (Task Management System) for tasks assigned to this agent's role with a status of "assigned" or "accepted."

If it finds anything, it writes a trigger file (`/tmp/inbox_new_message`) and fast-restarts the agent in 2 seconds instead of the normal longer backoff. The idea: if there's work waiting, don't make it wait.

## What went wrong

The original implementation checked whether pending items *exist*. Files in the inbox? Work found. Tasks in TMS with status "assigned"? Work found. Simple, correct, catastrophic.

Here's why: some items are never consumed. A comms test probe message sits in the inbox permanently with the subject "COMMS TEST (ignore)." The agent reads it, correctly ignores it, and the file stays. A stale TMS task that the agent can't act on -- wrong state, missing dependency, already handled in a previous session -- also stays in "assigned" status.

The wrapper doesn't know any of this. It just sees: files exist. Work found. Restart.

The agent wakes up, reads the same stale items, ignores them, exits cleanly. The wrapper checks again. Same files. Same tasks. Work found. Restart. Two seconds later, same thing. Two seconds after that, same thing. An unbreakable 2-second loop.

## Level-triggered vs edge-triggered: the hardware analogy

This failure mode has a precise name in hardware interrupt design, and the name makes the fix obvious.

**Level-triggered** interrupts fire as long as the signal is HIGH. The interrupt handler *must* clear the condition, or the interrupt fires again immediately. Think of it as a smoke alarm that screams as long as smoke is present. If you can't clear the smoke, the alarm never stops.

**Edge-triggered** interrupts fire on the *transition* from LOW to HIGH. Once the transition fires the interrupt, the signal can stay HIGH forever without re-firing. The interrupt only fires again when the signal goes LOW and then back HIGH -- a new event. Think of it as a doorbell: it rings when someone presses it, not continuously while the button is held down.

Our `check_pending_work()` was a smoke alarm in a room with permanent haze. The stale items were smoke that could never be cleared. What we needed was a doorbell: ring when *new* work appears, stay quiet when the same old work is still sitting there.

## The fix: a fingerprint ledger

The solution is a persistent ledger file (`/agent-data/config/seen_pending_work`) stored on the agent's PVC. It tracks which items have already been surfaced to the agent.

Each pending item gets a fingerprint combining its filename, modification time, and size:

```python
def fp(p):
    st = p.stat()
    return f'{p.name}:{int(st.st_mtime)}:{st.st_size}'
```

The fingerprint is deliberately not content-based. It's fast (just a stat call, no file read) and it catches the cases that matter: a file rewritten with new content gets a new mtime and possibly a new size, so it re-triggers. Same file, untouched? Same fingerprint. Already seen.

On each call to `check_pending_work()`:

1. Collect fingerprints for every currently pending item -- inbox files and TMS tasks alike.
2. Load the set of previously-seen fingerprints from the ledger.
3. Compare: `new = [label for pfp, label in pending if pfp not in seen]`.
4. If new items exist, return "work found." Edge triggered.
5. If every item was already seen, return "no work." Stale items don't re-trigger.
6. Rewrite the ledger with the current fingerprint set.

Step 6 is critical for long-term health. The ledger is rewritten with only the *currently pending* fingerprints. If an item was consumed (the agent processed it and the file was removed), its fingerprint drops out of the ledger automatically. No unbounded growth. The ledger stays proportional to the count of currently pending items, not the total items ever seen.

## Atomic persistence

The ledger rewrite uses atomic file replacement:

```python
tmp = seen_file.with_suffix('.tmp')
tmp.write_text('\n'.join(sorted({pfp for pfp, _ in pending})))
os.replace(tmp, seen_file)
```

Write to a temp file, then `os.replace()` atomically swaps it into place. A concurrent reader (or a crash mid-write) never sees a truncated or half-written ledger. This matters because the wrapper can be interrupted by signals at any point.

## The broken PAUSE gate

While investigating the hot-loop, we found a second bug hiding behind it. The operator has a `/loop-pause` command that creates a `PAUSE` file on disk. This is the emergency stop -- it's supposed to halt all automated restarts and prompt injection so a human can intervene.

But two code paths ignored the PAUSE file entirely: the fast-restart path in `check_pending_work()` and the post-start tmux wakeup injection that sends "check your inbox" to the agent. With both paths ignoring PAUSE, the emergency stop couldn't actually stop anything. The hot-loop was unstoppable even when the operator tried to intervene.

The fix: both paths now gate on `[[ ! -f "$PAUSE_FILE" ]]` before acting. When paused, `check_pending_work()` is skipped entirely -- no fast restart. The post-start wakeup injection is also skipped -- no "check your inbox" prompt. The agent sits idle until the operator removes the PAUSE file.

## Why no special-casing

It would have been tempting to fix this by filtering out known stale items -- skip anything with "COMMS TEST" in the subject, ignore tasks older than N hours. That approach is brittle. The next unconsumed item type would create the same hot-loop, and we'd be playing whack-a-mole forever.

The fingerprint ledger is content-agnostic. It doesn't know or care *why* an item is stale. It only knows whether the agent has already been woken up for it. Any item, regardless of type or content, triggers exactly once. Future item types work without code changes.

## Verification

We tested the fix with a standalone harness covering four scenarios:

- **Stale item**: an unconsumed inbox file triggers the first check, then goes quiet on subsequent checks. Edge-triggered behavior confirmed.
- **New work**: a genuinely new task file still triggers a restart. The edge detection doesn't over-filter.
- **Changed item**: same filename but new mtime (rewritten content) re-triggers. The fingerprint catches the change.
- **Drained inbox**: after all items are consumed and removed, the ledger prunes their fingerprints. No unbounded growth.

## The broader lesson

Level-triggered detection is the default because it's simpler to implement. "Is there work? If yes, act." But level-triggered only works when the handler can *clear the condition*. If items can be permanently pending -- and in any system with agents that selectively process their inboxes, they can -- level-triggered detection degrades into a hot-loop.

Edge-triggered detection costs a small amount of state (the ledger) but eliminates an entire class of failure. The pattern applies anywhere you have a polling loop that checks for "things to do": message queues with dead letters, task schedulers with permanently blocked tasks, health checkers with known-unhealthy endpoints.

The fingerprint ledger is twelve lines of Python and one file on disk. The hot-loop it fixed was burning hours of compute. That's the kind of leverage you get when you reach for the right abstraction instead of the first one that compiles.

---

*GenBrain AI is the company behind [agent.ceo](https://agent.ceo) -- a platform where AI agents run an organization with real roles, real accountability, and real production bugs. We write about what we learn the hard way so you don't have to.*

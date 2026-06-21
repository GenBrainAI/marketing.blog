# Launch social — Platform Keys + Prepaid Credits (DRAFT — HOLD for founder sign-off)

> 🟡 **DRAFT — DO NOT PUBLISH.** Publish is HELD pending founder sign-off after live verification + the funded founder test org. Drafted 2026-06-20 for task-73666e00. Founder-posts-manually workflow; flip to READY only after CEO relays the founder's go.
>
> ⛔ **GA-GATING (CEO 2026-06-20 22:05Z):** Feature is currently founder-test-only (probe-credits-qa), NOT general availability. These posts are the GA version — the "run X on a wallet today" framing must not go out until CEO confirms self-signup is open and gives the GA signal + canonical publish date. Time the post to actual GA, don't imply it's live for everyone the moment the founder tests it.
> Feature details grounded in the two live docs (fetched 2026-06-20): /docs/prepaid-credits, /docs/coding-agent-key-setup.
> Companion blog draft: workspace/blog/2026-06-21-one-wallet-any-coding-agent-prepaid-credits.md
> Doc links (both, curl 200 2026-06-20): https://agent.ceo/docs/prepaid-credits + https://agent.ceo/docs/coding-agent-key-setup
> X limit 280; t.co links = 23 each. Counts measured below.

---

## 1. Launch — LinkedIn  *(DRAFT — HOLD)*
**Hook:** one wallet, any coding agent — stop juggling five providers' API keys.
**Links:** both docs.

```
Spinning up an AI coding agent usually starts with a scavenger hunt: an Anthropic key for Claude Code, an OpenAI key for Codex, a Google key for Gemini, something else for the next runtime. Five signups, five cards, five things to rotate or forget to turn off.

We're shipping two features that collapse that into one decision.

Platform keys: pick a runtime — claude-code, codex, gemini-cli, opencode, or hermes (model-agnostic via OpenRouter) — and the credentials are handled underneath. Or bring your own keys (BYOK), or set them up later. Your call, per organization.

Prepaid credits: fund a single USD wallet in $100 bulks. Usage is metered live, in dollars, at provider cost + a small markup (1.5x). When the balance hits zero, agents pause automatically — usage never runs unbounded. Prefer continuity? Auto-recharge tops up from your saved card with a daily cap, and a failed charge keeps agents paused instead of retrying silently.

A hard floor at zero turns the scariest thing about autonomous spend — the runaway loop — from a financial event into a one-click pause.

Pick a runtime, fund a wallet, let your agents work:
→ Credits: agent.ceo/docs/prepaid-credits
→ Key setup: agent.ceo/docs/coding-agent-key-setup
```

---

## 2. Launch — X  *(DRAFT — HOLD)*
**Hook:** one wallet, any coding agent.
**Link:** prepaid-credits doc.

```
Stop juggling five providers' API keys. Run Claude Code, Codex, Gemini, OpenCode or Hermes on one prepaid USD wallet — metered live in dollars, agents pause at $0 so usage never runs unbounded. Optional auto-recharge with a daily cap → agent.ceo/docs/prepaid-credits
```
*(259 chars with t.co link — under 280, measured)*

---

## 3. Launch — X  *(DRAFT — HOLD)*
**Hook:** bring a card, not five keys (key-sources angle).
**Link:** coding-agent-key-setup doc.

```
Three ways to credential your agent fleet on agent.ceo: run on platform keys billed to a prepaid wallet, bring your own key, or set up later. Pick a runtime — claude-code, codex, gemini-cli, opencode, hermes — and credentials are handled underneath → agent.ceo/docs/coding-agent-key-setup
```
*(274 chars with t.co link — under 280, measured)*

---

_Pipeline note: 🟡 DRAFT — HOLD for founder sign-off. Do NOT publish until CEO relays the founder's go after live verification. Blog + this social set together cover: 5 runtimes, 3 key sources, $100 USD wallet, 1.5x markup, pause-at-$0, auto-recharge, and link both live docs._

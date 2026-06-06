---
platform: twitter
status: draft
date: 2026-08-23
note: Saturday technical — MDX gotcha thread
---

## Thread: The MDX gotcha that will break your AI content pipeline

If you generate blog content with AI and deploy to an MDX-based site, you will hit this bug. Here is what happens and how to fix it:

---

1/ THE PROBLEM. Markdown (.md) is forgiving. MDX (.mdx) is not. MDX parses content as JSX. A bare angle bracket without a closing tag crashes the entire build. Your .md renders fine. The identical content in .mdx does not.

---

2/ WHY AI MAKES IT WORSE. LLMs write angle brackets constantly -- comparisons, HTML-like examples, placeholder text. In .md, harmless. In .mdx, every one is a build-breaking JSX parse error. And the error message points to the wrong line.

---

3/ THE FIX. Add regex verification between generation and commit. Strip code blocks first (those are safe). Then check for unescaped angle brackets in the remaining text. If any fail, rewrite the line before committing.

---

4/ THE RESULT. Our agent runs this on every post. 10 consecutive posts, 0 build failures. The check adds 2 seconds per post. The alternative is a broken deploy at 2am.

agent.ceo/blog/ai-marketing-agent-content-pipeline-case-study #MDX #AIAgents #ContentAutomation

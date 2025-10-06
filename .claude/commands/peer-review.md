peer-review (EcoMind Edition)

ROLE
You are Claude Code, performing a second-opinion technical review of Codex’s primary review for the EcoMind project — a privacy-first AI sustainability tracker that calculates carbon, water, and energy usage across LLM and API calls.

INPUT

Primary review path: ./codex_reviews/latest.md

Referenced patch (if any):

./codex_diffs/latest.patch or a timestamped variant under ./codex_diffs/

Context files may include:

Frontend: ./ext-chrome/src/

Backend / API: ./server/ or ./webapp/

Shared logic: ./common/metrics/, ./common/energy_calc/

STRICT REQUIREMENTS

Fair, objective, and verifiable. Be explicit about uncertainty.

Evidence-based critique — include file:line references with ≤2-line code quotes.

Comprehensive Checklist:

✅ Builds & lints (TypeScript, Python, manifest v3, CI)

⚙️ Logic / invariants / edge cases (e.g., metric resets, API errors, offline mode)

⚡ Performance & complexity (avoid redundant energy calculations, background task leaks)

🔒 Security / input validation (API key privacy, local storage, permissions)

🔁 API & backward compatibility (Chrome extension manifest, metric schema)

🧠 Error handling / logging / telemetry (especially user privacy compliance)

🌍 i18n / config / docs / deps (language strings, .env vars, dependencies)

If Codex’s review is weak, misleading, or harmful, state why and recommend rejection or revision clearly.

You may propose a single minimal unified diff (in diff syntax), but do not apply it.

Disk Persistence (Claude meta-review only) — never write to ./codex_reviews/*:

REPORT FILES

Write meta-review to:

./codex_meta_reviews/claude/ror_<YYYYMMDD_HHMMSS>.md

Update symlink/copy: ./codex_meta_reviews/claude/latest.md

OPTIONAL PATCH FILES (if emitted)

Write to:

./codex_meta_reviews/claude/diffs/diff_<YYYYMMDD_HHMMSS>.patch

Update symlink/copy: ./codex_meta_reviews/claude/diffs/latest.patch

Timestamped files are append-only. Rotate latest.* safely (symlink preferred).
Always print absolute paths under the Artifacts section.

Never write or modify any files in ./codex_reviews/* to avoid recursive triggers.

Be concise and structured — no hidden reasoning chain.

OUTPUT FORMAT

Summary
Brief statement of your findings and Codex’s review quality.

Evidence Review
File-line evidence and context for key agreements/disagreements.

Checklist Review
Table or list summarizing which areas are ✅ OK, ⚠️ partial, ❌ weak.

Risks
Enumerate concrete risks (logic, security, perf, user data privacy, etc.).

Alternatives (optional)
If Codex missed better approaches, note them here.

Patch (optional unified diff in ```diff)

Tests
Show snippets or assertions that would fail before → pass after.

Rollback Plan
How to revert or disable changes safely (especially in browser extension context).

Artifacts
Absolute paths of generated meta-review and patch files.

Verdict
APPROVE or REQUEST_CHANGES + a one-sentence rationale.
# show-me-the-code

ROLE  
You are Claude Code. Start an investigation for the user request (feature/bug/refactor) in the Ecomind Chrome extension. Identify impacted files, show relevant code, propose a strictly minimal and safe change, and **do not apply anything** until the user approves.

INPUT  
- The user describes the intent for the Ecomind Chrome extension (AI usage tracking, environmental impact estimation, privacy features, etc.). Examine the repository. Quote relevant lines with file:line (d2 lines per citation).

STRICT REQUIREMENTS  
1) Locate and **show** the exact code sections you plan to change (file:line + d2-line quotes).  
2) Explain *why* this location is correct and what invariants you preserve for the extension's core functionality.  
3) Propose the **smallest** change that solves the intent without breaking AI tracking or privacy features.  
4) Output a **single unified diff** in a ```diff fenced block.  
5) **Disk Persistence** (ONLY if `status` is NOT `"approved_by_claude"`):
   - PATCH (apply-safe):
     - Write unified diff ONLY to: `./codex_diffs/diff_<YYYYMMDD_HHMMSS>.patch`
     - Also update: `./codex_diffs/latest.patch`
   - REVIEW (LLM/human context):
     - Summary, Evidence, Checklist, Risks, Alternatives, Patch (same diff), Tests, Rollback, Verdict, Artifacts
     - To: `./codex_diffs/review_<YYYYMMDD_HHMMSS>.md`
     - Also update: `./codex_diffs/latest.review.md`
   - BUNDLE (context + diff together):
     - Full review sections **ending with** the unified diff in ```diff
     - To: `./codex_diffs/bundle_<YYYYMMDD_HHMMSS>.md`
     - Also update: `./codex_diffs/latest.bundle.md`
   - Timestamped files are append-only; only rotate latest.* (symlink preferred; copy if symlink fails).  
   - Print absolute paths under **Artifacts**.  
6) Wait for explicit **user** approval before applying any change.  
7) Be concise and evidence-based; no hidden chain-of-thought.

ECOMIND-SPECIFIC CONTEXT  
- Core functionality: Track AI API calls (OpenAI, Anthropic, etc.) without accessing prompt content
- Privacy-first: Never log conversation data, only metadata (provider, model, timestamps)
- MV3 limitations: Request body access restricted, focus on URL-based detection
- Key files: `src/bg/service-worker.ts`, `src/ui/popup.ts`, `src/ui/options.ts`, `manifest.json`
- Extension structure: TypeScript + Vite build, Chrome storage API, webRequest API

OUTPUT FORMAT  
- Summary  
- Evidence (file:line bullets, d2-line quotes)  
- Extension Impact (API tracking, privacy, MV3 compliance, UI/UX)
- Checklist (builds/lints, logic, perf, security, API/BC, error handling/logging/telemetry, i18n/config/docs/deps)  
- Risks (High/Med/Low + why, especially privacy/security risks)  
- Alternatives (optional)  
- Patch (unified diff in ```diff)  
- Tests (failing�passing, including extension loading and basic functionality)  
- Rollback Plan  
- Artifacts (absolute paths to patch/review/bundle, latest pointers or gate message)  
- Verdict (APPROVE or REQUEST_CHANGES + one sentence)
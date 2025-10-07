# auto-review

ROLE
You are Claude Code performing an automated fix-and-review workflow based on external review feedback (e.g., from Codex or human reviewers).

INPUT
- Review feedback provided as command arguments containing:
  - Severity level (High, Medium, Low)
  - File paths and line numbers
  - Issue descriptions
  - Expected fixes

WORKFLOW
1. **Parse Feedback**: Extract all issues from arguments
2. **Implement Fixes**: Address each issue with targeted code changes
3. **Verify Changes**: Ensure fixes don't break existing functionality
4. **Document**: Record what was fixed and why
5. **Optional**: Save artifacts for peer review

STRICT REQUIREMENTS
1) Address ALL issues mentioned in the feedback
2) Use targeted edits - don't refactor unrelated code
3) Verify file paths and line numbers exist before editing
4) Test critical changes (migrations, API contracts, auth/permissions)
5) Document each fix with file:line references
6) Save timestamped review report to `./codex_reviews/auto_fix_<YYYYMMDD_HHMMSS>.md`
7) Update `./codex_reviews/latest.md` as symlink or copy
8) If changes are substantial, generate unified diff in `./codex_diffs/auto_fix_<YYYYMMDD_HHMMSS>.patch`

OUTPUT FORMAT
- **Summary**: Brief overview of issues found and fixed
- **Fixes Applied**: For each issue:
  - File path:line
  - Issue description
  - Fix implemented
  - Verification performed
- **Changes**: List of modified files
- **Testing**: Tests run (if applicable)
- **Artifacts**: Paths to review report and patches
- **Status**: COMPLETED or NEEDS_MANUAL_REVIEW

EXAMPLES

Example 1: MV3 model detection issue
```
/auto-review High • ext-chrome/src/bg/service-worker.ts:88 extracts model from body but MV3 restricts request body access, causing 'unknown' models for most API calls
```

Response: Implement URL-based model extraction as fallback for web UIs (ChatGPT, Claude), add tooltip explaining MV3 limitation, prepare infrastructure for response header inspection.

Example 2: Missing domain tracking
```
/auto-review Medium • ext-chrome/src/common/constants.ts:48 Anthropic provider missing claude.ai domain, preventing tracking of Claude web UI usage
```

Response: Add 'claude.ai' to Anthropic domains array, implement URL-based extraction for /api/organizations/ endpoints to detect 'claude-web' usage.

Example 3: Documentation mismatch
```
/auto-review Low • ext-chrome/IMPLEMENTATION_STATUS.md:21 advertises badge counter but storage.ts:180 only implements tooltip with setTitle()
```

Response: Update documentation to reflect tooltip-only implementation, add explanation that badge was replaced with tooltip for cleaner UI.

NOTES
- Be thorough but surgical - only change what's needed
- Always verify the fix addresses the root cause
- Document reasoning for future reference
- If unsure about a fix, mark as NEEDS_MANUAL_REVIEW
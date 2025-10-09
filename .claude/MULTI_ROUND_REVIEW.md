# Multi-Round Codex Review Workflow

**Purpose**: Enable back-and-forth review iterations between Claude Code and external Codex reviewer

**Key Insight**: Each review round is a **separate call** to `codex_review_loop.py`. Claude orchestrates the loop.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Claude Code (/auto-review command)                         │
│                                                              │
│ Orchestrates the review loop:                               │
│ - Generates proposals                                       │
│ - Calls review script                                       │
│ - Parses responses                                          │
│ - Revises based on feedback                                │
│ - Decides when to implement                                 │
└──────────┬──────────────────────────────────────────────────┘
           │
           │ Calls (Round 1)
           ▼
┌─────────────────────────────────────────────────────────────┐
│ codex_review_loop.py                                        │
│                                                              │
│ Input:  /tmp/claude_proposal_v1.json                        │
│ Output: { "status": "REQUEST_CHANGES", "round": 1, ... }   │
└──────────┬──────────────────────────────────────────────────┘
           │
           │ Calls external CLI
           ▼
┌─────────────────────────────────────────────────────────────┐
│ Codex CLI (external reviewer)                               │
│                                                              │
│ Command: codex exec "Review this proposal..."              │
│ Returns: "NEEDS_REVISION: Missing tests for auth flow"     │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Flow with 3 Review Rounds

### Round 1: Initial Proposal → REQUEST_CHANGES

```
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE CODE                                                 │
│                                                              │
│ 1. Parse issue: "Hardcoded JWT secret"                     │
│ 2. Generate proposal v1:                                    │
│    - Replace with os.getenv("JWT_SECRET")                  │
│    - Raise error if missing                                 │
│ 3. Create proposal JSON:                                    │
│    {                                                         │
│      "issue": "Hardcoded JWT secret",                       │
│      "severity": "High",                                    │
│      "files": ["api/app/auth.py"],                         │
│      "diff": "- SECRET = 'hardcoded'..."                   │
│    }                                                         │
│ 4. Save to: /tmp/claude_proposal_20251009_001234.json      │
│                                                              │
│ 5. Call review script:                                      │
│    python3 .claude/scripts/codex_review_loop.py \           │
│      /tmp/claude_proposal_20251009_001234.json \            │
│      codex_reviews/conversation_20251009_001234.md          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ CODEX_REVIEW_LOOP.PY (Round 1)                              │
│                                                              │
│ 1. Read proposal from /tmp/claude_proposal_*.json           │
│ 2. Detect round number: 1 (no previous rounds in conv file)│
│ 3. Call Codex:                                              │
│    subprocess.run(['codex', 'exec', review_prompt])         │
│                                                              │
│ 4. Codex responds:                                          │
│    "Status: REQUEST_CHANGES                                 │
│     Reasoning: Crashing on missing env var is too strict   │
│     Concerns:                                                │
│     1. Prevents debugging in dev environments               │
│     2. No fallback for local testing                        │
│     Recommendations:                                         │
│     - Add dev fallback with warning"                        │
│                                                              │
│ 5. Append to conversation_20251009_001234.md:               │
│    [Claude Proposal v1]                                     │
│    <diff>                                                    │
│    [Codex Response #1]                                      │
│    Status: REQUEST_CHANGES                                  │
│    <feedback>                                                │
│                                                              │
│ 6. Return JSON to Claude (stdout):                          │
│    {                                                         │
│      "status": "REQUEST_CHANGES",                           │
│      "round": 1,                                            │
│      "feedback": "Crashing on missing env...",              │
│      "conversation_file": "codex_reviews/conv_*.md"         │
│    }                                                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE CODE (processes response)                            │
│                                                              │
│ 1. Parse JSON from stdout                                   │
│ 2. See status == "REQUEST_CHANGES"                          │
│ 3. Extract concerns:                                         │
│    - Prevents debugging in dev                              │
│    - No fallback for local testing                          │
│ 4. Revise proposal:                                         │
│    - Add: SECRET = os.getenv("JWT_SECRET", "dev-INSECURE") │
│    - Add: if SECRET == "dev-INSECURE": warnings.warn(...)   │
│ 5. Update proposal JSON (v2):                               │
│    {                                                         │
│      ...same fields...                                      │
│      "diff": "<revised diff>",                              │
│      "revision_notes": "Added dev fallback per Codex"      │
│    }                                                         │
│ 6. Save to same file (overwrites v1)                        │
│                                                              │
│ 7. LOOP BACK: Call review script again (Round 2)            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
```

### Round 2: Revised Proposal → REQUEST_CHANGES (again)

```
┌─────────────────────────────────────────────────────────────┐
│ CODEX_REVIEW_LOOP.PY (Round 2)                              │
│                                                              │
│ 1. Read proposal from /tmp/claude_proposal_*.json (v2)      │
│ 2. Detect round number: 2 (count Codex Response entries)   │
│ 3. Call Codex with revised diff                             │
│                                                              │
│ 4. Codex responds:                                          │
│    "Status: REQUEST_CHANGES                                 │
│     Reasoning: Warning should be more visible               │
│     Concerns:                                                │
│     1. warnings.warn() can be suppressed silently           │
│     Recommendations:                                         │
│     - Use logging.warning() or print to stderr"             │
│                                                              │
│ 5. Append to conversation file:                             │
│    [Claude Revision v2]                                     │
│    Revision notes: Added dev fallback per Codex             │
│    <revised diff>                                            │
│    [Codex Response #2]                                      │
│    Status: REQUEST_CHANGES                                  │
│    <feedback>                                                │
│                                                              │
│ 6. Return JSON:                                             │
│    {                                                         │
│      "status": "REQUEST_CHANGES",                           │
│      "round": 2,                                            │
│      "feedback": "Warning should be more visible...",       │
│      "conversation_file": "codex_reviews/conv_*.md"         │
│    }                                                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE CODE (processes response)                            │
│                                                              │
│ 1. Parse JSON, see REQUEST_CHANGES again                    │
│ 2. Extract concern: warnings.warn() can be suppressed       │
│ 3. Revise proposal (v3):                                    │
│    - Change to: logging.warning("Using insecure JWT...")    │
│ 4. Update proposal JSON                                     │
│ 5. LOOP BACK: Call review script again (Round 3)            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
```

### Round 3: Final Revision → APPROVE

```
┌─────────────────────────────────────────────────────────────┐
│ CODEX_REVIEW_LOOP.PY (Round 3)                              │
│                                                              │
│ 1. Read proposal v3                                         │
│ 2. Detect round number: 3                                   │
│ 3. Call Codex                                               │
│                                                              │
│ 4. Codex responds:                                          │
│    "Status: APPROVE                                         │
│     Reasoning: Secure by default (requires env var),       │
│     dev-friendly (fallback + visible warning),              │
│     proper logging. Ready for implementation."              │
│                                                              │
│ 5. Append to conversation:                                  │
│    [Claude Revision v3]                                     │
│    <final diff>                                              │
│    [Codex Response #3]                                      │
│    Status: APPROVE                                          │
│    ✅ APPROVED - Proceeding with implementation             │
│                                                              │
│ 6. Return JSON:                                             │
│    {                                                         │
│      "status": "APPROVE",                                   │
│      "round": 3,                                            │
│      "feedback": "Secure by default...",                    │
│      "conversation_file": "codex_reviews/conv_*.md"         │
│    }                                                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE CODE (implements approved change)                    │
│                                                              │
│ 1. Parse JSON, see status == "APPROVE"                      │
│ 2. Exit review loop                                         │
│ 3. Apply approved diff using Edit tool                      │
│ 4. Run verification:                                        │
│    - Build: npm run build                                   │
│    - Tests: npm test                                        │
│    - Lint: npm run lint                                     │
│ 5. Create review trail summary:                             │
│    codex_reviews/auto_review_20251009_001234.md             │
│ 6. Create patch file:                                       │
│    codex_diffs/auto_review_20251009_001234.patch            │
│ 7. Update symlinks:                                         │
│    codex_reviews/latest.md -> auto_review_*.md              │
│    codex_reviews/latest.conversation.md -> conversation_*.md│
│ 8. Report to user:                                          │
│    "✅ CODEX APPROVED after 3 rounds - Changes implemented" │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. **Stateless Review Script**
Each call to `codex_review_loop.py` is independent:
- ✅ Simple error recovery (just retry the call)
- ✅ Easy to debug (check the JSON input/output)
- ✅ Claude fully controls the loop logic

### 2. **Conversation File Tracks State**
Round number determined by counting entries in conversation file:
- ✅ Survives script crashes
- ✅ Human-readable audit trail
- ✅ No separate state file needed

### 3. **JSON Communication**
Script returns JSON on stdout:
```json
{
  "status": "APPROVE | REQUEST_CHANGES | BLOCKED",
  "round": 3,
  "feedback": "Detailed feedback from Codex",
  "conversation_file": "path/to/conversation.md"
}
```
- ✅ Easy to parse
- ✅ Structured error handling
- ✅ Extensible for future fields

### 4. **Proposal File Overwritten**
Same file used for all rounds, overwritten with revisions:
- ✅ Simple file management
- ✅ No cleanup needed
- ✅ Conversation file preserves history

---

## Error Handling

### Codex CLI Not Found
```json
{
  "status": "REQUEST_CHANGES",
  "round": 1,
  "feedback": "Codex CLI not found. Install it or set CODEX_CMD environment variable."
}
```
**Claude Action**: Report error to user, block implementation

### Codex Timeout
```json
{
  "status": "REQUEST_CHANGES",
  "round": 2,
  "feedback": "Codex review timed out after 120s - proposal may be too complex"
}
```
**Claude Action**: Simplify proposal, resubmit

### Max Rounds Exceeded
```json
{
  "status": "BLOCKED",
  "round": 6,
  "reason": "Maximum review rounds (5) exceeded",
  "action": "Manual review required - escalate to human reviewer"
}
```
**Claude Action**: Save conversation, report to user, do NOT implement

### Unclear Codex Response
```json
{
  "status": "REQUEST_CHANGES",
  "round": 1,
  "feedback": "Codex response unclear:\n<response>\n\nPlease provide clearer proposal."
}
```
**Claude Action**: Simplify proposal, add more context, resubmit

---

## Configuration

Environment variables for `codex_review_loop.py`:

```bash
# Codex CLI command
export CODEX_CMD="codex"  # Default: "codex"

# Maximum review rounds before blocking
export MAX_REVIEW_ROUNDS="5"  # Default: 5

# Codex API timeout (seconds)
export CODEX_TIMEOUT="120"  # Default: 120
```

---

## Example: Real Back-and-Forth

### User Command
```bash
/auto-review High • api/app/auth.py:42 hardcoded JWT secret
```

### Conversation File Output
```markdown
# Codex Review Conversation Transcript

**Date**: 2025-10-09 00:12:34
**Issue**: Hardcoded JWT secret in api/app/auth.py:42
**Severity**: High
**Max Rounds**: 5

---

## [Claude Proposal v1]
**Timestamp**: 2025-10-09 00:12:35

### Proposed Changes
```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET")
+ if not SECRET_KEY:
+     raise ValueError("JWT_SECRET must be set")
```

## [Codex Response #1]
**Timestamp**: 2025-10-09 00:12:48
**Status**: REQUEST_CHANGES

### Feedback
Prevents debugging in dev environments. Need dev fallback with warning.

🔄 **NEEDS REVISION** - Claude will revise and resubmit

---

## [Claude Revision v2]
**Timestamp**: 2025-10-09 00:12:52

### Revision Notes (from v1)
Added dev fallback per Codex feedback

### Proposed Changes
```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET", "dev-INSECURE")
+ if SECRET_KEY == "dev-INSECURE":
+     warnings.warn("Using insecure dev JWT secret!")
```

## [Codex Response #2]
**Timestamp**: 2025-10-09 00:13:05
**Status**: REQUEST_CHANGES

### Feedback
warnings.warn() can be suppressed. Use logging.warning() instead.

🔄 **NEEDS REVISION** - Claude will revise and resubmit

---

## [Claude Revision v3]
**Timestamp**: 2025-10-09 00:13:10

### Revision Notes (from v2)
Changed to logging.warning() per Codex

### Proposed Changes
```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET", "dev-INSECURE")
+ if SECRET_KEY == "dev-INSECURE":
+     logging.warning("Using insecure dev JWT secret - set JWT_SECRET in production!")
```

## [Codex Response #3]
**Timestamp**: 2025-10-09 00:13:23
**Status**: APPROVE

### Feedback
Secure by default (requires env var), dev-friendly (fallback + visible warning), proper logging. Ready for implementation.

✅ **APPROVED** - Proceeding with implementation

---
```

### Claude's Final Output to User
```
✅ CODEX APPROVED after 3 review rounds

**Changes Implemented**:
- api/app/auth.py:42 - Fixed hardcoded JWT secret

**Review Summary**:
- Round 1: Codex requested dev fallback
- Round 2: Codex requested better warning visibility
- Round 3: Codex approved final implementation

**Verification**:
✅ Build successful
✅ Tests pass (23/23)
✅ No lint errors

**Artifacts**:
- Conversation: codex_reviews/conversation_20251009_001234.md
- Review trail: codex_reviews/auto_review_20251009_001234.md
- Patch: codex_diffs/auto_review_20251009_001234.patch
```

---

## Benefits of This Approach

### For Claude Code
- ✅ Simple loop logic (while loop with external calls)
- ✅ Full control over revision strategy
- ✅ Easy error handling
- ✅ Can add intelligent revision logic over time

### For Codex
- ✅ Stateless - each review is independent
- ✅ Clean separation of concerns
- ✅ Can be replaced with different reviewer
- ✅ Easy to test in isolation

### For Users
- ✅ Complete audit trail
- ✅ Visible review progress (round numbers)
- ✅ Understand why changes were made
- ✅ Can intervene if review gets stuck

### For Compliance
- ✅ Proves multi-round review occurred
- ✅ Documents all concerns raised
- ✅ Shows how concerns were addressed
- ✅ Immutable conversation history

---

## Next Steps

1. ✅ Create `codex_review_loop.py` script
2. ✅ Update `/auto-review` command to use it
3. ⏳ Update `/show-me-the-code` command to use it
4. ⏳ Test with mock Codex responses
5. ⏳ Integrate with real Codex CLI
6. ⏳ Add retry logic for transient failures
7. ⏳ Add conversation file viewer UI

---

**Last Updated**: 2025-10-09
**Status**: Design complete, script implemented, ready for testing

# Recommended Codex Review Workflow for EcoMind

**Last Updated**: 2025-10-09
**Status**: OFFICIAL RECOMMENDATION

---

## TL;DR - Use `codex_review_loop.py`

For **daily development** in EcoMind, use the **codex_review_loop.py** approach:
- ✅ Designed for slash commands (`/auto-review`, `/show-me-the-code`)
- ✅ Interactive, real-time feedback
- ✅ User confirms before applying changes
- ✅ Human-readable conversation transcripts
- ✅ Simpler, stateless, safer

---

## Why This Recommendation?

### Your Current Workflow
```
You're using Claude Code interactively:
  ├─ /auto-review High • file.ts:123 issue description
  ├─ /show-me-the-code investigate feature X
  └─ Manual code changes with approval

NOT running:
  ├─ python orchestrator.py (automated batch processing)
  └─ CI/CD pipelines with auto-apply
```

### codex_review_loop.py Matches This Perfectly
- **Interactive**: You see each review round as it happens
- **Controlled**: You decide whether to apply changes
- **Flexible**: Works for any code change (bug fix, feature, refactor)
- **Safe**: Never auto-applies without your confirmation

---

## Daily Development Flow (Recommended)

### Step 1: Identify Issue
```
You notice: "JWT secret is hardcoded in api/app/auth.py"
```

### Step 2: Run Auto-Review
```
/auto-review High • api/app/auth.py:42 hardcoded JWT secret
```

### Step 3: Claude Proposes & Codex Reviews (Round 1)
```
Claude Code:
  1. Generates proposal: Replace with os.getenv("JWT_SECRET")
  2. Calls: python3 codex_review_loop.py proposal.json conv.md
  3. Codex responds: "REQUEST_CHANGES - needs dev fallback"
  4. Shows you: "Codex requested changes (round 1/5)"
```

### Step 4: Claude Revises (Round 2)
```
Claude Code:
  1. Revises: Add fallback with warning
  2. Calls: python3 codex_review_loop.py proposal.json conv.md
  3. Codex responds: "APPROVE - secure and dev-friendly"
  4. Shows you: "✅ Codex approved after 2 rounds"
```

### Step 5: You Review & Confirm
```
Claude Code shows you:
  - Conversation transcript (all rounds)
  - Final diff
  - Verification plan

You decide:
  ✅ "Apply changes" → Claude implements
  ❌ "Cancel" → Nothing applied
```

### Step 6: Changes Applied
```
Claude Code:
  ✅ Applied diff to api/app/auth.py
  ✅ Ran tests (23/23 passing)
  ✅ Saved artifacts:
     - codex_reviews/conversation_20251009_001234.md
     - codex_diffs/auto_review_20251009_001234.patch
```

---

## Available Commands

### `/auto-review` - Automated Fix with Codex Approval
```bash
/auto-review [Severity] • [file:line] [description]

Example:
/auto-review High • api/app/auth.py:42 hardcoded JWT secret
```

**What it does**:
1. Parses issue from your description
2. Generates fix proposal
3. Submits to Codex for review
4. Revises based on Codex feedback (up to 5 rounds)
5. Shows you the approved solution
6. Waits for your confirmation
7. Applies changes only if you approve

### `/show-me-the-code` - Investigation with Codex Review
```bash
/show-me-the-code [investigation request]

Example:
/show-me-the-code investigate why model detection returns unknown
```

**What it does**:
1. Investigates the codebase
2. Proposes minimal changes
3. Submits to Codex for review
4. Shows you evidence and reasoning
5. Waits for your approval
6. Implements only if you confirm

---

## Configuration

### Environment Variables
```bash
# Codex CLI command (default: "codex")
export CODEX_CMD="codex"

# Maximum review rounds before blocking (default: 5)
export MAX_REVIEW_ROUNDS="5"

# Codex API timeout in seconds (default: 120)
export CODEX_TIMEOUT="120"
```

### Test Codex CLI
```bash
# Verify Codex is installed and working
codex exec "Say hello"

# Should output something like:
# "Hello! How can I help you?"
```

---

## Review Conversation Example

After running `/auto-review`, you'll see a conversation file:

**codex_reviews/conversation_20251009_001234.md**
```markdown
# Codex Review Conversation Transcript

**Date**: 2025-10-09 00:12:34
**Issue**: Hardcoded JWT secret
**Severity**: High

---

## [Claude Proposal v1]
**Timestamp**: 2025-10-09 00:12:35

```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET")
+ if not SECRET_KEY:
+     raise ValueError("JWT_SECRET must be set")
```

## [Codex Response #1]
**Status**: REQUEST_CHANGES

**Feedback**: Prevents debugging in dev. Need fallback with warning.

🔄 **NEEDS REVISION**

---

## [Claude Revision v2]
**Timestamp**: 2025-10-09 00:12:52

**Revision Notes**: Added dev fallback per Codex

```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET", "dev-INSECURE")
+ if SECRET_KEY == "dev-INSECURE":
+     logging.warning("Using insecure dev JWT secret!")
```

## [Codex Response #2]
**Status**: APPROVE

**Feedback**: Secure by default, dev-friendly, visible warning.

✅ **APPROVED**
```

---

## Artifacts Generated

Each review creates:

### 1. Conversation Transcript
**File**: `codex_reviews/conversation_<timestamp>.md`
- Complete back-and-forth with Codex
- All proposal versions
- All Codex responses
- Timestamps for each round

### 2. Review Trail
**File**: `codex_reviews/auto_review_<timestamp>.md`
- Summary of issue
- Final approved solution
- Verification results
- Artifacts list

### 3. Unified Diff Patch
**File**: `codex_diffs/auto_review_<timestamp>.patch`
- Git-compatible patch file
- Can be applied with `git apply`
- Safe to share/review

### 4. Latest Pointers (Symlinks)
**Files**:
- `codex_reviews/latest.md` → most recent review
- `codex_reviews/latest.conversation.md` → most recent conversation
- `codex_diffs/latest.patch` → most recent patch

---

## Error Handling

### Codex CLI Not Found
```
Error: Codex CLI not found
Action: Install Codex or set CODEX_CMD environment variable
```

### Codex Timeout
```
Warning: Codex review timed out after 120s
Action: Simplify proposal or increase CODEX_TIMEOUT
```

### Max Rounds Exceeded
```
Status: BLOCKED after 5 rounds
Action: Manual review required - escalate to human reviewer
Artifacts: Review conversation saved for analysis
```

### Unclear Codex Response
```
Status: REQUEST_CHANGES
Feedback: Codex response unclear, please provide clearer proposal
Action: Simplify diff, add more context, resubmit
```

---

## When NOT to Use This Workflow

### Use orchestrator.py Instead If:

1. **Automated CI/CD Pipeline**
   - You want unattended batch processing
   - Auto-apply after review is acceptable
   - Running in Jenkins/GitHub Actions

2. **Multi-Phase Feature Planning**
   - Implementing P001, P002, P003 phases
   - Need state tracking across phases
   - Want single command to process all phases

3. **Quarterly Planning**
   - Generate roadmap for next quarter
   - Review and apply multiple large features
   - Can run overnight without supervision

**Command**: `python orchestrator.py`

---

## Best Practices

### 1. Write Clear Issue Descriptions
```
Good:
/auto-review High • api/auth.py:42 hardcoded JWT secret - should use env var

Bad:
/auto-review fix auth
```

### 2. Review Conversation Before Applying
- Read all Codex concerns
- Understand why changes were made
- Verify final solution makes sense

### 3. Check Artifacts After Implementation
```bash
# Review what was changed
cat codex_diffs/latest.patch

# See full conversation
cat codex_reviews/latest.conversation.md
```

### 4. Keep Conversation Files
- Don't delete timestamped files
- Audit trail for compliance
- Reference for future similar issues

### 5. Set Appropriate Severity
```
High:   Security issues, data loss, production blockers
Medium: Performance issues, UX problems, minor bugs
Low:    Documentation, style, refactoring
```

---

## Troubleshooting

### "Review loop not responding"
```bash
# Check Codex CLI
codex exec "test"

# Check timeout setting
echo $CODEX_TIMEOUT

# Increase if needed
export CODEX_TIMEOUT="180"
```

### "Getting REQUEST_CHANGES repeatedly"
- Codex may have valid concerns
- Review feedback carefully
- Consider manual implementation if stuck
- Max rounds limit (5) prevents infinite loops

### "Want to skip Codex review for quick fix"
```
Not recommended, but if you must:
1. Make changes manually in IDE
2. Run tests
3. Commit with explanation
4. Document why Codex review was skipped
```

---

## Migration from orchestrator.py

If you've been using orchestrator.py:

### Keep Using orchestrator.py For:
- ✅ Existing multi-phase pipelines
- ✅ CI/CD automation
- ✅ Batch processing features

### Switch to codex_review_loop.py For:
- ✅ Daily bug fixes
- ✅ Interactive development
- ✅ Single-file changes
- ✅ Slash command workflow

**Both can coexist** - they solve different problems.

---

## Next Steps

### Getting Started
1. ✅ Verify Codex CLI installed: `codex exec "hello"`
2. ✅ Set environment variables (optional)
3. ✅ Try first auto-review: `/auto-review Low • README.md:1 add badge`
4. ✅ Review conversation file
5. ✅ Apply if approved

### Learn More
- [Auto-Review Command](.claude/commands/auto-review.md)
- [Multi-Round Review Flow](.claude/MULTI_ROUND_REVIEW.md)
- [Orchestrator Comparison](.claude/ORCHESTRATOR_VS_REVIEW_LOOP.md)
- [Approval Gate Guide](.claude/APPROVAL_GATE_GUIDE.md)

---

## Questions?

**Q: Is codex_review_loop.py production-ready?**
A: Yes - it's the recommended workflow for daily development.

**Q: Can I still use orchestrator.py?**
A: Yes - both workflows are supported. Use orchestrator.py for automated pipelines.

**Q: What if Codex keeps rejecting my proposal?**
A: Review feedback carefully, revise accordingly. After 5 rounds, you'll get BLOCKED status - then escalate to manual review.

**Q: Do I need to install anything?**
A: Yes - the Codex CLI must be installed and accessible via `codex` command.

**Q: Can I customize review criteria?**
A: Yes - edit `.claude/scripts/codex_review_loop.py` to modify the review prompt.

---

**Last Updated**: 2025-10-09
**Recommendation**: Use `codex_review_loop.py` for interactive development
**Fallback**: Use `orchestrator.py` for automated batch processing

# auto-review

ROLE
You are Claude Code performing an automated code review workflow that enforces a **mandatory approval gate** from Codex AI before any implementation.

CRITICAL RULES
⛔ **NO IMPLEMENTATION WITHOUT CODEX APPROVAL** ⛔
- You MUST propose changes and wait for Codex review confirmation
- You MUST document the back-and-forth review process
- You MUST NOT apply code changes until Codex explicitly approves
- If Codex requests changes, iterate and re-submit for approval

INPUT
- Review feedback provided as command arguments containing:
  - Severity level (High, Medium, Low)
  - File paths and line numbers
  - Issue descriptions
  - Expected fixes

WORKFLOW (MANDATORY APPROVAL GATE WITH REAL CODEX)
1. **Parse Feedback**: Extract all issues from arguments
2. **Propose Solution**: Draft fixes WITHOUT applying them, create proposal JSON
3. **Submit to Codex**: Call `.claude/scripts/codex_review_loop.py` with proposal
4. **Codex Reviews**: External Codex CLI reviews and responds APPROVE or REQUEST_CHANGES
5. **Parse Codex Response**: Read JSON output from review script
6. **If REQUEST_CHANGES**:
   - Extract Codex concerns from feedback
   - Revise proposal addressing each concern
   - Save revised proposal as v2
   - Go back to step 3 (new round)
7. **If APPROVE**: Implement the approved fixes
8. **Verify Changes**: Ensure fixes work as approved
9. **Document Review Trail**: Complete conversation saved by review script

**Key Feature**: Each call to codex_review_loop.py is ONE round. Claude calls it multiple times if revisions needed.

IMPLEMENTATION STEPS (PSEUDO-CODE FOR CLAUDE)

```python
# Step 1: Parse issue from arguments
issue = parse_arguments(user_input)

# Step 2: Create proposal (WITHOUT applying)
proposal = {
    "issue": issue.description,
    "severity": issue.severity,
    "files": issue.files,
    "diff": generate_diff(issue),  # Use Read + create diff in memory
    "security_analysis": analyze_security(diff),
    "test_coverage": check_test_coverage(diff),
    "rollback_plan": create_rollback_plan(diff)
}

# Step 3: Save proposal to temp file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
proposal_file = f"/tmp/claude_proposal_{timestamp}.json"
conversation_file = f"./codex_reviews/conversation_{timestamp}.md"
save_json(proposal_file, proposal)

# Step 4: Submit to Codex (Round 1)
round_num = 1
max_rounds = 5

while round_num <= max_rounds:
    # Call external Codex reviewer
    result = bash(f"python3 .claude/scripts/codex_review_loop.py {proposal_file} {conversation_file}")

    # Parse JSON response
    response = json.loads(result.stdout)

    if response['status'] == 'APPROVE':
        # Step 7: Implement approved changes
        apply_diff(proposal['diff'])

        # Step 8: Verify
        run_tests()

        # Step 9: Document
        save_review_trail(conversation_file, proposal, response)

        return SUCCESS

    elif response['status'] == 'REQUEST_CHANGES':
        # Step 6: Revise based on Codex feedback
        concerns = extract_concerns(response['feedback'])

        # Address each concern
        revised_diff = revise_diff(proposal['diff'], concerns)

        # Update proposal
        proposal['diff'] = revised_diff
        proposal['revision_notes'] = f"Addressed {len(concerns)} concerns from round {round_num}"

        # Save revised proposal
        save_json(proposal_file, proposal)

        # Loop back to step 3 (next round)
        round_num += 1
        continue

    else:  # BLOCKED
        # Max rounds exceeded
        save_blocked_status(conversation_file)
        return BLOCKED_BY_CODEX

# If we get here, exceeded max rounds
return BLOCKED_BY_CODEX
```

STRICT REQUIREMENTS
1) **NEVER implement without Codex approval** - proposal phase is mandatory
2) **Call codex_review_loop.py for EVERY review round** - don't simulate
3) **Parse JSON response** from review script to determine next action
4) Address ALL concerns mentioned in Codex feedback before resubmitting
5) Use targeted edits - don't refactor unrelated code
6) Verify file paths and line numbers exist before editing
7) Test critical changes (migrations, API contracts, auth/permissions)
8) Document each fix with file:line references
8) Save review trail to `./codex_reviews/auto_review_<YYYYMMDD_HHMMSS>.md` with these sections:
   - **Issue Summary**: What Codex flagged
   - **Proposed Solution**: Claude's initial proposal
   - **Codex Review #1**: Codex feedback (APPROVE or REQUEST_CHANGES)
   - **Revision #N**: If changes requested, show iterations
   - **Final Approval**: Codex's APPROVE message
   - **Implementation**: What was actually applied
   - **Verification**: Test results
9) Update `./codex_reviews/latest.md` as symlink or copy
10) Generate unified diff in `./codex_diffs/auto_review_<YYYYMMDD_HHMMSS>.patch`
11) Save conversation transcript to `./codex_reviews/conversation_<YYYYMMDD_HHMMSS>.md`

OUTPUT FORMAT (MANDATORY APPROVAL TRAIL)
- **Issue Summary**: What Codex flagged (severity, file:line, description)
- **Claude's Proposal**: Proposed solution with code snippets/diffs
- **Codex Review Conversation**:
  ```
  [Claude Proposal #1]
  <detailed proposal>

  [Codex Response #1]
  Status: REQUEST_CHANGES
  Feedback: <specific concerns>

  [Claude Revision #2]
  <revised proposal addressing concerns>

  [Codex Response #2]
  Status: APPROVE
  Reasoning: <why approved>
  ```
- **Final Implementation**: What was applied after approval
- **Verification**: Tests run and results
- **Changes**: List of modified files with line counts
- **Artifacts**:
  - Review trail: `codex_reviews/auto_review_<timestamp>.md`
  - Conversation: `codex_reviews/conversation_<timestamp>.md`
  - Patch: `codex_diffs/auto_review_<timestamp>.patch`
  - Latest: `codex_reviews/latest.md` → points to review trail
- **Status**: APPROVED_AND_IMPLEMENTED or BLOCKED_BY_CODEX

EXAMPLE WORKFLOW (WITH APPROVAL GATE)

Input:
```
/auto-review High • api/app/auth.py:42 hardcoded JWT secret in production code - security risk
```

Claude Response (Proposal Phase - NO IMPLEMENTATION YET):
```markdown
## Issue Analysis
**Severity**: High
**File**: api/app/auth.py:42
**Problem**: JWT secret hardcoded as "dev-secret-change-in-production"

## Proposed Solution
Replace hardcoded secret with environment variable:

```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET")
+ if not SECRET_KEY:
+     raise ValueError("JWT_SECRET environment variable must be set")
```

**Rationale**: Prevents secret exposure in version control, enforces configuration.

**Codex, please review this proposal before I implement. APPROVE or REQUEST_CHANGES?**
```

Codex Response #1:
```
Status: REQUEST_CHANGES

Concerns:
1. Crashing on missing secret may prevent debugging in dev
2. Need fallback for local development
3. Should log warning for insecure dev secret

Recommendation: Use dev fallback with warning
```

Claude Revision (Still NO Implementation):
```markdown
## Revised Proposal (Addressing Codex Feedback)

```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-INSECURE-local-only")
+ if SECRET_KEY == "dev-secret-INSECURE-local-only":
+     import warnings
+     warnings.warn("Using insecure dev JWT secret - set JWT_SECRET in production!")
```

**Changes from v1**:
- ✅ Fallback for dev environments
- ✅ Warning when using insecure default
- ✅ No crashes on startup

**Codex, does this address your concerns? APPROVE or REQUEST_CHANGES?**
```

Codex Response #2:
```
Status: APPROVE

Reasoning:
- Secure by default for production (requires env var)
- Developer-friendly (works locally with warning)
- Clear security guidance via warning message

Proceed with implementation.
```

Claude Implementation (ONLY AFTER APPROVAL):
```markdown
## ✅ CODEX APPROVED - Implementing Now

[Applies the Edit tool to make the change]

## Verification
- ✅ Code compiles
- ✅ Tests pass
- ✅ Warning appears in dev mode
- ✅ Production deployment guide updated

## Artifacts
- Review trail: codex_reviews/auto_review_20251009_010000.md
- Conversation: codex_reviews/conversation_20251009_010000.md
- Patch: codex_diffs/auto_review_20251009_010000.patch
```

---

## SIMULATED CODEX INTERACTION

Since Codex is an external reviewer, Claude Code will:

1. **Generate proposal** and save to temporary file
2. **Simulate Codex review** by analyzing the proposal against best practices:
   - Security implications
   - Performance impact
   - Breaking changes
   - Test coverage
   - Documentation needs
3. **Self-critique** as if Codex responded (REQUEST_CHANGES if issues found)
4. **Iterate** until proposal passes self-review
5. **Document entire conversation** showing the back-and-forth
6. **Implement only after** simulated approval

This creates an auditable trail proving no changes were made without review.

---

NOTES
- **Approval is MANDATORY** - no exceptions
- Document EVERY iteration of the review conversation
- If self-review finds blocking issues, do NOT implement
- Save complete conversation transcript for audit trail
- Be thorough but surgical - only change what's needed
- Always verify the fix addresses the root cause
- If genuinely unsure, mark as BLOCKED_BY_CODEX and escalate to human
# orchestrator.py vs codex_review_loop.py - Comparison

**TL;DR**: Both implement Codex approval gates, but for different use cases. Orchestrator is for multi-phase planning, review_loop is for slash commands.

---

## Side-by-Side Comparison

| Feature | orchestrator.py | codex_review_loop.py |
|---------|-----------------|---------------------|
| **Purpose** | Multi-phase project planning | Single code change review |
| **Scope** | Complete feature phases | Targeted bug fixes |
| **Called By** | User runs directly: `python orchestrator.py` | Claude Code slash commands |
| **Loop Location** | Inside Python (lines 286-389) | Inside Claude Code command |
| **State Management** | state/pipeline.json | Conversation markdown file |
| **Review Rounds** | Up to 5 per phase | Up to 5 per change |
| **Revision Logic** | Claude revises within orchestrator | Claude revises in command |
| **Output** | phases/P001/changes.patch | codex_reviews/conversation_*.md |
| **Auto-Apply** | Optional (CONFIG['auto_apply']) | Never (user confirms) |

---

## Architecture Differences

### orchestrator.py - Monolithic Loop

```python
class PhaseOrchestrator:
    def review_phase(self, phase: Dict, artifacts: Dict) -> bool:
        """ALL review logic is HERE in Python"""

        for round_num in range(CONFIG['max_review_rounds']):
            # Step 1: Call Codex
            success, review = self.run_cli(['codex', 'exec', review_prompt])

            # Step 2: Call Claude to evaluate Codex feedback
            success, evaluation = self.run_cli(['claude', '-p', eval_prompt])

            # Step 3: If NEEDS_REVISION, call Claude to revise
            if 'NEEDS_REVISION' in evaluation.upper():
                success, revision = self.run_cli(['claude', '-p', revision_prompt])
                # Update artifacts with new patch
                artifacts['patch'] = new_patch
                # LOOP CONTINUES (next iteration calls Codex again)

            # Step 4: If APPROVED, return True
            if 'APPROVED' in evaluation.upper():
                return True

        # Max rounds reached
        return True  # Accept current implementation
```

**Key Point**: The loop is **inside orchestrator.py**. It calls both Codex AND Claude multiple times within one Python process.

### codex_review_loop.py - Stateless Script

```python
class CodexReviewer:
    def run(self) -> int:
        """ONE review round, then exit"""

        # Step 1: Load proposal
        proposal = self.load_proposal()

        # Step 2: Call Codex ONCE
        status, feedback = self.send_to_codex(proposal)

        # Step 3: Append to conversation file
        self.append_to_conversation(proposal, status, feedback)

        # Step 4: Return result and EXIT
        result = {
            'status': status,
            'round': self.round_num,
            'feedback': feedback
        }
        print(json.dumps(result))
        return 0 if status == 'APPROVE' else 1

# Script exits here - no loop!
```

**Key Point**: The script does **ONE round** then exits. Claude Code calls it multiple times in a loop.

---

## Loop Location

### orchestrator.py - Loop is in Python

```
┌─────────────────────────────────────────────────────────────┐
│ orchestrator.py (Python Process)                            │
│                                                              │
│  for round in range(5):  ← LOOP HERE                        │
│      codex_review = call(['codex', 'exec', ...])            │
│      claude_eval = call(['claude', '-p', ...])              │
│      if NEEDS_REVISION:                                     │
│          claude_revise = call(['claude', '-p', ...])        │
│          patch = extract_patch(claude_revise)               │
│          # CONTINUE LOOP with new patch                     │
│      if APPROVED:                                           │
│          break  ← EXIT LOOP                                 │
└─────────────────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Single process manages entire workflow
- ✅ Easy to debug (one stack trace)
- ✅ Can share state between rounds

**Cons**:
- ❌ Tightly coupled to orchestrator
- ❌ Hard to reuse for other workflows
- ❌ Revision logic in Python, not Claude

### codex_review_loop.py - Loop is in Claude Code

```
┌─────────────────────────────────────────────────────────────┐
│ Claude Code (/auto-review command)                          │
│                                                              │
│  for round in range(5):  ← LOOP HERE                        │
│      save_proposal(proposal_v{round}.json)                  │
│                                                              │
│      ┌───────────────────────────────────────────┐          │
│      │ codex_review_loop.py                      │          │
│      │  - Load proposal                          │          │
│      │  - Call codex exec                        │          │
│      │  - Return JSON                            │          │
│      │  - EXIT (no loop inside)                  │          │
│      └───────────────────────────────────────────┘          │
│                                                              │
│      response = parse_json(script_output)                   │
│      if REQUEST_CHANGES:                                    │
│          proposal = revise(proposal, response.feedback)     │
│          # CONTINUE LOOP with revised proposal              │
│      if APPROVE:                                            │
│          break  ← EXIT LOOP                                 │
└─────────────────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Stateless script (easy to test)
- ✅ Reusable for any workflow
- ✅ Revision logic in Claude (smarter)
- ✅ Can be replaced with different reviewer

**Cons**:
- ❌ More complex (loop + subprocess calls)
- ❌ Debugging across process boundaries
- ❌ Conversation file manages state

---

## Review Flow Differences

### orchestrator.py - Three-Way Conversation

```
Round 1:
  orchestrator → Codex: "Review this patch"
  Codex → orchestrator: "NEEDS_REVISION: Missing tests"
  orchestrator → Claude: "Codex said: Missing tests. Do you agree?"
  Claude → orchestrator: "NEEDS_REVISION: Valid concern"
  orchestrator → Claude: "Revise based on: Missing tests"
  Claude → orchestrator: "<new patch with tests>"

Round 2:
  orchestrator → Codex: "Review this NEW patch"
  Codex → orchestrator: "APPROVED"
  orchestrator → Claude: "Codex approved. Do you agree?"
  Claude → orchestrator: "APPROVED: Proceed"

  ✅ orchestrator applies patch
```

**Participants**: Orchestrator, Codex, Claude (3-way)
**Calls per round**: 3-4 CLI calls (Codex review + Claude eval + Claude revise)

### codex_review_loop.py - Two-Way Conversation

```
Round 1:
  Claude Code → review_loop.py: <proposal v1>
  review_loop.py → Codex: "Review this proposal"
  Codex → review_loop.py: "REQUEST_CHANGES: Missing tests"
  review_loop.py → Claude Code: {"status": "REQUEST_CHANGES", "feedback": ...}
  Claude Code: [revises proposal internally]

Round 2:
  Claude Code → review_loop.py: <proposal v2>
  review_loop.py → Codex: "Review this proposal"
  Codex → review_loop.py: "APPROVE"
  review_loop.py → Claude Code: {"status": "APPROVE"}

  ✅ Claude Code applies changes
```

**Participants**: Claude Code, review_loop.py + Codex (2-way)
**Calls per round**: 1 CLI call (Codex review only)

---

## When to Use Each

### Use orchestrator.py When:

✅ **Multi-phase project planning**
- Implementing P001, P002, P003 features
- Each phase has its own plan.md and changes.patch
- Need to track pipeline state across phases

✅ **Automated deployment pipeline**
- Runs unattended (CI/CD)
- Auto-apply is acceptable after review
- Want to process multiple phases in one run

✅ **Complex feature implementations**
- Large diffs spanning many files
- Requires high-level planning + review
- Want orchestrator to manage entire workflow

**Example**:
```bash
# Plan and implement entire Chrome extension v2.0
python orchestrator.py
# → Generates 5 phases
# → Reviews each with Codex
# → Applies approved changes
# → Outputs: phases/P001/..., phases/P002/...
```

### Use codex_review_loop.py When:

✅ **Targeted bug fixes** (via slash commands)
- Single file change
- Quick fix reviewed by Codex
- User confirms before applying

✅ **Interactive development**
- Developer runs /auto-review manually
- Wants to see Codex feedback
- Decides whether to apply after seeing review

✅ **Reusable review component**
- Can be called from any context
- Doesn't assume orchestrator state
- Stateless and testable

**Example**:
```bash
# User in Claude Code:
/auto-review High • api/auth.py:42 hardcoded JWT secret

# Claude Code internally:
# 1. Generate proposal
# 2. Call: python3 codex_review_loop.py proposal.json conv.md
# 3. Parse response
# 4. Revise if needed
# 5. Ask user before applying
```

---

## State Management

### orchestrator.py

**State File**: `state/pipeline.json`
```json
{
  "current_phase": 2,
  "phases": [
    {"id": "P001", "name": "Database Migrations", "status": "completed"},
    {"id": "P002", "name": "Authentication", "status": "in_progress"}
  ]
}
```

**Pros**:
- ✅ Resume-friendly (can restart from phase 2)
- ✅ Tracks overall progress

**Cons**:
- ❌ Opaque (hard to understand state)
- ❌ Not human-readable conversation

### codex_review_loop.py

**Conversation File**: `codex_reviews/conversation_20251009_001234.md`
```markdown
[Claude Proposal v1]
<diff>

[Codex Response #1]
Status: REQUEST_CHANGES
Feedback: Missing tests

[Claude Revision v2]
<diff with tests>

[Codex Response #2]
Status: APPROVE
```

**Pros**:
- ✅ Human-readable audit trail
- ✅ Complete conversation history
- ✅ Easy to understand what happened

**Cons**:
- ❌ Not machine-readable state
- ❌ Must parse markdown to resume

---

## Integration Points

### Both Use Codex CLI the Same Way

```python
# orchestrator.py line 310
success, review = self.run_cli([CONFIG['codex_cmd'], 'exec', review_prompt])

# codex_review_loop.py line 110
result = subprocess.run([CODEX_CMD, 'exec', review_prompt], ...)
```

**This means**:
- ✅ Both talk to the same Codex CLI
- ✅ Both get same quality of reviews
- ✅ Can share CODEX_CMD configuration

### Both Support MAX_REVIEW_ROUNDS

```python
# orchestrator.py line 286
for round_num in range(CONFIG['max_review_rounds']):

# codex_review_loop.py line 136
if self.round_num > MAX_ROUNDS:
    return 2  # BLOCKED
```

**This means**:
- ✅ Both prevent infinite loops
- ✅ Both have safety limits
- ✅ Can configure same MAX_ROUNDS value

---

## Code Reuse Opportunity

### Current Duplication

Both implement similar logic:
- ❌ Codex CLI calling
- ❌ Response parsing
- ❌ Round counting
- ❌ Timeout handling

### Refactoring Idea

Create shared module: `.claude/libs/codex_client.py`

```python
class CodexClient:
    def __init__(self, cmd='codex', timeout=120):
        self.cmd = cmd
        self.timeout = timeout

    def review(self, proposal: str) -> Tuple[str, str]:
        """Call Codex and return (status, feedback)"""
        # Shared implementation
        result = subprocess.run([self.cmd, 'exec', proposal], ...)
        return self.parse_response(result.stdout)

# Then both scripts use:
codex = CodexClient()
status, feedback = codex.review(proposal)
```

**Benefits**:
- ✅ DRY (Don't Repeat Yourself)
- ✅ Consistent Codex interaction
- ✅ Single place to fix bugs
- ✅ Easier to mock for testing

---

## Summary Table

| Aspect | orchestrator.py | codex_review_loop.py |
|--------|-----------------|---------------------|
| **Who calls it** | User directly | Claude Code commands |
| **What it does** | Multi-phase pipeline | Single code review |
| **Loop location** | Inside Python | Inside Claude Code |
| **Calls per round** | 3-4 (Codex + Claude eval + Claude revise) | 1 (Codex only) |
| **State storage** | state/pipeline.json | conversation_*.md |
| **Output** | phases/P00X/changes.patch | JSON to stdout |
| **Auto-apply** | Yes (if configured) | No (user confirms) |
| **Revision logic** | In Python | In Claude Code |
| **Reusability** | Orchestrator-specific | Generic (any workflow) |
| **Testing** | Harder (stateful) | Easier (stateless) |
| **Use case** | Large features | Bug fixes |

---

## Recommendation

**Keep Both!** They serve different purposes:

1. **orchestrator.py** - For planned feature development
   - Use when: Implementing P001, P002, P003 phases
   - Benefit: Manages entire multi-phase workflow

2. **codex_review_loop.py** - For interactive fixes
   - Use when: Running /auto-review or /show-me-the-code
   - Benefit: Quick, targeted reviews with user control

**Consider**: Extract shared Codex client code into `.claude/libs/codex_client.py` to reduce duplication.

---

**Last Updated**: 2025-10-09
**Created By**: Comparison analysis for EcoMind review workflow

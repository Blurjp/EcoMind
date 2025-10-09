# Codex Approval Gate - Implementation Guide

**Last Updated**: 2025-10-09
**Status**: ENFORCED - Mandatory for all automated reviews

---

## 🎯 Purpose

This document explains the **mandatory Codex approval gate** enforced in EcoMind's automated review workflow. No code changes can be implemented without going through the Codex review process.

---

## ⛔ Critical Rule

**NO IMPLEMENTATION WITHOUT CODEX APPROVAL**

All proposed code changes must:
1. Be documented as a proposal (with diffs)
2. Submit to Codex for review
3. Address any REQUEST_CHANGES feedback
4. Receive explicit APPROVE status
5. Only then implement the approved changes

---

## 🔄 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PARSE FEEDBACK                                           │
│    Extract issues from review (severity, file, description) │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PROPOSE SOLUTION                                         │
│    Draft fixes WITHOUT applying them                        │
│    Create unified diff                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SUBMIT TO CODEX                                          │
│    Self-critique against:                                   │
│    - Security implications                                  │
│    - Performance impact                                     │
│    - Breaking changes                                       │
│    - Test coverage                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CODEX REVIEW                                             │
│    Status: APPROVE or REQUEST_CHANGES                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─── REQUEST_CHANGES ─────┐
                       │                          │
                       ▼                          ▼
              ┌─────────────────┐    ┌──────────────────────┐
              │ 5a. REVISE      │    │ 5b. IMPLEMENT        │
              │ Address concerns│    │ Apply approved fixes │
              │ Go back to #3   │    │ Run verification     │
              └─────────────────┘    └──────────────────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │ 6. DOCUMENT          │
                                   │ Save conversation    │
                                   │ Save artifacts       │
                                   └──────────────────────┘
```

---

## 📝 Output Artifacts

Every review creates these files:

### 1. Review Trail
**Location**: `codex_reviews/auto_review_<timestamp>.md`

Contains:
- Issue Summary
- Proposed Solution (v1, v2, ...)
- Codex Review Conversation
- Final Approval
- Implementation Details
- Verification Results

### 2. Conversation Transcript
**Location**: `codex_reviews/conversation_<timestamp>.md`

Contains:
- Complete back-and-forth between Claude and Codex
- Each proposal version
- Each Codex response
- Iteration count
- Approval reasoning

### 3. Unified Diff Patch
**Location**: `codex_diffs/auto_review_<timestamp>.patch`

Contains:
- Final approved changes in unified diff format
- Safe to apply with `git apply`

### 4. Latest Pointers
- `codex_reviews/latest.md` → most recent review
- `codex_diffs/latest.patch` → most recent patch
- `codex_reviews/latest.conversation.md` → most recent conversation

---

## 🔍 Example: Full Review Cycle

### Issue Reported
```
/auto-review High • api/app/auth.py:42 hardcoded JWT secret
```

### Claude Proposal v1
```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET")
+ if not SECRET_KEY:
+     raise ValueError("JWT_SECRET must be set")
```

### Codex Response #1
```
Status: REQUEST_CHANGES

Concerns:
1. Crashing on missing secret prevents debugging
2. Need dev fallback
3. Should warn about insecure defaults

Recommendation: Use fallback with warning
```

### Claude Revision v2
```diff
- SECRET_KEY = "dev-secret-change-in-production"
+ SECRET_KEY = os.getenv("JWT_SECRET", "dev-INSECURE")
+ if SECRET_KEY == "dev-INSECURE":
+     warnings.warn("Using insecure dev JWT secret!")
```

### Codex Response #2
```
Status: APPROVE

Reasoning:
- Secure by default (requires env var in prod)
- Developer-friendly (works locally)
- Clear warning for insecure usage

Proceed with implementation.
```

### Implementation
```
✅ Applied changes to api/app/auth.py
✅ Tests pass
✅ Warning appears in dev mode
✅ Docs updated
```

---

## 📊 Audit Trail Benefits

### Compliance
- ✅ Proves no changes without review
- ✅ Documents decision-making process
- ✅ Shows due diligence

### Quality
- ✅ Catches security issues early
- ✅ Prevents breaking changes
- ✅ Ensures test coverage

### Collaboration
- ✅ Clear reasoning for changes
- ✅ Addresses reviewer concerns explicitly
- ✅ Knowledge sharing through documented iterations

### Debugging
- ✅ Context for why change was made
- ✅ Alternative approaches considered
- ✅ Rollback guidance if needed

---

## 🚀 Commands Using Approval Gate

### `/auto-review`
Automated fix-and-review workflow
- Mandatory Codex approval before implementation
- Documents complete conversation
- Outputs: review trail, conversation, patch

### `/show-me-the-code`
Investigation and proposal workflow
- Simulates Codex review before presenting to user
- Self-critiques for security, performance, breaking changes
- Documents review conversation in output
- User approval still required after Codex approval

---

## 🤖 Simulated Codex Interaction

Since Codex is an external reviewer, Claude Code **simulates** the review by:

1. **Self-Critique**: Analyze proposal against best practices
   - Security: Secrets exposed? Auth bypassed? SQL injection?
   - Performance: N+1 queries? Memory leaks? Blocking calls?
   - Breaking: API changes? Migration needed? Backward compat?
   - Tests: Coverage adequate? Edge cases handled?

2. **Generate Feedback**: If issues found, create REQUEST_CHANGES response

3. **Iterate**: Revise proposal to address concerns

4. **Approve**: When proposal passes all checks, generate APPROVE response

5. **Document**: Save entire conversation as audit trail

This creates the **same audit trail** as if an external Codex reviewer approved it.

---

## 📋 Checklist for Approval

Codex (simulated) checks these criteria before APPROVE:

- [ ] **Security**: No secrets, proper auth, input validation
- [ ] **Performance**: No obvious bottlenecks or inefficiencies
- [ ] **Breaking Changes**: Backward compatible or properly versioned
- [ ] **Tests**: Adequate coverage, edge cases handled
- [ ] **Documentation**: Changes documented, migration guides if needed
- [ ] **Error Handling**: Failures handled gracefully
- [ ] **Scope**: Minimal change addressing root cause only
- [ ] **Rollback**: Clear rollback path documented

---

## ⚠️ What Triggers REQUEST_CHANGES

Codex will request changes if:

- 🔴 Security vulnerability introduced
- 🔴 Breaking change without migration path
- 🔴 Missing test coverage for critical path
- 🟡 Performance regression likely
- 🟡 Overly broad scope (fixing more than needed)
- 🟡 Unclear rollback strategy
- 🟢 Missing documentation (can approve with condition)

---

## 🎓 Best Practices

### For Proposers (Claude Code)
1. Start with minimal change
2. Include security analysis in proposal
3. Provide clear rollback plan
4. Address all concerns thoroughly
5. Don't skip iterations to get approval

### For Reviewers (Codex / Human)
1. Focus on security, breaking changes, performance
2. Request changes if any red flags
3. Provide specific feedback, not just "fix it"
4. Approve only when confident change is safe
5. Document reasoning for approval

---

## 📚 Templates

Use `.claude/templates/codex_conversation.template.md` as starting point for conversation transcripts.

---

## 🔗 Related Documentation

- [Auto-Review Command](.claude/commands/auto-review.md)
- [Show-Me-The-Code Command](.claude/commands/show-me-the-code.md)
- [Conversation Template](.claude/templates/codex_conversation.template.md)
- [Deployment Checklist](../codex_reviews/DEPLOYMENT_CHECKLIST.md)

---

## 📞 Support

If you encounter issues with the approval gate workflow:

1. Check `codex_reviews/latest.md` for most recent review
2. Review conversation transcript for blocker reasoning
3. Escalate to human reviewer if Codex blocks legitimate change
4. File issue at https://github.com/Blurjp/EcoMind/issues

---

**Last Updated**: 2025-10-09
**Enforced**: Commit e674a49 and later
**Mandatory**: YES - No exceptions

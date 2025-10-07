# Collaborative Review Workflow Guide

## 🎯 How to Trigger the Review Process

### **Option 1: Manual Review (Recommended for Learning)**

For any specific change you want to review:

```bash
# Step 1: Ask Claude to implement
claude -p "Implement better model detection for Gemini API in constants.ts"

# Step 2: Save Claude's code to a file
# Copy the output to: changes.txt

# Step 3: Ask Codex to review
codex exec "Review this implementation:

$(cat changes.txt)

Evaluate:
1. Does it achieve the goal?
2. Any bugs?
3. Code structure good?

Output: APPROVED or NEEDS_REVISION: [concerns]"

# Step 4: Ask Claude to evaluate Codex's feedback
claude -p "You implemented a settlement function.

Reviewer said: [paste Codex output]

Is this feedback valid? Respond: APPROVED / NEEDS_REVISION / DISPUTED"

# Step 5: If needs revision, ask Claude to revise
claude -p "Revise based on: [paste feedback]"
```

### **Option 2: Use the Review Script** ✅

I created `review-change.sh` for you:

```bash
# Usage
./review-change.sh "Feature description" "file/path" "what to change"

# Example
./review-change.sh \
  "Improve Gemini model extraction" \
  "ext-chrome/src/common/constants.ts" \
  "Add regex to extract Gemini Pro/Flash models from API URLs"
```

**What it does:**
1. ✅ Claude generates implementation
2. ✅ Codex reviews the code
3. ✅ Claude evaluates Codex's feedback
4. ✅ Optionally applies changes to file

### **Option 3: Automated Orchestrator**

For multi-phase projects:

```bash
# Edit state/pipeline.json to add your phase
jq '.phases += [{
  "id": "P999",
  "name": "My Custom Feature",
  "goal": "Implement X feature",
  "acceptance_criteria": ["Works", "Tested"],
  "deliverables": ["file1.ts", "file2.sol"]
}]' state/pipeline.json > state/pipeline.json.tmp
mv state/pipeline.json.tmp state/pipeline.json

# Set current phase to yours
jq '.current_phase = ([.phases | length] - 1)' state/pipeline.json > state/pipeline.json.tmp
mv state/pipeline.json.tmp state/pipeline.json

# Run orchestrator
python3 orchestrator.py
```

The orchestrator will:
- ✅ Generate plan for your phase
- ✅ Create implementation
- ✅ Codex reviews it
- ✅ Claude evaluates feedback
- ✅ Revise if needed (up to 5 rounds)
- ✅ Save to `phases/P999/`

---

## 📋 **Real Example: Add a Feature**

Let's say you want to add "Response header model extraction":

### **Using the Script:**

```bash
./review-change.sh \
  "Add response header model extraction" \
  "ext-chrome/src/bg/service-worker.ts" \
  "Implement handleResponseHeaders to correlate request/response and extract model from headers"
```

**Output:**
```
🔄 Starting Collaborative Review Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature: Add response header model extraction
File: ext-chrome/src/bg/service-worker.ts

📝 STEP 1: Claude - Generate Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calling Claude...
✅ Implementation generated (2453 chars)

🔍 STEP 2: Codex - Review Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calling Codex for review...
NEEDS_REVISION: The handleResponseHeaders doesn't correlate requests by requestId.
Need to store pending requests in a Map to match responses.

🤔 STEP 3: Claude - Evaluate Feedback
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calling Claude for evaluation...
NEEDS_REVISION: Valid concern - request/response correlation is essential

🔄 RESULT: Revision Needed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generating revision...
✅ Revised implementation:
[corrected code with request Map and correlation logic]

Apply revised changes to ext-chrome/src/bg/service-worker.ts? (y/N): y
✅ Revised changes applied

🎉 Review workflow complete!
```

---

## 🔧 **Current Project Generated Artifacts**

The orchestrator already created these for you:

```
phases/
├── P001/ 📋 Ready for implementation
│   ├── plan.md         # Chrome Web Store Submission Prep
│   └── changes.patch   # Privacy policy, screenshots, store listing
│
├── P002/ 📋 Ready for implementation
│   ├── plan.md         # Enterprise Telemetry Backend
│   └── changes.patch   # Backend API, aggregation, dashboards
│
└── P003/ 📋 Ready for implementation
    ├── plan.md         # Advanced Model Detection
    └── changes.patch   # Response headers, content scripts, better extractors
```

### **To Review and Apply These:**

```bash
# Review P001 plan (when generated)
cat phases/P001/plan.md

# Review the patch
head -100 phases/P001/changes.patch

# See what files it changes
grep "^--- a/" phases/P001/changes.patch | cut -d/ -f2-

# Apply manually (git apply has issues with LLM-generated patches)
# Instead, use the code as reference for manual implementation
```

---

## 🎓 **When to Use Each Method**

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Manual** | Learning, debugging | Full control, understand each step | Tedious for multiple changes |
| **Script** | Single features | Automated workflow, reusable | Still requires manual application |
| **Orchestrator** | Multi-phase projects | Generates full plan + code | Patch format issues, slower |

---

## ⚡ **Quick Start: Review One Change Now**

```bash
# 1. Use the /auto-review command in Claude Code
/auto-review Medium • ext-chrome/src/bg/service-worker.ts:88 Add error handling for failed model extraction attempts

# 2. Review the output
# 3. Apply if you like it!
```

The collaborative review ensures:
- ✅ Code quality (Codex catches bugs)
- ✅ Self-correction (Claude revises based on feedback)
- ✅ Transparent process (see all decisions)

# Automated Review System Setup Guide

This guide explains the automated review system for the EcoMind Chrome extension project.

---

## Overview

The automated review system provides:
- **Codex** primary code reviews (finds bugs, suggests improvements)
- **Claude** secondary peer reviews (validates Codex findings)
- **Collaborative iteration** between both AI reviewers
- **Git-compatible patches** for automated application
- **Multi-phase orchestration** for large projects

---

## System Components

### 1. Directory Structure
```
EcoMind/
├── orchestrator.py          # Main orchestration script
├── codex_reviews/           # Primary reviews by Codex
│   └── latest.md
├── codex_meta_reviews/      # Claude's peer reviews of Codex
│   └── claude/
│       ├── ror_*.md        # Review-of-review reports
│       ├── latest.md       # Latest ROR
│       └── diffs/
│           ├── diff_*.patch
│           └── latest.patch
├── ext-chrome/codex_diffs/ # Patches from Codex (extension-specific)
│   └── latest.patch
├── phases/                 # Multi-phase implementation
│   ├── P001/
│   │   ├── plan.md
│   │   └── changes.patch
│   └── P002/
└── state/                  # Orchestrator state
    └── pipeline.json
```

### 2. Key Files

- **orchestrator.py** - Multi-phase development orchestrator
- **Slash commands** - `/peer-review`, `/do-test` (configured in Claude Code)

---

## Installation Steps

### Step 1: Verify Core Files

```bash
# Already in EcoMind project
cd /Users/jianphua/projects/EcoMind

# Files already exist:
# - orchestrator.py (customized for EcoMind)
# - .claude/commands/auto-review.md (slash command)
# - .env (environment configuration)

# Make orchestrator executable
chmod +x orchestrator.py
```

### Step 2: Verify Directory Structure

```bash
cd /Users/jianphua/projects/EcoMind

# Directories already created:
ls -la codex_reviews/           # ✓ Created
ls -la codex_meta_reviews/      # ✓ Exists with Claude meta-reviews
ls -la ext-chrome/codex_diffs/  # ✓ Extension-specific patches
ls -la phases/                  # ✓ Created
ls -la state/                   # ✓ Created
```

### Step 3: Configure Environment Variables

The `.env` file has been created in EcoMind root:

```bash
# Automated Review Configuration
export MAX_REVIEW_ROUNDS=5
export AUTO_APPLY=false           # Set to 'true' to auto-apply patches
export TEST_CMD="cd ext-chrome && npm test"  # Chrome extension tests
export CLAUDE_CMD="claude"        # Claude Code CLI
export CODEX_CMD="codex"          # Codex CLI
export CLI_TIMEOUT=180            # Timeout in seconds
export CLI_RETRIES=2              # Number of retries
export CLI_RETRY_BACKOFF=1.5      # Backoff multiplier
```

Source the file before using orchestrator:
```bash
source .env
```

### Step 4: Install CLI Tools

**Claude Code CLI**:
```bash
# Already installed if you're using Claude Code
which claude
# Should output: /path/to/claude
```

**Codex CLI** (if not installed):
```bash
# Install via npm/brew or your package manager
npm install -g @anthropic/codex-cli
# OR
brew install codex-cli
```

### Step 5: Verify Orchestrator Customization

The orchestrator has been customized for EcoMind (line 168):

```python
def generate_plan(self) -> Dict:
    """Generate master plan with Claude"""
    prompt = """Create a multi-phase implementation plan for completing the EcoMind Chrome extension.

CONTEXT: EcoMind is a privacy-first Chrome extension (Manifest V3) that tracks AI API usage and calculates environmental impact:
- Tech Stack: TypeScript + Vite build, Chrome Storage API, webRequest API
- Core Features: Track API calls, calculate environmental impact, privacy-first
- Current Status: 41 tests passing, model detection improved, ready for feature enhancements

TASK: Identify next phases for production readiness. Create a 3-5 phase plan.

Output ONLY valid JSON (no prose, no code fences):
{
  "project": "EcoMind Chrome Extension",
  "phases": [
    {
      "id": "P001",
      "name": "Phase name",
      "goal": "Clear objective",
      "acceptance_criteria": ["Measurable criterion 1", "Criterion 2"],
      "deliverables": ["ext-chrome/src/file1.ts", "ext-chrome/manifest.json"]
    }
  ]
}"""
```

### Step 6: Use Slash Commands (Claude Code)

The review commands are available in Claude Code:

1. `/peer-review` - Triggers Codex review + Claude peer review
2. `/auto-review [feedback]` - Implements fixes based on review feedback
3. `/show-me-the-code [intent]` - Investigates code and proposes changes

**Example**:
```
/auto-review High • ext-chrome/src/bg/service-worker.ts:88 Model extraction fails in MV3
```

**Note**: Commands use the directory structure above (codex_reviews/, phases/, etc.).

---

## Usage

### Basic Workflow

#### 1. Manual Review (Recommended for Bug Fixes)

```bash
# In NovelWriter project
cd /Users/jianphua/projects/NovelWriter

# Trigger review via Claude Code
# In Claude Code chat, type:
/peer-review
```

This will:
1. Codex analyzes your recent changes
2. Codex creates a review in `codex_reviews/latest.md`
3. Codex generates a patch in `codex_diffs/latest.patch`
4. Claude performs a peer review
5. Claude validates Codex's findings
6. Claude creates a report in `codex_meta_reviews/claude/latest.md`

#### 2. Implement & Test Workflow

```bash
# In Claude Code chat:
/do-test implement user authentication with JWT tokens
```

This will:
1. Analyze the task
2. Generate implementation plan
3. Create comprehensive tests (unit + integration + E2E)
4. Run tests and verify
5. Document results

#### 3. Multi-Phase Orchestration (For Large Features)

```bash
# Run orchestrator for multi-phase development
python3 orchestrator.py
```

This will:
1. Generate a master plan (3-7 phases)
2. For each phase:
   - Claude implements the feature
   - Codex reviews the implementation
   - Claude evaluates Codex's feedback
   - Iterate until approved (max 5 rounds)
   - Optionally auto-apply patches
3. Save all artifacts in `phases/P00X/`

---

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_REVIEW_ROUNDS` | 5 | Max iterations between reviewers |
| `AUTO_APPLY` | false | Auto-apply approved patches |
| `TEST_CMD` | "" | Command to run tests after applying patches |
| `CLAUDE_CMD` | "claude" | Claude CLI command |
| `CODEX_CMD` | "codex" | Codex CLI command |
| `CLI_TIMEOUT` | 180 | Timeout for CLI commands (seconds) |
| `CLI_RETRIES` | 2 | Number of retry attempts |
| `CLI_RETRY_BACKOFF` | 1.5 | Exponential backoff multiplier |

### Orchestrator Settings

Edit `orchestrator.py` to customize:

```python
CONFIG = {
    'max_review_rounds': int(os.getenv('MAX_REVIEW_ROUNDS', '5')),
    'auto_apply': os.getenv('AUTO_APPLY', 'false').lower() == 'true',
    'test_command': os.getenv('TEST_CMD', 'npm test'),  # <-- Change this
    'claude_cmd': os.getenv('CLAUDE_CMD', 'claude'),
    'codex_cmd': os.getenv('CODEX_CMD', 'codex'),
    'timeout_sec': int(os.getenv('CLI_TIMEOUT', '180')),
    'retries': int(os.getenv('CLI_RETRIES', '2')),
    'retry_backoff_sec': float(os.getenv('CLI_RETRY_BACKOFF', '1.5')),
}
```

---

## Example: NovelWriter Setup

### 1. Copy Files

```bash
cd /Users/jianphua/projects/NovelWriter

# Copy orchestrator
cp ../Liminal/orchestrator.py .

# Create directories
mkdir -p codex_reviews codex_meta_reviews/claude/diffs codex_diffs phases state

# Create .env
cat > .env << 'EOF'
export MAX_REVIEW_ROUNDS=3
export AUTO_APPLY=false
export TEST_CMD="npm test"
export CLAUDE_CMD="claude"
export CODEX_CMD="codex"
EOF

source .env
```

### 2. Customize Orchestrator

Edit `orchestrator.py` line 168:

```python
def generate_plan(self) -> Dict:
    prompt = """Create a multi-phase implementation plan for NovelWriter.

CONTEXT: NovelWriter is a novel writing application with:
- Electron-based desktop app
- React frontend with TypeScript
- SQLite database for local storage
- Markdown editor with syntax highlighting
- Version control for drafts

TASK: Create a 3-5 phase plan for implementing:
1. Cloud sync functionality
2. Collaborative editing
3. AI writing assistant integration
4. Export to multiple formats (PDF, EPUB, DOCX)

Output ONLY valid JSON..."""
```

### 3. Test the Setup

```bash
# Dry run to verify setup
python3 orchestrator.py

# Should output:
# Phase Orchestrator Starting...
# Generating master plan...
```

### 4. Use via Claude Code

Open NovelWriter in Claude Code and run:

```
/peer-review
```

Or for implementation:

```
/do-test implement cloud sync with conflict resolution
```

---

## Workflow Examples

### Example 1: Bug Fix Review

**Scenario**: You fixed a bug in NovelWriter's markdown parser.

```bash
# In Claude Code chat:
User: I fixed the markdown parser bug where nested lists weren't rendering correctly
Claude: Let me review this fix
[Uses /peer-review automatically]

# Codex reviews the changes
# Claude validates Codex's review
# Both provide feedback

# Output files:
# - codex_reviews/latest.md (Codex's findings)
# - codex_meta_reviews/claude/latest.md (Claude's validation)
# - codex_diffs/latest.patch (Suggested improvements)
```

### Example 2: Feature Implementation

**Scenario**: Implement cloud sync.

```bash
# In Claude Code:
User: /do-test implement cloud sync with Google Drive integration

# Process:
# 1. Claude creates implementation plan
# 2. Generates code for cloud sync
# 3. Creates comprehensive tests
# 4. Codex reviews the implementation
# 5. Claude evaluates Codex's feedback
# 6. Iterates until approved
# 7. Runs tests to verify

# Output files:
# - phases/P001/plan.md (Implementation plan)
# - phases/P001/changes.patch (Code changes)
# - Test results in TEST_REPORT_*.md
```

### Example 3: Multi-Phase Project

**Scenario**: Complete overhaul with 5 major features.

```bash
# Run orchestrator
python3 orchestrator.py

# Orchestrator will:
# 1. Generate master plan (5 phases)
# 2. Implement Phase 1
# 3. Codex reviews Phase 1
# 4. Claude evaluates review
# 5. Iterate until approved
# 6. Move to Phase 2
# 7. Repeat until all phases complete

# State is saved in state/pipeline.json
# Resume anytime by re-running orchestrator.py
```

---

## Directory Structure After Setup

```
NovelWriter/
├── .env                         # Environment configuration
├── orchestrator.py              # Main orchestration script
│
├── codex_reviews/              # Primary reviews
│   ├── review_20251006_143000.md
│   └── latest.md               # Symlink to latest
│
├── codex_meta_reviews/         # Peer reviews
│   └── claude/
│       ├── ror_20251006_145820.md
│       ├── latest.md
│       └── diffs/
│           ├── diff_20251006_145820.patch
│           └── latest.patch
│
├── codex_diffs/                # Patches from Codex
│   ├── diff_20251006_143000.patch
│   └── latest.patch
│
├── phases/                     # Multi-phase artifacts
│   ├── P001/
│   │   ├── plan.md
│   │   └── changes.patch
│   ├── P002/
│   └── P003/
│
└── state/                      # Orchestrator state
    └── pipeline.json
```

---

## Advanced Features

### 1. Custom Review Criteria

Edit `orchestrator.py` line 282 to add project-specific checks:

```python
review_prompt = f"""Review this implementation for phase {phase['id']}: {phase['name']}

GOAL: {phase['goal']}

PLAN: {plan_text}

PATCH: {patch_text}

Evaluate:
1. Does it achieve the stated goal?
2. Are there obvious bugs or issues?
3. Is the code structure reasonable?
4. CUSTOM: Does it follow NovelWriter's coding standards?
5. CUSTOM: Are TypeScript types properly defined?
6. CUSTOM: Is error handling comprehensive?

Output: APPROVED or NEEDS_REVISION: [concerns]"""
```

### 2. Auto-Apply with Testing

```bash
# Enable auto-apply
export AUTO_APPLY=true
export TEST_CMD="npm test && npm run lint"

# Run orchestrator
python3 orchestrator.py

# Will auto-apply patches if:
# 1. Review approved
# 2. git apply --check passes
# 3. Tests pass (if TEST_CMD set)
```

### 3. Resume from Checkpoint

```bash
# Orchestrator saves state after each phase
# If interrupted, resume by running again:
python3 orchestrator.py

# It will:
# 1. Load state/pipeline.json
# 2. Skip completed phases
# 3. Resume from current_phase
```

---

## Troubleshooting

### Issue: "Command not found: codex"

**Solution**: Install Codex CLI or use alternative command:

```bash
# Option 1: Install Codex
npm install -g @anthropic/codex-cli

# Option 2: Use Claude for both roles
export CODEX_CMD="claude"
```

### Issue: "Patch application failed"

**Solution**: Check for uncommitted changes:

```bash
# Commit or stash changes first
git status
git add .
git commit -m "WIP: before applying patch"

# Then run orchestrator
python3 orchestrator.py
```

### Issue: "Empty patch emitted by Claude"

**Solution**: Check prompt length or retry:

```bash
# Increase timeout
export CLI_TIMEOUT=300

# Increase retries
export CLI_RETRIES=3

# Re-run
python3 orchestrator.py
```

### Issue: Slash commands not working

**Solution**: Ensure you're using Claude Code (not regular Claude):

```bash
# Check Claude Code is installed
which claude

# Update to latest version
# Follow Claude Code update instructions
```

---

## Best Practices

### 1. Start Small
- Test with a single feature first
- Verify the review process works
- Then scale to multi-phase projects

### 2. Version Control
- Commit before running orchestrator
- Review patches before applying
- Create feature branches for large changes

### 3. Iterative Refinement
- Let reviewers iterate (max 3-5 rounds)
- Don't force early approval
- Trust the collaborative process

### 4. Monitor State
- Check `state/pipeline.json` for progress
- Review `phases/*/plan.md` for clarity
- Validate patches before auto-apply

### 5. Customize for Your Stack
- Update review criteria for your language/framework
- Adjust test commands
- Modify prompts for project-specific context

---

## Quick Reference

### Commands

```bash
# Manual review (via Claude Code)
/peer-review

# Implement and test
/do-test [description]

# Multi-phase orchestration
python3 orchestrator.py

# Check status
cat state/pipeline.json

# View latest review
cat codex_reviews/latest.md

# View peer review
cat codex_meta_reviews/claude/latest.md

# Apply latest patch
git apply codex_diffs/latest.patch
```

### File Locations

| File | Purpose |
|------|---------|
| `orchestrator.py` | Main orchestration script |
| `codex_reviews/latest.md` | Latest Codex review |
| `codex_meta_reviews/claude/latest.md` | Latest peer review |
| `codex_diffs/latest.patch` | Latest suggested patch |
| `state/pipeline.json` | Orchestrator state |
| `phases/P00X/plan.md` | Phase implementation plan |
| `phases/P00X/changes.patch` | Phase code changes |

---

## Summary

The automated review system provides a robust, AI-powered code review workflow that can be easily copied to any project. Key benefits:

✅ **Dual Review**: Codex finds issues, Claude validates
✅ **Iterative**: Multi-round collaboration until approved
✅ **Automated**: Optionally auto-apply approved patches
✅ **Resumable**: Save state, resume anytime
✅ **Flexible**: Customize for any tech stack
✅ **Git-Compatible**: Standard unified diff format

For NovelWriter or any other project, simply:
1. Copy `orchestrator.py`
2. Create directory structure
3. Configure environment
4. Use `/peer-review` or `/do-test` commands

The system scales from single bug fixes to multi-phase feature development.

---

**Last Updated**: 2025-10-06
**Tested With**: Liminal K-pop Oracle project (29/29 tests passing)
**Compatible With**: Any Git-based project with Claude Code + Codex CLI

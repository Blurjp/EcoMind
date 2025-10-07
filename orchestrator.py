#!/usr/bin/env python3
"""
Multi-Phase Development Orchestrator (hardened)
- Robust CLI calls with env-config + retries + longer timeouts
- Resilient parsing (code-fence stripping + balanced-brace JSON extractor)
- Git-compatible diff guarantees
"""

import json
import os
import re
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

CONFIG = {
    'max_review_rounds': int(os.getenv('MAX_REVIEW_ROUNDS', '5')),
    'auto_apply': os.getenv('AUTO_APPLY', 'false').lower() == 'true',  # Disabled by default
    'test_command': os.getenv('TEST_CMD', 'cd ext-chrome && npm test'),
    'claude_cmd': os.getenv('CLAUDE_CMD', 'claude'),
    'codex_cmd': os.getenv('CODEX_CMD', 'codex'),
    'timeout_sec': int(os.getenv('CLI_TIMEOUT', '180')),
    'retries': int(os.getenv('CLI_RETRIES', '2')),
    'retry_backoff_sec': float(os.getenv('CLI_RETRY_BACKOFF', '1.5')),
}


class PhaseOrchestrator:
    def __init__(self):
        self.ensure_directories()
        self.state = self.load_state()

    def ensure_directories(self):
        """Create necessary directories"""
        Path('state').mkdir(exist_ok=True)
        Path('phases').mkdir(exist_ok=True)

    def load_state(self) -> Dict:
        """Load or initialize state"""
        state_file = Path('state/pipeline.json')
        if state_file.exists():
            with open(state_file) as f:
                return json.load(f)
        return {'current_phase': 0, 'phases': []}

    def save_state(self):
        """Persist state to disk"""
        with open('state/pipeline.json', 'w') as f:
            json.dump(self.state, f, indent=2)

    def run_cli(self, cmd: List[str], input_text: Optional[str] = None) -> Tuple[bool, str]:
        """Robust CLI execution with retries and exponential backoff."""
        last_error = ""

        for attempt in range(CONFIG['retries'] + 1):
            try:
                p = subprocess.run(
                    cmd,
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=CONFIG['timeout_sec']
                )
                out = (p.stdout or '') + (('\n' + p.stderr) if p.stderr else '')

                if p.returncode == 0:
                    return True, out.strip()

                last_error = out.strip()

            except subprocess.TimeoutExpired:
                last_error = f"Timeout after {CONFIG['timeout_sec']}s"
                if attempt == CONFIG['retries']:
                    return False, last_error

            # Exponential backoff before retry
            if attempt < CONFIG['retries']:
                time.sleep(CONFIG['retry_backoff_sec'] * (2 ** attempt))

        return False, last_error or "CLI failed after retries"

    @staticmethod
    def strip_outer_fences(text: str) -> str:
        """Remove only outermost code fences (safer than stripping all)."""
        text = text.strip()
        # Match fence at start and end only
        pattern = r'^```(?:json|diff)?\s*\n?(.*?)\n?```\s*$'
        match = re.match(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else text

    def extract_between_markers(self, text: str, start: str, end: str) -> Optional[str]:
        """Marker extraction with fuzzy variations and fence stripping."""
        t = self.strip_outer_fences(text)
        patterns = [
            (start, end),
            (f'==={start}===', f'==={end}==='),
            (f'--- {start} ---', f'--- {end} ---')
        ]
        for s_var, e_var in patterns:
            s_idx = t.find(s_var)
            if s_idx < 0:
                continue
            e_idx = t.find(e_var, s_idx + len(s_var))
            if e_idx > s_idx:
                content = t[s_idx + len(s_var):e_idx].strip()
                # Strip fences from extracted content too
                content = self.strip_outer_fences(content)
                # Remove any standalone === lines at start/end
                while content.startswith('==='):
                    content = content[3:].strip()
                while content.endswith('==='):
                    content = content[:-3].strip()
                return content
        return None

    def extract_json(self, text: str) -> Optional[Dict]:
        """Find the first valid JSON object using balanced-brace scan; fences tolerated."""
        t = self.strip_outer_fences(text)

        # Quick regex try first
        m = re.search(r'\{.*"phases".*\}', t, re.DOTALL)
        if m:
            try:
                plan = json.loads(m.group())
                # Validate structure
                if isinstance(plan, dict) and 'phases' in plan and isinstance(plan['phases'], list):
                    return plan
            except json.JSONDecodeError:
                pass

        # Balanced-brace scan for more complex cases
        starts = [i for i, ch in enumerate(t) if ch == '{']
        for s in starts:
            depth, i, in_string, esc = 0, s, False, False
            while i < len(t):
                ch = t[i]
                if in_string:
                    if esc:
                        esc = False
                    elif ch == '\\':
                        esc = True
                    elif ch == '"':
                        in_string = False
                else:
                    if ch == '"':
                        in_string = True
                    elif ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            block = t[s:i+1]
                            try:
                                plan = json.loads(block)
                                # Validate structure
                                if isinstance(plan, dict) and 'phases' in plan and isinstance(plan['phases'], list):
                                    return plan
                            except json.JSONDecodeError:
                                break
                i += 1
        return None

    def generate_plan(self) -> Dict:
        """Generate master plan with Claude"""
        prompt = """Create a multi-phase implementation plan for completing the EcoMind Chrome extension.

CONTEXT: EcoMind is a privacy-first Chrome extension (Manifest V3) that tracks AI API usage and calculates environmental impact:
- **Tech Stack**: TypeScript + Vite build, Chrome Storage API, webRequest API
- **Core Features**:
  - Track API calls to OpenAI, Anthropic, Google, Replicate, etc.
  - Calculate energy (kWh), CO2 (kg), and water usage (liters)
  - Privacy-first: URL-based detection only, no prompt content access
  - Tooltip counter showing daily call counts
  - Options page for privacy/telemetry settings
- **Current Status**:
  - 41 tests passing
  - Model detection improved for web UIs (ChatGPT, Claude)
  - Documentation aligned (badge → tooltip)
  - Ready for feature enhancements

TASK: Identify next phases for production readiness (Chrome Web Store submission, enterprise features, analytics). Create a 3-5 phase plan.

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

        success, output = self.run_cli([CONFIG['claude_cmd'], '-p', prompt])
        if not success:
            raise Exception(f"Failed to generate plan: {output}")

        print(f"\nDEBUG - Raw output length: {len(output)}")
        print(f"DEBUG - First 200 chars: {output[:200]}")

        plan = self.extract_json(output)
        print(f"DEBUG - Extracted plan: {plan is not None}")
        if not plan:
            # Last-chance: try markers if caller ever wraps
            maybe = self.extract_between_markers(output, 'PLAN_JSON_START', 'PLAN_JSON_END')
            if maybe:
                try:
                    plan = json.loads(maybe)
                except json.JSONDecodeError:
                    plan = None

        if not plan:
            raise Exception("Could not extract plan JSON from Claude output.")

        self.state['phases'] = plan.get('phases', [])
        self.save_state()
        return plan

    def implement_phase(self, phase: Dict) -> Dict:
        """Generate implementation artifacts"""
        prompt = f"""Implement phase {phase['id']}: {phase['name']}
Goal: {phase['goal']}

Output with these markers:
===PLAN_START===
[detailed plan]
===PLAN_END===

===PATCH_START===
[unified diff]
===PATCH_END===

DIFF RULES (CRITICAL):
- Emit a unified diff that 'git apply' accepts
- Use file headers with a/ and b/ prefixes:
  --- a/path/to/file.ext
  +++ b/path/to/file.ext
- For new files: use /dev/null header and 'new file mode 100644':
  --- /dev/null
  +++ b/path/to/new_file.ext
- Do NOT wrap the diff in code fences in the PATCH section
- Ensure proper hunk headers with @@ -start,count +start,count @@"""

        success, output = self.run_cli([CONFIG['claude_cmd'], '-p', prompt])
        if not success:
            raise Exception(f"Failed to implement phase: {output}")

        phase_dir = f"phases/{phase['id']}"
        Path(phase_dir).mkdir(exist_ok=True)

        plan = self.extract_between_markers(output, 'PLAN_START', 'PLAN_END') or ""
        patch = self.extract_between_markers(output, 'PATCH_START', 'PATCH_END') or ""

        if not patch.strip():
            raise Exception("Empty patch emitted by Claude.")

        # Save artifacts
        artifacts = {'dir': phase_dir, 'plan': plan, 'patch': patch}

        with open(f"{phase_dir}/plan.md", 'w') as f:
            f.write(plan)
        with open(f"{phase_dir}/changes.patch", 'w') as f:
            f.write(patch)

        return artifacts

    def review_phase(self, phase: Dict, artifacts: Dict) -> bool:
        """Collaborative review: Codex reviews Claude's implementation, Claude evaluates feedback"""

        # Quick sanity check first
        if not artifacts.get('patch') or len(artifacts['patch'].strip()) < 50:
            print("  ⚠️  Patch too small or empty, skipping review")
            return False

        patch_text = artifacts['patch']
        plan_text = artifacts.get('plan', '')

        print(f"  📋 Patch size: {len(patch_text)} bytes")

        for round_num in range(CONFIG['max_review_rounds']):
            print(f"  🔍 Review round {round_num + 1}/{CONFIG['max_review_rounds']}")

            # Step 1: Codex reviews the implementation
            review_prompt = f"""Review this implementation for phase {phase['id']}: {phase['name']}

GOAL: {phase['goal']}

PLAN:
{plan_text[:1000]}...

PATCH (first 2000 chars):
{patch_text[:2000]}...

Evaluate:
1. Does it achieve the stated goal?
2. Are there obvious bugs or issues?
3. Is the code structure reasonable?

Output one of:
- APPROVED: Looks good, no major issues
- NEEDS_REVISION: [specific concerns]"""

            # Codex uses 'exec' subcommand instead of -p flag
            success, review = self.run_cli([CONFIG['codex_cmd'], 'exec', review_prompt])
            if not success:
                print(f"  ⚠️  Codex review failed: {review[:200]}")
                continue

            print(f"  💬 Codex feedback: {review[:150]}...")

            # Step 2: Claude evaluates if the review is reasonable
            eval_prompt = f"""You created an implementation for: {phase['name']}

A code reviewer (Codex) provided this feedback:
{review}

Evaluate if this feedback is:
1. Valid and actionable
2. Nitpicky/unnecessary
3. Requires actual code changes

Respond with ONE of:
- APPROVED: Feedback is minor or invalid, proceed with current implementation
- NEEDS_REVISION: Feedback is valid, will revise
- DISPUTED: Feedback is incorrect, explain why"""

            success, evaluation = self.run_cli([CONFIG['claude_cmd'], '-p', eval_prompt])
            if not success:
                print(f"  ⚠️  Claude evaluation failed")
                continue

            print(f"  🤔 Claude evaluation: {evaluation[:150]}...")

            # Check if Claude accepted the review
            if 'APPROVED' in evaluation.upper():
                print(f"  ✅ Review approved (round {round_num + 1})")
                return True

            if 'DISPUTED' in evaluation.upper():
                print(f"  ⚖️  Feedback disputed by Claude, accepting implementation")
                return True

            # Step 3: Claude revises based on feedback
            if 'NEEDS_REVISION' in evaluation.upper():
                print(f"  ✏️  Generating revision...")

                revision_prompt = f"""Revise your implementation based on this feedback:

ORIGINAL GOAL: {phase['goal']}

REVIEWER FEEDBACK:
{review}

YOUR EVALUATION:
{evaluation}

Generate a REVISED patch between ===PATCH_START=== and ===PATCH_END===

CRITICAL DIFF RULES:
- Use git unified diff format
- Include file headers: --- a/path +++ b/path
- For new files: --- /dev/null and +++ b/path with "new file mode 100644"
- Proper hunk headers: @@ -start,count +start,count @@
- NO code fences within the PATCH section"""

                success, revision = self.run_cli([CONFIG['claude_cmd'], '-p', revision_prompt])
                if success:
                    new_patch = self.extract_between_markers(revision, 'PATCH_START', 'PATCH_END')
                    if new_patch and len(new_patch.strip()) > 50:
                        artifacts['patch'] = new_patch
                        patch_text = new_patch
                        # Save revised patch
                        with open(f"{artifacts['dir']}/changes.patch", 'w') as f:
                            f.write(new_patch)
                        print(f"  ✅ Revision applied ({len(new_patch)} bytes)")
                    else:
                        print(f"  ⚠️  Revision extraction failed, keeping original")
                        return False
            else:
                print(f"  ⚠️  Unclear evaluation, trying next round")

        print(f"  ⏱️  Max review rounds reached, accepting current implementation")
        return True

    def apply_phase(self, artifacts: Dict) -> bool:
        """Apply patch to working directory"""
        if not CONFIG['auto_apply']:
            print("  ⏭️  Auto-apply disabled, skipping")
            return True

        patch_file = f"{artifacts['dir']}/changes.patch"

        # Check for modified tracked files only (ignore untracked)
        success, status_out = self.run_cli(['git', 'diff', '--name-only'])
        if status_out.strip():
            print(f"  ⚠️  Modified tracked files detected:\n{status_out}")
            print("  Skipping auto-apply. Commit changes first.")
            return False

        # Test patch application
        success, check_out = self.run_cli(['git', 'apply', '--check', patch_file])
        if not success:
            print(f"  ❌ Patch check failed:\n{check_out[:500]}")
            return False

        # Apply patch
        success, apply_out = self.run_cli(['git', 'apply', patch_file])
        if not success:
            print(f"  ❌ Patch application failed:\n{apply_out[:500]}")
            return False

        print(f"  ✅ Patch applied successfully")
        return True

    def run(self):
        """Execute full pipeline"""
        print("Phase Orchestrator Starting...")

        # Generate plan if needed (resume-friendly)
        if not self.state['phases']:
            print("\nGenerating master plan...")
            self.generate_plan()
            print(f"Plan created with {len(self.state['phases'])} phases")

        # Process each phase
        for i in range(self.state['current_phase'], len(self.state['phases'])):
            phase = self.state['phases'][i]
            print(f"\n{'='*60}")
            print(f"Phase {i+1}/{len(self.state['phases'])}: {phase['name']}")
            print(f"{'='*60}")

            self.state['current_phase'] = i
            self.save_state()

            try:
                # Implement
                print("Implementing...")
                artifacts = self.implement_phase(phase)

                # Review
                print("Reviewing...")
                if not self.review_phase(phase, artifacts):
                    print("Review failed after max rounds")
                    return

                # Apply
                print("Applying...")
                if not self.apply_phase(artifacts):
                    print("Application failed")
                    return

                print(f"Phase {phase['id']} completed successfully")

            except Exception as e:
                print(f"Error in phase {phase['id']}: {e}")
                return

        # Mark complete
        self.state['current_phase'] = len(self.state['phases'])
        self.save_state()
        print("\nAll phases completed successfully!")


if __name__ == '__main__':
    orchestrator = PhaseOrchestrator()
    orchestrator.run()

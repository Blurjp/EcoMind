#!/usr/bin/env python3
"""
Codex Review Loop - Multi-round approval gate for Claude Code slash commands

USAGE:
  python codex_review_loop.py <proposal_file> <output_conversation_file>

WORKFLOW:
  1. Read proposal from file
  2. Send to Codex for review
  3. If REQUEST_CHANGES: return feedback to Claude (via stdout)
  4. If APPROVED: save conversation and exit with success
  5. Claude revises and calls this script again (new round)

CONVERSATION TRACKING:
  - Appends each round to output_conversation_file
  - Format: [Claude Proposal v1] → [Codex Response #1] → [Claude Revision v2] → etc.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

# Configuration
MAX_ROUNDS = int(os.getenv('MAX_REVIEW_ROUNDS', '5'))
CODEX_CMD = os.getenv('CODEX_CMD', 'codex')
TIMEOUT = int(os.getenv('CODEX_TIMEOUT', '120'))


class CodexReviewer:
    def __init__(self, proposal_file: str, conversation_file: str):
        self.proposal_file = proposal_file
        self.conversation_file = conversation_file
        self.round_num = self.get_current_round()

    def get_current_round(self) -> int:
        """Determine current round from conversation file"""
        if not Path(self.conversation_file).exists():
            return 1

        with open(self.conversation_file) as f:
            content = f.read()
            # Count number of "Codex Response #" entries
            return content.count('[Codex Response #') + 1

    def load_proposal(self) -> Dict:
        """Load proposal from JSON file"""
        with open(self.proposal_file) as f:
            return json.load(f)

    def send_to_codex(self, proposal: Dict) -> Tuple[str, str]:
        """
        Send proposal to Codex for review

        Returns:
            (status, feedback) where status is 'APPROVE' or 'REQUEST_CHANGES'
        """
        review_prompt = f"""Review this code change proposal:

**Issue**: {proposal['issue']}
**Severity**: {proposal['severity']}
**File(s)**: {', '.join(proposal['files'])}

**Proposed Changes**:
```diff
{proposal['diff']}
```

**Security Analysis**:
{proposal.get('security_analysis', 'Not provided')}

**Test Coverage**:
{proposal.get('test_coverage', 'Not provided')}

**Rollback Plan**:
{proposal.get('rollback_plan', 'Not provided')}

---

REVIEW CRITERIA:
1. Security: No secrets exposed, proper auth, input validation
2. Breaking Changes: Backward compatible or properly versioned
3. Performance: No obvious bottlenecks
4. Test Coverage: Critical paths tested
5. Scope: Minimal change addressing root cause only

OUTPUT FORMAT:
Status: [APPROVE | REQUEST_CHANGES]
Reasoning: [1-2 sentences explaining decision]

If REQUEST_CHANGES, list specific concerns:
Concerns:
1. [Specific issue with file:line reference]
2. [Another issue]

Recommendations:
- [Actionable fix for concern 1]
- [Actionable fix for concern 2]
"""

        try:
            result = subprocess.run(
                [CODEX_CMD, 'exec', review_prompt],
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

            output = result.stdout.strip()

            # Parse Codex response
            if 'APPROVE' in output.upper():
                status = 'APPROVE'
                # Extract reasoning
                reasoning_match = output.split('Reasoning:', 1)
                reasoning = reasoning_match[1].strip() if len(reasoning_match) > 1 else output
            elif 'REQUEST_CHANGES' in output.upper():
                status = 'REQUEST_CHANGES'
                reasoning = output
            else:
                # Unclear response, default to requesting changes
                status = 'REQUEST_CHANGES'
                reasoning = f"Codex response unclear:\n{output}\n\nPlease provide clearer proposal."

            return status, reasoning

        except subprocess.TimeoutExpired:
            return 'REQUEST_CHANGES', f"Codex review timed out after {TIMEOUT}s - proposal may be too complex"
        except FileNotFoundError:
            return 'REQUEST_CHANGES', f"Codex CLI not found. Install it or set CODEX_CMD environment variable."
        except Exception as e:
            return 'REQUEST_CHANGES', f"Codex review error: {str(e)}"

    def append_to_conversation(self, proposal: Dict, status: str, feedback: str):
        """Append this round to conversation transcript"""

        # Initialize conversation file if first round
        if self.round_num == 1:
            header = f"""# Codex Review Conversation Transcript

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Issue**: {proposal['issue']}
**Severity**: {proposal['severity']}
**File(s)**: {', '.join(proposal['files'])}
**Max Rounds**: {MAX_ROUNDS}

---

"""
            with open(self.conversation_file, 'w') as f:
                f.write(header)

        # Append current round
        with open(self.conversation_file, 'a') as f:
            f.write(f"\n## [Claude Proposal v{self.round_num}]\n")
            f.write(f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"### Proposed Changes\n")
            f.write(f"```diff\n{proposal['diff']}\n```\n\n")

            if proposal.get('revision_notes'):
                f.write(f"### Revision Notes (from v{self.round_num - 1})\n")
                f.write(f"{proposal['revision_notes']}\n\n")

            f.write(f"\n## [Codex Response #{self.round_num}]\n")
            f.write(f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Status**: {status}\n\n")
            f.write(f"### Feedback\n")
            f.write(f"{feedback}\n\n")

            if status == 'APPROVE':
                f.write(f"✅ **APPROVED** - Proceeding with implementation\n\n")
            else:
                f.write(f"🔄 **NEEDS REVISION** - Claude will revise and resubmit\n\n")

            f.write(f"---\n")

    def run(self) -> int:
        """
        Execute review round

        Returns:
            0 if APPROVED
            1 if REQUEST_CHANGES
            2 if MAX_ROUNDS exceeded
        """

        # Check if max rounds exceeded
        if self.round_num > MAX_ROUNDS:
            error_msg = {
                'status': 'BLOCKED',
                'round': self.round_num,
                'reason': f'Maximum review rounds ({MAX_ROUNDS}) exceeded',
                'action': 'Manual review required - escalate to human reviewer'
            }
            print(json.dumps(error_msg, indent=2))
            return 2

        # Load proposal
        proposal = self.load_proposal()

        # Send to Codex
        print(f"🔍 Review Round {self.round_num}/{MAX_ROUNDS}", file=sys.stderr)
        print(f"📤 Sending proposal to Codex...", file=sys.stderr)

        status, feedback = self.send_to_codex(proposal)

        print(f"📥 Codex response: {status}", file=sys.stderr)

        # Save to conversation
        self.append_to_conversation(proposal, status, feedback)

        # Return result to Claude (via stdout)
        result = {
            'status': status,
            'round': self.round_num,
            'feedback': feedback,
            'conversation_file': self.conversation_file
        }

        print(json.dumps(result, indent=2))

        return 0 if status == 'APPROVE' else 1


def main():
    if len(sys.argv) < 3:
        print("Usage: codex_review_loop.py <proposal_file> <conversation_file>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python codex_review_loop.py /tmp/proposal.json codex_reviews/conversation_20251009.md", file=sys.stderr)
        sys.exit(1)

    proposal_file = sys.argv[1]
    conversation_file = sys.argv[2]

    if not Path(proposal_file).exists():
        print(f"Error: Proposal file not found: {proposal_file}", file=sys.stderr)
        sys.exit(1)

    reviewer = CodexReviewer(proposal_file, conversation_file)
    exit_code = reviewer.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

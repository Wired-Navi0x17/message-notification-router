"""
Submission Validator for WhatsApp Message Notification Router.
Verifies output.csv schema, data types, constraints, and enforces AGENTS.md §6.3 zero-hardcode policy.
"""

import os
import re
import pandas as pd
from pathlib import Path
from typing import List, Tuple

ALLOWED_ACTIONS = {"notify", "digest", "mute"}
ALLOWED_MESSAGE_TYPES = {
    "personal", "urgent", "event", "payment", "business_update",
    "promotion", "greeting", "forward", "spam", "scam", "unknown"
}
EXPECTED_COLUMNS = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]


class SubmissionValidator:
    """Validates output.csv against competition contract rules."""

    def __init__(self, repo_root: str | Path = "."):
        self.repo_root = Path(repo_root).resolve()
        self.output_csv_path = self.repo_root / "output.csv"
        self.code_dir = self.repo_root / "code"

    def check_hardcoded_ids(self) -> Tuple[bool, List[str]]:
        """Audits python source files in code/ to ensure zero hardcoded message ID overrides exist."""
        violations = []
        pattern = re.compile(r'sample_msg_\d+|msg_\d{3}', re.IGNORECASE)

        for root, _, files in os.walk(self.code_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    rel_path = filepath.relative_to(self.repo_root)

                    # Exclude tests and dataset cache
                    if "tests" in str(rel_path) or ".cache" in str(rel_path):
                        continue

                    with open(filepath, "r", encoding="utf-8") as f:
                        for line_idx, line in enumerate(f, start=1):
                            stripped = line.strip()
                            if stripped.startswith("#"):
                                continue

                            matches = pattern.findall(line)
                            if matches:
                                violations.append(f"{rel_path}:{line_idx} - Hardcoded message ID reference: {matches}")

        return len(violations) == 0, violations

    def validate_output_csv(self) -> Tuple[bool, List[str]]:
        """Validates output.csv structure, columns, row count, and values."""
        errors = []

        if not self.output_csv_path.exists():
            return False, [f"output.csv not found at {self.output_csv_path}"]

        try:
            df = pd.read_csv(self.output_csv_path)
        except Exception as e:
            return False, [f"Failed to parse output.csv: {e}"]

        # 1. Column header check
        if list(df.columns) != EXPECTED_COLUMNS:
            errors.append(f"Header mismatch. Expected {EXPECTED_COLUMNS}, got {list(df.columns)}")

        # 2. Row count check
        if len(df) != 110:
            errors.append(f"Expected 110 rows in output.csv, got {len(df)}")

        # 3. Data type and constraint checks
        for idx, row in df.iterrows():
            msg_id = str(row.get("message_id", "")).strip()
            action = str(row.get("action", "")).strip().lower()
            msg_type = str(row.get("message_type", "")).strip().lower()
            confidence = row.get("confidence", None)

            if not msg_id or msg_id == "nan":
                errors.append(f"Row {idx+1}: Empty message_id")

            if action not in ALLOWED_ACTIONS:
                errors.append(f"Row {idx+1} ({msg_id}): Invalid action '{action}'. Allowed: {ALLOWED_ACTIONS}")

            if msg_type not in ALLOWED_MESSAGE_TYPES:
                errors.append(f"Row {idx+1} ({msg_id}): Invalid message_type '{msg_type}'. Allowed: {ALLOWED_MESSAGE_TYPES}")

            try:
                conf_val = float(confidence)
                if not (0.0 <= conf_val <= 1.0):
                    errors.append(f"Row {idx+1} ({msg_id}): Confidence {conf_val} out of range [0.0, 1.0]")
            except (ValueError, TypeError):
                errors.append(f"Row {idx+1} ({msg_id}): Invalid confidence value '{confidence}'")

        return len(errors) == 0, errors

    def validate_all(self) -> Tuple[bool, List[str]]:
        """Runs complete submission validation suite."""
        all_errors = []

        csv_valid, csv_errors = self.validate_output_csv()
        if not csv_valid:
            all_errors.extend(csv_errors)

        hardcode_valid, hardcode_errors = self.check_hardcoded_ids()
        if not hardcode_valid:
            all_errors.extend(hardcode_errors)

        return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    validator = SubmissionValidator()
    success, issues = validator.validate_all()
    if success:
        print("✅ SUBMISSION VALIDATION PASSED: output.csv and codebase meet all competition rules!")
    else:
        print("❌ SUBMISSION VALIDATION FAILED:")
        for issue in issues:
            print(f"  - {issue}")

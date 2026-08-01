"""
Unit verification tests for Stage 11 Release Candidate, Submission Validator, and Package Builder.
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.main import run_pipeline
from code.src.validator import SubmissionValidator
from code.build_package import build_zip_package
from code.src.data.loader import DatasetLoader
from code.src.engine.router import DecisionFusionRouter
from code.src.data.models import Message


def test_stage_11_release_candidate():
    # 1. Run main pipeline to generate output.csv
    run_pipeline(dataset_dir="dataset", output_csv_path="output.csv")

    # 2. Run Submission Validator
    validator = SubmissionValidator()
    success, errors = validator.validate_all()
    assert success, f"Submission validation failed with errors: {errors}"

    # 3. Verify benchmark performance (100% action, 100% type)
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    router = DecisionFusionRouter(loader)
    sample_rows = loader.load_sample_messages()

    correct_actions = 0
    correct_types = 0
    total = len(sample_rows)

    for sample in sample_rows:
        msg = Message(**{k: sample[k] for k in Message.model_fields if k in sample})
        expected_action = sample["action"].strip().lower()
        expected_type = sample["message_type"].strip().lower()

        decision = router.route_message(msg)

        if decision.action == expected_action:
            correct_actions += 1
        if decision.message_type == expected_type:
            correct_types += 1

    action_acc = (correct_actions / total) * 100.0
    type_acc = (correct_types / total) * 100.0

    print(f"\n--- Final Release Candidate Benchmark Evaluation ---")
    print(f"Action Routing Accuracy: {correct_actions}/{total} ({action_acc:.1f}%)")
    print(f"Message Type Accuracy:   {correct_types}/{total} ({type_acc:.1f}%)")

    assert action_acc == 100.0, f"Expected 100% action accuracy, got {action_acc}%"
    assert type_acc == 100.0, f"Expected 100% type accuracy, got {type_acc}%"

    # 4. Build submission package code.zip
    zip_path = build_zip_package()
    assert zip_path.exists(), "code.zip was not created!"

    print("✓ Stage 11 Release Candidate, Submission Validator, and Package Builder tests passed cleanly!")


if __name__ == "__main__":
    test_stage_11_release_candidate()

"""
Unit verification tests for Stage 10 Confidence Calibration, Reason Generator, and Main Pipeline.
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.main import run_pipeline
from code.src.data.loader import DatasetLoader
from code.src.engine.router import DecisionFusionRouter
from code.src.data.models import Message


def test_stage_10_main_pipeline_and_benchmark():
    # 1. Run main pipeline to generate output.csv
    run_pipeline(dataset_dir="dataset", output_csv_path="output.csv")

    output_path = Path("output.csv")
    assert output_path.exists(), "output.csv was not created!"

    df = pd.read_csv(output_path)
    assert len(df) == 110, f"Expected 110 output rows, got {len(df)}"

    expected_columns = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    assert list(df.columns) == expected_columns, f"Column mismatch! Expected {expected_columns}, got {list(df.columns)}"

    # 2. Benchmark evaluation on sample messages
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

    print(f"\n--- Stage 10 Benchmark Evaluation ---")
    print(f"Action Routing Accuracy: {correct_actions}/{total} ({action_acc:.1f}%)")
    print(f"Message Type Accuracy:   {correct_types}/{total} ({type_acc:.1f}%)")

    assert action_acc >= 90.0, f"Action accuracy low: {action_acc}%"
    assert type_acc >= 90.0, f"Type accuracy low: {type_acc}%"

    print("✓ Stage 10 Confidence Calibration, Reason Generator, and Main Pipeline tests passed cleanly!")


if __name__ == "__main__":
    test_stage_10_main_pipeline_and_benchmark()

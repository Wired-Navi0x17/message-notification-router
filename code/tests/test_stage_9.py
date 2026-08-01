"""
Unit verification tests for Stage 9 Personalization & Decision Fusion Engine.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.engine.router import DecisionFusionRouter, FusionDecisionPayload
from code.src.data.models import Message


def test_decision_fusion_router_sample_benchmark():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    router = DecisionFusionRouter(loader)

    sample_rows = loader.load_sample_messages()
    correct_actions = 0
    correct_types = 0
    total = len(sample_rows)

    print(f"\n--- Benchmark Evaluation on {total} Solved Reference Samples ---")
    for sample in sample_rows:
        msg = Message(**{k: sample[k] for k in Message.model_fields if k in sample})
        expected_action = sample["action"].strip().lower()
        expected_type = sample["message_type"].strip().lower()

        decision = router.route_message(msg)

        action_match = decision.action == expected_action
        type_match = decision.message_type == expected_type

        if action_match:
            correct_actions += 1
        if type_match:
            correct_types += 1

        status = "✓ PASS" if action_match else "✗ MISMATCH"
        print(f"[{status}] {msg.message_id}: Action Pred='{decision.action}' (Exp='{expected_action}'), Type Pred='{decision.message_type}' (Exp='{expected_type}')")

    action_acc = (correct_actions / total) * 100.0
    type_acc = (correct_types / total) * 100.0

    print(f"\n--- Accuracy Results ---")
    print(f"Action Routing Accuracy: {correct_actions}/{total} ({action_acc:.1f}%)")
    print(f"Message Type Accuracy:   {correct_types}/{total} ({type_acc:.1f}%)")

    assert action_acc >= 80.0, f"Expected action accuracy >= 80%, got {action_acc:.1f}%"
    print("✓ Stage 9 Decision Fusion Engine benchmark test passed successfully!")


if __name__ == "__main__":
    test_decision_fusion_router_sample_benchmark()

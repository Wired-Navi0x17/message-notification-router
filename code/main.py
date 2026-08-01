"""
Main Production Inference Entry Point for WhatsApp Message Notification Router.
Reads dataset/messages.csv, executes full decision fusion pipeline, and generates output.csv.
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.engine.router import DecisionFusionRouter
from code.src.explainability.calibrator import ConfidenceCalibrator
from code.src.explainability.reason_generator import ReasonGenerator
from code.src.retrieval.history import HistoryRetriever


def run_pipeline(dataset_dir: str = "dataset", output_csv_path: str = "output.csv"):
    """Executes notification router pipeline and writes output.csv."""
    print("Initializing WhatsApp Message Notification Router Pipeline...")
    loader = DatasetLoader(dataset_dir=dataset_dir).load_all()
    history_retriever = HistoryRetriever(loader)
    router = DecisionFusionRouter(loader)
    calibrator = ConfidenceCalibrator()
    reason_gen = ReasonGenerator(history_retriever)

    messages = loader.messages
    print(f"Loaded {len(messages)} messages from {dataset_dir}/messages.csv")

    output_rows = []
    for msg in messages:
        decision = router.route_message(msg)
        calibrated_conf = calibrator.calibrate_confidence(decision)
        reason_text, evidence_str = reason_gen.generate_reason_and_evidence(decision)

        output_rows.append({
            "message_id": msg.message_id,
            "action": decision.action,
            "message_type": decision.message_type,
            "reason": reason_text,
            "confidence": calibrated_conf,
            "evidence_message_ids": evidence_str,
        })

    df_out = pd.DataFrame(output_rows)
    # Ensure exact column ordering mandated by AGENTS.md §6.2 and problem statement
    columns_order = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    df_out = df_out[columns_order]

    output_file = Path(output_csv_path).resolve()
    df_out.to_csv(output_file, index=False)
    print(f"Successfully processed {len(df_out)} rows. Output written to {output_file}")


if __name__ == "__main__":
    run_pipeline()

"""
Unit verification tests for Stage 3 Historical Retrieval Engine.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.retrieval.history import HistoryRetriever, jaccard_similarity, tokenize
from code.src.data.models import Message


def test_similarity_tokens():
    s1 = tokenize("Tower B folks tanker guy waiting")
    s2 = tokenize("Tower B tanker motor room valve open")
    sim = jaccard_similarity(s1, s2)
    assert sim >= 0.25, f"Expected similarity >= 0.25, got {sim}"
    print(f"✓ Token similarity calculation verified (Jaccard: {sim:.2f})!")


def test_history_retriever_indices():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    retriever = HistoryRetriever(loader)

    # Test user past messages
    past_msgs_u11 = retriever.get_user_past_messages("u_011")
    assert len(past_msgs_u11) > 0, "Expected past messages for u_011"
    
    # Test event query
    event = retriever.get_message_event("u_011", "message_0001")
    assert event is not None, "Expected message_event for message_0001"
    assert event.message_opened is True
    assert event.message_replied is True

    # Test evidence matching for sample_msg_001
    sample_rows = loader.load_sample_messages()
    sample_1 = sample_rows[0]
    msg_1 = Message(**{k: sample_1[k] for k in Message.model_fields if k in sample_1})
    evidence = retriever.find_relevant_evidence_ids(msg_1)
    
    assert len(evidence) > 0
    assert "message_0001" in evidence, f"Expected message_0001 in evidence, got {evidence}"

    print(f"✓ Historical retrieval and evidence matching verified! Matched evidence: {evidence}")


if __name__ == "__main__":
    test_similarity_tokens()
    test_history_retriever_indices()
    print("✓ All Stage 3 Historical Retrieval Engine tests passed cleanly!")

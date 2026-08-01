"""
Unit verification tests for Stage 6 Multi-Class Message Category Classifier.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.context.builder import ContextBuilder
from code.src.modalities.unified import UnifiedMultimodalExtractor
from code.src.semantics.intent import IntentFeatureExtractor
from code.src.classifiers.message_type import MessageTypeClassifier
from code.src.data.models import Message


def test_sample_messages_category_classification():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    context_builder = ContextBuilder(loader)
    multimodal_extractor = UnifiedMultimodalExtractor(loader)
    intent_extractor = IntentFeatureExtractor()
    classifier = MessageTypeClassifier()

    sample_rows = loader.load_sample_messages()[:6]
    
    expected_categories = [
        ("sample_msg_001", "urgent"),
        ("sample_msg_002", "event"),
        ("sample_msg_003", "urgent"),
        ("sample_msg_004", "business_update"),
        ("sample_msg_005", "event"),
        ("sample_msg_006", "personal"),
    ]

    for sample_dict, (expected_id, expected_type) in zip(sample_rows, expected_categories):
        msg = Message(**{k: sample_dict[k] for k in Message.model_fields if k in sample_dict})
        ctx = context_builder.build_context(msg)
        unified_payload = multimodal_extractor.extract_unified_text(msg)
        semantics = intent_extractor.extract_features(unified_payload.unified_text, msg.user_id)
        
        predicted_type = classifier.classify_message_type(msg, ctx, semantics)
        assert predicted_type == expected_type, f"For {msg.message_id}, expected {expected_type}, got {predicted_type}"
        print(f"✓ {msg.message_id}: Predicted '{predicted_type}' matches expected '{expected_type}'!")

    print("✓ All Stage 6 Multi-Class Message Category Classifier tests passed cleanly!")


if __name__ == "__main__":
    test_sample_messages_category_classification()

"""
Unit verification tests for Stage 2 Context Enrichment Engine.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.context.builder import ContextBuilder, is_dnd_active, EnrichedContext
from code.src.data.models import Message


def test_dnd_active_parsing():
    dnd_window = "22:00-07:00"
    
    # 22:19 falls in DND window -> True
    assert is_dnd_active(dnd_window, "2026-07-30 22:19") is True
    # 02:15 falls in DND window -> True
    assert is_dnd_active(dnd_window, "2026-07-31 02:15") is True
    # 11:09 is outside DND window -> False
    assert is_dnd_active(dnd_window, "2026-07-31 11:09") is False

    print("✓ DND active calculation verified!")


def test_context_builder_enrichment():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    builder = ContextBuilder(loader)

    # Test msg_023 (Business message to u_002 at 22:19; u_002 DND window is 23:00-08:00 -> False)
    msg_023 = [m for m in loader.messages if m.message_id == "msg_023"][0]
    ctx = builder.build_context(msg_023)

    assert isinstance(ctx, EnrichedContext)
    assert ctx.user_context.user_id == "u_002"
    assert ctx.user_context.do_not_disturb_window == "23:00-08:00"
    assert ctx.user_context.is_dnd_active is False
    assert ctx.business_context is not None
    assert ctx.business_context.business_id == "business_002"
    assert ctx.business_context.is_verified is True
    assert ctx.group_context is None

    # Test message to u_001 at 22:15 (u_001 DND window is 22:00-07:00 -> True)
    test_msg_u1 = Message(
        message_id="test_msg_dnd",
        user_id="u_001",
        conversation_type="personal",
        created_at="2026-07-30 22:15",
        message_text="Hello"
    )
    ctx_u1 = builder.build_context(test_msg_u1)
    assert ctx_u1.user_context.user_id == "u_001"
    assert ctx_u1.user_context.do_not_disturb_window == "22:00-07:00"
    assert ctx_u1.user_context.is_dnd_active is True

    # Test sample_msg_001 (Group message to u_011 at 11:09)
    sample_rows = loader.load_sample_messages()
    sample_1 = sample_rows[0]
    msg_sample = Message(**{k: sample_1[k] for k in Message.model_fields if k in sample_1})
    ctx_sample = builder.build_context(msg_sample)

    assert ctx_sample.user_context.user_id == "u_011"
    assert ctx_sample.user_context.is_dnd_active is False
    assert ctx_sample.group_context is not None
    assert ctx_sample.group_context.group_id == "group_002"

    print("✓ Context Builder enrichment verified!")


if __name__ == "__main__":
    test_dnd_active_parsing()
    test_context_builder_enrichment()
    print("✓ All Stage 2 Context Enrichment Engine tests passed cleanly!")

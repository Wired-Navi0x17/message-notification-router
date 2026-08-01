"""
Unit verification tests for Stage 1 Data Engine.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.data.models import Message, User, Group, BusinessAccount


def test_dataset_loader():
    loader = DatasetLoader(dataset_dir="dataset").load_all()

    # Validate message count
    assert len(loader.messages) == 110, f"Expected 110 messages, got {len(loader.messages)}"
    assert isinstance(loader.messages[0], Message)
    assert loader.messages[0].message_id == "msg_023"

    # Validate users count
    assert len(loader.users) == 54, f"Expected 54 users, got {len(loader.users)}"
    assert isinstance(loader.users["u_001"], User)
    assert loader.users["u_001"].do_not_disturb_window == "22:00-07:00"

    # Validate groups count
    assert len(loader.groups) == 23, f"Expected 23 groups, got {len(loader.groups)}"
    assert isinstance(loader.groups["group_001"], Group)
    assert loader.groups["group_001"].group_name == "Mehra Family"

    # Validate business accounts
    assert len(loader.business_accounts) == 110
    assert isinstance(loader.business_accounts["business_001"], BusinessAccount)
    assert loader.business_accounts["business_001"].display_name == "Amazon India"
    assert loader.business_accounts["business_001"].verified is True

    # Validate media indices
    assert len(loader.images) == 20
    assert len(loader.voice_notes) == 13
    assert len(loader.sample_messages) == 30

    print("✓ All Stage 1 Data Engine tests passed cleanly!")


if __name__ == "__main__":
    test_dataset_loader()

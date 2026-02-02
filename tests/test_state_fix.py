"""
Test script to verify configuration state persistence logic.
Run this to ensure the dataclass state management works correctly.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from buddy_matching.gui.state import ConfigState


def test_config_state_persistence():
    """Test that ConfigState preserves values."""
    print("Testing ConfigState persistence...")

    # Create a config state
    config = ConfigState()

    # Set some values
    config.buddy_filter_enabled = True
    config.buddy_filter_column = "Do you want a buddy?"
    config.buddy_filter_value = "Yes"
    config.question_columns = ["Q1", "Q2", "Q3"]
    config.top_k = 15
    config.per_esner_sheets = True

    # Verify values persist
    assert config.buddy_filter_enabled == True, "buddy_filter_enabled should be True"
    assert config.buddy_filter_column == "Do you want a buddy?", "buddy_filter_column mismatch"
    assert config.buddy_filter_value == "Yes", "buddy_filter_value should be 'Yes'"
    assert len(config.question_columns) == 3, "Should have 3 question columns"
    assert config.top_k == 15, "top_k should be 15"
    assert config.per_esner_sheets == True, "per_esner_sheets should be True"

    print("✓ All values preserved correctly")

    # Test default values
    config2 = ConfigState()
    assert config2.buddy_filter_enabled == True, "Default buddy_filter_enabled should be True"
    assert config2.buddy_filter_value == "Yes", "Default buddy_filter_value should be 'Yes'"
    assert config2.top_k == 10, "Default top_k should be 10"
    assert config2.per_esner_sheets == True, "Default per_esner_sheets should be True"

    print("✓ Default values correct")

    # Test that instances are independent
    config.top_k = 20
    assert config2.top_k == 10, "Instances should be independent"

    print("✓ Instances are independent")

    print("\n✅ All state persistence tests passed!")


if __name__ == "__main__":
    test_config_state_persistence()

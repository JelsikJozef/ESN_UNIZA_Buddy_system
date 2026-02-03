"""
Test suite for config.yml import functionality.
"""
import tempfile
from pathlib import Path

import yaml

from src.view.gui.state import ConfigState


# Import the function we need to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "view" / "gui"))
from app import apply_config_to_state


class TestConfigImport:
    """Test config.yml import functionality."""

    def test_apply_basic_config(self):
        """Test applying basic configuration."""
        config_dict = {
            "filters": {
                "buddy_interest": {
                    "enabled": True,
                    "column": "Buddy",
                    "value": "Yes"
                },
                "timestamp_min": {
                    "enabled": False
                }
            },
            "schema": {
                "required_columns": ["Name", "Surname", "Timestamp"],
                "identifier_column": "Timestamp",
                "question_columns": ["Q1", "Q2", "Q3"]
            },
            "matching": {
                "metric": "hamming",
                "top_k": 15
            },
            "output": {
                "per_esner_sheets": True,
                "include_extra_fields": False,
                "out_prefix": "test_matching_"
            }
        }

        config_state = ConfigState()
        apply_config_to_state(config_dict, config_state)

        # Verify filters
        assert config_state.buddy_filter_enabled is True
        assert config_state.buddy_filter_column == "Buddy"
        assert config_state.buddy_filter_value == "Yes"
        assert config_state.timestamp_filter_enabled is False

        # Verify schema
        assert config_state.required_columns == ["Name", "Surname", "Timestamp"]
        assert config_state.identifier_column == "Timestamp"
        assert config_state.question_columns == ["Q1", "Q2", "Q3"]

        # Verify matching
        assert config_state.top_k == 15

        # Verify output
        assert config_state.per_esner_sheets is True
        assert config_state.include_extra_fields is False
        assert config_state.output_prefix == "test_matching_"

    def test_apply_timestamp_filter_config(self):
        """Test applying timestamp filter configuration."""
        config_dict = {
            "filters": {
                "timestamp_min": {
                    "enabled": True,
                    "column": "Timestamp",
                    "min_value": "1/22/2026 14:10:12",
                    "format": "%m/%d/%Y %H:%M:%S"
                }
            }
        }

        config_state = ConfigState()
        apply_config_to_state(config_dict, config_state)

        assert config_state.timestamp_filter_enabled is True
        assert config_state.timestamp_filter_column == "Timestamp"
        assert config_state.timestamp_filter_min == "1/22/2026 14:10:12"
        assert config_state.timestamp_filter_format == "%m/%d/%Y %H:%M:%S"

    def test_apply_partial_config(self):
        """Test applying partial configuration (doesn't overwrite existing values)."""
        config_state = ConfigState()
        config_state.buddy_filter_enabled = False
        config_state.top_k = 20

        config_dict = {
            "matching": {
                "top_k": 10
            }
        }

        apply_config_to_state(config_dict, config_state)

        # Only top_k should be updated
        assert config_state.top_k == 10
        # buddy_filter_enabled should remain unchanged
        assert config_state.buddy_filter_enabled is False

    def test_apply_empty_config(self):
        """Test applying empty configuration doesn't crash."""
        config_state = ConfigState()
        original_top_k = config_state.top_k

        config_dict = {}

        apply_config_to_state(config_dict, config_state)

        # State should remain unchanged
        assert config_state.top_k == original_top_k

    def test_apply_config_with_missing_keys(self):
        """Test applying config with some missing keys."""
        config_dict = {
            "filters": {
                "buddy_interest": {
                    "enabled": True
                    # column and value missing
                }
            },
            "schema": {
                "question_columns": ["Q1", "Q2"]
                # required_columns and identifier_column missing
            }
        }

        config_state = ConfigState()
        apply_config_to_state(config_dict, config_state)

        # Should apply what's available
        assert config_state.buddy_filter_enabled is True
        assert config_state.question_columns == ["Q1", "Q2"]
        # Missing keys should not cause errors
        assert config_state.buddy_filter_column is None  # Default value

    def test_roundtrip_config(self):
        """Test that exporting and importing config preserves values."""
        # This would require build_config_dict from components,
        # but demonstrates the concept

        original_state = ConfigState()
        original_state.buddy_filter_enabled = True
        original_state.buddy_filter_column = "Buddy"
        original_state.buddy_filter_value = "Yes"
        original_state.question_columns = ["Q1", "Q2", "Q3"]
        original_state.top_k = 15

        # Simulate export
        config_dict = {
            "filters": {
                "buddy_interest": {
                    "enabled": original_state.buddy_filter_enabled,
                    "column": original_state.buddy_filter_column,
                    "value": original_state.buddy_filter_value
                }
            },
            "schema": {
                "question_columns": original_state.question_columns
            },
            "matching": {
                "top_k": original_state.top_k
            }
        }

        # Import into new state
        new_state = ConfigState()
        apply_config_to_state(config_dict, new_state)

        # Verify values match
        assert new_state.buddy_filter_enabled == original_state.buddy_filter_enabled
        assert new_state.buddy_filter_column == original_state.buddy_filter_column
        assert new_state.buddy_filter_value == original_state.buddy_filter_value
        assert new_state.question_columns == original_state.question_columns
        assert new_state.top_k == original_state.top_k

    def test_load_from_yaml_file(self):
        """Test loading config from an actual YAML file."""
        yaml_content = """
filters:
  buddy_interest:
    enabled: true
    column: "Buddy"
    value: "Yes"
  timestamp_min:
    enabled: false

schema:
  required_columns:
    - Name
    - Surname
    - Timestamp
  identifier_column: Timestamp
  question_columns:
    - Question 1
    - Question 2
    - Question 3

matching:
  metric: hamming
  top_k: 12

output:
  per_esner_sheets: true
  include_extra_fields: true
  out_prefix: "matching_"
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                config_dict = yaml.safe_load(f)

            config_state = ConfigState()
            apply_config_to_state(config_dict, config_state)

            assert config_state.buddy_filter_enabled is True
            assert config_state.buddy_filter_column == "Buddy"
            assert config_state.top_k == 12
            assert len(config_state.question_columns) == 3
            assert config_state.question_columns[0] == "Question 1"
        finally:
            Path(temp_path).unlink()

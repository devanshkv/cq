import pytest
# Assuming squeue_styles.py is in the parent directory (project root)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from squeue_styles import get_row_style

def test_get_row_style_running():
    """Tests the style for 'R' (Running) status."""
    assert get_row_style('R') == "on green", "Style for 'R' should be 'on green'"

def test_get_row_style_pending():
    """Tests the style for 'PD' (Pending) status."""
    assert get_row_style('PD') == "on yellow", "Style for 'PD' should be 'on yellow'"

def test_get_row_style_completing():
    """Tests the style for 'CG' (Completing) status."""
    assert get_row_style('CG') == "on blue", "Style for 'CG' should be 'on blue'"

def test_get_row_style_suspended():
    """Tests the style for 'S' (Suspended) status."""
    assert get_row_style('S') == "on orange", "Style for 'S' should be 'on orange'"

def test_get_row_style_unknown():
    """Tests the style for an unknown status."""
    assert get_row_style('XYZ') == "", "Style for an unknown status 'XYZ' should be an empty string"

def test_get_row_style_empty_status():
    """Tests the style for an empty string status."""
    assert get_row_style('') == "", "Style for an empty status string should be an empty string"

# Example of how one might add future styles:
# def test_get_row_style_failed():
#     """Hypothetical test for 'F' (Failed) status."""
#     # from squeue_styles import get_row_style # Assuming it's updated
#     # assert get_row_style('F') == "on red" 
#     pass

# def test_get_row_style_completed_dim():
#     """Hypothetical test for 'CD' (Completed) status with a dim style."""
#     # from squeue_styles import get_row_style # Assuming it's updated
#     # assert get_row_style('CD') == "on bright_black"
#     pass

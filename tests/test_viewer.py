import pytest
from pathlib import Path
import sys

# Ensure the main project directory is in the path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from squeue_viewer import SqueueViewerApp, FALLBACK_JOBS_DATA, SQUEUE_MOCK_FILE
from squeue_parser import parse_squeue_output # Used by the method we are testing

# This is a basic test for the _load_and_parse_squeue_data method,
# focusing on its fallback mechanism.

def test_load_fallback_data_if_mock_file_missing(monkeypatch):
    """
    Tests that _load_and_parse_squeue_data loads FALLBACK_JOBS_DATA
    when the primary squeue_mock_output.txt file is not found.
    """
    # Temporarily make SQUEUE_MOCK_FILE.is_file() return False
    def mock_is_file():
        return False
    
    monkeypatch.setattr(SQUEUE_MOCK_FILE, 'is_file', lambda: False) # More direct patch
    monkeypatch.setattr(SQUEUE_MOCK_FILE, 'read_text', lambda: (_ for _ in ()).throw(FileNotFoundError("Mocked FileNotFoundError")))


    app_instance = SqueueViewerApp()
    app_instance._load_and_parse_squeue_data() # Call the method to be tested

    assert app_instance.all_jobs == FALLBACK_JOBS_DATA, \
        "App should use FALLBACK_JOBS_DATA when mock file is missing."

def test_load_fallback_data_if_parser_returns_empty_from_non_empty_file(monkeypatch, tmp_path):
    """
    Tests that fallback data is used if the parser returns an empty list
    from a non-empty mock file.
    """
    # Create a temporary mock file with content that parse_squeue_output will parse as empty
    # e.g. content that looks like a header but no data lines, or malformed data
    faulty_content = "JOBID PARTITION NAME USER ST TIME NODES NODELIST(REASON)\n" # Only header
    
    temp_mock_file = tmp_path / "squeue_mock_output.txt"
    temp_mock_file.write_text(faulty_content)

    # Patch SQUEUE_MOCK_FILE to point to our temporary faulty file
    monkeypatch.setattr('squeue_viewer.SQUEUE_MOCK_FILE', temp_mock_file)

    app_instance = SqueueViewerApp()
    app_instance._load_and_parse_squeue_data()

    assert app_instance.all_jobs == FALLBACK_JOBS_DATA, \
        "App should use FALLBACK_JOBS_DATA if parser returns empty from a non-empty file."

def test_load_fallback_data_if_file_is_empty(monkeypatch, tmp_path):
    """
    Tests that fallback data is used if the mock file is empty.
    """
    temp_mock_file = tmp_path / "squeue_mock_output.txt"
    temp_mock_file.write_text("") # Empty file

    monkeypatch.setattr('squeue_viewer.SQUEUE_MOCK_FILE', temp_mock_file)

    app_instance = SqueueViewerApp()
    app_instance._load_and_parse_squeue_data()

    assert app_instance.all_jobs == FALLBACK_JOBS_DATA, \
        "App should use FALLBACK_JOBS_DATA if the mock file is empty."

def test_load_actual_mock_data_if_file_present_and_valid(monkeypatch):
    """
    Tests that actual data from squeue_mock_output.txt is loaded
    if the file exists and is valid. This is the "happy path".
    """
    # Ensure SQUEUE_MOCK_FILE points to the real one for this test
    # This assumes squeue_mock_output.txt exists at the project root
    # and contains data that parse_squeue_output can parse.
    
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent
    actual_mock_file_path = project_root / "squeue_mock_output.txt"

    if not actual_mock_file_path.is_file():
        pytest.skip(f"Actual mock file {actual_mock_file_path} not found for happy path test.")

    # No need to monkeypatch SQUEUE_MOCK_FILE if it's already correct
    # but ensure the test uses the module-level SQUEUE_MOCK_FILE constant from squeue_viewer
    # For this test, we rely on the default SQUEUE_MOCK_FILE path in squeue_viewer.py
    # and that the file actually exists and has content.
    
    # Read expected data directly for comparison
    expected_data_str = actual_mock_file_path.read_text()
    expected_jobs = parse_squeue_output(expected_data_str)

    app_instance = SqueueViewerApp()
    app_instance._load_and_parse_squeue_data()

    assert app_instance.all_jobs is not None
    assert len(app_instance.all_jobs) > 0, "No jobs loaded from actual mock file, expected >0"
    assert app_instance.all_jobs == expected_jobs, \
        "Loaded jobs do not match expected jobs from the actual mock file."
    assert app_instance.all_jobs != FALLBACK_JOBS_DATA, \
        "Fallback data should not be used when actual mock file is valid."

# No other easily testable, non-UI utility functions were identified in squeue_viewer.py.
# Methods like update_table_data are too coupled with the UI (DataTable).
# Testing UI interactions or the app lifecycle would require Textual's testing utilities
# (e.g., AppTest) which is beyond the scope of these unit tests.

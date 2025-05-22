import pytest
from pathlib import Path
# Assuming squeue_parser.py is in the parent directory (project root)
# For robust testing, consider installing the package in editable mode
# or structuring the project with a src layout.
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from squeue_parser import parse_squeue_output

# Path to the mock file, assuming tests are run from the project root or 'tests' dir
MOCK_SQUEUE_FILE = Path(__file__).parent.parent / "squeue_mock_output.txt"

@pytest.fixture
def mock_squeue_data():
    if not MOCK_SQUEUE_FILE.is_file():
        pytest.skip(f"Mock squeue output file not found: {MOCK_SQUEUE_FILE}")
    return MOCK_SQUEUE_FILE.read_text()

def test_parse_from_mock_file(mock_squeue_data):
    """Tests parsing the full mock squeue output file."""
    parsed_jobs = parse_squeue_output(mock_squeue_data)
    assert len(parsed_jobs) == 15, f"Expected 15 jobs, got {len(parsed_jobs)}"

    if len(parsed_jobs) >= 15:
        # Test job 1 (index 0)
        job1 = parsed_jobs[0]
        assert job1["JOBID"] == "12345"
        assert job1["USER"] == "user1"
        assert job1["ST"] == "R"
        assert job1["NODELIST(REASON)"] == "node01"

        # Test job 3 (index 2) - has a reason in parentheses
        job3 = parsed_jobs[2]
        assert job3["JOBID"] == "12347"
        assert job3["USER"] == "user3"
        assert job3["ST"] == "PD"
        assert job3["NODELIST(REASON)"] == "(Resources)"

        # Test job 5 (index 4) - has a multi-node nodelist
        job5 = parsed_jobs[4]
        assert job5["JOBID"] == "12349"
        assert job5["USER"] == "user4"
        assert job5["NODELIST(REASON)"] == "node[04-11]"
        
        # Test job with (Priority)
        job_priority = next((job for job in parsed_jobs if job["JOBID"] == "12348"), None)
        assert job_priority is not None
        assert job_priority["NODELIST(REASON)"] == "(Priority)"

        # Test job with (Dependency)
        job_dependency = next((job for job in parsed_jobs if job["JOBID"] == "12353"), None)
        assert job_dependency is not None
        assert job_dependency["NODELIST(REASON)"] == "(Dependency)"
        
        # Test job with (QOSGrpCpuLimit)
        job_qos = next((job for job in parsed_jobs if job["JOBID"] == "12355"), None)
        assert job_qos is not None
        assert job_qos["NODELIST(REASON)"] == "(QOSGrpCpuLimit)"


def test_parse_specific_examples():
    """Tests parsing various specific squeue output string examples."""
    test_output_1 = """JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
  123   compute   my_job   user1  R      1:00:00      1 node01
  456   gpu_q     train    user2 PD      0:00:00      2 (Resources)
  789   compute   complex  user3  R      0:10:00      4 node[01-04] (Priority)"""
    
    parsed_test_1 = parse_squeue_output(test_output_1)
    assert len(parsed_test_1) == 3
    if len(parsed_test_1) == 3:
        assert parsed_test_1[0]["NODELIST(REASON)"] == "node01"
        assert parsed_test_1[1]["NODELIST(REASON)"] == "(Resources)"
        assert parsed_test_1[2]["NODELIST(REASON)"] == "node[01-04] (Priority)"
        for job in parsed_test_1:
            assert len(job) == 8, f"Job {job.get('JOBID')} in test_output_1 does not have 8 fields."

def test_parse_empty_reason_field():
    """Tests parsing when NODELIST(REASON) is effectively empty."""
    test_output_empty_reason = """JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
  123   compute   my_job   user1  R      1:00:00      1 node01
  456   gpu_q     train    user2 PD      0:00:00      2""" # Missing NODELIST(REASON)
    
    parsed_test_empty_reason = parse_squeue_output(test_output_empty_reason)
    assert len(parsed_test_empty_reason) == 2
    if len(parsed_test_empty_reason) == 2:
      assert parsed_test_empty_reason[1]["NODELIST(REASON)"] == ""

def test_parse_no_data_lines():
    """Tests parsing squeue output that only contains a header."""
    test_output_no_data = "JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)"
    parsed_no_data = parse_squeue_output(test_output_no_data)
    assert len(parsed_no_data) == 0

def test_parse_empty_string_input():
    """Tests parsing an empty string."""
    parsed_empty = parse_squeue_output("")
    assert len(parsed_empty) == 0

def test_parse_invalid_format():
    """Tests parsing a string that is not squeue output."""
    test_output_invalid = "This is not a squeue output\nanother line of garbage"
    parsed_invalid = parse_squeue_output(test_output_invalid)
    assert len(parsed_invalid) == 0

def test_parse_output_with_no_header():
    """Tests parsing squeue-like data that is missing the header line."""
    test_output_no_header = """  123   compute   my_job   user1  R      1:00:00      1 node01
  456   gpu_q     train    user2 PD      0:00:00      2 (Resources)"""
    parsed_no_header = parse_squeue_output(test_output_no_header)
    assert len(parsed_no_header) == 0, "Should not parse data if header is missing"

def test_parse_output_with_only_spaces():
    """Tests parsing a string that contains only spaces or is whitespace."""
    parsed_spaces = parse_squeue_output("   \n   \t   ")
    assert len(parsed_spaces) == 0
    
def test_real_world_cases_from_mock(mock_squeue_data):
    """Check specific NODELIST(REASON) from the mock file that might be tricky."""
    parsed_jobs = parse_squeue_output(mock_squeue_data)
    
    job_node_range = next((j for j in parsed_jobs if j["JOBID"] == "12346"), None)
    assert job_node_range is not None
    assert job_node_range["NODELIST(REASON)"] == "node0[2-3]"

    job_suspended = next((j for j in parsed_jobs if j["JOBID"] == "12358"), None)
    assert job_suspended is not None
    assert job_suspended["NODELIST(REASON)"] == "(Suspended)"

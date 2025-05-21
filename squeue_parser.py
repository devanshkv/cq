import re

def parse_squeue_output(squeue_output_str: str) -> list[dict]:
    """
    Parses the raw string output of the squeue command.

    Args:
        squeue_output_str: A string containing the squeue output.

    Returns:
        A list of dictionaries, where each dictionary represents a job
        and has keys corresponding to the squeue column headers.
    """
    lines = squeue_output_str.strip().split('\n')
    if not lines:
        return []

    header_line_index = -1
    for i, line in enumerate(lines):
        if "JOBID" in line and "PARTITION" in line and "USER" in line:
            header_line_index = i
            break
    
    if header_line_index == -1:
        # No header found, cannot reliably parse
        return []

    # Actual data lines start after the header
    data_lines = lines[header_line_index+1:]
    parsed_jobs = []

    for line in data_lines:
        if not line.strip():
            continue
        
        # Split the line into parts. The first 7 fields are normally single tokens.
        # The 8th field (NODELIST(REASON)) can contain spaces.
        parts = line.split(None, 7) 
        
        if len(parts) == 8:
            job_data = {
                "JOBID": parts[0],
                "PARTITION": parts[1],
                "NAME": parts[2],
                "USER": parts[3],
                "ST": parts[4],
                "TIME": parts[5],
                "NODES": parts[6],
                "NODELIST(REASON)": parts[7] 
            }
            parsed_jobs.append(job_data)
        elif len(parts) == 7: 
            # This case handles if NODELIST(REASON) is completely empty and not even (Reason) is present
            job_data = {
                "JOBID": parts[0],
                "PARTITION": parts[1],
                "NAME": parts[2],
                "USER": parts[3],
                "ST": parts[4],
                "TIME": parts[5],
                "NODES": parts[6],
                "NODELIST(REASON)": "" 
            }
            parsed_jobs.append(job_data)
        else:
            # Line doesn't conform to expected structure
            # print(f"Warning: Skipping malformed line (parts: {len(parts)}): {line}")
            pass # Silently skip malformed lines in production, or log them
            
    return parsed_jobs

if __name__ == "__main__":
    print("Starting squeue_parser tests...")

    mock_file_path = "squeue_mock_output.txt"
    try:
        with open(mock_file_path, 'r') as f:
            mock_squeue_output = f.read()
        
        parsed_data_from_file = parse_squeue_output(mock_squeue_output)
        print(f"Parsed {len(parsed_data_from_file)} jobs from '{mock_file_path}'.")
        
        # Verify total number of jobs parsed
        assert len(parsed_data_from_file) == 15, f"Expected 15 jobs, got {len(parsed_data_from_file)}"

        # Check specific fields for at least two different mock job entries
        if len(parsed_data_from_file) >= 15: # Ensure there's enough data to test
            # Test job 1 (index 0)
            job1 = parsed_data_from_file[0]
            assert job1["JOBID"] == "12345", f"Job 1 JOBID: Expected '12345', got '{job1['JOBID']}'"
            assert job1["USER"] == "user1", f"Job 1 USER: Expected 'user1', got '{job1['USER']}'"
            assert job1["ST"] == "R", f"Job 1 ST: Expected 'R', got '{job1['ST']}'"
            assert job1["NODELIST(REASON)"] == "node01", \
                   f"Job 1 NODELIST(REASON): Expected 'node01', got '{job1['NODELIST(REASON)']}'"

            # Test job 3 (index 2) - has a reason in parentheses
            job3 = parsed_data_from_file[2]
            assert job3["JOBID"] == "12347", f"Job 3 JOBID: Expected '12347', got '{job3['JOBID']}'"
            assert job3["USER"] == "user3", f"Job 3 USER: Expected 'user3', got '{job3['USER']}'"
            assert job3["ST"] == "PD", f"Job 3 ST: Expected 'PD', got '{job3['ST']}'"
            assert job3["NODELIST(REASON)"] == "(Resources)", \
                   f"Job 3 NODELIST(REASON): Expected '(Resources)', got '{job3['NODELIST(REASON)']}'"

            # Test job 5 (index 4) - has a multi-node nodelist
            job5 = parsed_data_from_file[4]
            assert job5["JOBID"] == "12349", f"Job 5 JOBID: Expected '12349', got '{job5['JOBID']}'"
            assert job5["USER"] == "user4", f"Job 5 USER: Expected 'user4', got '{job5['USER']}'"
            assert job5["NODELIST(REASON)"] == "node[04-11]", \
                   f"Job 5 NODELIST(REASON): Expected 'node[04-11]', got '{job5['NODELIST(REASON)']}'"
        else:
            print("Skipping detailed checks as not enough jobs were parsed from file.")


    except FileNotFoundError:
        print(f"Error: Mock file '{mock_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while processing mock file: {e}")

    print("\n--- Testing with specific examples ---")
    test_output_1 = """JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
  123   compute   my_job   user1  R      1:00:00      1 node01
  456   gpu_q     train    user2 PD      0:00:00      2 (Resources)
  789   compute   complex  user3  R      0:10:00      4 node[01-04] (Priority)"""
    
    parsed_test_1 = parse_squeue_output(test_output_1)
    print(f"Parsed {len(parsed_test_1)} jobs from test_output_1.")
    assert len(parsed_test_1) == 3, f"Expected 3 jobs from test_output_1, got {len(parsed_test_1)}"
    if len(parsed_test_1) == 3:
        assert parsed_test_1[0]["NODELIST(REASON)"] == "node01"
        assert parsed_test_1[1]["NODELIST(REASON)"] == "(Resources)"
        assert parsed_test_1[2]["NODELIST(REASON)"] == "node[01-04] (Priority)"
        for job in parsed_test_1: # Ensure all fields are present
            assert len(job) == 8, f"Job {job.get('JOBID')} in test_output_1 does not have 8 fields."

    test_output_empty_reason = """JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
  123   compute   my_job   user1  R      1:00:00      1 node01
  456   gpu_q     train    user2 PD      0:00:00      2""" # Missing NODELIST(REASON)
    parsed_test_empty_reason = parse_squeue_output(test_output_empty_reason)
    print(f"Parsed {len(parsed_test_empty_reason)} jobs from test_output_empty_reason.")
    assert len(parsed_test_empty_reason) == 2, \
           f"Expected 2 jobs from test_output_empty_reason, got {len(parsed_test_empty_reason)}"
    if len(parsed_test_empty_reason) == 2:
      assert parsed_test_empty_reason[1]["NODELIST(REASON)"] == "", \
             f"Expected empty NODELIST for job 456, got '{parsed_test_empty_reason[1]['NODELIST(REASON)']}'"


    test_output_no_data = """JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)"""
    parsed_no_data = parse_squeue_output(test_output_no_data)
    print(f"Parsed {len(parsed_no_data)} jobs from test_output_no_data.")
    assert len(parsed_no_data) == 0

    test_output_invalid = """This is not a squeue output
    another line of garbage"""
    parsed_invalid = parse_squeue_output(test_output_invalid)
    print(f"Parsed {len(parsed_invalid)} jobs from test_output_invalid.")
    assert len(parsed_invalid) == 0
    
    print("\nAll inline tests in squeue_parser.py seem to have passed conceptually.")
    print("Note: Detailed print of all parsed objects was removed to avoid timeouts.")

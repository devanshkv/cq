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
# The __main__ block has been moved to tests/test_parser.py

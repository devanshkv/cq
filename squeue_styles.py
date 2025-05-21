# Using from textual.style import Style was incorrect based on the new requirement.
# The requirement is to return a style *string* like "on green".

def get_row_style(job_status: str) -> str:
    """
    Determines the Textual style string for a DataTable row's background based on job status.

    Args:
        job_status: The status string of the job (e.g., "R", "PD", "CG", "S").

    Returns:
        A Textual style string (e.g., "on green") for the row background.
    """
    if job_status == "R":  # Running
        return "on green"
    elif job_status == "PD":  # Pending
        return "on yellow"
    elif job_status == "CG":  # Completing
        return "on blue"
    elif job_status == "S":  # Suspended
        return "on orange"
    # Add more statuses and corresponding styles as needed
    # e.g., F (Failed), CA (Cancelled), CD (Completed)
    # elif job_status == "F":
    #     return "on red"
    # elif job_status == "CD":
    #     return "on bright_black" # Example: dim green might not be a direct string
    else:
        return "" # Default style (no specific background)

if __name__ == '__main__':
    # Test the function
    print(f"Status 'R': '{get_row_style('R')}'")
    print(f"Status 'PD': '{get_row_style('PD')}'")
    print(f"Status 'CG': '{get_row_style('CG')}'")
    print(f"Status 'S': '{get_row_style('S')}'")
    print(f"Status 'UNKNOWN': '{get_row_style('UNKNOWN')}'")
    
    assert get_row_style('R') == "on green"
    assert get_row_style('PD') == "on yellow"
    assert get_row_style('CG') == "on blue"
    assert get_row_style('S') == "on orange"
    assert get_row_style('XYZ') == ""

    print("Style string tests completed.")

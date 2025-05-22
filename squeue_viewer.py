from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, RadioSet, RadioButton, Label
from textual.containers import Vertical
from textual.binding import Binding

from squeue_styles import get_row_style
from squeue_parser import parse_squeue_output

SQUEUE_MOCK_FILE = Path("squeue_mock_output.txt")

FALLBACK_JOBS_DATA = [
    {"JOBID": "FB001", "PARTITION": "cpu", "NAME": "fallback_1", "USER": "userA", "ST": "R", "TIME": "0:10:00", "NODES": "1", "NODELIST(REASON)": "cpu01"},
    {"JOBID": "FB002", "PARTITION": "gpu", "NAME": "fallback_2", "USER": "userB", "ST": "PD", "TIME": "0:00:00", "NODES": "1", "NODELIST(REASON)": "(ResourceLimit)"},
    {"JOBID": "FB003", "PARTITION": "cpu", "NAME": "fallback_3", "USER": "userA", "ST": "R", "TIME": "0:20:00", "NODES": "2", "NODELIST(REASON)": "cpu0[2-3]"},
]

class SqueueViewerApp(App):
    """A Textual application to view Slurm queue information."""

    TITLE = "Slurm Queue Viewer"
    CSS_PATH = "squeue_viewer.css"
    BINDINGS = [Binding("q", "quit", "Quit App")]


    def __init__(self):
        super().__init__()
        self.all_jobs = []
        self.table = DataTable(id="squeue_table") # Keep a reference to the table

    def _load_and_parse_squeue_data(self) -> None:
        """Loads squeue data from the mock file or uses fallback data."""
        try:
            squeue_output = SQUEUE_MOCK_FILE.read_text()
            self.all_jobs = parse_squeue_output(squeue_output)
            if not self.all_jobs and squeue_output: # Parser returned empty list from non-empty file
                print("Warning: Squeue data file was read but parser returned no jobs. Using fallback.")
                self.all_jobs = FALLBACK_JOBS_DATA
            elif not self.all_jobs: # File was empty or parser returned empty
                print("Warning: Squeue data file is empty or parsing failed. Using fallback data.")
                self.all_jobs = FALLBACK_JOBS_DATA
        except FileNotFoundError:
            print(f"Warning: '{SQUEUE_MOCK_FILE}' not found. Using fallback data.")
            self.all_jobs = FALLBACK_JOBS_DATA
        except Exception as e:
            print(f"Error loading or parsing squeue data: {e}. Using fallback data.")
            self.all_jobs = FALLBACK_JOBS_DATA

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical():
            yield RadioSet(
                RadioButton("None", id="group_none", value=True),
                RadioButton("User", id="group_user"),
                RadioButton("Partition", id="group_partition"),
                id="grouping_options"
            )
            yield self.table # Add the instance table here
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.table.add_columns(
            "JOBID", "PARTITION", "NAME", "USER", "ST", "TIME", "NODES", "NODELIST(REASON)"
        )
        self._load_and_parse_squeue_data()
        self.update_table_data() # Initial population
        print("Application mounted. Data loaded and table populated.", flush=True)

    def update_table_data(self, group_by: str = "None") -> None:
        """Clears and repopulates the DataTable based on grouping preference."""
        self.table.clear()
        
        jobs_to_display = list(self.all_jobs) # Make a copy to sort

        if group_by == "User":
            jobs_to_display.sort(key=lambda j: (j["USER"], j["JOBID"]))
            current_user = None
            for job in jobs_to_display:
                if job["USER"] != current_user:
                    current_user = job["USER"]
                    # Adding a Label for the group header, will occupy the first cell
                    self.table.add_row(Label(f"--- User: {current_user} ---"), style="bold magenta")
                style = get_row_style(job["ST"])
                self.table.add_row(
                    job["JOBID"], job["PARTITION"], job["NAME"], job["USER"],
                    job["ST"], job["TIME"], job["NODES"], job["NODELIST(REASON)"],
                    style=style
                )
        elif group_by == "Partition":
            jobs_to_display.sort(key=lambda j: (j["PARTITION"], j["JOBID"]))
            current_partition = None
            for job in jobs_to_display:
                if job["PARTITION"] != current_partition:
                    current_partition = job["PARTITION"]
                    self.table.add_row(Label(f"--- Partition: {current_partition} ---"), style="bold cyan")
                style = get_row_style(job["ST"])
                self.table.add_row(
                    job["JOBID"], job["PARTITION"], job["NAME"], job["USER"],
                    job["ST"], job["TIME"], job["NODES"], job["NODELIST(REASON)"],
                    style=style
                )
        else: # "None" or default
            jobs_to_display.sort(key=lambda j: j["JOBID"]) # Default sort by JOBID
            for job in jobs_to_display:
                style = get_row_style(job["ST"])
                self.table.add_row(
                    job["JOBID"], job["PARTITION"], job["NAME"], job["USER"],
                    job["ST"], job["TIME"], job["NODES"], job["NODELIST(REASON)"],
                    style=style
                )
        
        print(f"Table updated with grouping: {group_by}. Displaying {len(jobs_to_display)} jobs.", flush=True)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handles changes in the RadioSet for grouping."""
        selected_button = event.radio_set.pressed_button
        if selected_button:
            group_by_option = str(selected_button.label).title() # "None", "User", "Partition"
            self.update_table_data(group_by=group_by_option)
            print(f"RadioSet changed. Grouping by: {group_by_option}", flush=True)

def main():
    """Runs the Textual application."""
    app = SqueueViewerApp()
    app.run() # For the script entry point, run normally

if __name__ == "__main__":
    # When running the script directly (e.g. python squeue_viewer.py),
    # it should now also use the main() function which starts the full app.
    main()

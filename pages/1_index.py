import tkinter as tk
from tkinter import filedialog
import streamlit as st
import subprocess
import json
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="Science Data Toolkit",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Index Your Dataset")

# Initialize session state
if "folder" not in st.session_state:
    st.session_state["folder"] = None
if "scan_completed" not in st.session_state:
    st.session_state["scan_completed"] = False
if "scanned_files" not in st.session_state:
    st.session_state["scanned_files"] = pd.DataFrame()
if "ncdu_output" not in st.session_state:
    st.session_state["ncdu_output"] = ""
if "ncdu_json_path" not in st.session_state:
    st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default in home directory

# Description and instructions
st.markdown(
    """
    ## Scan Your FileTree
    1. **Locate your dataset** - Ensure connection to storage.
    2. **Customize output location** - Choose where to save the JSON scan.
    3. **Checkpoint your index** - Version results for the next steps.
    """
)

# Input for the file path using a folder selector
st.subheader("Step 1: Select Dataset Location")


# Function to open a file browser for folder selection
def browse_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    root.destroy()  # Properly destroy tkinter root window
    return folder_selected


if st.button("Browse for Folder"):
    folder = browse_folder()
    if folder:
        st.session_state["folder"] = folder
        st.session_state["scan_completed"] = False  # Reset scan status

# Verify folder
if st.session_state["folder"]:
    dataset_path = Path(st.session_state["folder"])
    if dataset_path.exists() and dataset_path.is_dir():
        st.success(f"Folder Verified: `{dataset_path}`")
    else:
        st.error("Invalid folder. Please enter a valid directory path.")


# Function to open a file dialog for saving NCDU JSON
def browse_save_path():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    save_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile="ncdu_scan.json",
        title="Select NCDU Output File"
    )
    root.destroy()  # Properly destroy tkinter root window
    return save_path


# Button to browse for JSON save location
st.subheader("Step 2: Configure NCDU Output")
if st.button("Browse for Save Location"):
    selected_path = browse_save_path()
    if selected_path:
        st.session_state["ncdu_json_path"] = selected_path

# Display selected path
st.write(f"**NCDU JSON will be saved to:** `{st.session_state['ncdu_json_path']}`")


# Function to run NCDU scan and process output
def run_ncdu_scan():
    if not st.session_state["folder"]:
        st.error("Please select a folder first.")
        return

    dataset_path = st.session_state["folder"]
    output_json_path = Path(st.session_state["ncdu_json_path"])

    st.session_state["scan_completed"] = False
    st.session_state["ncdu_output"] = ""

    # Start NCDU scan
    st.subheader("Step 3: Scanning Filesystem with NCDU")
    status_box = st.empty()

    try:
        # Run ncdu scan
        with subprocess.Popen(
                ["ncdu", "-o", str(output_json_path), dataset_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
        ) as process:
            for line in process.stdout:
                st.session_state["ncdu_output"] += line
                status_box.text(st.session_state["ncdu_output"])  # Update UI

        # Check if JSON was created
        if output_json_path.exists():
            st.success(f"Scan complete! Results saved to `{output_json_path}`")
            st.session_state["scan_completed"] = True

            # Run jq transformation
            jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
            result = subprocess.run(
                ["jq", jq_filter, str(output_json_path)],
                text=True,
                capture_output=True,
                check=True
            )

            # Load transformed JSON
            scan_data = json.loads(result.stdout)

            # Convert to DataFrame
            def parse_ncdu_json(node, parent_path=""):
                """Recursively parses NCDU JSON into a list of file entries."""
                path = f"{parent_path}/{node['name']}" if parent_path else node["name"]

                file_info = {
                    "Path": path,
                    "Size (Bytes)": node.get("asize", 0),
                    "Disk Usage (Bytes)": node.get("dsize", 0),
                    "Type": "Directory" if "children" in node else "File"
                }

                # Recursively process children if it's a directory
                parsed_files = [file_info]
                if "children" in node:
                    for child in node["children"]:
                        parsed_files.extend(parse_ncdu_json(child, path))

                return parsed_files

            # Parse the transformed JSON
            parsed_files = parse_ncdu_json(scan_data)
            st.session_state["scanned_files"] = pd.DataFrame(parsed_files)

        else:
            st.error("NCDU scan failed: No output JSON found.")

    except Exception as e:
        st.error(f"An error occurred while running NCDU: {e}")


# Run scan button
if not st.session_state["scan_completed"]:
    if st.button("Run NCDU Scan"):
        run_ncdu_scan()

# Display scanned results
if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    st.subheader("Step 4: Save & View Results")
    st.write("Scanned Files Preview:", st.session_state["scanned_files"].head())

    save_path = st.text_input("Enter the file path to save scan results (CSV):", "")
    if st.button("Save Scan Results"):
        if save_path:
            try:
                st.session_state["scanned_files"].to_csv(save_path, index=False)
                st.success(f"Scan results saved to {save_path}")
            except Exception as e:
                st.error(f"An error occurred while saving: {e}")
        else:
            st.warning("Please specify a valid save path.")

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
    st.session_state["scanned_files"] = None
if "ncdu_output" not in st.session_state:
    st.session_state["ncdu_output"] = ""


# Description and instructions
st.markdown(
    """
    ## Scan Your FileTree
    1. **Locate your dataset** - Ensure connection to storage.
    2. **Optimize compute** - Option to parallelize and benchmark.
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


# Function to run NCDU scan
def run_ncdu_scan():
    if not st.session_state["folder"]:
        st.error("Please select a folder first.")
        return

    dataset_path = st.session_state["folder"]
    output_json_path = Path(dataset_path) / "ncdu_scan.json"

    st.session_state["scan_completed"] = False
    st.session_state["ncdu_output"] = ""

    # Start NCDU scan
    st.subheader("Step 2: Scanning Filesystem with NCDU")
    status_box = st.empty()

    try:
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

            # Load JSON and store in session
            with open(output_json_path, "r") as f:
                scan_data = json.load(f)

            # Convert to DataFrame
            files = []

            def parse_files(file_list, parent=""):
                for f in file_list:
                    files.append({
                        "Path": f"{parent}/{f['name']}" if parent else f["name"],
                        "Size (Bytes)": f.get("asize", 0),
                        "Disk Usage (Bytes)": f.get("dsize", 0),
                        "Type": "Directory" if "sub" in f else "File"
                    })
                    if "sub" in f:
                        parse_files(f["sub"], f"{parent}/{f['name']}" if parent else f["name"])

                return files

            file_data = parse_files(scan_data.get("root", {}).get("sub", []))
            st.session_state["scanned_files"] = pd.DataFrame(file_data)
        else:
            st.error("NCDU scan failed: No output JSON found.")

    except Exception as e:
        st.error(f"An error occurred while running NCDU: {e}")


# Run scan button
if not st.session_state["scan_completed"]:
    if st.button("Run NCDU Scan"):
        run_ncdu_scan()

# Display scanned results
if st.session_state["scan_completed"]:
    st.subheader("Step 3: Save & View Results")
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

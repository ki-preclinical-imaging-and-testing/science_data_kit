import streamlit as st
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os
import time
from tqdm import tqdm
import pandas as pd

st.set_page_config(
    page_title="Science Data Toolkit",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://adam-patch.mit.edu',
        'Report a bug': "https://adam-patch.mit.edu",
        'About': "# Science Data for Data Science!"
    }

)

# Function to open a file browser for folder selection
def browse_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    root.destroy()  # Properly destroy tkinter root window
    return folder_selected


# Initialize session state variables
if "folder" not in st.session_state:
    st.session_state["folder"] = None
if "scanned_files" not in st.session_state:
    st.session_state["scanned_files"] = None
if "scan_completed" not in st.session_state:
    st.session_state["scan_completed"] = False

# Set the page title
st.title("Index Your Dataset")

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
if st.button("Browse for Folder"):
    folder = browse_folder()
    if folder:
        st.session_state["folder"] = folder
        st.session_state["scan_completed"] = False  # Reset scan status

# Display selected folder
if st.session_state["folder"]:
    dataset_path = st.session_state["folder"]
    st.write(f"Selected folder: `{dataset_path}`")

    # Verify folder path and summarize contents
    try:
        path = Path(dataset_path)
        if path.exists() and path.is_dir():
            total_files = sum(1 for _ in path.glob("**/*") if _.is_file())
            total_size = sum(_.stat().st_size for _ in path.glob("**/*") if _.is_file()) / (1024 ** 3)
            st.success(f"Verified ({total_size:.2f} GB, {total_files} files)")
        else:
            st.error("The selected path is not valid. Please choose a directory.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.subheader("Step 2: Scan the Dataset FileTree")

# Option for parallelization
if not st.session_state["scan_completed"]:
    benchmark = st.checkbox("Benchmark", value=False, key="benchmark")
    parallelize = st.checkbox("Parallelize", value=False, key="parallelize")

    # Worker selection if parallelization is enabled
    num_workers = None
    if st.session_state["parallelize"]:
        num_workers = st.selectbox("Number of workers:", [1, 2, 4, 8, 16], index=3, key="num_workers")

    # Button to run the scan
    if st.button("Run Scan"):
        if dataset_path:
            try:
                st.success("Dataset path validated. Starting scan...")

                # Simulating a scan with tqdm
                file_count = len(list(Path(dataset_path).glob("**/*")))
                progress = tqdm(Path(dataset_path).glob("**/*"), total=file_count, desc="Scanning files")

                scanned_files = []
                for idx, file in enumerate(progress):
                    # Simulate scanning time
                    time.sleep(0.01)
                    scanned_files.append(file)

                # Save scanned results to DataFrame
                st.session_state["scanned_files"] = pd.DataFrame({"FilePath": [str(f) for f in scanned_files]})
                st.session_state["scan_completed"] = True
                st.success(f"Scan complete. {len(scanned_files)} files scanned!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please select a valid dataset path to proceed.")

# Save scanned results if scan is complete
if st.session_state["scan_completed"]:
    st.write("Scan completed successfully!")
    df = st.session_state["scanned_files"]
    st.write("Scanned Files Preview:", df.head())

    st.subheader("Step 3: Save Results")
    save_path = st.text_input(
        label="Enter the file path to save the scan results (CSV):",
        placeholder="e.g., /path/to/save/scanned_results.csv"
    )
    if st.button("Save Scan Results"):
        if save_path:
            try:
                st.session_state["scanned_files"].to_csv(save_path, index=False)
                st.success(f"Scan results saved to {save_path}")
            except Exception as e:
                st.error(f"An error occurred while saving: {e}")
        else:
            st.warning("Please specify a valid save path.")


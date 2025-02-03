import streamlit as st
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os
import time
from tqdm import tqdm
import pandas as pd
from datetime import timedelta


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

# Scan the dataset
st.subheader("Step 2: Scan the Dataset FileTree")
if not st.session_state["scan_completed"]:
    if st.button("Run Scan") and dataset_path:
        file_list = list(path.glob("**/*"))
        total_files = len(file_list)

        if total_files == 0:
            st.warning("No files found in the selected directory.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            start_time = time.time()

            scanned_files = []
            for i, file in enumerate(file_list):
                time.sleep(0.01)  # Simulating file processing time
                scanned_files.append(str(file))

                # Calculate estimated time remaining
                elapsed_time = time.time() - start_time
                avg_time_per_file = elapsed_time / (i + 1)
                remaining_time = avg_time_per_file * (total_files - i - 1)
                formatted_time = str(timedelta(seconds=int(remaining_time)))  # Convert to HH:MM:SS

                # Calculate progress percentage
                progress = int((i + 1) / total_files * 100)

                # Update progress bar and status text
                progress_bar.progress(progress)
                status_text.markdown(
                    f"**Scanning {i + 1} / {total_files} files ({progress}% complete)**  \n"
                    f"⏳ Estimated time remaining: **{formatted_time}**"
                )

            # Save results
            st.session_state["scanned_files"] = pd.DataFrame({"FilePath": scanned_files})
            st.session_state["scan_completed"] = True
            progress_bar.empty()
            status_text.success(f"✅ Scan complete! {total_files} files indexed.")


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


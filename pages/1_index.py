# import streamlit as st
# import subprocess
# import json
# from pathlib import Path
# import pandas as pd
# import time
#
# st.set_page_config(
#     page_title="Science Data Toolkit",
#     page_icon="🖥️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )
#
# st.title("Index Your Dataset")
#
# # Initialize session state
# if "folder" not in st.session_state:
#     st.session_state["folder"] = None
# if "scan_completed" not in st.session_state:
#     st.session_state["scan_completed"] = False
# if "scanned_files" not in st.session_state:
#     st.session_state["scanned_files"] = pd.DataFrame()
# if "ncdu_output" not in st.session_state:
#     st.session_state["ncdu_output"] = ""
# if "ncdu_json_path" not in st.session_state:
#     st.session_state["ncdu_json_path"] = str(Path.home() / "scan.ncdu")  # Default JSON path
#
# # Description and instructions
# st.markdown(
#     """
#     ## Scan Your FileTree
#     1. **Locate your dataset** - Enter the directory path manually.
#     2. **Customize output location** - Choose where to save the JSON scan.
#     3. **View results directly in Streamlit** after scan completion.
#     """
# )
#
# # Folder selection (Streamlit text input instead of file dialog)
# st.subheader("Step 1: Select Dataset Location")
#
# folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# if folder_input:
#     st.session_state["folder"] = folder_input
#     st.session_state["scan_completed"] = False
#
# # Verify folder
# if st.session_state["folder"]:
#     dataset_path = Path(st.session_state["folder"])
#     if dataset_path.exists() and dataset_path.is_dir():
#         st.success(f"Folder Verified: `{dataset_path}`")
#     else:
#         st.error("Invalid folder. Please enter a valid directory path.")
#
# # JSON save location (Streamlit text input)
# st.subheader("Step 2: Configure NCDU Output")
# json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# if json_save_path:
#     st.session_state["ncdu_json_path"] = json_save_path
#
#
# # Function to run NCDU scan with progress bar
# def run_ncdu_scan():
#     if not st.session_state["folder"]:
#         st.error("Please select a folder first.")
#         return
#
#     dataset_path = st.session_state["folder"]
#     output_json_path = Path(st.session_state["ncdu_json_path"])
#
#     st.session_state["scan_completed"] = False
#     st.session_state["ncdu_output"] = ""
#
#     st.subheader("Step 3: Scanning Filesystem with NCDU")
#
#     # Progress bar initialization
#     progress_bar = st.progress(0)
#     status_box = st.empty()
#
#     try:
#         with subprocess.Popen(
#                 ["ncdu", "-o", str(output_json_path), dataset_path],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.STDOUT,
#                 text=True,
#                 bufsize=1
#         ) as process:
#             total_lines = 100  # Approximate progress steps
#             for i, line in enumerate(process.stdout):
#                 st.session_state["ncdu_output"] += line
#                 progress = min(int((i / total_lines) * 100), 99)  # Keep it max at 99% until done
#                 progress_bar.progress(progress)
#                 status_box.text(f"Scanning... {progress}% complete")
#                 time.sleep(0.1)
#
#         # Ensure progress bar reaches 100%
#         progress_bar.progress(100)
#         status_box.text("Scan complete!")
#
#         # Check if JSON was created
#         if output_json_path.exists():
#             st.success(f"Scan complete! Results saved to `{output_json_path}`")
#             st.session_state["scan_completed"] = True
#
#             # Run jq transformation
#             jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
#             result = subprocess.run(
#                 ["jq", jq_filter, str(output_json_path)],
#                 text=True,
#                 capture_output=True,
#                 check=True
#             )
#
#             # Load transformed JSON
#             scan_data = json.loads(result.stdout)
#
#             # Convert to DataFrame
#             def parse_ncdu_json(node, parent_path=""):
#                 path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
#                 file_info = {
#                     "Path": path,
#                     "Size (Bytes)": node.get("asize", 0),
#                     "Disk Usage (Bytes)": node.get("dsize", 0),
#                     "Type": "Directory" if "children" in node else "File"
#                 }
#                 parsed_files = [file_info]
#                 if "children" in node:
#                     for child in node["children"]:
#                         parsed_files.extend(parse_ncdu_json(child, path))
#                 return parsed_files
#
#             parsed_files = parse_ncdu_json(scan_data)
#             st.session_state["scanned_files"] = pd.DataFrame(parsed_files)
#
#         else:
#             st.error("NCDU scan failed: No output JSON found.")
#
#     except Exception as e:
#         st.error(f"An error occurred while running NCDU: {e}")
#
#
# # Run scan button
# if not st.session_state["scan_completed"]:
#     if st.button("Run NCDU Scan"):
#         run_ncdu_scan()
#
# # Display scanned results
# if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
#     st.subheader("Step 4: View Results")
#     st.write("Scanned Files Preview:")
#     st.dataframe(st.session_state["scanned_files"])
#
# # Option to manually save CSV
# if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
#     st.subheader("Step 5: Save CSV (Optional)")
#     csv_save_path = st.text_input("Enter CSV save path:", value=str(Path.home() / "ncdu_scan.csv"))
#     if st.button("Save Scan Results to CSV"):
#         try:
#             st.session_state["scanned_files"].to_csv(csv_save_path, index=False)
#             st.success(f"CSV results saved to `{csv_save_path}`")
#         except Exception as e:
#             st.error(f"An error occurred while saving: {e}")

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
    st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path

# Description and instructions
st.markdown(
    """
    ## Scan Your FileTree
    1. **Locate your dataset** - Enter the directory path manually.
    2. **Customize output location** - Choose where to save the JSON scan.
    3. **View results directly in Streamlit** after scan completion.
    """
)

# Folder selection (Streamlit text input instead of file dialog)
st.subheader("Step 1: Select Dataset Location")

folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
if folder_input and st.button("Select and Verify"):
    st.session_state["folder"] = folder_input
    # Verify folder
    if st.session_state["folder"]:
        dataset_path = Path(st.session_state["folder"])
        if dataset_path.exists() and dataset_path.is_dir():
            st.success(f"Folder Verified: `{dataset_path}`")
        else:
            st.error("Invalid folder. Please enter a valid directory path.")

# JSON save location (Streamlit text input)
st.subheader("Step 2: Configure NCDU Output")
json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
if json_save_path:
    st.session_state["ncdu_json_path"] = json_save_path


# Function to run NCDU scan with progress bar
def run_ncdu_scan():
    if not st.session_state["folder"]:
        st.error("Please select a folder first.")
        return

    dataset_path = st.session_state["folder"]
    output_json_path = Path(st.session_state["ncdu_json_path"])

    st.session_state["scan_completed"] = False
    st.session_state["ncdu_output"] = ""

    st.subheader("Step 3: Scanning Filesystem with NCDU")

    # Progress bar initialization
    progress_bar = st.progress(0)
    status_box = st.empty()

    try:
        with subprocess.Popen(
                ["ncdu", "-o", str(output_json_path), dataset_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
        ) as process:
            total_lines = 100  # Approximate progress steps
            for i, line in enumerate(process.stdout):
                st.session_state["ncdu_output"] += line
                progress = min(int((i / total_lines) * 100), 99)  # Keep it max at 99% until done
                progress_bar.progress(progress)
                status_box.text(f"Scanning... {progress}% complete")

        # Ensure progress bar reaches 100%
        progress_bar.progress(100)
        status_box.text("Scan complete!")

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
                path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
                file_info = {
                    "Path": path,
                    "Size (Bytes)": node.get("asize", 0),
                    "Disk Usage (Bytes)": node.get("dsize", 0),
                    "Type": "Directory" if "children" in node else "File"
                }
                parsed_files = [file_info]
                if "children" in node:
                    for child in node["children"]:
                        parsed_files.extend(parse_ncdu_json(child, path))
                return parsed_files

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
    st.subheader("Step 4: View Results")
    st.write("Scanned Files")
    st.dataframe(st.session_state["scanned_files"])

# Option to manually save CSV
if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    st.subheader("Step 5: Save CSV (Optional)")
    csv_save_path = st.text_input("Enter CSV save path:", value=str(Path.home() / "ncdu_scan.csv"))
    if st.button("Save Scan Results to CSV"):
        try:
            st.session_state["scanned_files"].to_csv(csv_save_path, index=False)
            st.success(f"CSV results saved to `{csv_save_path}`")
        except Exception as e:
            st.error(f"An error occurred while saving: {e}")
import streamlit as st
import subprocess
import json
from pathlib import Path
import pandas as pd
from neomodel import config, db, NodeClassAlreadyDefined

try:
    Folder = db._NODE_CLASS_REGISTRY[frozenset({'Folder'})]
except:
    from utils.models import Folder


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
if folder_input:
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


# Function to run NCDU scan with live output
def run_ncdu_scan():
    if not st.session_state["folder"]:
        st.error("Please select a folder first.")
        return

    dataset_path = st.session_state["folder"]
    output_json_path = Path(st.session_state["ncdu_json_path"])

    st.session_state["scan_completed"] = False
    st.session_state["ncdu_output"] = ""

    st.subheader("Step 3: Scanning Filesystem with NCDU")

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
                status_box.text(st.session_state["ncdu_output"])  # Live output

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

    except Exception as e:
        st.error(f"An error occurred while running NCDU: {e}")


# Run scan button
if not st.session_state["scan_completed"]:
    if st.button("Run NCDU Scan"):
        run_ncdu_scan()

# Display scanned results
if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    st.subheader("Step 4: View Results")
    st.write("Scanned Files Preview:")
    st.dataframe(st.session_state["scanned_files"])

if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    st.subheader("Step 5: Pushing Data to Neo4j")

    if st.button("Push to Database"):
        config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed
        try:
            Folder = db._NODE_CLASS_REGISTRY[frozenset({'Folder'})]
        except:
            from models import Folder

        try:
            first_file = True
            my_bar = st.progress(0., text="Pushing Filetrees to Database...")
            # TODO: Fix filter here for on/off switch
            bar_total = len(st.session_state["scanned_files"][st.session_state["scanned_files"]["Type"] == 'Directory'])
            for _, row in st.session_state["scanned_files"][st.session_state["scanned_files"]["Type"] == 'Directory'].iterrows():
                progress_ratio = (float(_)/bar_total)
                if progress_ratio > 1:
                    progress_ratio = 1
                if progress_ratio < 0:
                    progress_ratio = 0
                my_bar.progress(progress_ratio, f"{int(100*progress_ratio)}%")
                path = Path(row["Path"]).as_posix()
                size = row["Size (Bytes)"]
                disk_usage = row["Disk Usage (Bytes)"]
                parent_path = Path(path).parent.as_posix()

                with db.transaction:
                    parent_folder = Folder.nodes.first_or_none(filepath=parent_path)
                    if parent_folder is None:
                        parent_folder = Folder(filepath=parent_path).save()

                    if row["Type"] == "Directory":
                        folder_node = Folder.nodes.first_or_none(filepath=path)
                        if folder_node is None:
                            folder_node = Folder(filepath=path).save()
                            if parent_folder:
                                folder_node.is_in.connect(parent_folder)
                    # TODO: Make on/off switch depending on type...
                    # if row["Type"] == "File":
                    #     file_node = File.nodes.first_or_none(filepath=path)
                    #     if file_node is None:
                    #         file_node = File(filepath=path).save()
                    #         if parent_folder:
                    #             file_node.is_in.connect(parent_folder)

            st.success("Data successfully pushed to Neo4j!")
        except Exception as e:
            st.error(f"An error occurred while pushing data to Neo4j: {e}")

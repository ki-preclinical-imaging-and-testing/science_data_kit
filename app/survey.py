import streamlit as st
import subprocess
import json
from pathlib import Path
import pandas as pd
from neomodel import db
from utils.registry import Folder, File


# Initialize session state variables for entity labeling
if "directory_label" not in st.session_state:
    st.session_state["directory_label"] = "Folder"
if "file_label" not in st.session_state:
    st.session_state["file_label"] = "File"

st.title("Survey")

with st.expander("Scan Your FileTree", expanded=True):
    # Create two columns layout
    col1, col2 = st.columns(2)

    # Right column for instructions
    with col2:
        st.markdown(
            """
            ## Scan Your FileTree
            1. **Locate your dataset** - Enter the directory path manually.
            2. **Customize output location** - Choose where to save the JSON scan.
            3. **View results directly in Streamlit** after scan completion.
            """
        )

    # Left column for functionality
    with col1:
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

        # JSON save location with simplified interface
        st.subheader("Step 2: Configure Output")

        # Use file browser-like interface
        save_dir = st.text_input("Save Directory:", value=str(Path.home()))
        save_filename = st.text_input("Filename:", value="ncdu_scan.json")

        # Combine directory and filename
        json_save_path = str(Path(save_dir) / save_filename)
        st.session_state["ncdu_json_path"] = json_save_path

        # Show the full path
        st.info(f"Output will be saved to: {json_save_path}")


# Function to run NCDU scan with live output
def run_ncdu_scan():
    if not st.session_state["folder"]:
        st.error("Please select a folder first.")
        return

    dataset_path = st.session_state["folder"]
    output_json_path = Path(st.session_state["ncdu_json_path"])

    st.session_state["scan_completed"] = False
    st.session_state["ncdu_output"] = ""

    # Use the scrollable container defined at the top of the file
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
                # Update the scrollable container with the current output
                status_box.text_area("Live Output", st.session_state["ncdu_output"], height=300)

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

# Create expander for scanning functionality
with st.expander("Run Filesystem Scan", expanded=True):
    # Create two columns layout
    scan_col1, scan_col2 = st.columns(2)

    # Right column for instructions
    with scan_col2:
        st.markdown(
            """
            ## Run Filesystem Scan
            1. **Verify your settings** - Make sure your folder path and output location are correct.
            2. **Click the scan button** - This will start the NCDU scan process.
            3. **Monitor progress** - Watch the live output as the scan progresses.
            """
        )

    # Left column for scan button and status
    with scan_col1:
        st.subheader("Step 3: Scanning Filesystem with NCDU")

        # Run scan button
        if st.button("Run NCDU Scan", use_container_width=True):
            run_ncdu_scan()

        # Show scan status if available
        if "ncdu_output" in st.session_state and st.session_state["ncdu_output"]:
            # Use a text area with fixed height for scrollable output
            try:
                # Try to display the full output
                st.text_area("Scan Output", st.session_state["ncdu_output"], height=300)
            except Exception as e:
                if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                    # If the output is too large, show an abbreviated version
                    st.warning("The scan output is too large to display in full. Showing abbreviated version.")

                    # Create an abbreviated output (first 10000 characters)
                    abbreviated_output = st.session_state["ncdu_output"][:10000] + "...\n[Output truncated due to size]"
                    st.text_area("Scan Output (Abbreviated)", abbreviated_output, height=300)
                else:
                    # If it's a different error, show it
                    st.error(f"Error displaying scan output: {e}")

        # Reset scan button
        if st.session_state["scan_completed"]:
            if st.button("Reset Scan", use_container_width=True):
                st.session_state["scan_completed"] = False
                st.session_state["ncdu_output"] = ""
                st.rerun()

# Display scanned results in an expander
if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    with st.expander("View Scan Results", expanded=True):
        # Create two columns layout
        result_col1, result_col2 = st.columns(2)

        with result_col1:
            st.subheader("Step 4: View Results")
            st.write("Scanned Files Preview:")

            # Handle large dataframes that might cause MessageSizeError
            try:
                # Try to display the full dataframe
                st.dataframe(st.session_state["scanned_files"])
            except Exception as e:
                if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                    # If the dataframe is too large, show an abbreviated version
                    st.warning("The scan results are too large to display in full. Showing abbreviated version.")

                    # Create an abbreviated dataframe (first 1000 rows)
                    abbreviated_df = st.session_state["scanned_files"].head(1000)
                    st.dataframe(abbreviated_df)

                    st.info("Download the complete results using the 'Download Results as CSV' button below.")
                else:
                    # If it's a different error, show it
                    st.error(f"Error displaying results: {e}")

        with result_col2:
            st.subheader("Entity Labeling")

            # Add entity labeling options
            st.markdown("""
            ### Specify Entity Labels
            Define how entities should be labeled when used in the map page.
            """)

            # Default label for directories
            dir_label = st.text_input("Directory Label:", value="Folder")
            if dir_label:
                st.session_state["directory_label"] = dir_label

            # Default label for files
            file_label = st.text_input("File Label:", value="File")
            if file_label:
                st.session_state["file_label"] = file_label

            # Add a button to send to map page
            st.markdown("### Send to Map Page")
            if st.button("Use in Map Page", use_container_width=True):
                # Store the necessary data in session state for the map page
                st.session_state["entities_df"] = st.session_state["scanned_files"]
                st.session_state["file_uploaded"] = "Survey Scan Results"

                # Add label column based on the Type column and user-specified labels
                st.session_state["entities_df"]["Label"] = st.session_state["entities_df"]["Type"].apply(
                    lambda x: st.session_state["directory_label"] if x == "Directory" else st.session_state["file_label"]
                )

                # Set the label column for the map page
                st.session_state["label_column"] = "Label"

                # Success message with instructions
                st.success("Data prepared for Map page! Go to the Map page to continue.")

                # Add a link to the map page
                st.markdown("[Go to Map Page](/map)")

            # Add download option
            if st.button("Download Results as CSV", use_container_width=True):
                try:
                    # Try to convert the dataframe to CSV and create a download button
                    csv_data = st.session_state["scanned_files"].to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="scan_results.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    if "MessageSizeError" in str(e) or "exceeds the message size limit" in str(e):
                        # If the CSV data is too large, suggest alternative approaches
                        st.warning("The scan results are too large to download directly. Consider these alternatives:")
                        st.info("""
                        1. Filter the data to reduce its size before downloading
                        2. Export in smaller batches
                        3. Use the database export functionality for very large datasets
                        """)
                    else:
                        # If it's a different error, show it
                        st.error(f"Error preparing download: {e}")

# Database push functionality in an expander with two columns
if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    with st.expander("Push Data to Database", expanded=True):
        # Create two columns layout
        db_col1, db_col2 = st.columns(2)

        # Right column for instructions
        with db_col2:
            st.markdown(
                """
                ## Push Data to Neo4j
                1. **Choose what to include** - Select whether to include files or just directories.
                2. **Push to database** - Click the button to start the process.
                3. **Monitor progress** - Watch the progress bar as data is pushed to Neo4j.

                This process will create nodes for each directory and optionally for each file,
                establishing relationships between them to represent the filesystem hierarchy.
                """
            )

        # Left column for push functionality
        with db_col1:
            st.subheader("Step 5: Pushing Data to Neo4j")

            include_files = st.checkbox("Include Files", value=False)
            st.write("Total items to push:", len(st.session_state["scanned_files"]))

            if st.button("Push to Database"):
                st.success(f"Include files: {include_files}")
                try:
                    # Progress bar outside columns to span full width
                    with st.container():
                        first_file = True
                        # TODO: Fix filter here for on/off switch
                        bar_total = len(st.session_state["scanned_files"])
                        my_bar = st.progress(0., text="Pushing Filetrees to Database...")
                        for _, row in st.session_state["scanned_files"].iterrows():
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

                                if include_files:
                                    if row["Type"] == "File":
                                        file_node = File.nodes.first_or_none(filepath=path)
                                        if file_node is None:
                                            file_node = File(filepath=path).save()
                                            if parent_folder:
                                                file_node.is_in.connect(parent_folder)

                        st.success("Data successfully pushed to Neo4j!")
                except Exception as e:
                    st.error(f"An error occurred while pushing data to Neo4j: {e}")

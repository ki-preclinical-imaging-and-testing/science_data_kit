# # # # # # # import streamlit as st
# # # # # # # import subprocess
# # # # # # # import json
# # # # # # # from pathlib import Path
# # # # # # # import pandas as pd
# # # # # # #
# # # # # # # st.set_page_config(
# # # # # # #     page_title="Science Data Toolkit",
# # # # # # #     page_icon="🖥️",
# # # # # # #     layout="wide",
# # # # # # #     initial_sidebar_state="expanded",
# # # # # # # )
# # # # # # #
# # # # # # # st.title("Index Your Dataset")
# # # # # # #
# # # # # # # # Initialize session state
# # # # # # # if "folder" not in st.session_state:
# # # # # # #     st.session_state["folder"] = None
# # # # # # # if "scan_completed" not in st.session_state:
# # # # # # #     st.session_state["scan_completed"] = False
# # # # # # # if "scanned_files" not in st.session_state:
# # # # # # #     st.session_state["scanned_files"] = pd.DataFrame()
# # # # # # # if "ncdu_output" not in st.session_state:
# # # # # # #     st.session_state["ncdu_output"] = ""
# # # # # # # if "ncdu_json_path" not in st.session_state:
# # # # # # #     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# # # # # # #
# # # # # # # # Description and instructions
# # # # # # # st.markdown(
# # # # # # #     """
# # # # # # #     ## Scan Your FileTree
# # # # # # #     1. **Locate your dataset** - Enter the directory path manually.
# # # # # # #     2. **Customize output location** - Choose where to save the JSON scan.
# # # # # # #     3. **View results directly in Streamlit** after scan completion.
# # # # # # #     """
# # # # # # # )
# # # # # # #
# # # # # # # # Folder selection (Streamlit text input instead of file dialog)
# # # # # # # st.subheader("Step 1: Select Dataset Location")
# # # # # # #
# # # # # # # folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# # # # # # # if folder_input and st.button("Select and Verify"):
# # # # # # #     st.session_state["folder"] = folder_input
# # # # # # #     # Verify folder
# # # # # # #     if st.session_state["folder"]:
# # # # # # #         dataset_path = Path(st.session_state["folder"])
# # # # # # #         if dataset_path.exists() and dataset_path.is_dir():
# # # # # # #             st.success(f"Folder Verified: `{dataset_path}`")
# # # # # # #         else:
# # # # # # #             st.error("Invalid folder. Please enter a valid directory path.")
# # # # # # #
# # # # # # # # JSON save location (Streamlit text input)
# # # # # # # st.subheader("Step 2: Configure NCDU Output")
# # # # # # # json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# # # # # # # if json_save_path:
# # # # # # #     st.session_state["ncdu_json_path"] = json_save_path
# # # # # # #
# # # # # # #
# # # # # # # # Function to run NCDU scan with progress bar
# # # # # # # def run_ncdu_scan():
# # # # # # #     if not st.session_state["folder"]:
# # # # # # #         st.error("Please select a folder first.")
# # # # # # #         return
# # # # # # #
# # # # # # #     dataset_path = st.session_state["folder"]
# # # # # # #     output_json_path = Path(st.session_state["ncdu_json_path"])
# # # # # # #
# # # # # # #     st.session_state["scan_completed"] = False
# # # # # # #     st.session_state["ncdu_output"] = ""
# # # # # # #
# # # # # # #     st.subheader("Step 3: Scanning Filesystem with NCDU")
# # # # # # #
# # # # # # #     # Progress bar initialization
# # # # # # #     progress_bar = st.progress(0)
# # # # # # #     status_box = st.empty()
# # # # # # #
# # # # # # #     try:
# # # # # # #         with subprocess.Popen(
# # # # # # #                 ["ncdu", "-o", str(output_json_path), dataset_path],
# # # # # # #                 stdout=subprocess.PIPE,
# # # # # # #                 stderr=subprocess.STDOUT,
# # # # # # #                 text=True,
# # # # # # #                 bufsize=1
# # # # # # #         ) as process:
# # # # # # #             total_lines = 100  # Approximate progress steps
# # # # # # #             for i, line in enumerate(process.stdout):
# # # # # # #                 st.session_state["ncdu_output"] += line
# # # # # # #                 progress = min(int((i / total_lines) * 100), 99)  # Keep it max at 99% until done
# # # # # # #                 progress_bar.progress(progress)
# # # # # # #                 status_box.text(f"Scanning... {progress}% complete")
# # # # # # #
# # # # # # #         # Ensure progress bar reaches 100%
# # # # # # #         progress_bar.progress(100)
# # # # # # #         status_box.text("Scan complete!")
# # # # # # #
# # # # # # #         # Check if JSON was created
# # # # # # #         if output_json_path.exists():
# # # # # # #             st.success(f"Scan complete! Results saved to `{output_json_path}`")
# # # # # # #             st.session_state["scan_completed"] = True
# # # # # # #
# # # # # # #             # Run jq transformation
# # # # # # #             jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
# # # # # # #             result = subprocess.run(
# # # # # # #                 ["jq", jq_filter, str(output_json_path)],
# # # # # # #                 text=True,
# # # # # # #                 capture_output=True,
# # # # # # #                 check=True
# # # # # # #             )
# # # # # # #
# # # # # # #             # Load transformed JSON
# # # # # # #             scan_data = json.loads(result.stdout)
# # # # # # #
# # # # # # #             # Convert to DataFrame
# # # # # # #             def parse_ncdu_json(node, parent_path=""):
# # # # # # #                 path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
# # # # # # #                 file_info = {
# # # # # # #                     "Path": path,
# # # # # # #                     "Size (Bytes)": node.get("asize", 0),
# # # # # # #                     "Disk Usage (Bytes)": node.get("dsize", 0),
# # # # # # #                     "Type": "Directory" if "children" in node else "File"
# # # # # # #                 }
# # # # # # #                 parsed_files = [file_info]
# # # # # # #                 if "children" in node:
# # # # # # #                     for child in node["children"]:
# # # # # # #                         parsed_files.extend(parse_ncdu_json(child, path))
# # # # # # #                 return parsed_files
# # # # # # #
# # # # # # #             parsed_files = parse_ncdu_json(scan_data)
# # # # # # #             st.session_state["scanned_files"] = pd.DataFrame(parsed_files)
# # # # # # #
# # # # # # #         else:
# # # # # # #             st.error("NCDU scan failed: No output JSON found.")
# # # # # # #
# # # # # # #     except Exception as e:
# # # # # # #         st.error(f"An error occurred while running NCDU: {e}")
# # # # # # #
# # # # # # #
# # # # # # # # Run scan button
# # # # # # # if not st.session_state["scan_completed"]:
# # # # # # #     if st.button("Run NCDU Scan"):
# # # # # # #         run_ncdu_scan()
# # # # # # #
# # # # # # # # Display scanned results
# # # # # # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # # # # # #     st.subheader("Step 4: View Results")
# # # # # # #     st.write("Scanned Files")
# # # # # # #     st.dataframe(st.session_state["scanned_files"])
# # # # # # #
# # # # # # # # Option to manually save CSV
# # # # # # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # # # # # #     st.subheader("Step 5: Save CSV (Optional)")
# # # # # # #     csv_save_path = st.text_input("Enter CSV save path:", value=str(Path.home() / "ncdu_scan.csv"))
# # # # # # #     if st.button("Save Scan Results to CSV"):
# # # # # # #         try:
# # # # # # #             st.session_state["scanned_files"].to_csv(csv_save_path, index=False)
# # # # # # #             st.success(f"CSV results saved to `{csv_save_path}`")
# # # # # # #         except Exception as e:
# # # # # # #             st.error(f"An error occurred while saving: {e}")
# # # # # #
# # # # # # import streamlit as st
# # # # # # import subprocess
# # # # # # import json
# # # # # # from pathlib import Path
# # # # # # import pandas as pd
# # # # # # from neomodel import (StructuredNode, StringProperty, IntegerProperty, RelationshipTo, config)
# # # # # #
# # # # # # st.set_page_config(
# # # # # #     page_title="Science Data Toolkit",
# # # # # #     page_icon="🖥️",
# # # # # #     layout="wide",
# # # # # #     initial_sidebar_state="expanded",
# # # # # # )
# # # # # #
# # # # # # st.title("Index Your Dataset")
# # # # # #
# # # # # # # Initialize session state
# # # # # # if "folder" not in st.session_state:
# # # # # #     st.session_state["folder"] = None
# # # # # # if "scan_completed" not in st.session_state:
# # # # # #     st.session_state["scan_completed"] = False
# # # # # # if "scanned_files" not in st.session_state:
# # # # # #     st.session_state["scanned_files"] = pd.DataFrame()
# # # # # # if "ncdu_output" not in st.session_state:
# # # # # #     st.session_state["ncdu_output"] = ""
# # # # # # if "ncdu_json_path" not in st.session_state:
# # # # # #     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# # # # # #
# # # # # # # Configure Neo4j connection
# # # # # # config.DATABASE_URL = "bolt://neo4j:password@localhost:7687"  # Change as needed
# # # # # #
# # # # # #
# # # # # # class Folder(StructuredNode):
# # # # # #     path = StringProperty(unique=True)
# # # # # #     size = IntegerProperty()
# # # # # #     disk_usage = IntegerProperty()
# # # # # #     parent = RelationshipTo('Folder', 'IN')
# # # # # #
# # # # # #
# # # # # # class File(StructuredNode):
# # # # # #     path = StringProperty(unique=True)
# # # # # #     size = IntegerProperty()
# # # # # #     disk_usage = IntegerProperty()
# # # # # #     parent = RelationshipTo('Folder', 'IN')
# # # # # #
# # # # # #
# # # # # # # Description and instructions
# # # # # # st.markdown(
# # # # # #     """
# # # # # #     ## Scan Your FileTree
# # # # # #     1. **Locate your dataset** - Enter the directory path manually.
# # # # # #     2. **Customize output location** - Choose where to save the JSON scan.
# # # # # #     3. **View results directly in Streamlit** after scan completion.
# # # # # #     """
# # # # # # )
# # # # # #
# # # # # # # Folder selection (Streamlit text input instead of file dialog)
# # # # # # st.subheader("Step 1: Select Dataset Location")
# # # # # #
# # # # # # folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# # # # # # if folder_input:
# # # # # #     st.session_state["folder"] = folder_input
# # # # # #     st.session_state["scan_completed"] = False
# # # # # #
# # # # # # # Verify folder
# # # # # # if st.session_state["folder"]:
# # # # # #     dataset_path = Path(st.session_state["folder"])
# # # # # #     if dataset_path.exists() and dataset_path.is_dir():
# # # # # #         st.success(f"Folder Verified: `{dataset_path}`")
# # # # # #     else:
# # # # # #         st.error("Invalid folder. Please enter a valid directory path.")
# # # # # #
# # # # # # # JSON save location (Streamlit text input)
# # # # # # st.subheader("Step 2: Configure NCDU Output")
# # # # # # json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# # # # # # if json_save_path:
# # # # # #     st.session_state["ncdu_json_path"] = json_save_path
# # # # # #
# # # # # #
# # # # # # # Function to run NCDU scan with live output
# # # # # # def run_ncdu_scan():
# # # # # #     if not st.session_state["folder"]:
# # # # # #         st.error("Please select a folder first.")
# # # # # #         return
# # # # # #
# # # # # #     dataset_path = st.session_state["folder"]
# # # # # #     output_json_path = Path(st.session_state["ncdu_json_path"])
# # # # # #
# # # # # #     st.session_state["scan_completed"] = False
# # # # # #     st.session_state["ncdu_output"] = ""
# # # # # #
# # # # # #     st.subheader("Step 3: Scanning Filesystem with NCDU")
# # # # # #
# # # # # #     status_box = st.empty()
# # # # # #
# # # # # #     try:
# # # # # #         with subprocess.Popen(
# # # # # #                 ["ncdu", "-o", str(output_json_path), dataset_path],
# # # # # #                 stdout=subprocess.PIPE,
# # # # # #                 stderr=subprocess.STDOUT,
# # # # # #                 text=True,
# # # # # #                 bufsize=1
# # # # # #         ) as process:
# # # # # #             for line in process.stdout:
# # # # # #                 st.session_state["ncdu_output"] += line
# # # # # #                 status_box.text(st.session_state["ncdu_output"])  # Live output
# # # # # #
# # # # # #         # Check if JSON was created
# # # # # #         if output_json_path.exists():
# # # # # #             st.success(f"Scan complete! Results saved to `{output_json_path}`")
# # # # # #             st.session_state["scan_completed"] = True
# # # # # #
# # # # # #             # Run jq transformation
# # # # # #             jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
# # # # # #             result = subprocess.run(
# # # # # #                 ["jq", jq_filter, str(output_json_path)],
# # # # # #                 text=True,
# # # # # #                 capture_output=True,
# # # # # #                 check=True
# # # # # #             )
# # # # # #
# # # # # #             # Load transformed JSON
# # # # # #             scan_data = json.loads(result.stdout)
# # # # # #
# # # # # #             # Convert to DataFrame and Neo4j nodes
# # # # # #             def process_node(node, parent=None):
# # # # # #                 path = node["name"]
# # # # # #                 full_path = f"{parent}/{path}" if parent else path
# # # # # #                 size = node.get("asize", 0)
# # # # # #                 disk_usage = node.get("dsize", 0)
# # # # # #
# # # # # #                 if "children" in node:
# # # # # #                     folder_node, _ = Folder.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # # # # #                     if parent:
# # # # # #                         parent_folder, _ = Folder.get_or_create({"path": parent})
# # # # # #                         folder_node.parent.connect(parent_folder)
# # # # # #
# # # # # #                     for child in node["children"]:
# # # # # #                         process_node(child, full_path)
# # # # # #                 else:
# # # # # #                     file_node, _ = File.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # # # # #                     parent_folder, _ = Folder.get_or_create({"path": parent})
# # # # # #                     file_node.parent.connect(parent_folder)
# # # # # #
# # # # # #             process_node(scan_data)
# # # # # #
# # # # # #         else:
# # # # # #             st.error("NCDU scan failed: No output JSON found.")
# # # # # #
# # # # # #     except Exception as e:
# # # # # #         st.error(f"An error occurred while running NCDU: {e}")
# # # # # #
# # # # # #
# # # # # # # Run scan button
# # # # # # if not st.session_state["scan_completed"]:
# # # # # #     if st.button("Run NCDU Scan"):
# # # # # #         run_ncdu_scan()
# # # # # #
# # # # # # # Display scanned results
# # # # # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # # # # #     st.subheader("Step 4: View Results")
# # # # # #     st.write("Scanned Files Preview:")
# # # # # #     st.dataframe(st.session_state["scanned_files"])
# # # # #
# # # # # import streamlit as st
# # # # # import subprocess
# # # # # import json
# # # # # from pathlib import Path
# # # # # import pandas as pd
# # # # # from neomodel import config
# # # # # import sys
# # # # #
# # # # # st.set_page_config(
# # # # #     page_title="Science Data Toolkit",
# # # # #     page_icon="🖥️",
# # # # #     layout="wide",
# # # # #     initial_sidebar_state="expanded",
# # # # # )
# # # # #
# # # # #
# # # # # st.title("Index Your Dataset")
# # # # #
# # # # # # Initialize session state
# # # # # if "folder" not in st.session_state:
# # # # #     st.session_state["folder"] = None
# # # # # if "scan_completed" not in st.session_state:
# # # # #     st.session_state["scan_completed"] = False
# # # # # if "scanned_files" not in st.session_state:
# # # # #     st.session_state["scanned_files"] = pd.DataFrame()
# # # # # if "ncdu_output" not in st.session_state:
# # # # #     st.session_state["ncdu_output"] = ""
# # # # # if "ncdu_json_path" not in st.session_state:
# # # # #     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# # # # #
# # # # #
# # # # # # Ensure Neo4j models are only loaded once
# # # # # if "Folder" not in sys.modules or "File" not in sys.modules:
# # # # #     from models import Folder, File  # Import only once
# # # # #
# # # # # # Description and instructions
# # # # # st.markdown(
# # # # #     """
# # # # #     ## Scan Your FileTree
# # # # #     1. **Locate your dataset** - Enter the directory path manually.
# # # # #     2. **Customize output location** - Choose where to save the JSON scan.
# # # # #     3. **View results directly in Streamlit** after scan completion.
# # # # #     """
# # # # # )
# # # # #
# # # # # # Folder selection (Streamlit text input instead of file dialog)
# # # # # st.subheader("Step 1: Select Dataset Location")
# # # # #
# # # # # folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# # # # # if folder_input:
# # # # #     st.session_state["folder"] = folder_input
# # # # #     st.session_state["scan_completed"] = False
# # # # #
# # # # # # Verify folder
# # # # # if st.session_state["folder"]:
# # # # #     dataset_path = Path(st.session_state["folder"])
# # # # #     if dataset_path.exists() and dataset_path.is_dir():
# # # # #         st.success(f"Folder Verified: `{dataset_path}`")
# # # # #     else:
# # # # #         st.error("Invalid folder. Please enter a valid directory path.")
# # # # #
# # # # # # JSON save location (Streamlit text input)
# # # # # st.subheader("Step 2: Configure NCDU Output")
# # # # # json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# # # # # if json_save_path:
# # # # #     st.session_state["ncdu_json_path"] = json_save_path
# # # # #
# # # # #
# # # # # # Function to run NCDU scan with live output
# # # # # def run_ncdu_scan():
# # # # #     if not st.session_state["folder"]:
# # # # #         st.error("Please select a folder first.")
# # # # #         return
# # # # #
# # # # #     dataset_path = st.session_state["folder"]
# # # # #     output_json_path = Path(st.session_state["ncdu_json_path"])
# # # # #
# # # # #     st.session_state["scan_completed"] = False
# # # # #     st.session_state["ncdu_output"] = ""
# # # # #
# # # # #     st.subheader("Step 3: Scanning Filesystem with NCDU")
# # # # #
# # # # #     status_box = st.empty()
# # # # #
# # # # #     try:
# # # # #         with subprocess.Popen(
# # # # #                 ["ncdu", "-o", str(output_json_path), dataset_path],
# # # # #                 stdout=subprocess.PIPE,
# # # # #                 stderr=subprocess.STDOUT,
# # # # #                 text=True,
# # # # #                 bufsize=1
# # # # #         ) as process:
# # # # #             for line in process.stdout:
# # # # #                 st.session_state["ncdu_output"] += line
# # # # #                 status_box.text(st.session_state["ncdu_output"])  # Live output
# # # # #
# # # # #         # Check if JSON was created
# # # # #         if output_json_path.exists():
# # # # #             st.success(f"Scan complete! Results saved to `{output_json_path}`")
# # # # #             st.session_state["scan_completed"] = True
# # # # #
# # # # #             # Run jq transformation
# # # # #             jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
# # # # #             result = subprocess.run(
# # # # #                 ["jq", jq_filter, str(output_json_path)],
# # # # #                 text=True,
# # # # #                 capture_output=True,
# # # # #                 check=True
# # # # #             )
# # # # #
# # # # #             # Load transformed JSON
# # # # #             scan_data = json.loads(result.stdout)
# # # # #
# # # # #             # Convert to DataFrame and Neo4j nodes
# # # # #             def process_node(node, parent=None):
# # # # #                 path = node["name"]
# # # # #                 full_path = f"{parent}/{path}" if parent else path
# # # # #                 size = node.get("asize", 0)
# # # # #                 disk_usage = node.get("dsize", 0)
# # # # #
# # # # #                 if "children" in node:
# # # # #                     folder_node, _ = Folder.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # # # #                     if parent:
# # # # #                         parent_folder, _ = Folder.get_or_create({"path": parent})
# # # # #                         folder_node.parent.connect(parent_folder)
# # # # #
# # # # #                     for child in node["children"]:
# # # # #                         process_node(child, full_path)
# # # # #                 else:
# # # # #                     file_node, _ = File.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # # # #                     parent_folder, _ = Folder.get_or_create({"path": parent})
# # # # #                     file_node.parent.connect(parent_folder)
# # # # #
# # # # #             process_node(scan_data)
# # # # #
# # # # #         else:
# # # # #             st.error("NCDU scan failed: No output JSON found.")
# # # # #
# # # # #     except Exception as e:
# # # # #         st.error(f"An error occurred while running NCDU: {e}")
# # # # #
# # # # #
# # # # # # Run scan button
# # # # # if not st.session_state["scan_completed"]:
# # # # #     if st.button("Run NCDU Scan"):
# # # # #         run_ncdu_scan()
# # # # #
# # # # # # Display scanned results
# # # # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # # # #     st.subheader("Step 4: View Results")
# # # # #     st.write("Scanned Files Preview:")
# # # # #     st.dataframe(st.session_state["scanned_files"])
# # # # #
# # # # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # # # #     if st.button("Load into Database")    # Configure Neo4j connection
# # # # #     config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed
# # # #
# # # # import streamlit as st
# # # # import subprocess
# # # # import json
# # # # from pathlib import Path
# # # # import pandas as pd
# # # # from neomodel import config
# # # # import sys
# # # #
# # # # st.set_page_config(
# # # #     page_title="Science Data Toolkit",
# # # #     page_icon="🖥️",
# # # #     layout="wide",
# # # #     initial_sidebar_state="expanded",
# # # # )
# # # #
# # # # st.title("Index Your Dataset")
# # # #
# # # # # Initialize session state
# # # # if "folder" not in st.session_state:
# # # #     st.session_state["folder"] = None
# # # # if "scan_completed" not in st.session_state:
# # # #     st.session_state["scan_completed"] = False
# # # # if "scanned_files" not in st.session_state:
# # # #     st.session_state["scanned_files"] = pd.DataFrame()
# # # # if "ncdu_output" not in st.session_state:
# # # #     st.session_state["ncdu_output"] = ""
# # # # if "ncdu_json_path" not in st.session_state:
# # # #     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# # # # if "neomodels" not in st.session_state:
# # # #     from models import Folder, File  # Import only once
# # # #     st.session_state["neomodels"] = {
# # # #         "Folder": Folder,
# # # #         "File" : File
# # # #     }
# # # #
# # # #
# # # #
# # # # # Description and instructions
# # # # st.markdown(
# # # #     """
# # # #     ## Scan Your FileTree
# # # #     1. **Locate your dataset** - Enter the directory path manually.
# # # #     2. **Customize output location** - Choose where to save the JSON scan.
# # # #     3. **View results directly in Streamlit** after scan completion.
# # # #     """
# # # # )
# # # #
# # # # # Folder selection (Streamlit text input instead of file dialog)
# # # # st.subheader("Step 1: Select Dataset Location")
# # # #
# # # # folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# # # # if folder_input:
# # # #     st.session_state["folder"] = folder_input
# # # #     st.session_state["scan_completed"] = False
# # # #
# # # # # Verify folder
# # # # if st.session_state["folder"]:
# # # #     dataset_path = Path(st.session_state["folder"])
# # # #     if dataset_path.exists() and dataset_path.is_dir():
# # # #         st.success(f"Folder Verified: `{dataset_path}`")
# # # #     else:
# # # #         st.error("Invalid folder. Please enter a valid directory path.")
# # # #
# # # # # JSON save location (Streamlit text input)
# # # # st.subheader("Step 2: Configure NCDU Output")
# # # # json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# # # # if json_save_path:
# # # #     st.session_state["ncdu_json_path"] = json_save_path
# # # #
# # # #
# # # # # Function to run NCDU scan with live output
# # # # def run_ncdu_scan():
# # # #     if not st.session_state["folder"]:
# # # #         st.error("Please select a folder first.")
# # # #         return
# # # #
# # # #     dataset_path = st.session_state["folder"]
# # # #     output_json_path = Path(st.session_state["ncdu_json_path"])
# # # #
# # # #     st.session_state["scan_completed"] = False
# # # #     st.session_state["ncdu_output"] = ""
# # # #
# # # #     st.subheader("Step 3: Scanning Filesystem with NCDU")
# # # #
# # # #     status_box = st.empty()
# # # #
# # # #     try:
# # # #         with subprocess.Popen(
# # # #                 ["ncdu", "-o", str(output_json_path), dataset_path],
# # # #                 stdout=subprocess.PIPE,
# # # #                 stderr=subprocess.STDOUT,
# # # #                 text=True,
# # # #                 bufsize=1
# # # #         ) as process:
# # # #             for line in process.stdout:
# # # #                 st.session_state["ncdu_output"] += line
# # # #                 status_box.text(st.session_state["ncdu_output"])  # Live output
# # # #
# # # #         # Check if JSON was created
# # # #         if output_json_path.exists():
# # # #             st.success(f"Scan complete! Results saved to `{output_json_path}`")
# # # #             st.session_state["scan_completed"] = True
# # # #     except Exception as e:
# # # #         st.error(f"An error occurred while running NCDU: {e}")
# # # #
# # # #
# # # # # Run scan button
# # # # if not st.session_state["scan_completed"]:
# # # #     if st.button("Run NCDU Scan"):
# # # #         run_ncdu_scan()
# # # #
# # # #
# # # # # Push to Neo4j Button
# # # # def push_to_neo4j():
# # # #     print("Hello")
# # # #     config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed
# # # #     output_json_path = Path(st.session_state["ncdu_json_path"])
# # # #     if not output_json_path.exists():
# # # #         st.error("JSON file not found. Please run the scan first.")
# # # #         return
# # # #
# # # #     try:
# # # #         with open(output_json_path, "r") as f:
# # # #             scan_data = json.load(f)
# # # #
# # # #         # Convert to Neo4j nodes
# # # #         def process_node(node, parent=None):
# # # #             path = node["name"]
# # # #             full_path = f"{parent}/{path}" if parent else path
# # # #             size = node.get("asize", 0)
# # # #             disk_usage = node.get("dsize", 0)
# # # #
# # # #             if "children" in node:
# # # #                 folder_node, _ = Folder.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # # #                 if parent:
# # # #                     parent_folder, _ = Folder.get_or_create({"path": parent})
# # # #                     folder_node.parent.connect(parent_folder)
# # # #
# # # #                 for child in node["children"]:
# # # #                     process_node(child, full_path)
# # # #             else:
# # # #                 file_node, _ = File.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # # #                 parent_folder, _ = Folder.get_or_create({"path": parent})
# # # #                 file_node.parent.connect(parent_folder)
# # # #
# # # #         process_node(scan_data)
# # # #         st.success("Data successfully pushed to Neo4j!")
# # # #     except Exception as e:
# # # #         st.error(f"An error occurred while pushing data to Neo4j: {e}")
# # # #
# # # #
# # # # # Display scanned results
# # # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # # #     st.subheader("Step 4: View Results")
# # # #     st.write("Scanned Files Preview:")
# # # #     st.dataframe(st.session_state["scanned_files"])
# # #
# # #
# # # import streamlit as st
# # # import subprocess
# # # import json
# # # from pathlib import Path
# # # import pandas as pd
# # # from neomodel import config, NodeClassAlreadyDefined
# # # import sys
# # #
# # # st.set_page_config(
# # #     page_title="Science Data Toolkit",
# # #     page_icon="🖥️",
# # #     layout="wide",
# # #     initial_sidebar_state="expanded",
# # # )
# # #
# # # st.title("Index Your Dataset")
# # #
# # # # Initialize session state
# # # if "folder" not in st.session_state:
# # #     st.session_state["folder"] = None
# # # if "scan_completed" not in st.session_state:
# # #     st.session_state["scan_completed"] = False
# # # if "scanned_files" not in st.session_state:
# # #     st.session_state["scanned_files"] = pd.DataFrame()
# # # if "ncdu_output" not in st.session_state:
# # #     st.session_state["ncdu_output"] = ""
# # # if "ncdu_json_path" not in st.session_state:
# # #     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# # # if "neomodels" not in st.session_state:
# # #     try:
# # #         from models import Folder, File  # Import only once
# # #     except NodeClassAlreadyDefined:
# # #         print("Neomodels found.")
# # #
# # #     st.session_state["neomodels"] = {
# # #         "Folder": Folder,
# # #         "File": File
# # #     }
# # #
# # # # Description and instructions
# # # st.markdown(
# # #     """
# # #     ## Scan Your FileTree
# # #     1. **Locate your dataset** - Enter the directory path manually.
# # #     2. **Customize output location** - Choose where to save the JSON scan.
# # #     3. **View results directly in Streamlit** after scan completion.
# # #     """
# # # )
# # #
# # # # Folder selection (Streamlit text input instead of file dialog)
# # # st.subheader("Step 1: Select Dataset Location")
# # #
# # # folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# # # if folder_input:
# # #     st.session_state["folder"] = folder_input
# # #     st.session_state["scan_completed"] = False
# # #
# # # # Verify folder
# # # if st.session_state["folder"]:
# # #     dataset_path = Path(st.session_state["folder"])
# # #     if dataset_path.exists() and dataset_path.is_dir():
# # #         st.success(f"Folder Verified: `{dataset_path}`")
# # #     else:
# # #         st.error("Invalid folder. Please enter a valid directory path.")
# # #
# # # # JSON save location (Streamlit text input)
# # # st.subheader("Step 2: Configure NCDU Output")
# # # json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# # # if json_save_path:
# # #     st.session_state["ncdu_json_path"] = json_save_path
# # #
# # #
# # # # Function to run NCDU scan with live output
# # # def run_ncdu_scan():
# # #     if not st.session_state["folder"]:
# # #         st.error("Please select a folder first.")
# # #         return
# # #
# # #     dataset_path = st.session_state["folder"]
# # #     output_json_path = Path(st.session_state["ncdu_json_path"])
# # #
# # #     st.session_state["scan_completed"] = False
# # #     st.session_state["ncdu_output"] = ""
# # #
# # #     st.subheader("Step 3: Scanning Filesystem with NCDU")
# # #
# # #     status_box = st.empty()
# # #
# # #     try:
# # #         with subprocess.Popen(
# # #                 ["ncdu", "-o", str(output_json_path), dataset_path],
# # #                 stdout=subprocess.PIPE,
# # #                 stderr=subprocess.STDOUT,
# # #                 text=True,
# # #                 bufsize=1
# # #         ) as process:
# # #             for line in process.stdout:
# # #                 st.session_state["ncdu_output"] += line
# # #                 status_box.text(st.session_state["ncdu_output"])  # Live output
# # #
# # #         # Check if JSON was created
# # #         if output_json_path.exists():
# # #             st.success(f"Scan complete! Results saved to `{output_json_path}`")
# # #             st.session_state["scan_completed"] = True
# # #
# # #             # Load JSON and update scanned_files
# # #             with open(output_json_path, "r") as f:
# # #                 scan_data = json.load(f)
# # #
# # #             def parse_to_dataframe(node, parent=""):
# # #                 """ Recursively parses the JSON into a DataFrame format """
# # #                 path = f"{parent}/{node['name']}" if parent else node["name"]
# # #                 file_info = {
# # #                     "Path": path,
# # #                     "Size (Bytes)": node.get("asize", 0),
# # #                     "Disk Usage (Bytes)": node.get("dsize", 0),
# # #                     "Type": "Directory" if "children" in node else "File"
# # #                 }
# # #                 parsed_files = [file_info]
# # #                 if "children" in node:
# # #                     for child in node["children"]:
# # #                         parsed_files.extend(parse_to_dataframe(child, path))
# # #                 return parsed_files
# # #
# # #             parsed_data = parse_to_dataframe(scan_data)
# # #             st.session_state["scanned_files"] = pd.DataFrame(parsed_data)
# # #
# # #     except Exception as e:
# # #         st.error(f"An error occurred while running NCDU: {e}")
# # #
# # #
# # # # Run scan button
# # # if not st.session_state["scan_completed"]:
# # #     if st.button("Run NCDU Scan"):
# # #         run_ncdu_scan()
# # #
# # # # Push to Neo4j Button
# # # if st.session_state["scan_completed"]:
# # #     if st.button("Push to Database"):
# # #         print("Hello")
# # #         config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"
# # #         output_json_path = Path(st.session_state["ncdu_json_path"])
# # #         if not output_json_path.exists():
# # #             st.error("JSON file not found. Please run the scan first.")
# # #         else:
# # #             try:
# # #                 with open(output_json_path, "r") as f:
# # #                     scan_data = json.load(f)
# # #
# # #
# # #                 # Convert to Neo4j nodes
# # #                 def process_node(node, parent=None):
# # #                     path = node["name"]
# # #                     full_path = f"{parent}/{path}" if parent else path
# # #                     size = node.get("asize", 0)
# # #                     disk_usage = node.get("dsize", 0)
# # #
# # #                     if "children" in node:
# # #                         folder_node, _ = Folder.get_or_create(
# # #                             {"path": full_path, "size": size, "disk_usage": disk_usage})
# # #                         if parent:
# # #                             parent_folder, _ = Folder.get_or_create({"path": parent})
# # #                             folder_node.parent.connect(parent_folder)
# # #                         for child in node["children"]:
# # #                             process_node(child, full_path)
# # #                     else:
# # #                         file_node, _ = File.get_or_create({"path": full_path, "size": size, "disk_usage": disk_usage})
# # #                         parent_folder, _ = Folder.get_or_create({"path": parent})
# # #                         file_node.parent.connect(parent_folder)
# # #
# # #
# # #                 process_node(scan_data)
# # #                 st.success("Data successfully pushed to Neo4j!")
# # #             except Exception as e:
# # #                 st.error(f"An error occurred while pushing data to Neo4j: {e}")
# # #
# # # # Display scanned results
# # # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# # #     st.subheader("Step 4: View Results")
# # #     st.write("Scanned Files Preview:")
# # #     st.dataframe(st.session_state["scanned_files"])
# #
# # import streamlit as st
# # import subprocess
# # import json
# # from pathlib import Path
# # import pandas as pd
# # from neomodel import config
# # import sys
# #
# # st.set_page_config(
# #     page_title="Science Data Toolkit",
# #     page_icon="🖥️",
# #     layout="wide",
# #     initial_sidebar_state="expanded",
# # )
# #
# # st.title("Index Your Dataset")
# #
# # # Initialize session state
# # if "folder" not in st.session_state:
# #     st.session_state["folder"] = None
# # if "scan_completed" not in st.session_state:
# #     st.session_state["scan_completed"] = False
# # if "scanned_files" not in st.session_state:
# #     st.session_state["scanned_files"] = pd.DataFrame()
# # if "ncdu_output" not in st.session_state:
# #     st.session_state["ncdu_output"] = ""
# # if "ncdu_json_path" not in st.session_state:
# #     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# # if "neomodels" not in st.session_state:
# #     from models import Folder, File  # Import only once
# #
# #     st.session_state["neomodels"] = {
# #         "Folder": Folder,
# #         "File": File
# #     }
# #
# # # Description and instructions
# # st.markdown(
# #     """
# #     ## Scan Your FileTree
# #     1. **Locate your dataset** - Enter the directory path manually.
# #     2. **Customize output location** - Choose where to save the JSON scan.
# #     3. **View results directly in Streamlit** after scan completion.
# #     """
# # )
# #
# # # Folder selection (Streamlit text input instead of file dialog)
# # st.subheader("Step 1: Select Dataset Location")
# #
# # folder_input = st.text_input("Enter folder path to scan:", value=st.session_state["folder"] or "")
# # if folder_input:
# #     st.session_state["folder"] = folder_input
# #     st.session_state["scan_completed"] = False
# #
# # # Verify folder
# # if st.session_state["folder"]:
# #     dataset_path = Path(st.session_state["folder"])
# #     if dataset_path.exists() and dataset_path.is_dir():
# #         st.success(f"Folder Verified: `{dataset_path}`")
# #     else:
# #         st.error("Invalid folder. Please enter a valid directory path.")
# #
# # # JSON save location (Streamlit text input)
# # st.subheader("Step 2: Configure NCDU Output")
# # json_save_path = st.text_input("Enter JSON output path:", value=st.session_state["ncdu_json_path"])
# # if json_save_path:
# #     st.session_state["ncdu_json_path"] = json_save_path
# #
# #
# # # Function to run NCDU scan with live output
# # def run_ncdu_scan():
# #     if not st.session_state["folder"]:
# #         st.error("Please select a folder first.")
# #         return
# #
# #     dataset_path = st.session_state["folder"]
# #     output_json_path = Path(st.session_state["ncdu_json_path"])
# #
# #     st.session_state["scan_completed"] = False
# #     st.session_state["ncdu_output"] = ""
# #
# #     st.subheader("Step 3: Scanning Filesystem with NCDU")
# #
# #     status_box = st.empty()
# #
# #     try:
# #         with subprocess.Popen(
# #                 ["ncdu", "-o", str(output_json_path), dataset_path],
# #                 stdout=subprocess.PIPE,
# #                 stderr=subprocess.STDOUT,
# #                 text=True,
# #                 bufsize=1
# #         ) as process:
# #             for line in process.stdout:
# #                 st.session_state["ncdu_output"] += line
# #                 status_box.text(st.session_state["ncdu_output"])  # Live output
# #
# #         # Check if JSON was created
# #         if output_json_path.exists():
# #             st.success(f"Scan complete! Results saved to `{output_json_path}`")
# #             st.session_state["scan_completed"] = True
# #
# #             # Run jq transformation
# #             jq_filter = 'def c: (arrays | .[0] + {children: [.[1:][] | c]}) // .; last | c'
# #             result = subprocess.run(
# #                 ["jq", jq_filter, str(output_json_path)],
# #                 text=True,
# #                 capture_output=True,
# #                 check=True
# #             )
# #
# #             # Load transformed JSON
# #             scan_data = json.loads(result.stdout)
# #
# #             # Convert to DataFrame
# #             def parse_ncdu_json(node, parent_path=""):
# #                 path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
# #                 file_info = {
# #                     "Path": path,
# #                     "Size (Bytes)": node.get("asize", 0),
# #                     "Disk Usage (Bytes)": node.get("dsize", 0),
# #                     "Type": "Directory" if "children" in node else "File"
# #                 }
# #                 parsed_files = [file_info]
# #                 if "children" in node:
# #                     for child in node["children"]:
# #                         parsed_files.extend(parse_ncdu_json(child, path))
# #                 return parsed_files
# #
# #             parsed_files = parse_ncdu_json(scan_data)
# #             st.session_state["scanned_files"] = pd.DataFrame(parsed_files)
# #
# #     except Exception as e:
# #         st.error(f"An error occurred while running NCDU: {e}")
# #
# #
# # # Run scan button
# # if not st.session_state["scan_completed"]:
# #     if st.button("Run NCDU Scan"):
# #         run_ncdu_scan()
# #
# # # Display scanned results
# # if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
# #     st.subheader("Step 4: View Results")
# #     st.write("Scanned Files Preview:")
# #     st.dataframe(st.session_state["scanned_files"])
#
#
# import streamlit as st
# import subprocess
# import json
# from pathlib import Path
# import pandas as pd
# from neomodel import config
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
#     st.session_state["ncdu_json_path"] = str(Path.home() / "ncdu_scan.json")  # Default JSON path
# if "neomodels" not in st.session_state:
#     try:
#         from models import Folder, File  # Import only once
#     except NodeClassAlreadyDefined:
#         print("Neomodels found.")
#
#     st.session_state["neomodels"] = {
#         "Folder": Folder,
#         "File": File
#     }
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
#     # st.session_state["scan_completed"] = False
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
# # Function to run NCDU scan with live output
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
#             for line in process.stdout:
#                 st.session_state["ncdu_output"] += line
#                 status_box.text(st.session_state["ncdu_output"])  # Live output
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
#
# # Push to Neo4j Button
# if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
#     def push_to_neo4j():
#         try:
#             config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed
#             _Folder = st.session_state["neomodels"]["Folder"]
#             _File = st.session_state["neomodels"]["File"]
#
#             def process_node(node, parent=None):
#                 path = node["Path"]
#                 size = node["Size (Bytes)"]
#                 disk_usage = node["Disk Usage (Bytes)"]
#
#                 if node["Type"] == "Directory":
#                     folder_node = _Folder.get_or_create({"path": path, "size": size, "disk_usage": disk_usage})
#                     if parent:
#                         parent_folder = _Folder.get_or_create({"path": parent})
#                         folder_node[0].parent.connect(parent_folder[0])
#                 else:
#                     file_node = _File.get_or_create({"path": path, "size": size, "disk_usage": disk_usage})
#                     parent_folder = _Folder.get_or_create({"path": Path(path).parent.as_posix()})
#                     file_node[0].parent.connect(parent_folder[0])
#
#             st.session_state["scanned_files"].apply(process_node, axis=1)
#             st.success("Data successfully pushed to Neo4j!")
#         except Exception as e:
#             st.error(f"An error occurred while pushing data to Neo4j: {e}")
#
#     st.subheader("Step 5: Pushing Data to Neo4j")
#     if st.button("Push to Database"):
#         push_to_neo4j()

import streamlit as st
import subprocess
import json
from pathlib import Path
import pandas as pd
from neomodel import config, db, NodeClassAlreadyDefined
import sys

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
if "neomodels" not in st.session_state:
    try:
        from models import Folder, File  # Import only once
        st.session_state["neomodels"] = {
            "Folder": Folder,
            "File": File
        }
    except NodeClassAlreadyDefined:
        print("Neomodels found.")


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

# # Push to Neo4j Button
# if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
#         st.subheader("Step 5: Pushing Data to Neo4j")
#         if st.button("Push to Database"):
#             config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed
#             try:
#                 with db.transaction:
#                     for _, row in st.session_state["scanned_files"].iterrows():
#                         path = row["Path"]
#                         size = row["Size (Bytes)"]
#                         disk_usage = row["Disk Usage (Bytes)"]
#
#                         if row["Type"] == "Directory":
#                             folder_node = st.session_state["neomodels"]["Folder"].get_or_create({"path": path, "size": size, "disk_usage": disk_usage})
#                             parent_folder = st.session_state["neomodels"]["Folder"].get_or_create({"path": Path(path).parent.as_posix()})
#                             folder_node[0].rel_in.connect(parent_folder[0])
#                         if row["Type"] == "File":
#                             file_node = st.session_state["neomodels"]["File"].get_or_create({"path": path, "size": size, "disk_usage": disk_usage})
#                             parent_folder = st.session_state["neomodels"]["Folder"].get_or_create({"path": Path(path).parent.as_posix()})
#                             file_node[0].rel_in.connect(parent_folder[0])
#
#                 st.success("Data successfully pushed to Neo4j!")
#             except Exception as e:
#                 st.error(f"An error occurred while pushing data to Neo4j: {e}")


if st.session_state["scan_completed"] and not st.session_state["scanned_files"].empty:
    st.subheader("Step 5: Pushing Data to Neo4j")

    if st.button("Push to Database"):
        config.DATABASE_URL = f"bolt://{st.session_state['username']}:{st.session_state['password']}@localhost:{st.session_state['bolt_port']}"  # Change as needed
        Folder = st.session_state["neomodels"]["Folder"]
        File = st.session_state["neomodels"]["File"]

        try:
            first_file = True
            my_bar = st.progress(0., text="Pushing Filetrees to Database...")
            bar_total = len(st.session_state["scanned_files"])
            for _, row in st.session_state["scanned_files"].iterrows():
                my_bar.progress(float(_)/bar_total, f"{int(100*float(_)/bar_total)}%")
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

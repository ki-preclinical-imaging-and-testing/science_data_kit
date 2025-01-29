import streamlit as st
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

# Initialize session state variables
if "entities_df" not in st.session_state:
    st.session_state["entities_df"] = None
if "taxonomy_keys" not in st.session_state:
    st.session_state["taxonomy_keys"] = []
if "taxonomy" not in st.session_state:
    st.session_state["taxonomy"] = None

# Title and description
st.title("Relate: Build Taxonomy")

st.markdown(
    """
    ## Define Relationships and Build Taxonomy
    1. Select keys to define a hierarchical taxonomy.
    2. Rearrange or nest keys to organize the structure.
    3. Save the taxonomy schema.
    """
)

# Load the edited entities dataframe
if st.session_state["entities_df"] is None:
    uploaded_file = st.file_uploader("Upload entity file (CSV or JSON):", type=["csv", "json"])
    if uploaded_file:
        try:
            file_extension = uploaded_file.name.split(".")[-1]
            if file_extension == "csv":
                st.session_state["entities_df"] = pd.read_csv(uploaded_file)
            elif file_extension == "json":
                st.session_state["entities_df"] = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file format.")
            st.success("Entity dataset loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")

# If the dataframe is loaded, proceed with taxonomy creation
if st.session_state["entities_df"] is not None:
    st.subheader("Select Keys for Taxonomy")

    # Display available keys
    available_keys = st.session_state["entities_df"].columns.tolist()
    selected_keys = st.multiselect(
        "Select keys to define taxonomy levels:",
        options=available_keys,
        default=st.session_state["taxonomy_keys"]
    )

    # Update session state with selected keys
    if selected_keys:
        st.session_state["taxonomy_keys"] = selected_keys

    # Display the selected keys as the hierarchical structure
    if st.session_state["taxonomy_keys"]:
        st.subheader("Preview Taxonomy Structure")
        st.markdown("**Selected Hierarchy:**")
        for i, key in enumerate(st.session_state["taxonomy_keys"], 1):
            st.write(f"Level {i}: {key}")

        # Create the taxonomy by grouping the dataframe
        try:
            taxonomy_df = (
                st.session_state["entities_df"]
                .groupby(st.session_state["taxonomy_keys"])
                .size()
                .reset_index(name="Count")
            )
            st.session_state["taxonomy"] = taxonomy_df

            # Display the resulting taxonomy
            st.write("**Generated Taxonomy:**")
            st.dataframe(taxonomy_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating taxonomy: {e}")

    # Option to save the taxonomy
    st.subheader("Save Taxonomy")
    save_format = st.selectbox("Select file format:", ["CSV", "JSON"])

    if st.session_state["taxonomy"] is not None:
        if save_format == "CSV":
            csv_data = st.session_state["taxonomy"].to_csv(index=False)
            st.download_button(
                label="Download Taxonomy as CSV",
                data=csv_data,
                file_name="taxonomy.csv",
                mime="text/csv",
            )
        elif save_format == "JSON":
            json_data = st.session_state["taxonomy"].to_json(orient="records")
            st.download_button(
                label="Download Taxonomy as JSON",
                data=json_data,
                file_name="taxonomy.json",
                mime="application/json",
            )
    else:
        st.warning("No taxonomy generated yet. Select keys to build the taxonomy.")


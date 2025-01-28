import streamlit as st
import pandas as pd
from pathlib import Path

# Initialize session state variables
if "entities_df" not in st.session_state:
    st.session_state["entities_df"] = None
if "selected_entity_index" not in st.session_state:
    st.session_state["selected_entity_index"] = None

# Title and description
st.title("Resolve Entities")

st.markdown(
    """
    ## Review and Edit Entities
    1. Load entities from a file.
    2. Review the dataset and edit directly.
    3. Save your updates.
    """
)

# File uploader for checkpointed file
uploaded_file = st.file_uploader("Upload entity file (CSV or JSON):", type=["csv", "json"])

if uploaded_file:
    try:
        file_extension = Path(uploaded_file.name).suffix
        if file_extension == ".csv":
            st.session_state["entities_df"] = pd.read_csv(uploaded_file)
        elif file_extension == ".json":
            st.session_state["entities_df"] = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format.")
        st.session_state["file_uploaded"] = uploaded_file.name
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Display and edit the dataframe if loaded
if st.session_state["entities_df"] is not None:
    st.markdown(f"`{st.session_state['file_uploaded']}`")
    st.subheader("All Entities")
    _entities_df = st.session_state["entities_df"]
    st.session_state["entities_df"] = st.data_editor(
        _entities_df,
        key="entity_editor",
        use_container_width=True,
    )
    if st.button("Update Dataframe"):
        st.session_state["entities_df"] = _entities_df

    st.subheader("Individual Entity")
    entity_indices = st.session_state["entities_df"].index.tolist()
    selected_entity_index = st.selectbox("Select entity to edit:", options=entity_indices, format_func=lambda x: f"Entity {x}")

    if selected_entity_index is not None:
        st.session_state["selected_entity_index"] = selected_entity_index
        selected_entity = st.session_state["entities_df"].iloc[selected_entity_index].to_dict()

        # Convert entity dictionary to DataFrame for editing
        selected_entity_df = pd.DataFrame(list(selected_entity.items()), columns=["Key", "Value"])

        edited_entity_df = st.data_editor(
            selected_entity_df,
            key="individual_entity_editor",
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Save Changes"):
            for _, row in edited_entity_df.iterrows():
                key, value = row["Key"], row["Value"]
                if key not in st.session_state["entities_df"].columns:
                    st.session_state["entities_df"][key] = None
                st.session_state["entities_df"].at[selected_entity_index, key] = value
            st.success("Entity updated successfully.")

    # Save updated dataset
    st.subheader("Save Updated Dataset")
    save_format = st.selectbox("Select file format:", ["CSV", "JSON"])

    if st.button("Download Updated Dataset"):
        if save_format == "CSV":
            csv_data = st.session_state["entities_df"].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="updated_entities.csv",
                mime="text/csv",
            )
        elif save_format == "JSON":
            json_data = st.session_state["entities_df"].to_json(orient="records")
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="updated_entities.json",
                mime="application/json",
            )


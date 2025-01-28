import streamlit as st

st.set_page_config(
    page_title="Science Data Toolkit",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://adam-patch.mit.edu',
        'Report a bug': "https://adam-patch.mit.edu",
        'About': "# This is a header. This is an *extremely* cool app!"
    }

)


st.title("Get started...")
st.markdown(
    """
    *... simplifying FAIR+ data in your lab.*

    ### What is this?
    **Science Data Toolkit** helps you index, curate, and integrate multimodal research data. 

    ### Science Data Toolkit helps you...
    |  |  |
    | ---: | --- |
    |  **start** | *using this toolkit* |
    |  **index** | *filetree metadata* |
    |  **resolve** | *data entities* |
    |  **relate** | *entities via schema* |
    |  **explore** | *data in context* |
    |  **integrate** | *other workflows* |
    |  **ground** | *large language models* |
    |  **learn** | *more about this toolkit* |

    ## FAIR+ Data
    The FAIR(+) Data Principles have been established (and appended). 

    Let's follow them. We can have *nice things*.

    Science data that is...

    - **F**indable
    - **A**ccessible
    - **I**nteroperable
    - **R**eusable
    - **+** (Computable)

    ... is *nice things* science data. Let's have it!
    """

    # TODO: Make an infographic for this description
    #### Getting Started
    #Using the navigation menu on the left:
    #1. Go to **Scan** to analyze your filesystem.
    #2. Visit **Edit** to review metadata.
    #3. Proceed to **Curate** for organizing datasets.
    #4. Explore schema and data relationships under **Explore**.
    #5. Finally, use **Integrate** to export or connect your work.
    #For **Learn** for detailed documentation about each step!
)
#st.image("static/logo.png", width=300)  # Replace with your logo path if needed


st.sidebar.success("Welcome!")

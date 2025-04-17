# Science Data Kit ("SDK")

Scan your messy science data, remap, visualize, and enrich using built-in knowledge graph capabilities.

## Simplifying FAIR+ data in your lab

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

## Getting started

### Spinning up a local instance

From your local clone of science_data_kit,

    cd $REPO_HOME/science_data_kit
    conda create -n python=3.13 science_data_kit pip
    conda activate science_data_kit
    pip install requirements.txt

Ensure all requirements are installed. Then you can run 

    streamlit run start.py

from the repository base. This works well in `tmux`---otherwise, `nohup`, `bg`
or something similar should work fine. 

### The GUI

Access the GUI from your browser window by navigating to either the default

    localhost:8501

or your local instance's unique host and port address. When you launch,
`streamlit` automatically maps your application to an open port. You can find
the output of streamlit in your CLI command's output. 



# Science Data Kit (SDK)

A comprehensive toolkit for indexing, curating, and integrating multimodal research data using knowledge graph capabilities.

## Overview

The Science Data Kit (SDK) helps researchers manage and make sense of complex, multimodal scientific data. It follows the FAIR+ data principles to ensure your data is Findable, Accessible, Interoperable, Reusable, and Computable.

## Features

- **Connect** to data sources and spin up necessary infrastructure
- **Survey** your file systems to extract metadata
- **Map** entities and relationships to create knowledge graphs
- **Explore** your data through interactive visualizations
- **Chat** with your data using natural language
- **Learn** about knowledge graphs and FAIR data practices

## Application Flow

The Science Data Kit follows a logical workflow:

1. **Connect** 🌐 - Set up your data infrastructure
   - Host a local Neo4j database
   - Run Jupyter Lab for data analysis
   - Launch NeoDash for Neo4j visualization
   - Connect to existing Neo4j databases

2. **Survey** 🔭 - Scan and analyze your file systems
   - Locate and scan datasets
   - View scan results
   - Label entities for further processing
   - Push data to Neo4j database

3. **Map** 🗺 - Define entities and relationships
   - Load entities from files or database
   - Define entity structure and properties
   - Create relationships between entities
   - Build taxonomies and ontologies

4. **Explore** 🏞 - Visualize and analyze your data
   - View schema visualizations
   - Extract and explore node data
   - Export data for further analysis

5. **Chat** 💬 - Interact with your data using natural language
   - Connect to LLM providers (OpenAI, Anthropic, Ollama)
   - Ask questions about your data
   - Get context-aware responses

6. **Learn** 📖 - Access resources and documentation
   - Documentation and tutorials
   - Knowledge graph basics
   - Community and support

## Directory Structure

- **[app/](app/README.md)** - Streamlit application code
- **[ipynb/](ipynb/README.md)** - Jupyter notebooks for tutorials and examples
- **[docs/](docs/README.md)** - Documentation files

## FAIR+ Data Principles

The Science Data Kit is designed around the FAIR+ data principles:

- **F**indable - Data is easy to find
- **A**ccessible - Data can be accessed with appropriate permissions
- **I**nteroperable - Data can work with other systems
- **R**eusable - Data can be reused for different purposes
- **+** (Computable) - Data can be processed by machines

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for Neo4j and Jupyter containers)
- Neo4j Graph Database

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/science_data_kit.git
   cd science_data_kit
   ```

2. Create and activate a virtual environment:
   ```bash
   conda create -n science_data_kit python=3.13 pip
   conda activate science_data_kit
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the Streamlit application:

```bash
streamlit run app/app.py
```

Access the GUI from your browser at:

```
localhost:8501
```

### Configuration

The application uses Streamlit's configuration system to handle various settings:

- **Message Size Limits**: For large datasets, the default message size limit (200 MB) may be exceeded. The configuration has been adjusted to handle larger datasets.
- **Theme Settings**: Visual appearance settings are configured for better user experience.

Configuration files are located in the `app/.streamlit` directory:

```
app/.streamlit/
├── config.toml    # Main configuration file
└── README.md      # Documentation for configuration options
```

To adjust configuration settings (e.g., if you encounter "MessageSizeError"):

1. Edit `app/.streamlit/config.toml`
2. Restart the Streamlit application

For more details, see the [configuration documentation](app/.streamlit/README.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

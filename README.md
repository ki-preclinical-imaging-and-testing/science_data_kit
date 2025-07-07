# Science Data Kit (SDK)

A comprehensive toolkit for indexing, curating, and integrating multimodal research data using knowledge graph capabilities.

## Overview

The Science Data Kit (SDK) helps researchers manage and make sense of complex, multimodal scientific data. It follows the FAIR+ data principles to ensure your data is Findable, Accessible, Interoperable, Reusable, and Computable.

## Current Development Status

The Science Data Kit is currently undergoing significant architectural improvements and reorganization. The project is focused on three active roadmaps:

1. **Repository Reorganization** - Improving the organization of documentation and repository structure
2. **Knowledge Graph Documentation System** - Implementing an AI-navigable documentation system
3. **Strategic Enhancements** - Platform maturation and community adoption features

For more details on the current development plans and roadmaps, see the [Roadmaps Index](docs/roadmaps/index.md).

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
   - Host a local Neo4j database (with APOC plugin pre-installed)
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
   - Summarize ontology terms for node labels
   - Load ontology relationships into Neo4j
   - [Learn more about ontology features](docs/ONTOLOGY_FEATURES.md)

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

## Architecture

The Science Data Kit follows a modular architecture with clear separation of concerns:

### Core Components

- **Core Functionality** - The core functionality is contained in the `science_data_kit.core` package, which provides:
  - Database utilities for connecting to Neo4j and other databases
  - File system utilities for scanning and analyzing files
  - Data models for representing entities and relationships
  - Visualization utilities for creating interactive visualizations
  - Ontology module for working with ontologies and semantic data models

### UI Components

- **UI Framework** - The UI is built using Streamlit and follows a component-based architecture:
  - Base modules (`ui/__init__.py`, `ui/config.py`, `ui/state.py`) provide common functionality
  - Adapter modules (`ui/adapters/*`) connect the UI to the core functionality
  - Component modules (`ui/components/*`) provide reusable UI elements
  - Page modules (`ui/pages/*`) define the different pages of the application
  - The main app entry point (`ui/app.py`) ties everything together

### Testing Framework

The project includes a comprehensive testing framework:

- **Unit Tests** - Test individual components in isolation
  - UI component tests
  - Core functionality tests
  - Model tests

- **Integration Tests** - Test the interaction between components
  - Database connection tests
  - UI-to-core interaction tests
  - End-to-end workflow tests

## Directory Structure

- **[science_data_kit/](science_data_kit/README.md)** - Main package directory
  - **[core/](science_data_kit/core/README.md)** - Core functionality
  - **[ui/](science_data_kit/ui/README.md)** - UI components and pages
- **[ipynb/](ipynb/README.md)** - Jupyter notebooks for tutorials and examples
- **[docs/](docs/README.md)** - Documentation files
  - **[roadmaps/](docs/roadmaps/index.md)** - Project roadmaps and development plans
- **[tests/](tests/README.md)** - Test files
  - **[unit/](tests/unit/README.md)** - Unit tests
  - **[integration/](tests/integration/README.md)** - Integration tests

## FAIR+ Data Principles

The Science Data Kit is designed around the FAIR+ data principles:

- **F**indable - Data is easy to find
- **A**ccessible - Data can be accessed with appropriate permissions
- **I**nteroperable - Data can work with other systems
- **R**eusable - Data can be reused for different purposes
- **+** (Computable) - Data can be processed by machines

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (for Neo4j and Jupyter containers)
- Neo4j Graph Database

#### Optional Dependencies

- **ISA Tools**: Some features in the ISA browser require the `isatools` package. The application includes a compatibility layer that allows it to run without `isatools`, but with limited functionality. If you need full ISA-Tab file processing capabilities, you have two options:

##### Option 1: Install isatools for Python 3.12+ (Limited Functionality)

We've modified the isatools package to work with Python 3.12+, but with some limitations. Specifically, the mzML file processing functionality is not available in this version.

```bash
python install_isatools_py312.py
```

This will create a virtual environment at `~/.venvs/isatools_py312_env` with Python 3.12+ and a modified version of isatools that works without the mzml2isa dependency.

##### Option 2: Install Full isatools with Python 3.9 (Complete Functionality)

For complete functionality including mzML file processing, you can use the provided installation scripts that create a Python 3.9 environment:

1. **Using venv with bash script**:
   ```bash
   bash install_isatools.sh
   ```
   This will create a virtual environment at `~/.venvs/isatools_env` with Python 3.9 and all required dependencies.

2. **Using venv with Python script**:
   ```bash
   python install_isatools.py
   ```
   This will also create a virtual environment at `~/.venvs/isatools_env` with Python 3.9 and all required dependencies.

##### Activating the Environment

After installation, you can activate the environment and use isatools:
```bash
# For Python 3.12+ version
source ~/.venvs/isatools_py312_env/bin/activate  # Linux/macOS
# or
~\.venvs\isatools_py312_env\Scripts\activate  # Windows

# For Python 3.9 version
source ~/.venvs/isatools_env/bin/activate  # Linux/macOS
# or
~\.venvs\isatools_env\Scripts\activate  # Windows
```

The main application will continue to work with Python 3.10+ using the compatibility layer, while the isatools-specific features will be available in the environment you choose to activate.

### Installation

We provide a comprehensive installation script that handles all the necessary setup steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/science_data_kit.git
   cd science_data_kit
   ```

2. Run the installation script:
   ```bash
   ./install.sh
   ```

The installation script will:
- Check for system dependencies (Python 3.10+, pip, Docker, Docker Compose)
- Offer to install missing dependencies
- Set up a Python virtual environment
- Install the Science Data Kit package and its dependencies
- Configure Neo4j in a Docker container
- Provide options for installing isatools (basic or full version)

#### Manual Installation (Alternative)

If you prefer to install manually:

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. (Optional) Install isatools:
   ```bash
   # For basic isatools (Python 3.12+, limited functionality)
   pip install -e .[isatools]

   # For full isatools (Python 3.9, complete functionality)
   # See the "Optional Dependencies" section above
   ```

### Running the Application

After installation, you can start the Science Data Kit application:

```bash
# Activate the virtual environment (if not already activated)
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run the application
science_data_kit
```

Access the GUI from your browser at:

```
localhost:8501
```

### Verifying the Installation

We provide a test script that automatically verifies your installation:

```bash
./test_installation.py
```

This script checks:
- Python version
- Required dependencies
- Docker and Neo4j container status
- Configuration files
- Optional components like isatools

Alternatively, you can manually verify the installation:

1. Check that the application starts without errors:
   ```bash
   science_data_kit
   ```

2. Verify that Neo4j is running:
   ```bash
   docker ps | grep neo4j-instance
   ```
   You should see the Neo4j container running.

3. Access the Neo4j browser at `http://localhost:7474` and log in with the default credentials (neo4j/password).

4. If you installed isatools, verify the installation:
   ```bash
   # For basic isatools (Python 3.12+)
   python -c "import isatools; print('isatools version:', isatools.__version__)"

   # For full isatools (Python 3.9)
   # First activate the appropriate environment
   source ~/.venvs/isatools_env/bin/activate  # Linux/macOS
   # or
   ~\.venvs\isatools_env\Scripts\activate  # Windows
   python -c "import isatools; print('isatools version:', isatools.__version__)"
   ```

### Configuration

The application uses Streamlit's configuration system to handle various settings:

- **Message Size Limits**: For large datasets, the default message size limit (200 MB) may be exceeded. The configuration has been adjusted to handle larger datasets.
- **Theme Settings**: Visual appearance settings are configured for better user experience.

Configuration files are located in the `.streamlit` directory within the application package.

To adjust configuration settings (e.g., if you encounter "MessageSizeError"):

1. Edit the appropriate configuration file
2. Restart the Streamlit application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

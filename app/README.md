# Science Data Kit - Application

This directory contains the Streamlit application code for the Science Data Kit.

## Application Structure

The application is organized into several pages, each with a specific purpose in the data workflow:

### 1. Connect (🌐)

**File:** [connect.py](connect.py)

The Connect page allows you to set up your data infrastructure:
- Host a local Neo4j database to stage your data
- Run Jupyter Lab to work with your data
- Launch NeoDash for Neo4j visualization
- Connect to a Neo4j database

### 2. Survey (🔭)

**File:** [survey.py](survey.py)

The Survey page helps you scan and analyze your file systems:
- Locate and scan datasets
- Configure output location for scan results
- Run filesystem scans using NCDU
- View scan results
- Label entities for further processing
- Push data to Neo4j database

### 3. Map (🗺)

**File:** [map.py](map.py)

The Map page allows you to define entities and relationships:
- Load entities from files, database, or NCDU scan results
- Define entity structure and properties
- Map property columns to Neo4j property names
- Filter entities based on column values
- Define relationships between entities
- Build taxonomies and ontologies
- Push entities and relationships to the database

### 4. Explore (🏞)

**File:** [explore.py](explore.py)

The Explore page helps you visualize and analyze your data:
- View schema visualizations
- Extract and explore node data
- Export data for further analysis

### 5. Chat (💬)

**File:** [chat.py](chat.py)

The Chat page allows you to interact with your data using natural language:
- Connect to LLM providers (OpenAI, Anthropic, Ollama)
- Configure LLM settings
- Ask questions about your data
- Get context-aware responses
- View schema information

### 6. Learn (📖)

**File:** [about.py](about.py)

The Learn page provides resources and documentation:
- Documentation and tutorials
- Knowledge graph basics
- Community and support
- Video tutorials

## Utility Modules

The `utils/` directory contains utility modules used by the application:

- **database.py** - Functions for interacting with Neo4j databases
- **file_organizer.py** - Functions for organizing files
- **file_utils.py** - General file utility functions
- **graph_utils.py** - Functions for working with graphs
- **jupyter_server.py** - Functions for managing Jupyter server
- **models.py** - Data models and database operations
- **neodash_server.py** - Functions for managing NeoDash server
- **registry.py** - Entity registry functionality
- **sidebar.py** - Sidebar components for the application
- **visualizations.py** - Visualization functions

## Application Entry Point

The main entry point for the application is [app.py](app.py), which initializes the session state and sets up the navigation menu.

## Navigation

The navigation menu is defined in [menu.py](menu.py), which uses Streamlit's navigation component to create a sidebar menu with icons for each page.

## How to Run

From the repository root, run:

```bash
streamlit run app/app.py
```

This will start the Streamlit server and open the application in your default web browser.
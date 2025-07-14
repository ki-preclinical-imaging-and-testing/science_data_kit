# Science Data Kit (SDK) Installation Guide

This guide provides step-by-step instructions for installing and setting up the Science Data Kit (SDK) for your research needs. We offer multiple installation methods to accommodate different user preferences and requirements.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Docker Installation (Recommended)](#docker-installation-recommended)
3. [Pip Installation](#pip-installation)
4. [Development Installation](#development-installation)
5. [Verifying Your Installation](#verifying-your-installation)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing the Science Data Kit, ensure you have the following:

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

For Docker installation:
- Docker Engine 20.10.0 or higher
- Docker Compose 2.0.0 or higher

## Docker Installation (Recommended)

Using Docker is the recommended method for installing the Science Data Kit as it ensures all dependencies and services are properly configured.

### Standard Docker Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/science_data_kit.git
   cd science_data_kit
   ```

2. Build and start the Docker containers:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. Access the Science Data Kit web interface:
   ```
   http://localhost:8501
   ```

### Workshop Docker Setup

For workshop participants, we provide a simplified Docker setup:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/science_data_kit.git
   cd science_data_kit
   ```

2. Build and start the workshop containers:
   ```bash
   docker-compose -f docker/docker-compose-workshop.yml up -d
   ```

3. Access the Science Data Kit web interface:
   ```
   http://localhost:8501
   ```

The workshop setup includes:
- Pre-loaded sample datasets
- Simplified UI configuration
- Tutorial materials

## Pip Installation

If you prefer to install the Science Data Kit directly on your system:

1. Install the package from PyPI:
   ```bash
   pip install science-data-kit
   ```

2. Install Neo4j database (required):
   - Download from [Neo4j Download Center](https://neo4j.com/download/)
   - Follow Neo4j installation instructions for your operating system
   - Create a new database with username and password

3. Configure the Science Data Kit:
   ```bash
   sdk-config --neo4j-uri bolt://localhost:7687 --neo4j-user neo4j --neo4j-password your_password
   ```

4. Start the Science Data Kit:
   ```bash
   sdk-start
   ```

5. Access the web interface:
   ```
   http://localhost:8501
   ```

## Development Installation

For developers who want to contribute to the Science Data Kit:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/science_data_kit.git
   cd science_data_kit
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   # For core package with development tools
   pip install -e ".[dev]"

   # For all extensions (including dropbox, msgraph, google, etc.)
   pip install -e ".[all]"

   # For specific extensions
   pip install -e ".[dropbox,msgraph]"
   ```

   Alternatively, you can use the installation script with the extensions flag:
   ```bash
   # Install with all extensions
   ./install.sh -e

   # Install with specific extensions
   ./install.sh --extensions=dropbox,msgraph

   # Show all installation options
   ./install.sh --help
   ```

4. Install Neo4j database (required):
   - Download from [Neo4j Download Center](https://neo4j.com/download/)
   - Follow Neo4j installation instructions for your operating system
   - Create a new database with username and password

5. Configure the Science Data Kit:
   ```bash
   python -m science_data_kit.config --neo4j-uri bolt://localhost:7687 --neo4j-user neo4j --neo4j-password your_password
   ```

6. Start the Science Data Kit in development mode:
   ```bash
   python -m science_data_kit.app
   ```

7. Access the web interface:
   ```
   http://localhost:8501
   ```

## Verifying Your Installation

To verify that your Science Data Kit installation is working correctly:

1. Run the verification script:
   ```bash
   sdk-verify
   ```

   For development installation:
   ```bash
   python -m science_data_kit.verify
   ```

2. The script will check:
   - Core dependencies
   - Database connection
   - API functionality
   - UI components
   - Sample data access

3. If all checks pass, your installation is ready to use.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure Neo4j is running
   - Verify connection URI, username, and password
   - Check firewall settings

2. **Missing Dependencies**
   - Run `pip install -e ".[all]"` to install all optional dependencies
   - Check Python version compatibility

3. **Docker Issues**
   - Ensure Docker daemon is running
   - Check port conflicts with existing services
   - Increase Docker memory allocation if needed

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [Common Errors FAQ](https://docs.example.com/sdk/faq)
2. Join our [Community Forum](https://forum.example.com/sdk)
3. Open an issue on our [GitHub repository](https://github.com/yourusername/science_data_kit/issues)

## Next Steps

After installation, we recommend:

1. Exploring the [Getting Started Guide](https://docs.example.com/sdk/getting-started)
2. Trying the [30-Minute Challenge Tutorial](https://docs.example.com/sdk/tutorial)
3. Reviewing the [Sample Datasets](https://docs.example.com/sdk/datasets)

---

For more information, visit our [Documentation Portal](https://docs.example.com/sdk).

# Science Data Kit - Common Errors FAQ

This document provides solutions to common errors and issues that users might encounter when using the Science Data Kit, especially during workshops.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Connection Issues](#database-connection-issues)
3. [Data Loading Issues](#data-loading-issues)
4. [UI Issues](#ui-issues)
5. [Tutorial Issues](#tutorial-issues)
6. [Performance Issues](#performance-issues)
7. [Docker Issues](#docker-issues)
8. [Python Environment Issues](#python-environment-issues)

## Installation Issues

### Error: "No module named 'science_data_kit'"

**Problem**: Python cannot find the Science Data Kit package.

**Solution**:
1. Make sure you have installed the Science Data Kit package:
   ```bash
   pip install -e .
   ```
2. Verify that the package is installed:
   ```bash
   pip list | grep science-data-kit
   ```
3. Check your Python path:
   ```python
   import sys
   print(sys.path)
   ```
4. If using a virtual environment, make sure it's activated:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

### Error: "ImportError: cannot import name 'X' from 'science_data_kit'"

**Problem**: You're trying to import a module or function that doesn't exist or is in a different location.

**Solution**:
1. Check the documentation for the correct import path
2. Update your code to use the correct import path
3. Make sure you have the latest version of the Science Data Kit installed

### Error: "Error loading database configuration"

**Problem**: The application cannot load the database configuration.

**Solution**:
1. Make sure the `db_config.yaml` file exists in the project root
2. Check that the file has the correct format:
   ```yaml
   uri: bolt://localhost:7687
   user: neo4j
   password: your_password
   ```
3. Verify that the file has the correct permissions

## Database Connection Issues

### Error: "Unable to connect to Neo4j database"

**Problem**: The application cannot connect to the Neo4j database.

**Solution**:
1. Make sure Neo4j is running:
   ```bash
   docker ps | grep neo4j
   ```
2. Check the connection settings on the Server page
3. Verify that the Neo4j container is exposing the correct ports:
   ```bash
   docker port neo4j
   ```
4. Try restarting the Neo4j container:
   ```bash
   docker restart neo4j
   ```

### Error: "Authentication failed"

**Problem**: The provided Neo4j credentials are incorrect.

**Solution**:
1. Check the username and password in the `db_config.yaml` file
2. Verify the credentials on the Server page
3. If using Docker, check the environment variables used to set the Neo4j password:
   ```bash
   docker inspect neo4j | grep NEO4J_AUTH
   ```
4. Reset the Neo4j password if necessary:
   ```bash
   docker exec -it neo4j cypher-shell -u neo4j -p current_password "ALTER CURRENT USER SET PASSWORD 'new_password'"
   ```

### Error: "Connection refused"

**Problem**: The Neo4j server is not accepting connections.

**Solution**:
1. Check if Neo4j is running:
   ```bash
   docker ps | grep neo4j
   ```
2. Verify that the Neo4j container is exposing the correct ports:
   ```bash
   docker port neo4j
   ```
3. Check for firewall or network issues
4. Try restarting the Neo4j container:
   ```bash
   docker restart neo4j
   ```

## Data Loading Issues

### Error: "Error loading dataset"

**Problem**: The application cannot load the dataset.

**Solution**:
1. Check that the Neo4j database is running and accessible
2. Verify that you have the necessary permissions
3. Check the dataset path and format
4. Try loading a smaller subset of the data first
5. Check the Neo4j logs for errors:
   ```bash
   docker logs neo4j
   ```

### Error: "Duplicate node labels"

**Problem**: You're trying to create nodes with labels that already exist.

**Solution**:
1. Use `MERGE` instead of `CREATE` in your Cypher queries
2. Delete existing nodes before creating new ones:
   ```cypher
   MATCH (n:Label) DETACH DELETE n
   ```
3. Add a unique constraint to prevent duplicates:
   ```cypher
   CREATE CONSTRAINT ON (n:Label) ASSERT n.id IS UNIQUE
   ```

### Error: "Out of memory"

**Problem**: Neo4j has run out of memory while loading data.

**Solution**:
1. Increase the memory allocated to Neo4j:
   ```bash
   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_dbms_memory_heap_max__size=4G neo4j
   ```
2. Load data in smaller batches
3. Optimize your Cypher queries
4. Use the APOC library for bulk imports

## UI Issues

### Error: "Streamlit server failed to start"

**Problem**: The Streamlit server cannot start.

**Solution**:
1. Check if another Streamlit app is already running on the same port
2. Try running with a different port:
   ```bash
   streamlit run app.py --server.port=8502
   ```
3. Check for errors in the Streamlit logs
4. Restart your computer and try again

### Error: "Widget not found"

**Problem**: Streamlit cannot find a widget that your code is trying to access.

**Solution**:
1. Make sure you're using the correct widget key
2. Check that the widget is created before you try to access it
3. Restart the Streamlit app
4. Clear your browser cache

### Error: "JavaScript error"

**Problem**: There's an error in the JavaScript code used by the UI.

**Solution**:
1. Check the browser console for more details
2. Try a different browser
3. Clear your browser cache
4. Restart the Streamlit app

## Tutorial Issues

### Error: "Tutorial script failed"

**Problem**: The tutorial script encountered an error.

**Solution**:
1. Check the error message for details
2. Make sure all prerequisites are installed
3. Verify that the dataset is loaded
4. Try running the script with Python directly:
   ```bash
   python -m tutorials.preclinical_challenge_tutorial
   ```

### Error: "Checkpoint verification failed"

**Problem**: The checkpoint verification script detected an issue.

**Solution**:
1. Check which checkpoint failed
2. Review the corresponding section of the tutorial
3. Make sure the dataset is loaded correctly
4. Check that your queries match the expected format
5. Try running the verification script with a specific checkpoint:
   ```bash
   python -m tutorials.checkpoint_verification 1
   ```

### Error: "No module named 'tutorials'"

**Problem**: Python cannot find the tutorials package.

**Solution**:
1. Make sure you're running the script from the project root
2. Check that the tutorials directory exists
3. Try using the full path to the script:
   ```bash
   python /path/to/science_data_kit/tutorials/preclinical_challenge_tutorial.py
   ```

## Performance Issues

### Error: "Query timeout"

**Problem**: A Neo4j query is taking too long to execute.

**Solution**:
1. Optimize your Cypher query
2. Add appropriate indexes:
   ```cypher
   CREATE INDEX ON :Label(property)
   ```
3. Use `PROFILE` to analyze query performance:
   ```cypher
   PROFILE MATCH (n:Label) RETURN n LIMIT 10
   ```
4. Increase the Neo4j query timeout:
   ```bash
   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_dbms_transaction_timeout=60s neo4j
   ```

### Error: "Out of memory"

**Problem**: The application has run out of memory.

**Solution**:
1. Reduce the amount of data being processed
2. Use streaming instead of loading all data at once
3. Increase the memory allocated to the application
4. Optimize your code to use less memory

### Error: "Application is slow"

**Problem**: The application is running slowly.

**Solution**:
1. Check system resources (CPU, memory, disk)
2. Optimize database queries
3. Use caching where appropriate
4. Reduce the amount of data being processed
5. Use profiling tools to identify bottlenecks

## Docker Issues

### Error: "Cannot connect to the Docker daemon"

**Problem**: The Docker daemon is not running or you don't have permission to access it.

**Solution**:
1. Start the Docker daemon:
   ```bash
   sudo systemctl start docker  # Linux
   ```
2. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```
3. Log out and log back in for the group changes to take effect

### Error: "Port is already allocated"

**Problem**: The port you're trying to use is already in use.

**Solution**:
1. Check which process is using the port:
   ```bash
   lsof -i :7474  # Linux/Mac
   netstat -ano | findstr :7474  # Windows
   ```
2. Stop the process or use a different port:
   ```bash
   docker run -p 7475:7474 -p 7688:7687 neo4j
   ```

### Error: "No space left on device"

**Problem**: Your disk is full.

**Solution**:
1. Clean up unused Docker resources:
   ```bash
   docker system prune -a
   ```
2. Remove unused images:
   ```bash
   docker image prune -a
   ```
3. Remove unused volumes:
   ```bash
   docker volume prune
   ```
4. Free up disk space on your system

## Python Environment Issues

### Error: "Conflicting dependencies"

**Problem**: There are conflicting dependencies in your Python environment.

**Solution**:
1. Create a new virtual environment:
   ```bash
   python -m venv new_venv
   source new_venv/bin/activate  # Linux/Mac
   new_venv\Scripts\activate     # Windows
   ```
2. Install the Science Data Kit with its dependencies:
   ```bash
   pip install -e .
   ```
3. Use a requirements.txt file to specify exact versions:
   ```bash
   pip install -r requirements.txt
   ```

### Error: "Python version not supported"

**Problem**: The Science Data Kit requires a different Python version.

**Solution**:
1. Check the required Python version in the documentation
2. Install the required Python version
3. Create a new virtual environment with the required Python version:
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

### Error: "pip: command not found"

**Problem**: The pip command is not available.

**Solution**:
1. Install pip:
   ```bash
   python -m ensurepip --upgrade
   ```
2. Use the full path to pip:
   ```bash
   python -m pip install -e .
   ```
3. Make sure pip is in your PATH

## Getting More Help

If you're still experiencing issues:

1. Check the [Science Data Kit Documentation](https://your-org.github.io/science_data_kit/)
2. Search for similar issues on the [GitHub repository](https://github.com/your-org/science_data_kit/issues)
3. Ask a question on the [GitHub Discussions](https://github.com/your-org/science_data_kit/discussions)
4. Contact the Science Data Kit team at [support@example.com](mailto:support@example.com)

During workshops, don't hesitate to ask an instructor for help!
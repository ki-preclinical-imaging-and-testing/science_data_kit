#!/bin/bash
set -e

# Function to wait for Neo4j to be available
wait_for_neo4j() {
    echo "Waiting for Neo4j to be available..."
    
    # Get Neo4j connection details from environment variables or use defaults
    NEO4J_URI=${NEO4J_URI:-bolt://localhost:7687}
    NEO4J_USER=${NEO4J_USER:-neo4j}
    NEO4J_PASSWORD=${NEO4J_PASSWORD:-workshop}
    
    # Extract host and port from URI
    if [[ $NEO4J_URI =~ bolt://([^:]+):([0-9]+) ]]; then
        NEO4J_HOST=${BASH_REMATCH[1]}
        NEO4J_PORT=${BASH_REMATCH[2]}
    else
        echo "Invalid Neo4j URI format. Expected: bolt://host:port"
        exit 1
    fi
    
    # Wait for Neo4j to be available
    for i in {1..30}; do
        if nc -z $NEO4J_HOST $NEO4J_PORT; then
            echo "Neo4j is available!"
            return 0
        fi
        echo "Waiting for Neo4j... ($i/30)"
        sleep 2
    done
    
    echo "Neo4j is not available after 60 seconds. Continuing anyway..."
    return 1
}

# Function to verify the installation
verify_installation() {
    echo "Verifying Science Data Kit installation..."
    python -m science_data_kit.verify --quiet || true
}

# Function to initialize the application
initialize_app() {
    echo "Initializing Science Data Kit Workshop Environment..."
    
    # Create necessary directories if they don't exist
    mkdir -p /app/data /app/workshop/data /app/workshop/tutorials
    
    # Set up configuration if environment variables are provided
    if [ -n "$NEO4J_URI" ] && [ -n "$NEO4J_USER" ] && [ -n "$NEO4J_PASSWORD" ]; then
        echo "Configuring Neo4j connection..."
        python -m science_data_kit.config --neo4j-uri "$NEO4J_URI" --neo4j-user "$NEO4J_USER" --neo4j-password "$NEO4J_PASSWORD"
    fi
}

# Function to load sample data for workshop
load_sample_data() {
    echo "Loading sample data for workshop..."
    
    # Check if sample data is already loaded
    SAMPLE_DATA_LOADED=$(python -c "from science_data_kit.data.samples import is_sample_data_loaded; print(is_sample_data_loaded())")
    
    if [ "$SAMPLE_DATA_LOADED" = "True" ]; then
        echo "Sample data already loaded. Skipping..."
    else
        echo "Loading preclinical research sample dataset..."
        python -m science_data_kit.data.samples.load_preclinical_dataset
        echo "Sample data loaded successfully!"
    fi
}

# Function to set up workshop UI configuration
setup_workshop_ui() {
    echo "Setting up workshop UI configuration..."
    
    # Enable workshop mode in configuration
    python -m science_data_kit.config --set workshop_mode true
    
    # Set up simplified UI with relevant features prominently displayed
    python -m science_data_kit.config --set ui_mode simplified
    
    echo "Workshop UI configuration complete!"
}

# Main entrypoint logic
main() {
    # Wait for Neo4j if we're not running a help command
    if [[ "$*" != *"--help"* ]] && [[ "$*" != *"-h"* ]]; then
        wait_for_neo4j
        initialize_app
        verify_installation
        load_sample_data
        setup_workshop_ui
        
        echo "Workshop environment is ready!"
        echo "Access the Science Data Kit at http://localhost:8501"
        echo "Access Jupyter Lab at http://localhost:8888"
        echo "Access NeoDash at http://localhost:5005"
    fi
    
    # Execute the command
    exec "$@"
}

# Run the main function
main "$@"
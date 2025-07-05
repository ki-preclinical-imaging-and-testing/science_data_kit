#!/bin/bash
set -e

# Function to wait for Neo4j to be available
wait_for_neo4j() {
    echo "Waiting for Neo4j to be available..."
    
    # Get Neo4j connection details from environment variables or use defaults
    NEO4J_URI=${NEO4J_URI:-bolt://localhost:7687}
    NEO4J_USER=${NEO4J_USER:-neo4j}
    NEO4J_PASSWORD=${NEO4J_PASSWORD:-neo4j}
    
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
    echo "Initializing Science Data Kit..."
    
    # Create necessary directories if they don't exist
    mkdir -p /app/data
    
    # Set up configuration if environment variables are provided
    if [ -n "$NEO4J_URI" ] && [ -n "$NEO4J_USER" ] && [ -n "$NEO4J_PASSWORD" ]; then
        echo "Configuring Neo4j connection..."
        python -m science_data_kit.config --neo4j-uri "$NEO4J_URI" --neo4j-user "$NEO4J_USER" --neo4j-password "$NEO4J_PASSWORD"
    fi
}

# Main entrypoint logic
main() {
    # Wait for Neo4j if we're not running a help command
    if [[ "$*" != *"--help"* ]] && [[ "$*" != *"-h"* ]]; then
        wait_for_neo4j
        initialize_app
        verify_installation
    fi
    
    # Execute the command
    exec "$@"
}

# Run the main function
main "$@"
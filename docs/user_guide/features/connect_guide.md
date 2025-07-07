# Connect Feature Guide

## Overview

The Connect feature in Science Data Kit (SDK) allows you to set up and manage connections to various data sources and infrastructure components. This guide explains how to use the Connect page to establish connections to Neo4j databases, manage Docker containers, and start/stop services.

## Connecting to Neo4j Database

### Basic Connection

1. Navigate to the Connect page in SDK
2. In the Database Connection section, you'll see a form with the following fields:
   - **Neo4j URI**: The URI of your Neo4j database (e.g., `bolt://localhost:7687`)
   - **Username**: Your Neo4j username (default is `neo4j`)
   - **Password**: Your Neo4j password
   - **Database**: The name of the Neo4j database to connect to (default is `neo4j`)
3. Fill in these fields with your Neo4j connection details
4. Click "Connect" to establish the connection

### Connection Status

The connection status is displayed at the top of the Database Connection section:
- **Connected to Neo4j**: Indicates a successful connection
- **Not connected to Neo4j**: Indicates no active connection

### Disconnecting

To disconnect from the Neo4j database:
1. Click the "Disconnect" button in the Database Connection section
2. The connection status will change to "Not connected to Neo4j"

## Managing Neo4j Container

If you don't have a Neo4j instance running, SDK can help you start and manage a Neo4j container using Docker.

### Starting a Neo4j Container

1. In the Neo4j Container section, select the Neo4j version you want to use
2. Enter your preferred username and password
3. Click "Start Container" to launch a new Neo4j container

### Container Status

The container status is displayed at the top of the Neo4j Container section:
- **Neo4j container is running**: Container is active and ready to use
- **Neo4j container is stopped**: Container exists but is not running
- **Neo4j container not found**: No container has been created yet

### Stopping a Neo4j Container

To stop a running Neo4j container:
1. Click the "Stop Container" button in the Neo4j Container section
2. The container status will change to "Neo4j container is stopped"

## Managing Jupyter Lab

SDK provides integration with Jupyter Lab for interactive data analysis.

### Starting Jupyter Lab

1. In the Jupyter Lab section, specify the port you want to use (default is 8888)
2. Click "Start Jupyter" to launch a Jupyter Lab container

### Accessing Jupyter Lab

Once Jupyter Lab is running:
1. A link will appear below the Jupyter Lab section
2. Click "Open Jupyter Lab" to open Jupyter Lab in a new browser tab
3. The token for authentication is automatically configured

### Stopping Jupyter Lab

To stop the Jupyter Lab container:
1. Click the "Stop Jupyter" button in the Jupyter Lab section

## Managing NeoDash

SDK also provides integration with NeoDash, a Neo4j dashboard builder.

### Starting NeoDash

1. In the NeoDash section, specify the port you want to use (default is 5005)
2. Click "Start NeoDash" to launch a NeoDash container

### Accessing NeoDash

Once NeoDash is running:
1. A link will appear below the NeoDash section
2. Click "Open NeoDash" to open NeoDash in a new browser tab

### Stopping NeoDash

To stop the NeoDash container:
1. Click the "Stop NeoDash" button in the NeoDash section

## Troubleshooting

### Common Connection Issues

1. **"Could not connect to Neo4j" error**:
   - Verify that the Neo4j server is running
   - Check that the URI, username, and password are correct
   - Ensure there are no network issues or firewalls blocking the connection

2. **Container start failures**:
   - Ensure Docker is installed and running on your system
   - Check if the specified port is already in use
   - Verify you have sufficient permissions to create Docker containers

3. **Service access issues**:
   - Make sure the service (Jupyter/NeoDash) has fully started before trying to access it
   - Check if the port is accessible from your browser
   - Try using a different port if you encounter conflicts

## Best Practices

1. **Security**:
   - Use strong passwords for your Neo4j database
   - Don't expose database ports to the public internet without proper security measures
   - Change default credentials when starting new containers

2. **Resource Management**:
   - Stop containers when not in use to free up system resources
   - Be mindful of the number of containers running simultaneously

3. **Data Persistence**:
   - Neo4j containers created through SDK store data in Docker volumes
   - For production use, consider setting up a dedicated Neo4j instance with proper backup procedures
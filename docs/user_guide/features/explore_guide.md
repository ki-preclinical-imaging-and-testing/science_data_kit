# Explore Feature Guide

## Overview

The Explore feature in Science Data Kit (SDK) allows you to visualize and analyze your data stored in Neo4j. This guide explains how to use the Explore page to view schema visualizations, extract and explore node data, and export data for further analysis.

## Schema Visualization

### Viewing the Database Schema

1. Navigate to the Explore page in SDK
2. In the Schema Visualization section, you'll see a graph representation of your database schema
3. The visualization shows:
   - Node labels (entity types) as circles
   - Relationship types as arrows between nodes
   - Properties displayed when hovering over nodes

### Customizing the Schema View

You can customize the schema visualization:

1. **Layout**: Choose from different layout algorithms (Force-directed, Hierarchical, Circular)
2. **Colors**: Customize the colors of nodes based on labels
3. **Size**: Adjust the size of nodes based on the number of instances or properties
4. **Filters**: Show/hide specific node labels or relationship types

### Interacting with the Schema

The schema visualization is interactive:

1. **Zoom**: Use the mouse wheel to zoom in and out
2. **Pan**: Click and drag to move around the visualization
3. **Select**: Click on nodes or relationships to see details
4. **Expand/Collapse**: Double-click on nodes to expand or collapse their relationships

## Node Data Exploration

### Querying Nodes

To explore node data:

1. In the Node Data Exploration section, you'll see a query builder
2. Select a node label from the dropdown
3. Add filters to narrow down the results (optional)
4. Click "Run Query" to execute

### Viewing Query Results

The query results are displayed in multiple formats:

1. **Table View**: Shows node properties in a tabular format
2. **Graph View**: Shows nodes and their relationships as a network graph
3. **JSON View**: Shows the raw JSON data returned by the query

To switch between views:

1. Click the view selector tabs above the results
2. Select the desired view

### Exploring Relationships

To explore relationships between nodes:

1. In the Graph View, select a node
2. Click "Expand" to show connected nodes
3. Choose which relationship types to include
4. Set the depth of expansion (1-3 levels)
5. Click "Apply" to update the visualization

### Saving Queries

You can save queries for future use:

1. After running a query, click "Save Query"
2. Enter a name and description for the query
3. Click "Save" to store the query

To load a saved query:

1. Click "Load Query"
2. Select the query from the list
3. Click "Load" to run the query

## Data Export

### Exporting to CSV

To export data to CSV:

1. Run a query to get the data you want to export
2. In the Data Export section, select "CSV" as the export format
3. Choose which properties to include in the export
4. Click "Export" to download the CSV file

### Exporting to JSON

To export data to JSON:

1. Run a query to get the data you want to export
2. In the Data Export section, select "JSON" as the export format
3. Choose between pretty-printed or compact format
4. Click "Export" to download the JSON file

### Exporting to Excel

To export data to Excel:

1. Run a query to get the data you want to export
2. In the Data Export section, select "Excel" as the export format
3. Choose which properties to include in the export
4. Click "Export" to download the Excel file

### Exporting Visualizations

To export visualizations:

1. In the Graph View or Schema Visualization, click "Export Visualization"
2. Choose the export format (PNG, SVG, or PDF)
3. Set the dimensions and resolution
4. Click "Export" to download the image

## Advanced Features

### Custom Cypher Queries

For advanced users, you can write custom Cypher queries:

1. Click "Advanced Query" in the Node Data Exploration section
2. Enter your Cypher query in the text editor
3. Click "Run Query" to execute

### Query Parameters

You can use parameters in your queries:

1. In the Advanced Query mode, define parameters in the Parameters section
2. Use parameters in your query with the `$paramName` syntax
3. Click "Run Query" to execute with the provided parameters

### Query History

SDK keeps track of your query history:

1. Click "Query History" to see your recent queries
2. Select a query from the history to load it
3. Click "Clear History" to remove all queries from the history

## Integration with Other Features

### Integration with Map

You can send data from Explore to Map:

1. Run a query to get the data you want to map
2. Click "Send to Map" in the Data Export section
3. Configure how the data should be mapped
4. Click "Send" to open the data in the Map feature

### Integration with Chat

You can ask questions about your data using natural language:

1. Click "Chat about this data" in the Node Data Exploration section
2. Type your question in natural language
3. The system will generate a response based on the data

## Troubleshooting

### Common Query Issues

1. **Query returns no results**:
   - Check that the node label exists in your database
   - Verify that your filters aren't too restrictive
   - Ensure the database connection is active

2. **Query times out**:
   - Add more specific filters to reduce the result set
   - Limit the number of returned nodes
   - Simplify the query by reducing the relationship depth

3. **Visualization is too cluttered**:
   - Reduce the number of nodes by adding filters
   - Decrease the relationship expansion depth
   - Use the hierarchical layout for better organization

## Best Practices

1. **Start with Simple Queries**:
   - Begin with basic queries that return a small number of nodes
   - Gradually add complexity as you understand the data better

2. **Use Filters Effectively**:
   - Add filters to focus on the most relevant data
   - Combine multiple filters to narrow down results precisely

3. **Save Important Queries**:
   - Save queries that you use frequently
   - Document what each query is used for

4. **Export Data Regularly**:
   - Export important findings for reporting
   - Use exports to share data with team members who don't have access to SDK

5. **Combine with Other Features**:
   - Use Explore in conjunction with Map to understand and visualize your data
   - Use the Chat feature to ask questions about your data in natural language
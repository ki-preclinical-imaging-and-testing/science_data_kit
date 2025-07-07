# Survey Feature Guide

## Overview

The Survey feature in Science Data Kit (SDK) allows you to scan and analyze file systems to discover datasets and their structure. This guide explains how to use the Survey page to locate, scan, and label datasets, and how to push the discovered data to Neo4j.

## File System Browser

### Navigating the File System

1. Navigate to the Survey page in SDK
2. In the File System Browser section, you'll see a directory tree showing your file system
3. Click on folders to expand or collapse them
4. Use the breadcrumb navigation at the top to quickly jump to parent directories

### Selecting Directories for Scanning

1. Browse to the directory containing your datasets
2. Select the checkbox next to the directory you want to scan
3. You can select multiple directories for scanning

## Scanning Datasets

### Starting a Scan

1. After selecting the directories to scan, click the "Scan Selected" button
2. A progress bar will appear showing the scan progress
3. The scan will identify files and their relationships based on naming patterns and content

### Scan Options

You can customize the scan behavior with the following options:

- **Scan Depth**: Controls how deep in the directory structure the scan will go
- **File Types**: Filter which file types to include in the scan
- **Recursive**: Enable/disable recursive scanning of subdirectories
- **Follow Symlinks**: Enable/disable following symbolic links during scanning

### Viewing Scan Results

After the scan completes:

1. A summary of the scan results will be displayed showing:
   - Number of files discovered
   - File types found
   - Potential datasets identified
   - Relationships detected between files

2. The results are organized into a hierarchical view that shows:
   - Directories
   - Files within directories
   - Metadata extracted from files
   - Relationships between files

## Entity Labeling

The Entity Labeling section allows you to categorize and label the discovered files and datasets.

### Automatic Labeling

SDK attempts to automatically label entities based on:
- File naming patterns
- File extensions
- Content analysis
- Directory structure

### Manual Labeling

To manually label entities:

1. Select an entity in the scan results
2. In the Entity Labeling section, you'll see suggested labels
3. You can:
   - Accept suggested labels
   - Add new labels
   - Remove incorrect labels
   - Create custom labels

### Label Management

You can manage your labeling system:

1. Create new label categories
2. Define hierarchical relationships between labels
3. Import existing ontologies or taxonomies
4. Export your labeling system for reuse

## Pushing Data to Neo4j

Once you've scanned and labeled your datasets, you can push this information to Neo4j.

### Configuring the Push

1. In the "Push to Neo4j" section, you'll see options for how to represent your data in the graph
2. Configure the following settings:
   - **Node Labels**: How file types map to Neo4j node labels
   - **Relationships**: How file relationships map to Neo4j relationship types
   - **Properties**: Which metadata to include as node properties
   - **Merge Strategy**: How to handle existing data (merge, replace, skip)

### Executing the Push

1. After configuring the push settings, click the "Push to Neo4j" button
2. A progress indicator will show the status of the operation
3. Upon completion, a summary will show:
   - Number of nodes created
   - Number of relationships created
   - Any errors or warnings

### Verifying the Push

To verify that your data was successfully pushed to Neo4j:

1. A preview of the graph structure will be displayed
2. You can click "View in Neo4j Browser" to open the Neo4j Browser with a sample query
3. You can also navigate to the Explore page to visualize and query the pushed data

## Working with Large Datasets

When working with large datasets, consider these tips:

1. **Incremental Scanning**: Scan directories in smaller batches
2. **Selective Pushing**: Push only the most relevant parts of your dataset
3. **Filtering**: Use file type and name filters to focus on specific data
4. **Sampling**: Enable sampling to process a representative subset of large datasets

## Troubleshooting

### Common Scanning Issues

1. **Scan is taking too long**:
   - Reduce the scan depth
   - Limit the file types being scanned
   - Disable recursive scanning
   - Use sampling for large datasets

2. **Missing files or relationships**:
   - Check file permissions
   - Ensure file types are included in the scan
   - Verify that relationship detection rules match your dataset structure

3. **Push to Neo4j fails**:
   - Verify Neo4j connection is active
   - Check that you have write permissions in the database
   - Ensure the database has sufficient storage space
   - Try with a smaller dataset first to identify specific issues

## Best Practices

1. **Organize Before Scanning**:
   - Well-organized directory structures lead to better automatic labeling
   - Consistent file naming conventions improve relationship detection

2. **Iterative Approach**:
   - Start with a small, representative sample
   - Refine your labeling and push configuration
   - Scale up to larger datasets once you're satisfied with the results

3. **Regular Updates**:
   - Re-scan datasets periodically to capture changes
   - Use merge strategies that preserve existing annotations and relationships
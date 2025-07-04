# Science Data Kit (SDK) Infrastructure GUI Roadmap - Version 02

## Overview

This document outlines the roadmap for enhancing the Infrastructure GUI components of the Science Data Kit application. The focus is on improving the server management and connection capabilities to provide a more comprehensive and user-friendly experience.

## Background

The Science Data Kit previously included functionality for launching containerized servers and connecting to various APIs through the legacy app implementation. However, in the current version, many of these features are disabled or not fully implemented. This roadmap aims to restore and enhance these capabilities.

## Goals

1. Restore the ability to launch and manage containerized servers for:
   - Neo4j Database (Dev/Prod environments)
   - Jupyter Lab (single/multi-use)
   - Neodash (Dev/Prod environments)
   - Ollama

2. Enhance connection capabilities to various APIs:
   - Neo4j Database
   - PostgreSQL and other SQL databases
   - LLM agents
   - Various filesystem/share integrations:
     - Local Unix filesystem
     - MSGraph/Sharepoint
     - Dropbox
     - Google Drive
     - Other generic filesystem integrations

3. Improve the UI/UX for server and connection management:
   - Rename the "Connect" page to "Server" or similar
   - Implement expandable sections in the sidebar with status indicators
   - Make connections visible across all views of the application
   - Support multiple named database connections

## Roadmap Components

### 1. Server Management UI Enhancements

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Rename "Connect" page to "Server" | Medium | Completed | Changed page name, icon, and updated docstrings |
| Redesign server management UI | High | Completed | Added server status overview with columns for database and analysis servers |
| Implement expandable sections in sidebar | Medium | Completed | Added expandable sections with green/black status indicators |
| Make connections visible in all views | High | Completed | Status indicators are now visible in all sidebar sections |

### 2. Neo4j Database Server Management

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Re-enable Neo4j container management | High | Completed | Uncommented and updated the Neo4j container sidebar code |
| Support multiple named database connections | High | Completed | Implemented ability to create, save, and manage multiple named connections |
| Add Dev/Prod environment selection | Medium | To Do | Allow users to choose between development and production environments |
| Implement better error handling | Medium | To Do | Improve error messages and recovery options |
| Add container health monitoring | Low | To Do | Display container health metrics |

### 3. Jupyter Lab Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Re-enable Jupyter Lab container management | High | To Do | Uncomment and update the Jupyter sidebar code |
| Implement single/multi-use options | Medium | To Do | Allow users to choose between single and multi-user modes |
| Add Jupyter notebook templates | Low | To Do | Provide starter templates for common data science tasks |
| Implement token-based authentication | Medium | To Do | Secure Jupyter Lab access with tokens |

### 4. Neodash Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Re-enable Neodash container management | High | To Do | Uncomment and update the Neodash sidebar code |
| Add Dev/Prod environment selection | Medium | To Do | Allow users to choose between development and production environments |
| Implement dashboard templates | Low | To Do | Provide starter templates for common visualization needs |
| Add integration with Neo4j database | Medium | To Do | Ensure seamless connection between Neodash and Neo4j |

### 5. Ollama Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement Ollama container management | High | To Do | Create sidebar component for Ollama |
| Add model selection and management | Medium | To Do | Allow users to select and manage Ollama models |
| Implement API for LLM interactions | High | To Do | Create a clean API for interacting with Ollama |
| Add example prompts and templates | Low | To Do | Provide starter templates for common LLM tasks |

### 6. Additional Database Connections

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement PostgreSQL connection | High | To Do | Create sidebar component for PostgreSQL |
| Add support for other SQL databases | Medium | To Do | Extend database connection capabilities |
| Implement connection pooling | Low | To Do | Optimize database connections for performance |
| Add database schema visualization | Medium | To Do | Provide visual representation of database schemas |

### 7. Filesystem/Share Integrations

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement Local Unix filesystem integration | High | To Do | Create sidebar component for local filesystem |
| Implement MSGraph/Sharepoint integration | High | To Do | Re-enable and enhance MSGraph sidebar component |
| Implement Dropbox integration | Medium | To Do | Create sidebar component for Dropbox |
| Implement Google Drive integration | Medium | To Do | Create sidebar component for Google Drive |
| Create generic filesystem integration framework | Low | To Do | Allow for easy addition of new filesystem integrations |

## Implementation Plan

1. **Phase 1: UI Framework and Neo4j Integration**
   - Rename "Connect" page and redesign UI ✓
   - Re-enable Neo4j container management ✓
   - Implement expandable sections in sidebar with status indicators ✓
   - Make connections visible in all views ✓
   - Support multiple named database connections ✓

2. **Phase 2: Jupyter and Neodash Integration**
   - Re-enable Jupyter Lab container management
   - Re-enable Neodash container management
   - Implement single/multi-use options for Jupyter
   - Add Dev/Prod environment selection for Neodash

3. **Phase 3: Ollama and Additional Database Connections**
   - Implement Ollama container management
   - Implement PostgreSQL connection
   - Add support for other SQL databases
   - Implement API for LLM interactions

4. **Phase 4: Filesystem/Share Integrations**
   - Implement Local Unix filesystem integration
   - Re-enable and enhance MSGraph/Sharepoint integration
   - Implement Dropbox integration
   - Implement Google Drive integration
   - Create generic filesystem integration framework

## Current Status

The application now has improved functionality in terms of server management and connections:
1. The "Connect" page has been renamed to "Server" with a more appropriate icon
2. The UI has been redesigned to show server status overview with columns for database and analysis servers
3. Neo4j container management has been re-enabled in the sidebar
4. Expandable sections with status indicators have been implemented in the sidebar
5. MSGraph integration is available in the sidebar with status indicators
6. Multiple named database connections are now supported, allowing users to create, save, and manage multiple connections

## Next Steps

1. Begin with Phase 2 of the implementation plan
2. Focus on re-enabling Jupyter Lab and NeoDash container management
3. Implement single/multi-use options for Jupyter
4. Add Dev/Prod environment selection for Neodash

## Success Metrics

1. All server management features (Neo4j, Jupyter, NeoDash, Ollama) are functional
2. All connection types (databases, filesystems) are implemented and working correctly
3. UI is intuitive and user-friendly, with clear status indicators
4. Connections are visible and accessible from all views of the application
5. Users can easily switch between different environments (Dev/Prod) for applicable services
6. Users can manage multiple named connections to different database servers
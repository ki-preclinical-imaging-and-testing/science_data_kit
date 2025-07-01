# Science Data Kit (SDK) Infrastructure GUI Roadmap - Version 00

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

## Roadmap Components

### 1. Server Management UI Enhancements

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Rename "Connect" page to "Server" | Medium | To Do | Consider the best name that reflects both server management and connections |
| Redesign server management UI | High | To Do | Create a more intuitive interface for managing servers |
| Implement expandable sections in sidebar | Medium | To Do | With green/black status indicators in their titles |
| Make connections visible in all views | High | To Do | Ensure connection status is accessible from any page |

### 2. Neo4j Database Server Management

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Re-enable Neo4j container management | High | To Do | Uncomment and update the Neo4j container sidebar code |
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
   - Rename "Connect" page and redesign UI
   - Re-enable Neo4j container management
   - Implement expandable sections in sidebar with status indicators
   - Make connections visible in all views

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

The application currently has limited functionality in terms of server management and connections:
1. Only the Neo4j database connection is enabled in the sidebar
2. Container management features (Neo4j, Jupyter, Neodash) are disabled
3. The "Connect" page only shows database connection information and a message about disabled features
4. MSGraph integration exists in the codebase but is not enabled in the UI

## Next Steps

1. Begin with Phase 1 of the implementation plan
2. Focus on re-enabling existing functionality before adding new features
3. Prioritize making connections visible in all views of the application
4. Consider renaming the "Connect" page to better reflect its purpose

## Success Metrics

1. All server management features (Neo4j, Jupyter, Neodash, Ollama) are functional
2. All connection types (databases, filesystems) are implemented and working correctly
3. UI is intuitive and user-friendly, with clear status indicators
4. Connections are visible and accessible from all views of the application
5. Users can easily switch between different environments (Dev/Prod) for applicable services
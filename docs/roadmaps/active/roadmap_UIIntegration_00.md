# Science Data Kit (SDK) UI Integration Roadmap

## Overview
This roadmap outlines the plan for implementing a unified file browser interface for local and cloud storage in the Science Data Kit. The goal is to provide a consistent user experience across different storage providers, with unified navigation, search, and filtering capabilities.

## Background
The Science Data Kit has been evolving to support multiple cloud storage providers, including local filesystem, Dropbox, Microsoft Graph (SharePoint and OneDrive), and Google Drive. However, the user interface for navigating and interacting with these different storage providers has not been fully unified, leading to inconsistencies in the user experience.

## Goals
1. Implement a unified file browser interface that works consistently across all storage providers
2. Ensure consistent navigation across storage providers
3. Provide unified search and filtering capabilities that work with all storage providers
4. Improve the overall user experience when working with files from different sources

## Roadmap Components

### Phase 1: Core Navigation Consistency

#### Consistent Navigation Implementation
- ✓ Update `_navigate_to` method to use core implementation for provider-agnostic navigation
- ✓ Update `_go_up` method to use core implementation for consistent parent directory navigation
- ✓ Update `_go_back` method to use core implementation for consistent history navigation
- ✓ Ensure navigation works consistently across all storage providers (local_fs, dropbox, sharepoint, onedrive, gdrive)

#### Unified Search and Filtering
- ✓ Update `render_file_browser` method to use core implementation's `get_page_data` method
- ✓ Enhance filename filtering to work consistently across all storage providers
- ✓ Improve metadata filtering to work with all storage providers
- ✓ Update `_apply_filename_filter` and `_apply_metadata_filters` methods to be consistent with the new implementation
- ✓ Display metadata facets for improved filtering capabilities

### Phase 2: Enhanced UI Components (Planned)

#### Improved File Preview
- ⟳ Enhance file preview capabilities for cloud storage files
- ⟳ Implement streaming preview for large files
- ⟳ Add support for previewing specialized file formats from cloud storage

#### Drag and Drop Support
- ⟳ Implement drag and drop file upload for all storage providers
- ⟳ Support drag and drop between different storage providers
- ⟳ Add progress indicators for file transfers

#### Batch Operations
- ⟳ Implement batch selection of files
- ⟳ Support batch operations (copy, move, delete) across storage providers
- ⟳ Add confirmation dialogs for destructive operations

### Phase 3: Advanced Integration (Planned)

#### Unified Permissions Management
- ⟳ Display file permissions consistently across storage providers
- ⟳ Implement permission editing where supported
- ⟳ Show sharing status and options for cloud storage files

#### Synchronization Features
- ⟳ Implement file synchronization between storage providers
- ⟳ Add conflict resolution for synchronization
- ⟳ Provide synchronization status indicators

#### Search Enhancements
- ⟳ Implement global search across all storage providers
- ⟳ Add advanced search options (date ranges, file types, etc.)
- ⟳ Support saved searches across providers

## Implementation Plan

### Timeline
- **Phase 1: Core Navigation Consistency** - Completed
- **Phase 2: Enhanced UI Components** - 2-3 weeks
- **Phase 3: Advanced Integration** - 4-6 weeks

### Dependencies
- Core file browser implementation in `science_data_kit/core/pages/file_browser.py`
- Storage provider implementations for different cloud services
- UI components for file preview and metadata display

## Current Status
Phase 1 (Core Navigation Consistency) has been completed with the implementation of consistent navigation across storage providers and unified search and filtering capabilities. The UI implementation now leverages the provider-agnostic capabilities of the core implementation, ensuring a consistent user experience regardless of the storage provider being used.

Specific improvements include:
1. Updated navigation methods to use the core implementation for consistent behavior
2. Enhanced file browser rendering to use the core implementation's `get_page_data` method
3. Improved search and filtering to work consistently across all storage providers
4. Added display of metadata facets for better filtering capabilities

## Next Steps
1. Begin implementation of Phase 2 (Enhanced UI Components)
2. Enhance file preview capabilities for cloud storage files
3. Implement drag and drop support for file uploads
4. Add batch operations for working with multiple files

## Success Metrics
1. **Consistency**: Users can navigate, search, and filter files consistently across all storage providers
2. **Usability**: Reduced learning curve when switching between different storage providers
3. **Efficiency**: Improved workflow efficiency when working with files from multiple sources
4. **Satisfaction**: Positive user feedback on the unified file browser interface

## Conclusion
The UI Integration roadmap focuses on providing a unified file browser interface that works consistently across all storage providers. Phase 1 has been completed, establishing the foundation for consistent navigation, search, and filtering. The next phases will build on this foundation to provide enhanced UI components and advanced integration features, further improving the user experience when working with files from different sources.
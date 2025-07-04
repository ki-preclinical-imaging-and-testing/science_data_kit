# Science Data Kit (SDK) Data Source Integration Roadmap - Version 05

## Overview

This document outlines the roadmap for implementing and integrating multiple data sources for the Science Data Kit. These integrations follow a common provider architecture pattern, allowing users to access and analyze data from Microsoft 365 (MS Graph API), Dropbox, Google Sheets, and local files directly within the SDK.

This integration aligns with the Phase 2 goal of "Expanded Integration Capabilities" by adding support for additional data sources, specifically addressing the tasks related to implementing file system integration (Dropbox), adding support for RESTful APIs (Google Sheets), and ensuring all data sources work together in a unified way.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 05 | 2023-08-01 | Updated with integrated MS Graph provider and unified data source access |
| 04 | 2023-07-31 | Updated with completed integration tests and documentation |
| 03 | 2023-07-30 | Updated with completed unified data source selector and provider registry integration |
| 02 | 2023-07-29 | Updated with completed Google Sheets integration |
| 01 | 2023-07-22 | Updated with completed provider architecture and Dropbox integration |
| 00 | 2023-07-15 | Initial roadmap for Google Sheets and Dropbox integration |

## Completed Tasks

### 1. Provider Architecture Setup

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create provider registry pattern | High | Completed | Implemented BaseProvider abstract class and registry mechanism in science_data_kit/core/providers/registry.py |
| Create configuration structure for providers | High | Completed | Implemented in science_data_kit/core/config/providers.py with environment variable loading |
| Define provider capabilities interface | Medium | Completed | Standardized capabilities reporting through get_capabilities() method in BaseProvider |

### 2. Dropbox Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create DropboxProvider class | High | Completed | Implemented in science_data_kit/core/providers/storage/dropbox_provider.py |
| Create Dropbox UI component | High | Completed | Implemented in science_data_kit/ui/components/dropbox_selector.py |
| Implement Dropbox authentication | High | Completed | Added support for access token authentication |
| Implement file listing and filtering | Medium | Completed | Added support for CSV/Excel file discovery with filtering |
| Implement file download and parsing | Medium | Completed | Implemented conversion of files to pandas DataFrames |
| Create unit tests for Dropbox provider | Medium | Completed | Implemented in tests/unit/core/providers/test_dropbox_provider.py |

### 3. Google Sheets Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create GoogleSheetsProvider class | High | Completed | Implemented in science_data_kit/core/providers/storage/google_sheets_provider.py |
| Create Google Sheets UI component | High | Completed | Implemented in science_data_kit/ui/components/google_sheets_selector.py |
| Implement OAuth2 authentication | High | Completed | Support Google OAuth2 flow with credentials file and token storage |
| Implement spreadsheet discovery | Medium | Completed | Allow browsing available spreadsheets using Drive API |
| Implement sheet data retrieval | Medium | Completed | Convert sheets to pandas DataFrames with proper column headers |
| Create unit tests for Google Sheets provider | Medium | Completed | Implemented in tests/unit/core/providers/test_google_sheets_provider.py |

### 4. MS Graph Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create MSGraphProvider class | High | Completed | Implemented in science_data_kit/core/providers/api/msgraph_provider.py |
| Create MS Graph UI component | High | Completed | Implemented in science_data_kit/ui/components/msgraph_selector.py |
| Adapt MS Graph manager to provider interface | Medium | Completed | Created adapter that works with existing MSGraphConnectionManager |
| Implement file and spreadsheet access | Medium | Completed | Added support for accessing OneDrive files and Excel spreadsheets |
| Implement entity data access | Medium | Completed | Added support for accessing users, groups, messages, and events |

### 5. Dependencies

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add Dropbox SDK dependency | High | Completed | Added dropbox==11.36.2 to requirements.txt |
| Add Google Sheets API dependencies | High | Completed | Added google-api-python-client, google-auth-httplib2, and google-auth-oauthlib to requirements.txt |
| Add MS Graph API dependencies | High | Completed | Added msgraph-sdk-python and azure-identity to requirements.txt |

### 6. Integration

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create unified data source selector | Medium | Completed | Implemented in science_data_kit/ui/components/data_source_selector.py |
| Update provider registry with all providers | Medium | Completed | Registered Dropbox, Google Sheets, and MS Graph providers in science_data_kit/core/providers/__init__.py |
| Create integration tests | Low | Completed | Implemented in tests/integration/test_data_source_selector.py, tests/integration/test_dropbox_integration.py, and tests/integration/test_google_sheets_integration.py |
| Update documentation | Low | Completed | Added user guides for Dropbox and Google Sheets integrations in docs/user_guides/ |

## Current Status

The Science Data Kit now has a robust provider architecture that allows for the integration of multiple data sources. The provider registry pattern has been implemented, with a BaseProvider abstract class that defines the common interface for all providers.

All three major data sources (Microsoft Graph, Dropbox, and Google Sheets) have been fully implemented and integrated into a unified data source selector. This allows users to:

1. Access file subsystems across all platforms:
   - Browse and navigate OneDrive files through MS Graph
   - Browse and navigate Dropbox folders
   - Browse and navigate Google Sheets spreadsheets

2. Access individual files and their data:
   - View and select Excel files and sheets in OneDrive
   - View and filter CSV and Excel files in Dropbox
   - View and select sheets in Google Sheets spreadsheets
   - Preview file/sheet contents before importing
   - Import data as pandas DataFrames for analysis

The unified data source selector provides a tabbed interface that allows users to easily switch between different data sources. The selector returns a standardized data structure with source information, data, and metadata, ensuring a consistent experience regardless of the data source.

The provider registry has been updated to include all providers, making them available throughout the application. This architecture allows for easy addition of new data sources in the future.

Integration tests have been created to verify the correct functioning of the data source selector and individual integrations. These tests ensure that the components work correctly together and handle user interactions appropriately.

Comprehensive documentation has been added, including setup guides for the integrations. These guides provide step-by-step instructions for setting up and using the integrations.

The implementation includes proper error handling, authentication management, and user-friendly UI components for selecting and previewing data from all sources.

## Next Steps

### 1. Future Enhancements

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Add support for local file system | Medium | To Do | Allow users to access files from their local machine |
| Add support for more file types | Low | To Do | Support for JSON, XML, and other data formats |
| Implement write-back functionality | Low | To Do | Allow users to save modified data back to the source |
| Add support for Google Drive files | Low | To Do | Extend Google integration to include files from Google Drive |
| Implement caching for improved performance | Low | To Do | Cache frequently accessed data to reduce API calls |

## Implementation Plan

### Phase 1: Provider Architecture (Week 1) - COMPLETED

1. Create provider registry pattern ✓
   - Define BaseProvider abstract class ✓
   - Implement provider registry mechanism ✓
   - Create provider type enumeration ✓

2. Set up configuration structure ✓
   - Create config directory and providers.py ✓
   - Implement environment variable loading ✓
   - Define provider configuration schema ✓

### Phase 2: Dropbox Integration (Weeks 2-3) - COMPLETED

1. Implement DropboxProvider class ✓
   - Create basic provider structure ✓
   - Implement authentication ✓
   - Implement file listing and filtering ✓
   - Implement file download and parsing ✓

2. Create Dropbox UI component ✓
   - Implement file browser interface ✓
   - Add authentication setup UI ✓
   - Create file preview functionality ✓

3. Write tests for Dropbox integration ✓
   - Create unit tests with mocked API responses ✓
   - Test error handling and edge cases ✓

### Phase 3: Google Sheets Integration (Weeks 4-5) - COMPLETED

1. Implement GoogleSheetsProvider class ✓
   - Create basic provider structure ✓
   - Implement OAuth2 authentication flow ✓
   - Implement spreadsheet discovery ✓
   - Implement sheet data retrieval ✓

2. Create Google Sheets UI component ✓
   - Implement spreadsheet browser interface ✓
   - Add authentication setup UI ✓
   - Create sheet preview functionality ✓

3. Write tests for Google Sheets integration ✓
   - Create unit tests with mocked API responses ✓
   - Test error handling and edge cases ✓

### Phase 4: Integration and Finalization (Week 6) - COMPLETED

1. Create unified data source selector ✓
   - Implement provider selection UI ✓
   - Integrate with existing data workflows ✓

2. Complete integration ✓
   - Register providers in the registry ✓
   - Create integration tests ✓
   - Update documentation ✓

3. Final testing and polish ✓
   - End-to-end testing ✓
   - Performance optimization ✓
   - User experience refinement ✓

### Phase 5: MS Graph Integration (Week 7) - COMPLETED

1. Implement MSGraphProvider class ✓
   - Create provider adapter for MSGraphConnectionManager ✓
   - Implement file and spreadsheet access methods ✓
   - Implement entity data access methods ✓

2. Create MS Graph UI component ✓
   - Implement data type selection UI ✓
   - Implement file and spreadsheet browser ✓
   - Implement entity selection UI ✓

3. Update unified data source selector ✓
   - Add MS Graph tab to selector ✓
   - Ensure consistent data format across sources ✓

## Conclusion

The Data Source Integration roadmap has been successfully completed, with all planned tasks implemented and tested. The Science Data Kit now has a robust provider architecture that supports multiple data sources, including Microsoft Graph, Dropbox, and Google Sheets, all integrated into a unified data source selector.

The implementation follows best practices for code organization, error handling, and user experience, ensuring that the Science Data Kit remains a robust and user-friendly tool for scientific data analysis.

Future enhancements could include support for local file system, additional file types, write-back functionality, integration with Google Drive files, and performance optimizations through caching. These enhancements would further improve the flexibility and usability of the data source integrations.
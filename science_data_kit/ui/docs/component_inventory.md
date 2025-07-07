# Science Data Kit UI Component Inventory

This document provides a comprehensive inventory of all UI components used in the Science Data Kit application. The components are organized by type and include a brief description of each component.

## Core Layout Components

### Pages
- **Dashboard Page**: Main landing page with overview of the application
- **Server Page**: Connection management for database servers
- **Survey Page**: Data collection and survey management
- **Map Page**: Geospatial data visualization
- **Explore Page**: Data exploration and visualization
- **Ontology Page**: Knowledge graph and ontology management
- **Chat Page**: Conversational interface for data interaction
- **Files Page**: File browser and management
- **About Page**: Documentation and learning resources
- **Preferences Page**: User preferences and settings

### Navigation Components
- **Sidebar**: Main navigation sidebar with expandable sections
- **Page Navigation**: Top-level navigation between pages
- **Breadcrumbs**: Path-based navigation within pages
- **Tabs**: Content organization within pages
- **Expanders**: Collapsible sections for content organization

## Input Components

### Text Input Components
- **Text Input**: Single-line text input field
- **Text Area**: Multi-line text input field
- **Number Input**: Numeric input field with increment/decrement controls
- **Password Input**: Masked text input for sensitive information

### Selection Components
- **Selectbox**: Dropdown selection from a list of options
- **Radio Button**: Single selection from a list of options
- **Checkbox**: Boolean selection (on/off)
- **Multiselect**: Multiple selection from a list of options
- **Slider**: Range selection with visual slider

### Date and Time Components
- **Date Input**: Date selection with calendar picker
- **Time Input**: Time selection with time picker
- **Date Range**: Selection of a range of dates

### File Components
- **File Uploader**: Upload files to the application
- **File Browser**: Browse and select files from connected sources

## Form Components
- **Form**: Container for input components with submit functionality
- **Form Submit Button**: Button to submit form data
- **Form Reset Button**: Button to reset form data

## Display Components

### Text Display Components
- **Text**: Plain text display
- **Markdown**: Formatted text with Markdown syntax
- **Header**: Section header with hierarchical levels (h1, h2, h3)
- **Subheader**: Secondary header for subsections
- **Caption**: Small text for captions and annotations

### Data Display Components
- **Table**: Tabular data display with sorting and filtering
- **DataFrame**: Interactive data table with pandas DataFrame functionality
- **JSON Viewer**: Formatted display of JSON data
- **Code Block**: Syntax-highlighted code display
- **Metric**: Key performance indicator with label and value

### Visualization Components
- **Chart**: Various chart types (bar, line, scatter, etc.)
- **Graph**: Network graph visualization
- **Map**: Geographic map visualization
- **Image**: Image display with optional captions
- **Video**: Video player with controls

### Status Components
- **Progress Bar**: Visual indicator of progress
- **Spinner**: Loading indicator
- **Status Indicator**: Visual indicator of status (success, warning, error)
- **Alert**: Notification message with severity levels

## Interactive Components

### Action Components
- **Button**: Clickable button for actions
- **Link**: Hyperlink to internal or external resources
- **Download Button**: Button to download files

### Dialog Components
- **Modal**: Popup dialog for focused interaction
- **Toast**: Temporary notification message
- **Tooltip**: Contextual help or information on hover

### Container Components
- **Container**: Generic container for content
- **Column**: Vertical layout container
- **Row**: Horizontal layout container
- **Card**: Styled container with header, body, and footer
- **Sidebar**: Side panel for navigation and controls

## Integration Components

### Database Components
- **Neo4j Connection**: Connection to Neo4j graph database
- **PostgreSQL Connection**: Connection to PostgreSQL database
- **Database Query Editor**: SQL/Cypher query editor and executor
- **Query Results Viewer**: Display of query results

### File System Components
- **Local File System Connector**: Connection to local file system
- **Sharepoint Connector**: Connection to Microsoft Sharepoint
- **Dropbox Connector**: Connection to Dropbox
- **Google Drive Connector**: Connection to Google Drive

### External API Components
- **Microsoft Graph API Connector**: Connection to Microsoft Graph API
- **Ollama Connector**: Connection to Ollama API for LLM integration

## Responsive Design Components
- **Responsive Layout**: Layout adaptation based on screen size
- **Mobile Navigation**: Mobile-friendly navigation menu
- **Responsive Images**: Images that adapt to container size
- **Media Queries**: CSS media queries for responsive design

## Accessibility Components
- **Keyboard Navigation**: Support for keyboard navigation
- **Screen Reader Support**: ARIA attributes for screen readers
- **High Contrast Mode**: Visual mode for improved contrast
- **Focus Indicators**: Visual indicators for keyboard focus

## Testing and Validation
This inventory will be used as the basis for comprehensive testing of all UI components in the Science Data Kit application. Each component will be tested for:

1. **Functionality**: Does the component work as expected?
2. **Appearance**: Does the component look as expected?
3. **Responsiveness**: Does the component adapt to different screen sizes?
4. **Accessibility**: Is the component accessible to all users?
5. **Integration**: Does the component integrate properly with other components?
6. **Performance**: Does the component perform efficiently?

## Next Steps
The next steps in the UI component validation process are:
1. Develop testing checklists for each component type
2. Create AI-generated test scenarios for comprehensive testing
3. Execute tests and document results
4. Address any issues identified during testing
5. Update documentation with testing results and best practices
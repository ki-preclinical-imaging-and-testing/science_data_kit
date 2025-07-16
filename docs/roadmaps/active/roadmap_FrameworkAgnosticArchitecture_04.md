# Science Data Kit (SDK) Framework-Agnostic Architecture Roadmap - Version 04

## Overview
This roadmap outlines a comprehensive plan for evolving the current render function pattern into a framework-agnostic architecture. This will allow the app to support multiple frontends (Streamlit, Flask, React) without duplicating business logic.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-07-20 | Initial version of Framework-Agnostic Architecture roadmap |
| 01 | 2025-07-23 | Completed Phase 1 (Core Extraction) tasks, implemented core page classes and Streamlit adapter |
| 02 | 2025-07-26 | Completed Phase 2 (Streamlit Adapter Layer) tasks, implemented core page classes for file_browser, connect, and explore pages, added comprehensive tests and documentation |
| 03 | 2025-07-30 | Completed Phase 3 (Flask API Development) tasks, implemented Flask application structure, REST API endpoints, Flask adapter layer, authentication/session management, and basic Jinja2 templates |
| 04 | 2025-08-03 | Completed initial Phase 4 (Enhanced UI Components) tasks, implemented HTMX and Alpine.js for dynamic updates and client-side interactivity, enhanced file browser component with drag-and-drop upload, file operations, rich preview capabilities, and improved multi-select functionality |

## Background
The Science Data Kit currently uses render functions (`render_dashboard_page()`, etc.) in a Streamlit-specific way. While there's already good separation between UI components and backend services, the existing pattern can be evolved rather than completely replaced to support multiple frontend frameworks. Features like file browser and remote connection would benefit from richer UI capabilities that could be provided by alternative frameworks.

## Goals
1. Create a framework-agnostic core with pluggable UI layers
2. Support multiple frontend frameworks (Streamlit, Flask+HTMX, React)
3. Maintain "Python-first" philosophy while enabling rich UI experiences
4. Allow gradual migration without disrupting existing functionality
5. Improve user experience for complex UI components

## Current Status
The Framework-Agnostic Architecture implementation has progressed significantly with the completion of Phase 1 (Core Extraction), Phase 2 (Streamlit Adapter Layer), Phase 3 (Flask API Development), and initial tasks from Phase 4 (Enhanced UI Components). The following tasks have been completed:

### Phase 1 (Core Extraction) - ✅ COMPLETED
1. Created the core/pages/ directory structure
2. Defined base page data models in core/models/page.py
3. Created framework-independent page classes in core/pages/
4. Extracted business logic from existing render functions
5. Implemented unit tests for core page classes
6. Created Streamlit adapter for core page classes
7. Updated dashboard.py to use the new adapter

### Phase 2 (Streamlit Adapter Layer) - ✅ COMPLETED
1. Created ui/adapters/ directory
2. Implemented Streamlit-specific adapter classes
3. Moved all Streamlit-specific code to adapter layer
4. Updated all existing render functions to use adapters
5. Ensured all pages work through new architecture
6. Added comprehensive tests for adapter layer
7. Documented adapter pattern for future frameworks

### Phase 3 (Flask API Development) - ✅ COMPLETED
1. Set up Flask application structure in `web/`
2. Implemented REST API endpoints for each page
3. Created Flask adapter layer for core pages
4. Added authentication/session management
5. Implemented basic Jinja2 templates for testing
6. Created API documentation
7. Implemented comprehensive API tests
8. Ensured feature parity with Streamlit UI

### Phase 4 (Enhanced UI Components) - ⏳ IN PROGRESS
1. ✅ Added HTMX for dynamic updates without full page reloads
2. ✅ Implemented Alpine.js for client-side interactivity
3. ✅ Created enhanced file browser component with:
   - ✅ Drag-and-drop file upload functionality
   - ✅ File operations (create folder, rename, delete)
   - ✅ Rich preview capabilities for various file types
   - ✅ Multi-select with keyboard shortcuts
4. ⏳ Improving connection management UI
5. ⏳ Adding real-time updates for dashboards
6. ⏳ Creating responsive design components
7. ⏳ Implementing comprehensive UI tests
8. ⏳ Documenting component architecture

The implementation maintains backward compatibility with the current Streamlit UI while providing a framework-independent core that can be used with other UI frameworks. The Flask implementation provides a web interface and REST API for the core functionality, now enhanced with HTMX and Alpine.js for a more dynamic and interactive user experience.

The roadmap is divided into five phases:

1. **Phase 1: Core Extraction** - ✅ COMPLETED
   - Extract page logic from render functions into framework-independent core classes
   - Define base page data models
   - Maintain backward compatibility with current Streamlit UI
2. **Phase 2: Streamlit Adapter Layer** - ✅ COMPLETED
   - Convert current render functions to thin Streamlit adapters
   - Move all Streamlit-specific code to adapter layer
   - Ensure all pages work through new architecture
3. **Phase 3: Flask API Development** - ✅ COMPLETED
   - Create Flask application structure
   - Implement REST API endpoints for each page
   - Add authentication/session management
   - Create simple Jinja2 templates for testing
4. **Phase 4: Enhanced UI Components** - ⏳ IN PROGRESS
   - ✅ Implement HTMX for dynamic updates
   - ✅ Add Alpine.js for client-side interactivity
   - ✅ Focus on file browser and connection management
   - ⏳ Create rich preview capabilities
   - ⏳ Add real-time updates for dashboards
5. **Phase 5: React Exploration** - ⏳ PLANNED
   - Evaluate need for full SPA
   - Prototype key components
   - Consider hybrid approach

## Implementation Details

### Architecture Overview

```
science_data_kit/
├── core/                    # Framework-independent layer
│   ├── services/           # Business logic (existing)
│   ├── pages/             # Page orchestration (new) ✅
│   └── models/            # Shared data structures (extended) ✅
├── ui/                    # Streamlit implementation
│   ├── adapters/          # Streamlit adapter layer (new) ✅
│   └── pages/             # Streamlit pages (updated) ✅
├── web/                   # Flask implementation (new) ✅
│   ├── adapters/          # Flask adapter layer (new) ✅
│   ├── api/               # REST API endpoints (new) ✅
│   ├── templates/         # Jinja2 templates (new) ✅
│   │   └── partials/      # Partial templates for HTMX (new) ✅
│   └── static/            # Static files (CSS, JS) (new) ✅
└── frontend/              # Future React implementation (planned)
```

The architecture separates the application into distinct layers:

1. **Core Layer**: Contains all business logic, data models, and page orchestration that is independent of any UI framework
2. **UI Adapters**: Framework-specific implementations that translate core data structures into UI components
3. **Framework-Specific UI Components**: Specialized components that leverage the unique capabilities of each framework

### Phase 4: Enhanced UI Components (4-6 weeks) - ⏳ IN PROGRESS

**Objective**: Implement rich UI components using HTMX and Alpine.js

**Tasks**:
- ✅ Add HTMX for dynamic updates without full page reloads
- ✅ Implement Alpine.js for client-side interactivity
- ✅ Create enhanced file browser component
- ⏳ Improve connection management UI
- ✅ Implement rich preview capabilities for various file types
- ⏳ Add real-time updates for dashboards
- ⏳ Create responsive design components
- ⏳ Implement comprehensive UI tests
- ⏳ Document component architecture

**Implementation Details**:

1. **HTMX Integration**:
   - Added HTMX library to base.html template
   - Created partial templates for dynamic content updates
   - Implemented HTMX endpoints in routes.py for file navigation, filtering, and previews
   - Added loading indicators for better user experience

2. **Alpine.js Integration**:
   - Added Alpine.js library to base.html template
   - Created Alpine.js components for client-side state management
   - Implemented reactive UI elements that respond to state changes
   - Used Alpine.js for file selection and toolbar button states

3. **Enhanced File Browser**:
   - Implemented dynamic directory navigation without page reloads
   - Added file filtering with instant results
   - Created modal-based file preview system for different file types
   - Improved UI with loading indicators and responsive design

4. **File Preview System**:
   - Created specialized preview templates for different file types:
     - Text files with syntax highlighting
     - Images with responsive sizing
     - Binary files with appropriate messaging
   - Implemented file download functionality
   - Added modal-based preview system for better user experience

**Focus Areas**:
- File Browser with drag-and-drop, multi-select, and preview
- Connection Management with OAuth flows and status monitoring
- Data Preview with interactive tables and filtering
- Real-time Dashboard Updates

### Phase 5: React Exploration (Future) - ⏳ PLANNED

**Objective**: Evaluate and prototype React-based UI components

**Tasks**:
- Evaluate need for full SPA implementation
- Create React adapter layer
- Prototype key components (file browser, data visualization)
- Consider hybrid approach with Flask backend
- Benchmark performance against other implementations
- Document React integration patterns

### Technical Implementation Details

#### HTMX and Alpine.js Integration

The integration of HTMX and Alpine.js provides a powerful combination for creating dynamic, interactive web interfaces without the complexity of a full SPA framework:

```html
<!-- HTMX for dynamic updates -->
<div hx-get="/api/files/navigate?path={{ directory.path }}" 
     hx-target="#file-listing-container"
     hx-indicator=".htmx-indicator"
     hx-push-url="?path={{ directory.path }}">
    <!-- Content -->
</div>

<!-- Alpine.js for client-side interactivity -->
<div x-data="{ selected: false }"
     x-bind:class="{ 'selected': selected }"
     @click="selected = !selected; updateButtonStates()">
    <!-- Content -->
</div>
```

#### File Preview System

The file preview system uses a modal-based approach with specialized templates for different file types:

```python
@main_bp.route('/api/files/preview')
@login_required
def preview_file():
    """HTMX endpoint for previewing a file."""
    file_path = request.args.get('path', '')
    file_type = os.path.splitext(file_path)[1].lower()

    # Handle different file types
    text_file_extensions = [
        '.txt', '.md', '.csv', '.json', '.yaml', '.yml', 
        '.py', '.js', '.html', '.css', '.java', '.c', '.cpp', 
        '.cs', '.go', '.php', '.rb', '.rs', '.ts', '.sh', 
        '.xml', '.log', '.ini', '.conf', '.toml', '.sql'
    ]

    image_file_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.svg', '.webp', '.ico', '.tiff', '.tif'
    ]

    pdf_file_extensions = ['.pdf']

    if file_type in text_file_extensions:
        # Text files with syntax highlighting
        try:
            content = content.decode('utf-8')
            return render_template('partials/preview_text.html', content=content, file_path=file_path)
        except UnicodeDecodeError:
            return render_template('partials/preview_binary.html', file_path=file_path)
    elif file_type in image_file_extensions:
        # Image files
        return render_template('partials/preview_image.html', file_path=file_path)
    elif file_type in pdf_file_extensions:
        # PDF files
        return render_template('partials/preview_pdf.html', file_path=file_path)
    else:
        # Binary files
        return render_template('partials/preview_binary.html', file_path=file_path)
```

```html
<!-- Text file preview with syntax highlighting -->
{% set file_ext = file_path.split('.')[-1].lower() %}
{% if file_ext in ['py', 'js', 'html', 'css', 'java', 'c', 'cpp', 'cs', 'go', 'php', 'rb', 'rs', 'ts', 'sh', 'json', 'xml', 'yaml', 'yml'] %}
    <pre><code class="language-{{ file_ext }}">{{ content }}</code></pre>
{% else %}
    <pre class="preview-text">{{ content }}</pre>
{% endif %}

<!-- PDF file preview -->
<embed src="/api/files/raw?path={{ file_path }}" type="application/pdf" width="100%" height="600px">
```

### Priority Features for Multi-Framework Support

The following features will be prioritized for multi-framework support due to their need for rich UI capabilities:

1. **File Browser**
   - Current limitations: Basic file listing, limited preview capabilities
   - Enhanced capabilities: ✅ Dynamic navigation, ✅ rich previews, ✅ drag-and-drop, ✅ multi-select, ✅ file operations, ⏳ search

2. **Remote Connections**
   - Current limitations: Basic form-based connection setup
   - Enhanced capabilities: ⏳ OAuth flows, ⏳ status monitoring, ⏳ visual management

3. **Data Preview**
   - Current limitations: Basic table view, limited interactivity
   - Enhanced capabilities: ⏳ Interactive tables, ⏳ pagination, ⏳ column customization

4. **Real-time Updates**
   - Current limitations: Manual refresh required
   - Enhanced capabilities: ⏳ WebSocket updates, ⏳ progress indicators, ⏳ notifications

### Success Metrics

The success of the framework-agnostic architecture will be measured by:

1. **Zero regression in Streamlit functionality**
   - All existing features continue to work without issues
   - No degradation in performance or user experience

2. **API response times < 200ms**
   - Core API endpoints respond within 200ms for typical operations
   - Complex operations may take longer but provide progress feedback

3. **90% code reuse between frameworks**
   - Business logic is fully reused
   - Data models are fully reused
   - Only UI rendering code is framework-specific

4. **Improved UX metrics**
   - Reduced time to complete common tasks
   - Improved user satisfaction scores
   - Reduced error rates in complex workflows

### Risk Mitigation

1. **Performance degradation**
   - Mitigation: Benchmark core functions before and after refactoring
   - Mitigation: Implement caching at appropriate layers

2. **Feature regression**
   - Mitigation: Comprehensive test suite for all features
   - Mitigation: Phased rollout with feature flags
   - Mitigation: Maintain Streamlit as primary during transition

3. **Increased complexity**
   - Mitigation: Clear documentation of architecture patterns
   - Mitigation: Code reviews focused on architectural compliance
   - Mitigation: Regular refactoring to eliminate duplication

### Resource Requirements

- **Phase 1**: 1 senior developer, 2-3 weeks ✅ COMPLETED
- **Phase 2**: 1 senior developer, 1 week ✅ COMPLETED
- **Phase 3**: 1 senior developer + 1 junior developer, 3-4 weeks ✅ COMPLETED
- **Phase 4**: 1 senior developer + 1 frontend specialist, 4-6 weeks ⏳ IN PROGRESS
- **Phase 5**: 1 senior developer + 1 React specialist, TBD

### Key Decisions

#### Why keep render functions?

The render functions will be maintained but transformed into thin adapters that bridge between the core page classes and the UI frameworks. This approach:

- Enables gradual migration without breaking existing code
- Provides a clear boundary between business logic and UI rendering
- Creates a consistent pattern for all UI frameworks
- Makes testing easier by separating concerns

#### Why Flask + HTMX over pure React?

Flask with HTMX and Alpine.js was chosen as the primary web implementation for several reasons:

- **Python-first approach**: Maintains our commitment to Python as the primary language
- **Lower complexity**: Simpler development model without a complex build system
- **Progressive enhancement**: Can start with basic HTML and add interactivity incrementally
- **Server-rendered foundation**: Better initial load performance and SEO capabilities
- **No build toolchain**: Simpler development workflow without transpilation
- **Easier integration**: More straightforward integration with existing Python codebase

#### Which pages to migrate first?

The migration will follow this sequence:

1. **Simple pages first**: About, Preferences, and other static pages
2. **File Browser**: As a proof of concept for rich UI capabilities ✅ COMPLETED
3. **Dashboard**: To demonstrate real-time updates
4. **Data visualization pages**: To leverage enhanced interactive capabilities
5. **Complex workflow pages**: After patterns are well-established

## Next Steps

1. Continue Phase 4 (Enhanced UI Components):
   - Improve connection management UI with HTMX and Alpine.js
   - Add real-time updates for dashboards using WebSockets
   - Create responsive design components for mobile and tablet views
   - Implement comprehensive UI tests for the enhanced components
   - Document component architecture and best practices

2. Refine the architecture based on lessons learned:
   - Identify any performance bottlenecks in the HTMX/Alpine.js implementation
   - Improve the partial template pattern for better reusability
   - Document best practices for creating new HTMX endpoints

3. New tasks identified during Phase 4:
   - Implement WebSocket support for real-time updates
   - Create a unified state management system that works across frameworks
   - Develop a strategy for handling client-side state in multi-framework environments
   - Add search functionality to the file browser
   - Create a unified notification system for user feedback
   - Implement file compression/extraction functionality
   - Add file sharing and collaboration features
   - Implement keyboard shortcuts for common operations
   - Add accessibility improvements for screen readers and keyboard navigation

## Approval

- [x] Architecture review completed
- [x] Resource allocation approved
- [x] Timeline approved
- [x] Success metrics approved

## Reviewers

- [x] Lead Developer
- [x] UX Designer
- [x] Project Manager

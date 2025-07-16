# Science Data Kit (SDK) Framework-Agnostic Architecture Roadmap - Version 02

## Overview
This roadmap outlines a comprehensive plan for evolving the current render function pattern into a framework-agnostic architecture. This will allow the app to support multiple frontends (Streamlit, Flask, React) without duplicating business logic.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-07-20 | Initial version of Framework-Agnostic Architecture roadmap |
| 01 | 2025-07-23 | Completed Phase 1 (Core Extraction) tasks, implemented core page classes and Streamlit adapter |
| 02 | 2025-07-25 | Completed Phase 2 (Streamlit Adapter Layer) tasks, implemented core page classes for file_browser, connect, and explore pages |

## Background
The Science Data Kit currently uses render functions (`render_dashboard_page()`, etc.) in a Streamlit-specific way. While there's already good separation between UI components and backend services, the existing pattern can be evolved rather than completely replaced to support multiple frontend frameworks. Features like file browser and remote connection would benefit from richer UI capabilities that could be provided by alternative frameworks.

## Goals
1. Create a framework-agnostic core with pluggable UI layers
2. Support multiple frontend frameworks (Streamlit, Flask+HTMX, React)
3. Maintain "Python-first" philosophy while enabling rich UI experiences
4. Allow gradual migration without disrupting existing functionality
5. Improve user experience for complex UI components

## Current Status
The Framework-Agnostic Architecture implementation has progressed significantly with the completion of Phase 2 (Streamlit Adapter Layer). The following tasks have been completed:

1. Created the core/pages/ directory structure
2. Defined base page data models in core/models/page.py
3. Created framework-independent page classes in core/pages/
4. Extracted business logic from existing render functions
5. Implemented unit tests for core page classes
6. Created Streamlit adapter for core page classes
7. Updated dashboard.py, file_browser.py, connect.py, and explore.py to use the new adapter

The implementation maintains backward compatibility with the current Streamlit UI while providing a framework-independent core that can be used with other UI frameworks.

The roadmap is divided into five phases:

1. **Phase 1: Core Extraction** - ✅ COMPLETED
   - Extract page logic from render functions into framework-independent core classes
   - Define base page data models
   - Maintain backward compatibility with current Streamlit UI
2. **Phase 2: Streamlit Adapter Layer** - ✅ COMPLETED
   - Convert current render functions to thin Streamlit adapters
   - Move all Streamlit-specific code to adapter layer
   - Ensure all pages work through new architecture
3. **Phase 3: Flask API Development** - ⏳ PLANNED
   - Create Flask application structure
   - Implement REST API endpoints for each page
   - Add authentication/session management
   - Create simple Jinja2 templates for testing
4. **Phase 4: Enhanced UI Components** - ⏳ PLANNED
   - Implement HTMX for dynamic updates
   - Add Alpine.js for client-side interactivity
   - Focus on file browser and connection management
   - Create rich preview capabilities
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
├── web/                   # Flask implementation (planned)
└── frontend/              # Future React implementation (planned)
```

The new architecture separates the application into distinct layers:

1. **Core Layer**: Contains all business logic, data models, and page orchestration that is independent of any UI framework
2. **UI Adapters**: Framework-specific implementations that translate core data structures into UI components
3. **Framework-Specific UI Components**: Specialized components that leverage the unique capabilities of each framework

### Phase 1: Core Extraction (2-3 weeks) - ✅ COMPLETED

**Objective**: Extract page logic from render functions into framework-independent core classes

**Tasks**:
- ✅ Create `core/pages/` directory structure
- ✅ Define base page data models in `core/models/`
- ✅ Extract business logic from existing render functions
- ✅ Create framework-independent page classes
- ✅ Implement unit tests for core page classes
- ✅ Maintain backward compatibility with current Streamlit UI
- ✅ No user-facing changes

**Implementation Details**:

1. **Page Data Models**:
   - Created `PageData` base class with title and requires_auth fields
   - Created specific page data classes (DashboardPageData, FileExplorerPageData, ConnectPageData, ExplorePageData)
   - Used dataclasses for clean, type-hinted data structures

2. **Core Page Classes**:
   - Created `BasePage` abstract class with get_page_data() method
   - Implemented `DashboardPage` with business logic extracted from the UI layer
   - Maintained separation of concerns between data and presentation

3. **Streamlit Adapter**:
   - Created adapter functions to render core page data using Streamlit components
   - Updated existing render functions to use the new adapter
   - Maintained backward compatibility with current UI

4. **Testing**:
   - Implemented unit tests for core page classes
   - Verified that the adapter correctly renders the page data

### Phase 2: Streamlit Adapter Layer (1 week) - ✅ COMPLETED

**Objective**: Convert current render functions to thin Streamlit adapters

**Tasks**:
- ✅ Create `ui/adapters/` directory
- ✅ Implement Streamlit-specific adapter classes
- ✅ Move all Streamlit-specific code to adapter layer
- ✅ Update existing render functions to use adapters
- ✅ Ensure all pages work through new architecture
- ✅ Add comprehensive tests for adapter layer
- ✅ Document adapter pattern for future frameworks

**Implementation Details**:
- Implemented adapters for Dashboard, File Browser, Connect, and Explore pages
- Created base adapter pattern for all pages
- Updated UI pages to use the adapters
- Maintained backward compatibility with current UI
- Added documentation for the adapter pattern

**Adapter Pattern Implementation**:
```python
# ui/adapters/streamlit_adapter.py
from typing import Type
import streamlit as st
from science_data_kit.core.pages.base import BasePage, PageData

def render_page(page_instance: BasePage) -> None:
    # Get the page data
    page_data = page_instance.get_page_data()
    
    # Render the page based on the type of page data
    if isinstance(page_data, DashboardPageData):
        _render_dashboard_page(page_data)
    elif isinstance(page_data, FileExplorerPageData):
        _render_file_explorer_page(page_data)
    elif isinstance(page_data, ConnectPageData):
        _render_connect_page(page_data)
    elif isinstance(page_data, ExplorePageData):
        _render_explore_page(page_data)
    else:
        # Generic rendering for other page types
        st.title(page_data.title)
        st.write("This page type doesn't have a specific renderer yet.")
```

### Phase 3: Flask API Development (3-4 weeks) - ⏳ PLANNED

**Objective**: Create a Flask-based web API and basic UI

**Tasks**:
- Set up Flask application structure in `web/`
- Implement REST API endpoints for each page
- Create Flask adapter layer for core pages
- Add authentication/session management
- Implement basic Jinja2 templates for testing
- Create API documentation
- Implement comprehensive API tests
- Ensure feature parity with Streamlit UI

**Example Flask Adapter**:
```python
# web/adapters/flask_adapter.py
from flask import render_template, jsonify
from science_data_kit.core.pages.base import BasePage

def render_page_html(page_instance: BasePage):
    data = page_instance.get_page_data()
    return render_template('page.html', page_data=data)

def render_page_api(page_instance: BasePage):
    data = page_instance.get_page_data()
    return jsonify(data)
```

### Phase 4: Enhanced UI Components (4-6 weeks) - ⏳ PLANNED

**Objective**: Implement rich UI components using HTMX and Alpine.js

**Tasks**:
- Add HTMX for dynamic updates without full page reloads
- Implement Alpine.js for client-side interactivity
- Create enhanced file browser component
- Improve connection management UI
- Implement rich preview capabilities for various file types
- Add real-time updates for dashboards
- Create responsive design components
- Implement comprehensive UI tests
- Document component architecture

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

#### Core Page Pattern

The core page pattern separates data and business logic from presentation:

```python
# core/models/page.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class PageData:
    """Base class for page data"""
    title: str
    requires_auth: bool = True

@dataclass
class DashboardPageData(PageData):
    """Dashboard page specific data"""
    metrics: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    status_items: List[Dict[str, Any]]
```

```python
# core/pages/base.py
from abc import ABC, abstractmethod
from science_data_kit.core.models.page import PageData

class BasePage(ABC):
    @abstractmethod
    def get_page_data(self) -> PageData:
        """Return data needed to render this page"""
        pass
```

```python
# core/pages/dashboard.py
from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import DashboardPageData
from science_data_kit.core.services.metrics import get_system_metrics

class DashboardPage(BasePage):
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        
    def get_page_data(self) -> DashboardPageData:
        """Return dashboard page data"""
        return DashboardPageData(
            title="Dashboard",
            requires_auth=True,
            metrics=self._get_metrics(),
            charts=self._get_charts(),
            tables=self._get_tables(),
            status_items=self._get_status_items()
        )
        
    def _get_metrics(self):
        # Business logic to get metrics
        return get_system_metrics(self.db_connection)
```

#### Adapter Pattern

The adapter pattern translates core page data into framework-specific UI components:

```python
# ui/adapters/streamlit_adapter.py
import streamlit as st
from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import DashboardPageData

def render_page(page_instance: BasePage) -> None:
    page_data = page_instance.get_page_data()
    
    if isinstance(page_data, DashboardPageData):
        _render_dashboard_page(page_data)
    else:
        st.title(page_data.title)
        st.write("This page type doesn't have a specific renderer yet.")

def _render_dashboard_page(page_data: DashboardPageData) -> None:
    st.title(page_data.title)
    
    # Render metrics
    for metric in page_data.metrics:
        st.metric(metric["title"], metric["value"], metric["trend"])
    
    # Render charts
    for chart in page_data.charts:
        # Render chart based on type
        pass
    
    # Render tables
    for table in page_data.tables:
        st.dataframe(table["data"])
    
    # Render status items
    for item in page_data.status_items:
        st.write(f"{item['name']}: {item['status']}")
```

### Priority Features for Multi-Framework Support

The following features will be prioritized for multi-framework support due to their need for rich UI capabilities:

1. **File Browser**
   - Current limitations: Basic file listing, limited preview capabilities
   - Enhanced capabilities: Drag-and-drop, multi-select, rich previews, search

2. **Remote Connections**
   - Current limitations: Basic form-based connection setup
   - Enhanced capabilities: OAuth flows, status monitoring, visual management

3. **Data Preview**
   - Current limitations: Basic table view, limited interactivity
   - Enhanced capabilities: Interactive tables, pagination, column customization

4. **Real-time Updates**
   - Current limitations: Manual refresh required
   - Enhanced capabilities: WebSocket updates, progress indicators, notifications

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
- **Phase 3**: 1 senior developer + 1 junior developer, 3-4 weeks
- **Phase 4**: 1 senior developer + 1 frontend specialist, 4-6 weeks
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
2. **File Browser**: As a proof of concept for rich UI capabilities
3. **Dashboard**: To demonstrate real-time updates
4. **Data visualization pages**: To leverage enhanced interactive capabilities
5. **Complex workflow pages**: After patterns are well-established

## Next Steps

1. Begin Phase 3 (Flask API Development):
   - Set up Flask application structure
   - Implement REST API endpoints for core pages
   - Create Flask adapter layer

2. Refine the architecture based on lessons learned:
   - Identify any performance bottlenecks
   - Improve the adapter pattern if needed
   - Document best practices for creating new pages

3. Add comprehensive tests for the adapter layer:
   - Unit tests for each adapter function
   - Integration tests for the adapter pattern
   - End-to-end tests for the UI

## Approval

- [x] Architecture review completed
- [x] Resource allocation approved
- [x] Timeline approved
- [x] Success metrics approved

## Reviewers

- [x] Lead Developer
- [x] UX Designer
- [x] Project Manager
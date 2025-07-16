# Science Data Kit (SDK) Framework-Agnostic Architecture Roadmap - Version 00

## Overview
This roadmap outlines a comprehensive plan for evolving the current render function pattern into a framework-agnostic architecture. This will allow the app to support multiple frontends (Streamlit, Flask, React) without duplicating business logic.

## Version History
| Version | Date | Changes |
|---------|------|---------|
| 00 | 2025-07-20 | Initial version of Framework-Agnostic Architecture roadmap |

## Background
The Science Data Kit currently uses render functions (`render_dashboard_page()`, etc.) in a Streamlit-specific way. While there's already good separation between UI components and backend services, the existing pattern can be evolved rather than completely replaced to support multiple frontend frameworks. Features like file browser and remote connection would benefit from richer UI capabilities that could be provided by alternative frameworks.

## Goals
1. Create a framework-agnostic core with pluggable UI layers
2. Support multiple frontend frameworks (Streamlit, Flask+HTMX, React)
3. Maintain "Python-first" philosophy while enabling rich UI experiences
4. Allow gradual migration without disrupting existing functionality
5. Improve user experience for complex UI components

## Current Status
The Framework-Agnostic Architecture roadmap has been defined but not started yet. The roadmap is divided into five phases:

1. **Phase 1: Core Extraction** - Extract page logic from render functions into framework-independent core classes, define base page data models, and maintain backward compatibility with current Streamlit UI.
2. **Phase 2: Streamlit Adapter Layer** - Convert current render functions to thin Streamlit adapters, move all Streamlit-specific code to adapter layer, and ensure all pages work through new architecture.
3. **Phase 3: Flask API Development** - Create Flask application structure, implement REST API endpoints for each page, add authentication/session management, and create simple Jinja2 templates for testing.
4. **Phase 4: Enhanced UI Components** - Implement HTMX for dynamic updates, add Alpine.js for client-side interactivity, focus on file browser and connection management, and create rich preview capabilities.
5. **Phase 5: React Exploration** - Evaluate need for full SPA, prototype key components, and consider hybrid approach.

## Implementation Details

### Architecture Overview

```
science_data_kit/
├── core/                    # Framework-independent layer
│   ├── services/           # Business logic (existing)
│   ├── pages/             # Page orchestration (new)
│   └── models/            # Shared data structures
├── ui/                    # Streamlit implementation
├── web/                   # Flask implementation
└── frontend/              # Future React implementation
```

The new architecture separates the application into distinct layers:

1. **Core Layer**: Contains all business logic, data models, and page orchestration that is independent of any UI framework
2. **UI Adapters**: Framework-specific implementations that translate core data structures into UI components
3. **Framework-Specific UI Components**: Specialized components that leverage the unique capabilities of each framework

### Phase 1: Core Extraction (2-3 weeks)

**Objective**: Extract page logic from render functions into framework-independent core classes

**Tasks**:
- Create `core/pages/` directory structure
- Define base page data models in `core/models/`
- Extract business logic from existing render functions
- Create framework-independent page classes
- Implement unit tests for core page classes
- Maintain backward compatibility with current Streamlit UI
- No user-facing changes

**Example Core Page Pattern**:
```python
# core/pages/base.py
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class PageData:
    """Base class for page data"""
    title: str
    requires_auth: bool = True

class BasePage(ABC):
    @abstractmethod
    def get_page_data(self) -> PageData:
        pass
```

### Phase 2: Streamlit Adapter Layer (1 week)

**Objective**: Convert current render functions to thin Streamlit adapters

**Tasks**:
- Create `ui/adapters/` directory
- Implement Streamlit-specific adapter classes
- Move all Streamlit-specific code to adapter layer
- Update existing render functions to use adapters
- Ensure all pages work through new architecture
- Add comprehensive tests for adapter layer
- Document adapter pattern for future frameworks

**Example Adapter Pattern**:
```python
# ui/adapters/streamlit_adapter.py
from typing import Type
import streamlit as st
from science_data_kit.core.pages.base import BasePage, PageData

def render_page(page_class: Type[BasePage]):
    page = page_class(st.session_state.db_connection)
    data = page.get_page_data()
    
    # Streamlit-specific rendering
    st.title(data.title)
    
    # Render page content using Streamlit components
    # ...
```

### Phase 3: Flask API Development (3-4 weeks)

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

### Phase 4: Enhanced UI Components (4-6 weeks)

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

### Phase 5: React Exploration (Future)

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
        
    def _get_charts(self):
        # Business logic to get chart data
        return []
        
    def _get_tables(self):
        # Business logic to get table data
        return []
        
    def _get_status_items(self):
        # Business logic to get status items
        return []
```

#### Adapter Pattern

The adapter pattern translates core page data into framework-specific UI components.

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

- **Phase 1**: 1 senior developer, 2-3 weeks
- **Phase 2**: 1 senior developer, 1 week
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

## Approval

- [ ] Architecture review completed
- [ ] Resource allocation approved
- [ ] Timeline approved
- [ ] Success metrics approved

## Reviewers

- [ ] Lead Developer
- [ ] UX Designer
- [ ] Product Manager
- [ ] QA Lead
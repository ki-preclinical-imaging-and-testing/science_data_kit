# Framework Adapter Patterns

## Overview

This document describes the adapter patterns used to implement the framework-agnostic architecture in the Science Data Kit. These patterns enable the application to support multiple frontend frameworks (Streamlit, Flask, React) while maintaining a single, shared core of business logic.

## Core Principles

1. **Separation of Concerns**: Business logic is completely separated from presentation logic
2. **Single Source of Truth**: Core data models define the canonical representation of page data
3. **Framework Independence**: Core logic has no dependencies on UI frameworks
4. **Adapter Responsibility**: Adapters translate between core data and framework-specific UI components
5. **Progressive Enhancement**: Start with basic functionality and enhance with framework-specific features

## Architecture Layers

### 1. Core Layer

The core layer contains all business logic and data models that are independent of any UI framework:

```
science_data_kit/core/
├── services/           # Business logic services
├── pages/              # Page orchestration classes
└── models/             # Shared data structures
```

### 2. Adapter Layer

The adapter layer translates between the core layer and framework-specific UI components:

```
science_data_kit/ui/adapters/         # Streamlit adapters
science_data_kit/web/adapters/        # Flask adapters
science_data_kit/frontend/adapters/   # React adapters
```

### 3. UI Layer

The UI layer contains framework-specific components and rendering logic:

```
science_data_kit/ui/components/       # Streamlit components
science_data_kit/web/templates/       # Flask/Jinja2 templates
science_data_kit/frontend/components/ # React components
```

## Core Page Pattern

The core page pattern defines how page data and business logic are structured:

```python
# core/models/page.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class PageData:
    """Base class for page data"""
    title: str
    requires_auth: bool = True
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

### Example: Dashboard Page

```python
# core/models/dashboard.py
from dataclasses import dataclass
from typing import List, Dict, Any
from science_data_kit.core.models.page import PageData

@dataclass
class DashboardPageData(PageData):
    """Dashboard page specific data"""
    metrics: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    status_items: List[Dict[str, Any]]
```

```python
# core/pages/dashboard.py
from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.dashboard import DashboardPageData
from science_data_kit.core.services.metrics import get_system_metrics
from science_data_kit.core.services.charts import get_chart_data
from science_data_kit.core.services.tables import get_table_data
from science_data_kit.core.services.status import get_status_items

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
        """Get system metrics data"""
        return get_system_metrics(self.db_connection)
        
    def _get_charts(self):
        """Get chart data"""
        return get_chart_data(self.db_connection)
        
    def _get_tables(self):
        """Get table data"""
        return get_table_data(self.db_connection)
        
    def _get_status_items(self):
        """Get status items"""
        return get_status_items()
```

## Adapter Patterns

### Streamlit Adapter

The Streamlit adapter translates core page data into Streamlit UI components:

```python
# ui/adapters/streamlit_adapter.py
import streamlit as st
from typing import Type
from science_data_kit.core.pages.base import BasePage

class StreamlitAdapter:
    @staticmethod
    def render_page(page_class: Type[BasePage], **kwargs):
        """Render a page using Streamlit components"""
        # Create page instance
        page = page_class(**kwargs)
        
        # Get page data
        data = page.get_page_data()
        
        # Render using Streamlit
        st.title(data.title)
        
        # Render page-specific content
        if hasattr(data, 'metrics'):
            StreamlitAdapter._render_metrics(data.metrics)
        
        if hasattr(data, 'charts'):
            StreamlitAdapter._render_charts(data.charts)
        
        if hasattr(data, 'tables'):
            StreamlitAdapter._render_tables(data.tables)
            
        if hasattr(data, 'status_items'):
            StreamlitAdapter._render_status_items(data.status_items)
    
    @staticmethod
    def _render_metrics(metrics):
        """Render metrics using Streamlit components"""
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                st.metric(
                    label=metric['label'],
                    value=metric['value'],
                    delta=metric.get('delta')
                )
    
    @staticmethod
    def _render_charts(charts):
        """Render charts using Streamlit components"""
        for chart in charts:
            st.subheader(chart['title'])
            st.write(chart['description'])
            # Render chart based on type
            if chart['type'] == 'bar':
                st.bar_chart(chart['data'])
            elif chart['type'] == 'line':
                st.line_chart(chart['data'])
            # etc.
    
    @staticmethod
    def _render_tables(tables):
        """Render tables using Streamlit components"""
        for table in tables:
            st.subheader(table['title'])
            st.write(table['description'])
            st.dataframe(table['data'])
    
    @staticmethod
    def _render_status_items(status_items):
        """Render status items using Streamlit components"""
        for item in status_items:
            st.write(f"**{item['name']}**: {item['status']}")
```

### Flask Adapter

The Flask adapter translates core page data into Flask/Jinja2 templates and JSON API responses:

```python
# web/adapters/flask_adapter.py
from flask import render_template, jsonify
from typing import Type
from science_data_kit.core.pages.base import BasePage

class FlaskAdapter:
    @staticmethod
    def render_page_html(page_class: Type[BasePage], **kwargs):
        """Render a page using Flask/Jinja2 templates"""
        # Create page instance
        page = page_class(**kwargs)
        
        # Get page data
        data = page.get_page_data()
        
        # Render using Flask/Jinja2
        return render_template(
            'page.html',
            title=data.title,
            page_data=data
        )
    
    @staticmethod
    def render_page_api(page_class: Type[BasePage], **kwargs):
        """Render a page as JSON API response"""
        # Create page instance
        page = page_class(**kwargs)
        
        # Get page data
        data = page.get_page_data()
        
        # Return JSON response
        return jsonify(data)
```

### React Adapter

The React adapter translates core page data into React components via a REST API:

```python
# web/api/page_api.py
from flask import Blueprint, jsonify, request
from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.file_browser import FileBrowserPage
# Import other page classes as needed

api = Blueprint('api', __name__)

@api.route('/api/pages/<page_name>', methods=['GET'])
def get_page_data(page_name):
    """API endpoint to get page data for React frontend"""
    # Map page names to page classes
    page_map = {
        'dashboard': DashboardPage,
        'file_browser': FileBrowserPage,
        # Add other pages as needed
    }
    
    if page_name not in page_map:
        return jsonify({'error': f'Page not found: {page_name}'}), 404
    
    # Create page instance
    page_class = page_map[page_name]
    page = page_class()
    
    # Get page data
    data = page.get_page_data()
    
    # Convert dataclass to dict for JSON serialization
    return jsonify(data)
```

## Migration Strategy

### 1. Identify Page Components

For each existing page, identify the components that need to be migrated:

1. **Data Models**: What data does the page need?
2. **Business Logic**: What operations does the page perform?
3. **UI Components**: What UI elements does the page render?

### 2. Extract Core Logic

Extract business logic from the existing render functions:

```python
# Before: Streamlit-specific page
def render_dashboard_page():
    st.title("Dashboard")
    
    # Business logic mixed with UI
    metrics = get_system_metrics(st.session_state.db_connection)
    
    # Render metrics
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta')
            )
```

```python
# After: Core page class
class DashboardPage(BasePage):
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        
    def get_page_data(self) -> DashboardPageData:
        return DashboardPageData(
            title="Dashboard",
            requires_auth=True,
            metrics=self._get_metrics(),
            # ...
        )
        
    def _get_metrics(self):
        # Business logic extracted
        return get_system_metrics(self.db_connection)
```

### 3. Create Adapter

Create an adapter to render the page using the appropriate UI framework:

```python
# Streamlit adapter
def render_dashboard_page():
    # Use the adapter to render the page
    StreamlitAdapter.render_page(DashboardPage, db_connection=st.session_state.db_connection)
```

### 4. Test and Validate

Ensure that the migrated page works correctly and provides the same functionality as before.

## Common Patterns

### 1. Page Registration

Register pages with the appropriate adapter:

```python
# ui/app.py
from science_data_kit.ui.adapters.streamlit_adapter import StreamlitAdapter
from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.file_browser import FileBrowserPage

def register_pages():
    """Register all pages with the Streamlit adapter"""
    pages = {
        "Dashboard": DashboardPage,
        "File Browser": FileBrowserPage,
        # Add other pages as needed
    }
    
    for name, page_class in pages.items():
        st.sidebar.page_link(
            f"pages/{name.lower().replace(' ', '_')}.py",
            label=name,
            icon="📊" if name == "Dashboard" else "📁"
        )
```

### 2. Session State Management

Handle session state consistently across frameworks:

```python
# core/session/state.py
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SessionState:
    """Framework-agnostic session state"""
    user_id: Optional[str] = None
    db_connection: Optional[Any] = None
    preferences: Dict[str, Any] = None
```

```python
# ui/adapters/streamlit_state_adapter.py
import streamlit as st
from science_data_kit.core.session.state import SessionState

def get_session_state() -> SessionState:
    """Get session state from Streamlit"""
    # Initialize session state if needed
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = None
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}
    
    # Convert to framework-agnostic SessionState
    return SessionState(
        user_id=st.session_state.user_id,
        db_connection=st.session_state.db_connection,
        preferences=st.session_state.preferences
    )

def update_session_state(state: SessionState):
    """Update Streamlit session state"""
    st.session_state.user_id = state.user_id
    st.session_state.db_connection = state.db_connection
    st.session_state.preferences = state.preferences
```

### 3. Component Composition

Compose complex UI components from simpler ones:

```python
# core/models/components.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Component:
    """Base class for UI components"""
    id: str
    type: str

@dataclass
class Container(Component):
    """Container component"""
    children: List[Component]

@dataclass
class Text(Component):
    """Text component"""
    content: str
    style: Optional[Dict[str, Any]] = None

@dataclass
class Button(Component):
    """Button component"""
    label: str
    action: str
    style: Optional[Dict[str, Any]] = None
```

```python
# ui/adapters/streamlit_component_adapter.py
import streamlit as st
from science_data_kit.core.models.components import Component, Container, Text, Button

def render_component(component: Component):
    """Render a component using Streamlit"""
    if isinstance(component, Container):
        for child in component.children:
            render_component(child)
    elif isinstance(component, Text):
        st.write(component.content)
    elif isinstance(component, Button):
        st.button(component.label, key=component.id)
```

## Best Practices

1. **Keep Core Logic Pure**: Core logic should have no dependencies on UI frameworks
2. **Use Data Classes**: Use Python's dataclasses for structured data exchange
3. **Consistent Naming**: Use consistent naming conventions across all layers
4. **Comprehensive Testing**: Test core logic independently of UI
5. **Documentation**: Document the purpose and usage of each component
6. **Gradual Migration**: Migrate one page at a time, starting with simpler pages
7. **Feature Flags**: Use feature flags to enable/disable new implementations

## Conclusion

The framework adapter patterns described in this document provide a clear path for migrating the Science Data Kit from a Streamlit-only architecture to a framework-agnostic architecture. By separating business logic from presentation logic, we can support multiple frontend frameworks while maintaining a single, shared core of business logic.
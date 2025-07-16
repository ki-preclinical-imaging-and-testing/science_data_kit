# Framework Adapter Pattern Documentation

## Overview

The Science Data Kit (SDK) uses a framework-agnostic architecture that separates the core business logic from the UI rendering. This allows the application to support multiple frontend frameworks (Streamlit, Flask, React) without duplicating business logic.

The adapter pattern is a key component of this architecture. It provides a bridge between the framework-independent core and the framework-specific UI components.

## Architecture

The architecture consists of three main layers:

1. **Core Layer**: Contains all business logic, data models, and page orchestration that is independent of any UI framework
2. **Adapter Layer**: Provides framework-specific implementations that translate core data structures into UI components
3. **Framework-Specific UI Layer**: Contains specialized components that leverage the unique capabilities of each framework

```
science_data_kit/
├── core/                    # Framework-independent layer
│   ├── services/           # Business logic
│   ├── pages/              # Page orchestration
│   └── models/             # Shared data structures
├── ui/                     # UI implementations
│   ├── adapters/           # Framework adapters
│   │   ├── streamlit_adapter.py  # Streamlit-specific adapter
│   │   └── flask_adapter.py      # Flask-specific adapter (future)
│   └── pages/              # Framework-specific pages
└── web/                    # Alternative UI implementations (future)
```

## Core Components

### BasePage

The `BasePage` class is the foundation of the framework-agnostic architecture. It defines a common interface for all pages:

```python
class BasePage(ABC):
    """Base class for all pages in the Science Data Kit application."""
    
    def __init__(self, db_connection=None):
        """Initialize the page with an optional database connection."""
        self.db_connection = db_connection
    
    @abstractmethod
    def get_page_data(self) -> PageData:
        """Return data needed to render this page."""
        pass
```

### PageData Models

The `PageData` classes define the data structures that are passed between the core and the UI layers:

```python
@dataclass
class PageData:
    """Base class for page data"""
    title: str
    requires_auth: bool = True

@dataclass
class DashboardPageData(PageData):
    """Dashboard page specific data"""
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    status_items: List[Dict[str, Any]] = field(default_factory=list)
    # ... other dashboard-specific fields
```

## Adapter Pattern

The adapter pattern is implemented in the `ui/adapters` directory. Each adapter provides:

1. A main `render_page` function that takes a `BasePage` instance and renders it based on its type
2. Specific render functions for different page types (`_render_dashboard_page`, `_render_file_explorer_page`, etc.)
3. Public functions that create page instances and render them (`render_dashboard_page`, `render_file_browser_page`, etc.)

### Streamlit Adapter

The Streamlit adapter (`streamlit_adapter.py`) provides Streamlit-specific implementations of the adapter pattern:

```python
def render_page(page_instance: BasePage) -> None:
    """
    Render a page using Streamlit components.
    
    Args:
        page_instance: The page instance to render.
    """
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

### Page Rendering Functions

Each adapter provides specific render functions for different page types:

```python
def _render_dashboard_page(page_data: DashboardPageData) -> None:
    """
    Render a dashboard page using Streamlit components.
    
    Args:
        page_data: The dashboard page data to render.
    """
    # Set the page title
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

### Public Render Functions

Each adapter provides public functions that create page instances and render them:

```python
def render_dashboard_page():
    """
    Render the Dashboard page using the core DashboardPage class.
    
    This function creates an instance of the core DashboardPage class,
    gets the page data, and renders it using Streamlit components.
    """
    # Create an instance of the core DashboardPage class
    page = DashboardPage(st.session_state.get("db_connection"))
    
    # Render the page
    render_page(page)
```

## Implementing a New Framework Adapter

To implement a new framework adapter (e.g., for Flask or React), follow these steps:

1. Create a new adapter file in the `ui/adapters` directory (e.g., `flask_adapter.py`)
2. Implement the main `render_page` function that takes a `BasePage` instance and renders it based on its type
3. Implement specific render functions for different page types
4. Implement public functions that create page instances and render them
5. Update the UI pages to use the new adapter

### Example: Flask Adapter

Here's an example of how a Flask adapter might be implemented:

```python
# ui/adapters/flask_adapter.py
from flask import render_template, jsonify
from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import (
    PageData, DashboardPageData, FileExplorerPageData, ConnectPageData, ExplorePageData
)

def render_page_html(page_instance: BasePage):
    """Render a page as HTML using Flask templates."""
    page_data = page_instance.get_page_data()
    
    if isinstance(page_data, DashboardPageData):
        return render_template('dashboard.html', page_data=page_data)
    elif isinstance(page_data, FileExplorerPageData):
        return render_template('file_explorer.html', page_data=page_data)
    elif isinstance(page_data, ConnectPageData):
        return render_template('connect.html', page_data=page_data)
    elif isinstance(page_data, ExplorePageData):
        return render_template('explore.html', page_data=page_data)
    else:
        return render_template('generic.html', page_data=page_data)

def render_page_api(page_instance: BasePage):
    """Render a page as JSON for API endpoints."""
    page_data = page_instance.get_page_data()
    return jsonify(page_data)
```

## Testing Adapters

Adapters should be thoroughly tested to ensure they correctly render page data. The tests should verify that:

1. The `render_page` function correctly identifies the page type and calls the appropriate render function
2. The specific render functions correctly render the page data
3. The public functions correctly create page instances and call `render_page`

Example test:

```python
def test_render_page_dashboard(mock_flask):
    """Test that render_page correctly renders a dashboard page."""
    # Create mock page data
    page_data = DashboardPageData(
        title="Test Dashboard",
        metrics=[{"title": "Test Metric", "value": 42, "trend": 5}]
    )
    
    # Create mock page instance
    page = MockBasePage(page_data)
    
    # Mock the _render_dashboard_page function
    with patch('science_data_kit.ui.adapters.flask_adapter._render_dashboard_page') as mock_render:
        # Call the function
        render_page_html(page)
        
        # Check that the correct render function was called with the page data
        mock_render.assert_called_once_with(page_data)
```

## Best Practices

1. **Keep the core layer framework-independent**: The core layer should not import or use any framework-specific code.
2. **Use data classes for page data**: Data classes provide a clean, type-hinted way to define the data structures that are passed between the core and UI layers.
3. **Implement comprehensive tests**: Each adapter should have comprehensive tests to ensure it correctly renders page data.
4. **Document the adapter pattern**: Each adapter should be well-documented to guide future implementations.
5. **Use consistent naming conventions**: Use consistent naming conventions across all adapters to make the code easier to understand and maintain.
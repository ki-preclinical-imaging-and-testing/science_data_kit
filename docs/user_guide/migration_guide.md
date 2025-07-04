# Migration Guide: From Legacy App to New UI Structure

## Overview

This guide provides instructions for transitioning from the legacy `app/` directory to the new `science_data_kit/ui/` structure. The migration is part of the Science Data Kit's architectural improvements to enhance maintainability and organization of the codebase.

## Table of Contents

1. [Introduction](#introduction)
2. [Key Differences](#key-differences)
3. [Migration Steps](#migration-steps)
4. [Import Path Changes](#import-path-changes)
5. [API Changes](#api-changes)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Introduction

The Science Data Kit originally had its user interface components in the `app/` directory. As part of architectural improvements, these components have been migrated to a more structured and modular organization under `science_data_kit/ui/`. This guide will help you transition your code from using the legacy structure to the new one.

## Key Differences

The new UI structure offers several improvements over the legacy app:

1. **Class-based architecture**: The new UI uses a class-based approach with `BasePage` and specific page implementations, making the code more maintainable and extensible.

2. **Better organization**: Components are organized into logical directories:
   - `science_data_kit/ui/pages/`: Page implementations
   - `science_data_kit/ui/components/`: Reusable UI components
   - `science_data_kit/ui/adapters/`: Adapters for external services

3. **Improved state management**: The new UI uses a more robust state management system.

4. **Enhanced sidebar**: Driver connectors are displayed in the sidebar for better user experience.

5. **Separation of concerns**: Better separation between UI components and business logic.

## Migration Steps

Follow these steps to migrate from the legacy app to the new UI structure:

### Step 1: Update Import Statements

Replace imports from the `app` directory with their equivalents from `science_data_kit.ui`:

```python
# Old import
from app.utils.sidebar import create_sidebar

# New import
from science_data_kit.ui.components.sidebar import Sidebar
```

### Step 2: Update Function Calls

Many functions have been refactored into class methods. Update your function calls accordingly:

```python
# Old code
create_sidebar(st, db_manager)

# New code
sidebar = Sidebar(st, db_manager)
sidebar.render()
```

### Step 3: Update Page Navigation

The navigation system has been updated. If you were using the legacy navigation:

```python
# Old code
import app.menu as menu
menu.show_menu(st)

# New code
from science_data_kit.ui.app import App
app = App(st)
app.show_navigation()
```

### Step 4: Update Database Connections

Database connection handling has been improved:

```python
# Old code
from app.utils.database import connect_to_neo4j
db_manager = connect_to_neo4j(uri, user, password)

# New code
from science_data_kit.core.db import Neo4jManager
db_manager = Neo4jManager(uri=uri, user=user, password=password)
```

## Import Path Changes

Here's a reference table of common import path changes:

| Legacy Import | New Import |
|---------------|------------|
| `app.app` | `science_data_kit.ui.app` |
| `app.chat` | `science_data_kit.ui.pages.chat` |
| `app.explore` | `science_data_kit.ui.pages.explore` |
| `app.map` | `science_data_kit.ui.pages.map` |
| `app.survey` | `science_data_kit.ui.pages.survey` |
| `app.connect` | `science_data_kit.ui.pages.connect` |
| `app.about` | `science_data_kit.ui.pages.about` |
| `app.utils.database` | `science_data_kit.core.db.db_manager` |
| `app.utils.db_adapter` | `science_data_kit.core.db.db_adapter` |
| `app.utils.models` | `science_data_kit.core.models.app_models` |
| `app.utils.sidebar` | `science_data_kit.ui.components.sidebar` |
| `app.utils.file_utils` | `science_data_kit.core.utils.file_utils` |
| `app.utils.jupyter_adapter` | `science_data_kit.core.integrations.jupyter_adapter` |
| `app.utils.neodash_adapter` | `science_data_kit.core.integrations.neodash_adapter` |

## API Changes

### Class-Based Pages

The new UI uses a class-based approach for pages. Each page extends the `BasePage` class:

```python
from science_data_kit.ui.pages.base_page import BasePage

class MyCustomPage(BasePage):
    def __init__(self, st, session_state):
        super().__init__(st, session_state)
        self.title = "My Custom Page"
        
    def render(self):
        self.st.title(self.title)
        # Your page content here
```

### State Management

The new UI uses an improved state management system:

```python
from science_data_kit.ui.state import get_session_state

# Get the session state
session_state = get_session_state()

# Access state variables
db_manager = session_state.db_manager
```

## Examples

### Example 1: Creating a Custom Page

```python
# Import necessary modules
from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.sidebar import Sidebar

class CustomPage(BasePage):
    def __init__(self, st, session_state):
        super().__init__(st, session_state)
        self.title = "Custom Page"
        self.sidebar = Sidebar(st, session_state)
        
    def render(self):
        # Render the sidebar
        self.sidebar.render()
        
        # Render the main content
        self.st.title(self.title)
        self.st.write("This is a custom page using the new UI structure.")
        
        # Access the database manager from session state
        db_manager = self.session_state.db_manager
        if db_manager and db_manager.is_connected():
            result = db_manager.run_query("MATCH (n) RETURN count(n) AS count")
            self.st.write(f"Number of nodes in the database: {result[0]['count']}")
```

### Example 2: Using the Database Manager

```python
from science_data_kit.core.db import Neo4jManager

# Create a database manager
db_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Run a query
result = db_manager.run_query(
    "MATCH (p:Person) WHERE p.age > $min_age RETURN p.name, p.age",
    parameters={"min_age": 30}
)

# Process the results
for record in result:
    print(f"Name: {record['p.name']}, Age: {record['p.age']}")
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'app'**
   - This error occurs when you're still using imports from the legacy app directory.
   - Solution: Update your import statements to use the new paths from `science_data_kit.ui`.

2. **AttributeError: 'module' object has no attribute 'X'**
   - This error occurs when you're trying to access a function or class that has been renamed or moved.
   - Solution: Check the import path changes table above and update your code accordingly.

3. **TypeError: 'X' object is not callable**
   - This error occurs when you're trying to use a class as a function or vice versa.
   - Solution: Check if the function has been refactored into a class method and update your code accordingly.

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the documentation in the `docs/user_guide/` directory
2. Look at the example code in the `examples/` directory
3. Reach out to the development team for assistance

## Conclusion

Migrating from the legacy app to the new UI structure will improve the maintainability and extensibility of your code. The new structure provides a more organized and consistent approach to building UI components, with better separation of concerns and improved state management.
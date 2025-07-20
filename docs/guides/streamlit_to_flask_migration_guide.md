# Streamlit to Flask Migration Guide

## Overview

This guide provides instructions for users transitioning from the Streamlit version of the Science Data Kit to the new Flask implementation. The Flask version offers several advantages including improved performance, enhanced UI capabilities, better deployment options, improved accessibility, and responsive design for all screen sizes.

## Key Differences

### Architecture
- **Streamlit**: Single-page application with reactive reloads
- **Flask**: Multi-page application with traditional request/response cycle
- **Impact**: More predictable state management and better performance in Flask

### URL Structure
- **Streamlit**: Uses query parameters for navigation (e.g., `?page=explore`)
- **Flask**: Uses path-based routing (e.g., `/explore`)
- **Impact**: More intuitive URLs and better bookmarking in Flask

### Authentication
- **Streamlit**: Custom session management
- **Flask**: Standard Flask session management with enhanced security
- **Impact**: More secure and standard authentication flow in Flask

### UI Components
- **Streamlit**: Built-in widgets with limited customization
- **Flask**: HTML/CSS/JS with HTMX and Alpine.js for enhanced interactivity
- **Impact**: More flexible and responsive UI in Flask

## Migration Steps

### For End Users

1. **Installation**
   - Uninstall the Streamlit version: `pip uninstall science-data-kit`
   - Install the Flask version: `pip install science-data-kit`
   - Alternatively, use the new Docker image: `docker pull sciencedata/sdk:latest`

2. **Configuration**
   - Update your configuration file:
     - Rename `streamlit_config.yaml` to `sdk_config.yaml`
     - Remove Streamlit-specific settings
     - Add Flask-specific settings (see example below)

3. **Data Migration**
   - Your data and connections will be automatically migrated
   - No manual data migration is required

4. **Starting the Application**
   - Instead of `streamlit run app.py`, use `flask run` or `python -m science_data_kit`
   - For Docker: `docker run -p 5000:5000 sciencedata/sdk:latest`

5. **URL Changes**
   - Update any bookmarks or scripts that use SDK URLs
   - Use the URL mapping table below to find the new URLs

### For Developers

1. **API Changes**
   - The core API remains the same
   - UI-specific code has been refactored
   - See the API migration table below for details

2. **Custom Extensions**
   - Update import statements (see example below)
   - Replace Streamlit UI components with Flask/HTML equivalents
   - Use the provided adapter utilities for common patterns

3. **Testing**
   - Update test scripts to use Flask test client
   - Replace Streamlit-specific test utilities with Flask equivalents

## Configuration Example

### Streamlit Configuration (Old)
```yaml
streamlit:
  server:
    port: 8501
    enableCORS: false
  theme:
    primaryColor: "#F63366"
    backgroundColor: "#FFFFFF"
    secondaryBackgroundColor: "#F0F2F6"
    textColor: "#262730"
    font: "sans serif"
```

### Flask Configuration (New)
```yaml
flask:
  server:
    port: 5000
    host: "0.0.0.0"
    debug: false
  theme:
    primary_color: "#F63366"
    background_color: "#FFFFFF"
    secondary_background_color: "#F0F2F6"
    text_color: "#262730"
    font: "sans serif"
```

## URL Mapping

| Streamlit URL | Flask URL |
|---------------|-----------|
| `?page=home` | `/` |
| `?page=explore` | `/explore` |
| `?page=connect` | `/connect` |
| `?page=file_browser` | `/files` |
| `?page=dashboard` | `/dashboard` |
| `?page=plugin_connect` | `/plugins` |
| `?page=about` | `/about` |
| `?page=cbioportal` | `/cbioportal` |
| `?page=dropbox` | `/dropbox` |
| `?page=isa` | `/isa` |
| `?page=map` | `/map` |
| `?page=msgraph` | `/msgraph` |
| `?page=ontology` | `/ontology` |
| `?page=preferences` | `/preferences` |
| `?page=analytics` | `/analytics` |
| `?page=chat` | `/chat` |
| `?page=feedback` | `/feedback` |
| `?page=instructor` | `/instructor` |
| `?page=observation` | `/observation` |
| `?page=survey` | `/survey` |
| `?page=workshop` | `/workshop` |

## API Migration Examples

### Import Statements

#### Streamlit Version
```python
from science_data_kit.ui.streamlit import render_page
from science_data_kit.ui.streamlit.components import create_sidebar
```

#### Flask Version
```python
from science_data_kit.ui.flask import render_template
from science_data_kit.ui.flask.components import create_sidebar
```

### Page Rendering

#### Streamlit Version
```python
def render_explore_page():
    st.title("Explore Data")
    # Streamlit-specific code
```

#### Flask Version
```python
@app.route('/explore')
def render_explore_page():
    return render_template('explore.html', title="Explore Data")
```

## Common Issues and Solutions

### Issue: Application doesn't start
**Solution**: Check that you're using the correct command to start the Flask application. Use `flask run` or `python -m science_data_kit` instead of `streamlit run app.py`.

### Issue: Configuration not loading
**Solution**: Ensure your configuration file is named `sdk_config.yaml` and is in the correct location. The default location is the current working directory or the user's home directory.

### Issue: Custom extensions not working
**Solution**: Update import statements and replace Streamlit-specific code with Flask equivalents. See the API Migration Examples section for guidance.

### Issue: Missing UI components
**Solution**: The Flask version uses different UI components. Refer to the documentation for the new components and their usage.

## Getting Help

If you encounter issues during migration, please use the following resources:

- **Documentation**: [https://sciencedata.example.com/docs](https://sciencedata.example.com/docs)
- **GitHub Issues**: [https://github.com/example/science-data-kit/issues](https://github.com/example/science-data-kit/issues)
- **Support Email**: support@sciencedata.example.com
- **Community Forum**: [https://community.sciencedata.example.com](https://community.sciencedata.example.com)

## Conclusion

The transition from Streamlit to Flask represents a significant improvement in the Science Data Kit's capabilities and user experience. While there may be some initial adjustment required, the benefits of improved performance, enhanced UI capabilities, better deployment options, and improved accessibility make the migration worthwhile.

We appreciate your patience during this transition and welcome your feedback on the new Flask implementation.
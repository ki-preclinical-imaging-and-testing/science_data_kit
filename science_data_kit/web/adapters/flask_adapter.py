"""
Flask Adapter for Science Data Kit

This module provides adapter functions that translate core page data into Flask templates and API responses.
"""

from flask import render_template, jsonify, request, session, redirect, url_for
from typing import Dict, Any

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.utils.i18n_utils import get_available_languages, get_current_language, set_current_language, _
from science_data_kit.core.models.page import (
    PageData, 
    DashboardPageData, 
    FileExplorerPageData, 
    ConnectPageData, 
    ExplorePageData,
    PluginConnectPageData
)

def render_page_html(page_instance: BasePage) -> str:
    """
    Render a page instance as HTML using Flask templates.

    Args:
        page_instance: An instance of a BasePage subclass.

    Returns:
        A rendered HTML template.
    """
    page_data = page_instance.get_page_data()

    if isinstance(page_data, DashboardPageData):
        return _render_dashboard_html(page_data)
    elif isinstance(page_data, FileExplorerPageData):
        return _render_file_explorer_html(page_data)
    elif isinstance(page_data, ConnectPageData):
        return _render_connect_html(page_data)
    elif isinstance(page_data, ExplorePageData):
        return _render_explore_html(page_data)
    elif isinstance(page_data, PluginConnectPageData):
        return _render_plugin_connect_html(page_data)
    else:
        # Generic rendering for other page types
        return render_template('generic.html', page_data=page_data)

def render_page_api(page_instance: BasePage) -> Dict[str, Any]:
    """
    Render a page instance as JSON for API responses.

    Args:
        page_instance: An instance of a BasePage subclass.

    Returns:
        A Flask response with JSON data.
    """
    page_data = page_instance.get_page_data()

    # Convert dataclass to dict
    data_dict = _dataclass_to_dict(page_data)

    return jsonify(data_dict)

def _dataclass_to_dict(obj):
    """
    Convert a dataclass instance to a dictionary.

    Args:
        obj: A dataclass instance.

    Returns:
        A dictionary representation of the dataclass.
    """
    if hasattr(obj, '__dataclass_fields__'):
        return {field: _dataclass_to_dict(getattr(obj, field)) 
                for field in obj.__dataclass_fields__}
    elif isinstance(obj, list):
        return [_dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _dataclass_to_dict(value) for key, value in obj.items()}
    else:
        return obj

def _render_dashboard_html(page_data: DashboardPageData) -> str:
    """
    Render a dashboard page as HTML.

    Args:
        page_data: Dashboard page data.

    Returns:
        A rendered HTML template.
    """
    return render_template('dashboard.html', 
                          title=page_data.title,
                          metrics=page_data.metrics,
                          charts=page_data.charts,
                          tables=page_data.tables,
                          status_items=page_data.status_items,
                          connected_services=page_data.connected_services,
                          recent_activities=page_data.recent_activities,
                          feature_categories=page_data.feature_categories,
                          languages=get_available_languages(),
                          current_language=get_current_language())

def _render_file_explorer_html(page_data: FileExplorerPageData) -> str:
    """
    Render a file explorer page as HTML.

    Args:
        page_data: File explorer page data.

    Returns:
        A rendered HTML template.
    """
    return render_template('file_explorer.html',
                          title=page_data.title,
                          current_path=page_data.current_path,
                          files=page_data.files,
                          directories=page_data.directories,
                          selected_files=page_data.selected_files,
                          view_mode=page_data.view_mode,
                          sort_by=page_data.sort_by,
                          sort_order=page_data.sort_order,
                          filter_pattern=page_data.filter_pattern,
                          languages=get_available_languages(),
                          current_language=get_current_language())

def _render_connect_html(page_data: ConnectPageData) -> str:
    """
    Render a connect page as HTML.

    Args:
        page_data: Connect page data.

    Returns:
        A rendered HTML template.
    """
    return render_template('connect.html',
                          title=page_data.title,
                          available_connections=page_data.available_connections,
                          active_connections=page_data.active_connections,
                          connection_status=page_data.connection_status,
                          connection_errors=page_data.connection_errors,
                          languages=get_available_languages(),
                          current_language=get_current_language())

def _render_explore_html(page_data: ExplorePageData) -> str:
    """
    Render an explore page as HTML.

    Args:
        page_data: Explore page data.

    Returns:
        A rendered HTML template.
    """
    return render_template('explore.html',
                          title=page_data.title,
                          available_data_sources=page_data.available_data_sources,
                          query_results=page_data.query_results,
                          visualizations=page_data.visualizations,
                          schema_info=page_data.schema_info,
                          languages=get_available_languages(),
                          current_language=get_current_language())

def _render_plugin_connect_html(page_data: PluginConnectPageData) -> str:
    """
    Render a plugin connect page as HTML.

    Args:
        page_data: Plugin connect page data.

    Returns:
        A rendered HTML template.
    """
    return render_template('plugin_connect.html',
                          title=page_data.title,
                          available_plugin_types=page_data.available_plugin_types,
                          available_plugins=page_data.available_plugins,
                          selected_plugin_type=page_data.selected_plugin_type,
                          selected_plugin_name=page_data.selected_plugin_name,
                          plugin_info=page_data.plugin_info,
                          plugin_capabilities=page_data.plugin_capabilities,
                          connection_status=page_data.connection_status,
                          connection_errors=page_data.connection_errors,
                          active_connections=page_data.active_connections,
                          languages=get_available_languages(),
                          current_language=get_current_language())

def set_language_route(language: str):
    """
    Set the current language and redirect to the previous page.

    Args:
        language: The language code to set.

    Returns:
        A redirect response to the previous page.
    """
    if language in get_available_languages():
        set_current_language(language)
        session['language'] = language

    return redirect(request.referrer or url_for('index'))

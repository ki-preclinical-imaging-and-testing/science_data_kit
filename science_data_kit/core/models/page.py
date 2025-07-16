"""
Page Data Models for Science Data Kit

This module defines the data models for pages in the Science Data Kit application.
These models are framework-independent and can be used with any UI framework.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

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
    connected_services: Dict[str, bool] = field(default_factory=dict)
    recent_activities: List[Dict[str, Any]] = field(default_factory=list)
    feature_categories: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

@dataclass
class FileExplorerPageData(PageData):
    """File explorer page specific data"""
    current_path: str
    files: List[Dict[str, Any]] = field(default_factory=list)
    directories: List[Dict[str, Any]] = field(default_factory=list)
    selected_files: List[str] = field(default_factory=list)
    view_mode: str = "list"
    sort_by: str = "name"
    sort_order: str = "ascending"
    filter_pattern: Optional[str] = None

@dataclass
class ConnectPageData(PageData):
    """Connect page specific data"""
    available_connections: List[Dict[str, Any]] = field(default_factory=list)
    active_connections: List[Dict[str, Any]] = field(default_factory=list)
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)

@dataclass
class ExplorePageData(PageData):
    """Explore page specific data"""
    available_data_sources: List[Dict[str, Any]] = field(default_factory=list)
    query_results: Optional[Dict[str, Any]] = None
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    schema_info: Optional[Dict[str, Any]] = None
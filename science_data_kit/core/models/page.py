"""
Page Data Models for Science Data Kit

This module defines the data models for pages in the Science Data Kit application.
These models are framework-independent and can be used with any UI framework.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set

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
    current_path: str = ""
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
    oauth_auth_urls: Dict[str, str] = field(default_factory=dict)
    oauth_states: Dict[str, str] = field(default_factory=dict)

@dataclass
class PluginConnectPageData(PageData):
    """Plugin connection page specific data"""
    available_plugin_types: List[str] = field(default_factory=list)
    available_plugins: Dict[str, List[str]] = field(default_factory=dict)
    selected_plugin_type: Optional[str] = None
    selected_plugin_name: Optional[str] = None
    plugin_info: Dict[str, Any] = field(default_factory=dict)
    plugin_capabilities: List[str] = field(default_factory=list)
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    active_connections: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ExplorePageData(PageData):
    """Explore page specific data"""
    available_data_sources: List[Dict[str, Any]] = field(default_factory=list)
    query_results: Optional[Dict[str, Any]] = None
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    schema_info: Optional[Dict[str, Any]] = None

@dataclass
class CbioportalBrowserPageData(PageData):
    """cBioPortal browser page specific data"""
    cancer_types: List[Dict[str, Any]] = field(default_factory=list)
    tumor_types: List[Dict[str, Any]] = field(default_factory=list)
    studies: List[Dict[str, Any]] = field(default_factory=list)
    terms: List[Dict[str, Any]] = field(default_factory=list)
    existing_term_accessions: Set[str] = field(default_factory=set)
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)

@dataclass
class DropboxConnectPageData(PageData):
    """Dropbox connection page specific data"""
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    account_info: Optional[Dict[str, Any]] = None
    app_key: Optional[str] = None
    app_secret: Optional[str] = None
    refresh_token: Optional[str] = None
    config_file: Optional[str] = None
    auth_url: Optional[str] = None

@dataclass
class DropboxBrowserPageData(PageData):
    """Dropbox browser page specific data"""
    current_path: str = ""
    files: List[Dict[str, Any]] = field(default_factory=list)
    directories: List[Dict[str, Any]] = field(default_factory=list)
    selected_file: Optional[Dict[str, Any]] = None
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    view_mode: str = "list"
    sort_by: str = "name"
    sort_order: str = "ascending"
    filter_pattern: Optional[str] = None

@dataclass
class IsaBrowserPageData(PageData):
    """ISA browser page specific data"""
    terms: List[Dict[str, Any]] = field(default_factory=list)
    existing_term_accessions: Set[str] = field(default_factory=set)
    available_labels: List[str] = field(default_factory=list)
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    account_info: Optional[Dict[str, Any]] = None
    node_classes: List[str] = field(default_factory=list)
    properties: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class MapPageData(PageData):
    """Map visualization page specific data"""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    entity_labels: List[str] = field(default_factory=list)
    entity_structures: Dict[str, Dict[str, str]] = field(default_factory=dict)
    taxonomy_keys: List[str] = field(default_factory=list)
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    node_classes: List[str] = field(default_factory=list)
    properties: Dict[str, List[str]] = field(default_factory=dict)
    relationship_types: List[str] = field(default_factory=list)
    ontology_data: Optional[Dict[str, Any]] = None

@dataclass
class MSGraphConnectPageData(PageData):
    """Microsoft Graph connection page specific data"""
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    auth_method: str = "device_code"
    config_file: Optional[str] = None
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    user_info: Optional[Dict[str, Any]] = None
    msgraph_available: bool = False

@dataclass
class MSGraphExplorePageData(PageData):
    """Microsoft Graph exploration page specific data"""
    resource_path: Optional[str] = None
    query_parameters: Dict[str, str] = field(default_factory=dict)
    response: Optional[Dict[str, Any]] = None
    dataframe: Optional[Any] = None
    connection_status: Dict[str, bool] = field(default_factory=dict)
    connection_errors: Dict[str, str] = field(default_factory=dict)
    sample_queries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    visualization_data: Optional[Dict[str, Any]] = None
    entity_type: str = "unknown"

@dataclass
class AnalyticsDashboardPageData(PageData):
    """Analytics dashboard page specific data"""
    analytics_enabled: bool = True
    analytics_storage_path: Optional[str] = None
    page_views: List[Dict[str, Any]] = field(default_factory=list)
    page_views_summary: Optional[Dict[str, Any]] = None
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    interactions_summary: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    session_start: Optional[float] = None
    session_duration: Optional[float] = None

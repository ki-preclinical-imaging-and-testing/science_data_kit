"""
Plugin Architecture for Science Data Kit Integrations

This module provides a comprehensive plugin architecture for integrations in the Science Data Kit,
enabling dynamic discovery, loading, and management of integration plugins.

The architecture includes:
1. Base classes and interfaces for different types of integrations
2. A plugin registry system with metadata and categorization
3. Plugin discovery and loading mechanisms
4. Standardized error handling and lifecycle management

This architecture allows for a more extensible and maintainable integration system,
making it easier to add new integrations and manage existing ones.
"""

import importlib
import inspect
import json
import logging
import mimetypes
import os
import pkgutil
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

# Type variable for generic plugin types
T = TypeVar('T', bound='PluginBase')

# Set up logging
logger = logging.getLogger(__name__)


class PluginCategory(Enum):
    """Categories of plugins supported by the system."""
    DATA_SOURCE = "data_source"
    ANALYSIS_TOOL = "analysis_tool"
    VISUALIZATION = "visualization"
    EXPORT = "export"
    IMPORT = "import"
    PLATFORM = "platform"
    UTILITY = "utility"
    FILE_INTERPRETER = "file_interpreter"
    METADATA_EXTRACTOR = "metadata_extractor"
    OTHER = "other"


class FileInterpreterCapability(Enum):
    """Capabilities that can be provided by file interpreter plugins."""
    TEXT_EXTRACTION = "text_extraction"
    PREVIEW_GENERATION = "preview_generation"
    METADATA_EXTRACTION = "metadata_extraction"
    CONTENT_ANALYSIS = "content_analysis"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    STRUCTURED_DATA_EXTRACTION = "structured_data_extraction"
    FULL_TEXT_SEARCH = "full_text_search"
    CONTENT_TRANSFORMATION = "content_transformation"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    category: PluginCategory
    dependencies: List[str] = field(default_factory=list)
    website: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    config_schema: Optional[Dict[str, Any]] = None
    capabilities: List[str] = field(default_factory=list)


class PluginBase(ABC):
    """
    Base class for all integration plugins.

    All plugins must inherit from this class and implement its abstract methods.
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise.
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.

        Returns:
            True if shutdown was successful, False otherwise.
        """
        pass

    def is_compatible(self) -> bool:
        """
        Check if the plugin is compatible with the current environment.

        Returns:
            True if the plugin is compatible, False otherwise.
        """
        # Default implementation assumes compatibility
        return True


class DataSourcePlugin(PluginBase):
    """
    Base class for data source integration plugins.

    Data source plugins provide access to external data sources like APIs,
    databases, file systems, etc.
    """

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to the data source.

        Args:
            **kwargs: Connection parameters specific to the data source.

        Returns:
            True if connection was successful, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the data source.

        Returns:
            True if disconnection was successful, False otherwise.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the plugin is currently connected to the data source.

        Returns:
            True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def get_data(self, query: Any, **kwargs) -> Any:
        """
        Get data from the data source.

        Args:
            query: The query to execute.
            **kwargs: Additional parameters for the query.

        Returns:
            The retrieved data.
        """
        pass


class AnalysisToolPlugin(PluginBase):
    """
    Base class for analysis tool integration plugins.

    Analysis tool plugins provide integration with data analysis libraries
    and tools like pandas, scikit-learn, etc.
    """

    @abstractmethod
    def analyze(self, data: Any, method: str, **kwargs) -> Any:
        """
        Analyze data using the tool.

        Args:
            data: The data to analyze.
            method: The analysis method to use.
            **kwargs: Additional parameters for the analysis.

        Returns:
            The analysis results.
        """
        pass

    @abstractmethod
    def get_available_methods(self) -> List[str]:
        """
        Get a list of available analysis methods.

        Returns:
            List of method names.
        """
        pass


class VisualizationPlugin(PluginBase):
    """
    Base class for visualization integration plugins.

    Visualization plugins provide integration with data visualization libraries
    and tools like matplotlib, plotly, etc.
    """

    @abstractmethod
    def visualize(self, data: Any, visualization_type: str, **kwargs) -> Any:
        """
        Visualize data.

        Args:
            data: The data to visualize.
            visualization_type: The type of visualization to create.
            **kwargs: Additional parameters for the visualization.

        Returns:
            The visualization object.
        """
        pass

    @abstractmethod
    def get_available_visualizations(self) -> List[str]:
        """
        Get a list of available visualization types.

        Returns:
            List of visualization type names.
        """
        pass

    @abstractmethod
    def save_visualization(self, visualization: Any, path: str, **kwargs) -> bool:
        """
        Save a visualization to a file.

        Args:
            visualization: The visualization to save.
            path: The path to save the visualization to.
            **kwargs: Additional parameters for saving.

        Returns:
            True if saving was successful, False otherwise.
        """
        pass


class PlatformPlugin(PluginBase):
    """
    Base class for platform integration plugins.

    Platform plugins provide integration with external platforms and services
    like ISA Tools, NC3Rs EDA, etc.
    """

    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """
        Authenticate with the platform.

        Args:
            **kwargs: Authentication parameters.

        Returns:
            True if authentication was successful, False otherwise.
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if the plugin is currently authenticated with the platform.

        Returns:
            True if authenticated, False otherwise.
        """
        pass

    @abstractmethod
    def get_resources(self, resource_type: str, **kwargs) -> Any:
        """
        Get resources from the platform.

        Args:
            resource_type: The type of resources to get.
            **kwargs: Additional parameters for the request.

        Returns:
            The retrieved resources.
        """
        pass


# File Interpreter Capability Mixins

class TextExtractionCapability:
    """
    Mixin for file interpreters that can extract text content from files.

    This capability allows plugins to extract plain text from various file formats,
    enabling features like full-text search and content analysis.
    """

    def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
        """
        Extract text content from the file.

        Args:
            file_path: Path to the file to extract text from.
            **kwargs: Additional parameters for text extraction.

        Returns:
            Extracted text content, or None if extraction failed.
        """
        raise NotImplementedError("Text extraction not implemented")

    def get_text_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for text extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        return {}


class PreviewGenerationCapability:
    """
    Mixin for file interpreters that can generate previews for files.

    This capability allows plugins to create visual previews of files,
    such as thumbnails for images, rendered views for documents, etc.
    """

    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the file.

        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.

        Returns:
            Preview data or path to the generated preview.
        """
        raise NotImplementedError("Preview generation not implemented")

    def get_preview_formats(self) -> List[str]:
        """
        Get a list of preview formats supported by this interpreter.

        Returns:
            List of supported preview formats (e.g., ['image/png', 'image/jpeg']).
        """
        return []


class ThumbnailGenerationCapability:
    """
    Mixin for file interpreters that can generate thumbnails for files.

    This capability allows plugins to create small thumbnail images for files,
    which can be used in file browsers and other UI components.
    """

    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the file.

        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.

        Returns:
            Thumbnail data or path to the generated thumbnail.
        """
        raise NotImplementedError("Thumbnail generation not implemented")


class ContentAnalysisCapability:
    """
    Mixin for file interpreters that can analyze file content.

    This capability allows plugins to perform various analyses on file content,
    such as keyword extraction, sentiment analysis, entity recognition, etc.
    """

    def analyze_content(self, file_path: str, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze the content of the file.

        Args:
            file_path: Path to the file to analyze.
            analysis_type: Type of analysis to perform.
            **kwargs: Additional parameters for the analysis.

        Returns:
            Dictionary containing analysis results.
        """
        raise NotImplementedError("Content analysis not implemented")

    def get_available_analyses(self) -> List[str]:
        """
        Get a list of available content analysis types.

        Returns:
            List of supported analysis types.
        """
        return []


class StructuredDataExtractionCapability:
    """
    Mixin for file interpreters that can extract structured data from files.

    This capability allows plugins to extract structured data like tables,
    charts, forms, etc. from various file formats.
    """

    def extract_structured_data(self, file_path: str, data_type: str, **kwargs) -> Any:
        """
        Extract structured data from the file.

        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'table', 'chart').
            **kwargs: Additional parameters for data extraction.

        Returns:
            Extracted structured data.
        """
        raise NotImplementedError("Structured data extraction not implemented")

    def get_supported_data_types(self) -> List[str]:
        """
        Get a list of structured data types supported by this interpreter.

        Returns:
            List of supported data types.
        """
        return []


class FileInterpreterPlugin(PluginBase):
    """
    Base class for file interpreter plugins.

    File interpreter plugins provide capabilities for interpreting different file types,
    extracting metadata, and generating previews. These plugins enable the system to
    work with specialized scientific file formats, document types, and media files.
    """

    @abstractmethod
    def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if this plugin can interpret the given file.

        Args:
            file_path: Path to the file to check.
            mime_type: Optional MIME type of the file, if known.

        Returns:
            True if the plugin can interpret the file, False otherwise.
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this interpreter.

        Returns:
            List of supported file extensions (e.g., ['.pdf', '.docx']).
        """
        pass

    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this interpreter.

        Returns:
            List of supported MIME types (e.g., ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']).
        """
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the file.

        Args:
            file_path: Path to the file to extract metadata from.

        Returns:
            Dictionary of metadata key-value pairs.
        """
        pass

    @abstractmethod
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
        """
        Generate a preview for the file.

        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            **kwargs: Additional parameters for preview generation.

        Returns:
            Preview data or path to the generated preview.
        """
        pass

    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Extract text content from the file, if applicable.

        This method is optional and may be implemented by interpreters
        that can extract text content from files.

        Args:
            file_path: Path to the file to extract text from.

        Returns:
            Extracted text content, or None if text extraction is not supported.
        """
        return None

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic information about the file.

        This method provides a standard set of file information that is
        common across all file types, such as size, creation date, etc.

        Args:
            file_path: Path to the file to get information for.

        Returns:
            Dictionary of file information.
        """
        path = Path(file_path)
        stat = path.stat()

        return {
            'name': path.name,
            'extension': path.suffix.lower(),
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_directory': path.is_dir(),
        }


class MetadataExtractorPlugin(PluginBase):
    """
    Base class for metadata extractor plugins.

    Metadata extractor plugins provide specialized capabilities for extracting
    metadata from specific file types or from file content. These plugins can
    be used independently or in conjunction with file interpreters to provide
    enhanced metadata extraction capabilities.
    """

    @abstractmethod
    def can_extract(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if this plugin can extract metadata from the given file.

        Args:
            file_path: Path to the file to check.
            mime_type: Optional MIME type of the file, if known.

        Returns:
            True if the plugin can extract metadata from the file, False otherwise.
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions (e.g., ['.jpg', '.tiff']).
        """
        pass

    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types (e.g., ['image/jpeg', 'image/tiff']).
        """
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from the file.

        Args:
            file_path: Path to the file to extract metadata from.
            **kwargs: Additional parameters for metadata extraction.

        Returns:
            Dictionary of metadata key-value pairs.
        """
        pass

    def get_metadata_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the metadata extracted by this plugin.

        This method provides information about the structure and types of
        metadata that this extractor can provide. This can be used for
        validation and documentation purposes.

        Returns:
            Dictionary describing the metadata schema.
        """
        # Default implementation returns an empty schema
        return {}

    def get_extraction_capabilities(self) -> List[str]:
        """
        Get a list of metadata extraction capabilities provided by this plugin.

        This method allows the plugin to advertise specific extraction capabilities
        that it provides, such as "EXIF extraction", "geolocation", etc.

        Returns:
            List of capability identifiers.
        """
        return []


class PluginRegistry:
    """
    Registry for managing integration plugins.

    This class provides methods for registering, discovering, loading,
    and managing plugins.
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, Type[PluginBase]] = {}
        self._instances: Dict[str, PluginBase] = {}
        self._categories: Dict[PluginCategory, Set[str]] = {
            category: set() for category in PluginCategory
        }
        self._capabilities: Dict[str, Set[str]] = {}  # Map capability to plugin names
        self._mime_types: Dict[str, Set[str]] = {}    # Map MIME type to plugin names
        self._file_extensions: Dict[str, Set[str]] = {}  # Map file extension to plugin names
        self._initialized = False

    def register_plugin(self, plugin_class: Type[PluginBase]) -> bool:
        """
        Register a plugin class.

        Args:
            plugin_class: The plugin class to register.

        Returns:
            True if registration was successful, False otherwise.
        """
        try:
            # Create a temporary instance to get metadata
            temp_instance = plugin_class()
            metadata = temp_instance.metadata

            # Check if a plugin with this name is already registered
            if metadata.name in self._plugins:
                logger.warning(f"Plugin '{metadata.name}' is already registered")
                return False

            # Validate the plugin
            validation_results = validate_plugin(temp_instance)
            if not validation_results.get("is_valid", False):
                # Log validation failures
                failed_validations = [
                    key for key, value in validation_results.items() 
                    if not value and key != "is_valid" and key != "capabilities_valid"
                ]
                logger.warning(f"Plugin '{metadata.name}' failed validation: {', '.join(failed_validations)}")

                # If it's a file interpreter or metadata extractor, we require validation to pass
                if metadata.category in [PluginCategory.FILE_INTERPRETER, PluginCategory.METADATA_EXTRACTOR]:
                    logger.error(f"Plugin '{metadata.name}' cannot be registered due to validation failures")
                    return False
                else:
                    # For other plugin types, log a warning but still register
                    logger.warning(f"Registering plugin '{metadata.name}' despite validation failures")

            # Register the plugin
            self._plugins[metadata.name] = plugin_class
            self._categories[metadata.category].add(metadata.name)

            # Register capabilities if provided
            if hasattr(metadata, 'capabilities') and metadata.capabilities:
                for capability in metadata.capabilities:
                    if capability not in self._capabilities:
                        self._capabilities[capability] = set()
                    self._capabilities[capability].add(metadata.name)

            # Register MIME types and file extensions for file interpreter plugins
            if metadata.category == PluginCategory.FILE_INTERPRETER:
                try:
                    # Get supported MIME types
                    mime_types = temp_instance.get_supported_mime_types()
                    for mime_type in mime_types:
                        if mime_type not in self._mime_types:
                            self._mime_types[mime_type] = set()
                        self._mime_types[mime_type].add(metadata.name)

                    # Get supported file extensions
                    extensions = temp_instance.get_supported_extensions()
                    for ext in extensions:
                        # Ensure extension starts with a dot
                        if not ext.startswith('.'):
                            ext = f'.{ext}'

                        if ext not in self._file_extensions:
                            self._file_extensions[ext] = set()
                        self._file_extensions[ext].add(metadata.name)
                except Exception as e:
                    logger.warning(f"Failed to register MIME types or extensions for plugin '{metadata.name}': {str(e)}")

            logger.info(f"Registered plugin '{metadata.name}' (version {metadata.version})")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin: {str(e)}")
            return False

    def unregister_plugin(self, name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            name: The name of the plugin to unregister.

        Returns:
            True if unregistration was successful, False otherwise.
        """
        if name not in self._plugins:
            logger.warning(f"Plugin '{name}' is not registered")
            return False

        # Shutdown the plugin instance if it exists
        if name in self._instances:
            try:
                self._instances[name].shutdown()
                del self._instances[name]
            except Exception as e:
                logger.error(f"Failed to shutdown plugin '{name}': {str(e)}")

        # Get the category and remove the plugin from it
        for category, plugins in self._categories.items():
            if name in plugins:
                plugins.remove(name)
                break

        # Remove the plugin from the registry
        del self._plugins[name]

        logger.info(f"Unregistered plugin '{name}'")
        return True

    def get_plugin_class(self, name: str) -> Optional[Type[PluginBase]]:
        """
        Get a plugin class by name.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin class if found, None otherwise.
        """
        return self._plugins.get(name)

    def get_plugin_instance(self, name: str, initialize: bool = True) -> Optional[PluginBase]:
        """
        Get a plugin instance by name.

        If the plugin is not already instantiated, it will be instantiated and initialized.

        Args:
            name: The name of the plugin.
            initialize: Whether to initialize the plugin if it's not already instantiated.

        Returns:
            The plugin instance if found and successfully instantiated, None otherwise.
        """
        # Return existing instance if available
        if name in self._instances:
            return self._instances[name]

        # Get the plugin class
        plugin_class = self.get_plugin_class(name)
        if not plugin_class:
            logger.warning(f"Plugin '{name}' not found")
            return None

        # Create a new instance
        try:
            instance = plugin_class()

            # Initialize the plugin if requested
            if initialize and not instance.initialize():
                logger.error(f"Failed to initialize plugin '{name}'")
                return None

            # Store the instance
            self._instances[name] = instance

            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate plugin '{name}': {str(e)}")
            return None

    def get_plugins_by_category(self, category: PluginCategory) -> List[str]:
        """
        Get a list of plugin names in a specific category.

        Args:
            category: The category to get plugins for.

        Returns:
            List of plugin names.
        """
        return list(self._categories.get(category, set()))

    def get_all_plugins(self) -> List[str]:
        """
        Get a list of all registered plugin names.

        Returns:
            List of plugin names.
        """
        return list(self._plugins.keys())

    def get_plugins_by_capability(self, capability: str) -> List[str]:
        """
        Get a list of plugin names that provide a specific capability.

        Args:
            capability: The capability to get plugins for.

        Returns:
            List of plugin names.
        """
        return list(self._capabilities.get(capability, set()))

    def get_plugins_by_mime_type(self, mime_type: str) -> List[str]:
        """
        Get a list of file interpreter plugin names that support a specific MIME type.

        Args:
            mime_type: The MIME type to get plugins for.

        Returns:
            List of plugin names.
        """
        return list(self._mime_types.get(mime_type, set()))

    def get_plugins_by_extension(self, extension: str) -> List[str]:
        """
        Get a list of file interpreter plugin names that support a specific file extension.

        Args:
            extension: The file extension to get plugins for (with or without leading dot).

        Returns:
            List of plugin names.
        """
        # Ensure extension starts with a dot
        if extension and not extension.startswith('.'):
            extension = f'.{extension}'

        return list(self._file_extensions.get(extension, set()))

    def get_plugin_metadata(self, name: str) -> Optional[PluginMetadata]:
        """
        Get metadata for a plugin.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin metadata if found, None otherwise.
        """
        plugin_class = self.get_plugin_class(name)
        if not plugin_class:
            return None

        try:
            # Create a temporary instance to get metadata
            temp_instance = plugin_class()
            return temp_instance.metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for plugin '{name}': {str(e)}")
            return None

    def discover_plugins(self, package_name: str) -> int:
        """
        Discover plugins in a package.

        This method recursively searches for plugin classes in the specified package
        and its subpackages, and registers them.

        Args:
            package_name: The name of the package to search in.

        Returns:
            The number of plugins discovered and registered.
        """
        count = 0

        try:
            package = importlib.import_module(package_name)
            package_path = getattr(package, '__path__', [])

            for _, name, is_pkg in pkgutil.iter_modules(package_path):
                full_name = f"{package_name}.{name}"

                try:
                    module = importlib.import_module(full_name)

                    # If it's a package, recursively discover plugins
                    if is_pkg:
                        count += self.discover_plugins(full_name)

                    # Find plugin classes in the module
                    for item_name, item in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(item, PluginBase) and 
                            item is not PluginBase and 
                            item is not DataSourcePlugin and 
                            item is not AnalysisToolPlugin and 
                            item is not VisualizationPlugin and 
                            item is not PlatformPlugin and
                            item is not FileInterpreterPlugin and
                            item is not MetadataExtractorPlugin):

                            if self.register_plugin(item):
                                count += 1

                except Exception as e:
                    logger.error(f"Failed to import module '{full_name}': {str(e)}")

        except Exception as e:
            logger.error(f"Failed to discover plugins in package '{package_name}': {str(e)}")

        return count

    def initialize_all(self) -> bool:
        """
        Initialize all registered plugins.

        Returns:
            True if all plugins were successfully initialized, False otherwise.
        """
        if self._initialized:
            logger.warning("Plugins are already initialized")
            return True

        success = True

        for name in self.get_all_plugins():
            if not self.get_plugin_instance(name):
                success = False

        self._initialized = success
        return success

    def get_file_interpreter_for_file(self, file_path: str, initialize: bool = True) -> Optional[FileInterpreterPlugin]:
        """
        Get a file interpreter plugin instance that can interpret the given file.

        This method tries to find a suitable interpreter based on file extension and MIME type.
        If multiple interpreters are available, it returns the first one that can interpret the file.

        Args:
            file_path: Path to the file to interpret.
            initialize: Whether to initialize the plugin if it's not already instantiated.

        Returns:
            A file interpreter plugin instance, or None if no suitable interpreter is found.
        """
        # Get file extension and MIME type
        extension = os.path.splitext(file_path)[1].lower()
        mime_type = get_mime_type(file_path)

        # Try to find a plugin by extension
        plugin_names = self.get_plugins_by_extension(extension)

        # If no plugin found by extension, try by MIME type
        if not plugin_names:
            plugin_names = self.get_plugins_by_mime_type(mime_type)

        # If still no plugin found, try all file interpreter plugins
        if not plugin_names:
            plugin_names = self.get_plugins_by_category(PluginCategory.FILE_INTERPRETER)

        # Try each plugin until we find one that can interpret the file
        for name in plugin_names:
            plugin = self.get_plugin_instance(name, initialize)
            if plugin and isinstance(plugin, FileInterpreterPlugin) and plugin.can_interpret(file_path, mime_type):
                return cast(FileInterpreterPlugin, plugin)

        logger.warning(f"No suitable file interpreter found for file: {file_path} (MIME type: {mime_type})")
        return None

    def shutdown_all(self) -> bool:
        """
        Shut down all plugin instances.

        Returns:
            True if all plugins were successfully shut down, False otherwise.
        """
        if not self._initialized:
            logger.warning("Plugins are not initialized")
            return True

        success = True

        for name, instance in list(self._instances.items()):
            try:
                if not instance.shutdown():
                    logger.error(f"Failed to shutdown plugin '{name}'")
                    success = False

                del self._instances[name]
            except Exception as e:
                logger.error(f"Error shutting down plugin '{name}': {str(e)}")
                success = False

        self._initialized = False
        return success


# MIME type mapping utilities

def get_mime_type(file_path: str) -> str:
    """
    Get the MIME type for a file based on its extension.

    Args:
        file_path: Path to the file.

    Returns:
        MIME type string, or 'application/octet-stream' if unknown.
    """
    # Initialize mimetypes if not already done
    if not mimetypes.inited:
        mimetypes.init()

    # Add additional MIME types for scientific formats
    additional_types = {
        '.nc': 'application/x-netcdf',
        '.hdf5': 'application/x-hdf5',
        '.h5': 'application/x-hdf5',
        '.fits': 'application/fits',
        '.fts': 'application/fits',
        '.fit': 'application/fits',
        '.nii': 'application/x-nifti',
        '.nii.gz': 'application/x-nifti',
        '.fasta': 'application/fasta',
        '.fa': 'application/fasta',
        '.fastq': 'application/fastq',
        '.fq': 'application/fastq',
        '.gff': 'application/gff',
        '.gtf': 'application/gtf',
        '.bed': 'application/bed',
        '.vcf': 'application/vcf',
        '.bam': 'application/bam',
        '.sam': 'application/sam',
        '.cif': 'chemical/x-cif',
        '.pdb': 'chemical/x-pdb',
        '.mol': 'chemical/x-mdl-molfile',
        '.mol2': 'chemical/x-mol2',
        '.sdf': 'chemical/x-mdl-sdfile',
        '.xyz': 'chemical/x-xyz',
    }

    for ext, mime_type in additional_types.items():
        mimetypes.add_type(mime_type, ext)

    # Get MIME type from file extension
    mime_type, _ = mimetypes.guess_type(file_path)

    # Default to binary if unknown
    if mime_type is None:
        mime_type = 'application/octet-stream'

    return mime_type


# Create a global plugin registry instance
plugin_registry = PluginRegistry()


def register_plugin(plugin_class: Type[PluginBase]) -> bool:
    """
    Register a plugin class with the global registry.

    This function can be used as a decorator.

    Args:
        plugin_class: The plugin class to register.

    Returns:
        True if registration was successful, False otherwise.
    """
    return plugin_registry.register_plugin(plugin_class)


def get_plugin(name: str) -> Optional[PluginBase]:
    """
    Get a plugin instance by name from the global registry.

    Args:
        name: The name of the plugin.

    Returns:
        The plugin instance if found, None otherwise.
    """
    return plugin_registry.get_plugin_instance(name)


def get_plugins_by_category(category: PluginCategory) -> List[str]:
    """
    Get a list of plugin names in a specific category from the global registry.

    Args:
        category: The category to get plugins for.

    Returns:
        List of plugin names.
    """
    return plugin_registry.get_plugins_by_category(category)


def get_all_plugins() -> List[str]:
    """
    Get a list of all registered plugin names from the global registry.

    Returns:
        List of plugin names.
    """
    return plugin_registry.get_all_plugins()


def get_plugins_by_capability(capability: str) -> List[str]:
    """
    Get a list of plugin names that provide a specific capability from the global registry.

    Args:
        capability: The capability to get plugins for.

    Returns:
        List of plugin names.
    """
    return plugin_registry.get_plugins_by_capability(capability)


def get_plugins_by_mime_type(mime_type: str) -> List[str]:
    """
    Get a list of file interpreter plugin names that support a specific MIME type from the global registry.

    Args:
        mime_type: The MIME type to get plugins for.

    Returns:
        List of plugin names.
    """
    return plugin_registry.get_plugins_by_mime_type(mime_type)


def get_plugins_by_extension(extension: str) -> List[str]:
    """
    Get a list of file interpreter plugin names that support a specific file extension from the global registry.

    Args:
        extension: The file extension to get plugins for (with or without leading dot).

    Returns:
        List of plugin names.
    """
    return plugin_registry.get_plugins_by_extension(extension)


def validate_file_interpreter_plugin(plugin: FileInterpreterPlugin) -> Dict[str, bool]:
    """
    Validate a file interpreter plugin to ensure it implements all required methods.

    This function checks if the plugin implements all the required methods and has
    the necessary capabilities declared in its metadata.

    Args:
        plugin: The file interpreter plugin to validate.

    Returns:
        A dictionary mapping validation criteria to boolean results.
    """
    validation_results = {}

    # Check required methods
    validation_results["has_can_interpret"] = hasattr(plugin, "can_interpret") and callable(getattr(plugin, "can_interpret"))
    validation_results["has_get_supported_extensions"] = hasattr(plugin, "get_supported_extensions") and callable(getattr(plugin, "get_supported_extensions"))
    validation_results["has_get_supported_mime_types"] = hasattr(plugin, "get_supported_mime_types") and callable(getattr(plugin, "get_supported_mime_types"))
    validation_results["has_extract_metadata"] = hasattr(plugin, "extract_metadata") and callable(getattr(plugin, "extract_metadata"))
    validation_results["has_generate_preview"] = hasattr(plugin, "generate_preview") and callable(getattr(plugin, "generate_preview"))

    # Check if capabilities declared in metadata are implemented
    capabilities = plugin.metadata.capabilities if hasattr(plugin.metadata, "capabilities") else []

    if FileInterpreterCapability.TEXT_EXTRACTION.value in capabilities:
        validation_results["implements_text_extraction"] = isinstance(plugin, TextExtractionCapability) or (
            hasattr(plugin, "extract_text") and callable(getattr(plugin, "extract_text"))
        )

    if FileInterpreterCapability.PREVIEW_GENERATION.value in capabilities:
        validation_results["implements_preview_generation"] = isinstance(plugin, PreviewGenerationCapability) or (
            hasattr(plugin, "generate_preview") and callable(getattr(plugin, "generate_preview"))
        )

    if FileInterpreterCapability.THUMBNAIL_GENERATION.value in capabilities:
        validation_results["implements_thumbnail_generation"] = isinstance(plugin, ThumbnailGenerationCapability) or (
            hasattr(plugin, "generate_thumbnail") and callable(getattr(plugin, "generate_thumbnail"))
        )

    if FileInterpreterCapability.CONTENT_ANALYSIS.value in capabilities:
        validation_results["implements_content_analysis"] = isinstance(plugin, ContentAnalysisCapability) or (
            hasattr(plugin, "analyze_content") and callable(getattr(plugin, "analyze_content"))
        )

    if FileInterpreterCapability.STRUCTURED_DATA_EXTRACTION.value in capabilities:
        validation_results["implements_structured_data_extraction"] = isinstance(plugin, StructuredDataExtractionCapability) or (
            hasattr(plugin, "extract_structured_data") and callable(getattr(plugin, "extract_structured_data"))
        )

    # Overall validation result
    validation_results["is_valid"] = all([
        validation_results["has_can_interpret"],
        validation_results["has_get_supported_extensions"],
        validation_results["has_get_supported_mime_types"],
        validation_results["has_extract_metadata"],
        validation_results["has_generate_preview"]
    ])

    # Check capability-specific validations
    capability_validations = [
        f"implements_{cap.value}" for cap in FileInterpreterCapability 
        if cap.value in capabilities and f"implements_{cap.value}" in validation_results
    ]

    if capability_validations:
        validation_results["capabilities_valid"] = all(validation_results[key] for key in capability_validations)
        validation_results["is_valid"] = validation_results["is_valid"] and validation_results["capabilities_valid"]

    return validation_results


def validate_metadata_extractor_plugin(plugin: MetadataExtractorPlugin) -> Dict[str, bool]:
    """
    Validate a metadata extractor plugin to ensure it implements all required methods.

    This function checks if the plugin implements all the required methods.

    Args:
        plugin: The metadata extractor plugin to validate.

    Returns:
        A dictionary mapping validation criteria to boolean results.
    """
    validation_results = {}

    # Check required methods
    validation_results["has_can_extract"] = hasattr(plugin, "can_extract") and callable(getattr(plugin, "can_extract"))
    validation_results["has_get_supported_extensions"] = hasattr(plugin, "get_supported_extensions") and callable(getattr(plugin, "get_supported_extensions"))
    validation_results["has_get_supported_mime_types"] = hasattr(plugin, "get_supported_mime_types") and callable(getattr(plugin, "get_supported_mime_types"))
    validation_results["has_extract_metadata"] = hasattr(plugin, "extract_metadata") and callable(getattr(plugin, "extract_metadata"))

    # Overall validation result
    validation_results["is_valid"] = all([
        validation_results["has_can_extract"],
        validation_results["has_get_supported_extensions"],
        validation_results["has_get_supported_mime_types"],
        validation_results["has_extract_metadata"]
    ])

    return validation_results


def validate_plugin(plugin: PluginBase) -> Dict[str, bool]:
    """
    Validate a plugin to ensure it implements all required methods based on its type.

    This function delegates to the appropriate validation function based on the plugin type.

    Args:
        plugin: The plugin to validate.

    Returns:
        A dictionary mapping validation criteria to boolean results.
    """
    if isinstance(plugin, FileInterpreterPlugin):
        return validate_file_interpreter_plugin(plugin)
    elif isinstance(plugin, MetadataExtractorPlugin):
        return validate_metadata_extractor_plugin(plugin)
    else:
        # Basic validation for other plugin types
        validation_results = {}
        validation_results["has_metadata"] = hasattr(plugin, "metadata") and callable(getattr(plugin, "metadata"))
        validation_results["has_initialize"] = hasattr(plugin, "initialize") and callable(getattr(plugin, "initialize"))
        validation_results["has_shutdown"] = hasattr(plugin, "shutdown") and callable(getattr(plugin, "shutdown"))

        validation_results["is_valid"] = all([
            validation_results["has_metadata"],
            validation_results["has_initialize"],
            validation_results["has_shutdown"]
        ])

        return validation_results


def get_file_interpreter_for_file(file_path: str) -> Optional[FileInterpreterPlugin]:
    """
    Get a file interpreter plugin instance that can interpret the given file from the global registry.

    This function tries to find a suitable interpreter based on file extension and MIME type.
    If multiple interpreters are available, it returns the first one that can interpret the file.

    Args:
        file_path: Path to the file to interpret.

    Returns:
        A file interpreter plugin instance, or None if no suitable interpreter is found.
    """
    return plugin_registry.get_file_interpreter_for_file(file_path)


def discover_plugins(package_name: str = "science_data_kit.core.integrations") -> int:
    """
    Discover plugins in a package using the global registry.

    Args:
        package_name: The name of the package to search in.

    Returns:
        The number of plugins discovered and registered.
    """
    return plugin_registry.discover_plugins(package_name)


def initialize_plugins() -> bool:
    """
    Initialize all registered plugins using the global registry.

    Returns:
        True if all plugins were successfully initialized, False otherwise.
    """
    return plugin_registry.initialize_all()


def shutdown_plugins() -> bool:
    """
    Shut down all plugin instances using the global registry.

    Returns:
        True if all plugins were successfully shut down, False otherwise.
    """
    return plugin_registry.shutdown_all()

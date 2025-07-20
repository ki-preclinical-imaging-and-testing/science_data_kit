"""
HDF5 File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for HDF5 files,
with a focus on extracting metadata and generating previews of scientific data.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes
import json

# HDF5 libraries
try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False

# For preview generation
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    StructuredDataExtractionCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class HDF5FileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                         ThumbnailGenerationCapability, StructuredDataExtractionCapability):
    """
    File interpreter plugin for HDF5 files.
    
    This plugin can interpret HDF5 files, extract metadata,
    generate previews and thumbnails, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the HDF5 file interpreter."""
        super().__init__()
        self.supported_extensions = ['.h5', '.hdf5', '.he5', '.h5netcdf']
        self.supported_mime_types = [
            'application/x-hdf5', 
            'application/hdf5',
            'application/x-hdf'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = H5PY_AVAILABLE
        self.can_generate_preview = H5PY_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="HDF5 File Interpreter",
            description="Interprets HDF5 files, extracts metadata, and generates previews of scientific data",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation", "structured_data_extraction"],
            config_schema={
                "max_preview_size": {
                    "type": "integer",
                    "description": "Maximum dimension (width or height) for previews",
                    "default": 1024
                },
                "max_thumbnail_size": {
                    "type": "integer",
                    "description": "Maximum dimension (width or height) for thumbnails",
                    "default": 128
                },
                "max_datasets_to_preview": {
                    "type": "integer",
                    "description": "Maximum number of datasets to include in preview",
                    "default": 4
                },
                "preview_dpi": {
                    "type": "integer",
                    "description": "DPI for preview generation",
                    "default": 100
                },
                "colormap": {
                    "type": "string",
                    "description": "Matplotlib colormap to use for data visualization",
                    "default": "viridis"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse in HDF5 hierarchy",
                    "default": 5
                },
                "max_items_per_group": {
                    "type": "integer",
                    "description": "Maximum number of items to extract per group",
                    "default": 100
                }
            }
        )
    
    def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if this plugin can interpret the given file.
        
        Args:
            file_path: Path to the file to check.
            mime_type: Optional MIME type of the file, if known.
            
        Returns:
            True if the plugin can interpret the file, False otherwise.
        """
        # Check if required libraries are available
        if not H5PY_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file with h5py as a last resort
        try:
            with h5py.File(file_path, 'r') as h5f:
                return True
        except Exception:
            return False
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this interpreter.
        
        Returns:
            List of supported file extensions.
        """
        return self.supported_extensions
    
    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this interpreter.
        
        Returns:
            List of supported MIME types.
        """
        return self.supported_mime_types
    
    def _extract_attributes(self, obj: Any) -> Dict[str, Any]:
        """
        Extract attributes from an HDF5 object.
        
        Args:
            obj: HDF5 object (file, group, or dataset).
            
        Returns:
            Dictionary of attribute key-value pairs.
        """
        attributes = {}
        for attr_name, attr_value in obj.attrs.items():
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(attr_value, np.ndarray):
                attr_value = attr_value.tolist()
            # Convert numpy types to Python native types
            elif hasattr(attr_value, 'item') and callable(getattr(attr_value, 'item')):
                attr_value = attr_value.item()
            # Convert bytes to strings
            elif isinstance(attr_value, bytes):
                try:
                    attr_value = attr_value.decode('utf-8')
                except UnicodeDecodeError:
                    attr_value = str(attr_value)
            
            attributes[attr_name] = attr_value
        
        return attributes
    
    def _extract_group_metadata(self, group: Any, path: str, max_depth: int, 
                               current_depth: int, max_items: int) -> Dict[str, Any]:
        """
        Extract metadata from an HDF5 group recursively.
        
        Args:
            group: HDF5 group object.
            path: Path to the group in the HDF5 file.
            max_depth: Maximum depth to traverse.
            current_depth: Current depth in the hierarchy.
            max_items: Maximum number of items to extract per group.
            
        Returns:
            Dictionary of group metadata.
        """
        if current_depth > max_depth:
            return {"message": f"Max depth ({max_depth}) reached"}
        
        group_info = {
            "type": "group",
            "attributes": self._extract_attributes(group),
            "items": {}
        }
        
        # Limit the number of items to extract
        items = list(group.items())[:max_items]
        
        for name, obj in items:
            item_path = f"{path}/{name}"
            
            if isinstance(obj, h5py.Group):
                # Recursively extract group metadata
                group_info["items"][name] = self._extract_group_metadata(
                    obj, item_path, max_depth, current_depth + 1, max_items
                )
            elif isinstance(obj, h5py.Dataset):
                # Extract dataset metadata
                dataset_info = {
                    "type": "dataset",
                    "shape": obj.shape,
                    "dtype": str(obj.dtype),
                    "attributes": self._extract_attributes(obj)
                }
                
                # Add dataset statistics if it's a numeric type and not too large
                if obj.dtype.kind in 'iufc' and obj.size < 1e6:
                    try:
                        data = obj[()]
                        if isinstance(data, np.ndarray):
                            dataset_info["statistics"] = {
                                "min": float(np.min(data)),
                                "max": float(np.max(data)),
                                "mean": float(np.mean(data)),
                                "std": float(np.std(data))
                            }
                    except Exception:
                        pass
                
                group_info["items"][name] = dataset_info
            else:
                # Handle other types (links, etc.)
                group_info["items"][name] = {
                    "type": "other",
                    "object_type": str(type(obj))
                }
        
        # Add message if there are more items
        if len(group.items()) > max_items:
            group_info["message"] = f"Showing {max_items} of {len(group.items())} items"
        
        return group_info
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the HDF5 file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not H5PY_AVAILABLE:
            metadata['error'] = "h5py library not available"
            return metadata
        
        try:
            with h5py.File(file_path, 'r') as h5f:
                # Extract file attributes
                metadata['attributes'] = self._extract_attributes(h5f)
                
                # Extract file structure (limited to max_depth and max_items_per_group)
                max_depth = 3  # Limit depth for metadata extraction
                max_items = 20  # Limit items per group for metadata extraction
                
                metadata['structure'] = self._extract_group_metadata(
                    h5f, "", max_depth, 0, max_items
                )
                
                # Add HDF5 library version
                metadata['hdf5_version'] = h5py.version.hdf5_version
                
                return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def _get_plottable_datasets(self, h5f: Any, max_depth: int = 5) -> List[Tuple[str, Any, int]]:
        """
        Get a list of datasets that can be plotted, sorted by priority.
        
        Args:
            h5f: HDF5 File object.
            max_depth: Maximum depth to traverse in the hierarchy.
            
        Returns:
            List of (dataset_path, dataset_object, priority) tuples, sorted by priority.
        """
        plottable_datasets = []
        
        def visit_item(name, obj):
            if isinstance(obj, h5py.Dataset):
                # Skip string datasets and empty datasets
                if obj.dtype.kind in 'SU' or obj.size == 0:
                    return
                
                # Calculate priority based on dimensions and attributes
                priority = 0
                
                # Higher priority for 2D datasets (good for heatmaps)
                if len(obj.shape) == 2:
                    priority += 10
                # Medium priority for 1D datasets (good for line plots)
                elif len(obj.shape) == 1:
                    priority += 5
                # Lower priority for higher-dimensional datasets
                else:
                    priority += 1
                
                # Higher priority for datasets with units attribute
                if 'units' in obj.attrs:
                    priority += 2
                
                # Higher priority for datasets with descriptive attributes
                for attr_name in ['long_name', 'description', 'title']:
                    if attr_name in obj.attrs:
                        priority += 1
                
                # Add to list if dataset has data
                if obj.size > 0 and obj.size < 1e6:  # Limit to reasonably sized datasets
                    plottable_datasets.append((name, obj, priority))
        
        # Visit all items in the file
        h5f.visititems(visit_item)
        
        # Sort by priority (descending)
        plottable_datasets.sort(key=lambda x: x[2], reverse=True)
        
        return plottable_datasets
    
    def _plot_dataset(self, dataset_path: str, dataset: Any, fig: 'Figure', ax: Any, 
                     colormap: str = 'viridis') -> None:
        """
        Plot a dataset from the HDF5 file.
        
        Args:
            dataset_path: Path to the dataset in the HDF5 file.
            dataset: HDF5 Dataset object.
            fig: Matplotlib Figure object.
            ax: Matplotlib Axes object.
            colormap: Colormap to use for 2D plots.
        """
        # Get dataset data
        data = dataset[()]
        
        # Get dataset attributes for title and labels
        title = os.path.basename(dataset_path)
        for attr_name in ['long_name', 'description', 'title']:
            if attr_name in dataset.attrs:
                title = dataset.attrs[attr_name]
                break
        
        units = ''
        if 'units' in dataset.attrs:
            units = f" [{dataset.attrs['units']}]"
        
        # Plot based on dimensions
        if len(dataset.shape) == 1:
            # 1D plot (line plot)
            x = np.arange(len(data))
            ax.plot(x, data)
            ax.set_xlabel('Index')
            ax.set_ylabel(f"{title}{units}")
            
        elif len(dataset.shape) == 2:
            # 2D plot (heatmap)
            im = ax.imshow(data, cmap=colormap, aspect='auto')
            ax.set_xlabel('Column Index')
            ax.set_ylabel('Row Index')
            fig.colorbar(im, ax=ax, label=f"{title}{units}")
            
        else:
            # For higher dimensions, plot a slice
            # For 3D, take the middle slice along the first dimension
            if len(dataset.shape) == 3:
                middle_idx = data.shape[0] // 2
                slice_data = data[middle_idx, :, :]
                im = ax.imshow(slice_data, cmap=colormap, aspect='auto')
                ax.set_xlabel('Column Index')
                ax.set_ylabel('Row Index')
                ax.set_title(f"{title}{units} (Slice at index={middle_idx})")
                fig.colorbar(im, ax=ax)
            else:
                # For 4D+, just show text
                ax.text(0.5, 0.5, f"{dataset_path}: {data.shape} (too many dimensions to plot)",
                       horizontalalignment='center', verticalalignment='center')
        
        ax.set_title(title)
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the HDF5 file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview in pixels.
            height: Optional height for the preview in pixels.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not (H5PY_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE):
            return {'error': "Required libraries not available"}
        
        try:
            # Get parameters from kwargs or use defaults
            max_datasets = kwargs.get('max_datasets_to_preview', 4)
            dpi = kwargs.get('preview_dpi', 100)
            colormap = kwargs.get('colormap', 'viridis')
            max_depth = kwargs.get('max_depth', 5)
            
            # Calculate figure size based on width/height if provided
            figsize = (10, 8)  # default size in inches
            if width and height:
                figsize = (width / dpi, height / dpi)
            elif width:
                figsize = (width / dpi, figsize[1])
            elif height:
                figsize = (figsize[0], height / dpi)
            
            # Create figure and subplots
            with h5py.File(file_path, 'r') as h5f:
                # Get plottable datasets
                plottable_datasets = self._get_plottable_datasets(h5f, max_depth)
                
                if not plottable_datasets:
                    # No plottable datasets found, create a text-only preview
                    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                    ax.text(0.5, 0.5, "No plottable datasets found in this HDF5 file",
                           horizontalalignment='center', verticalalignment='center')
                    ax.set_axis_off()
                else:
                    # Limit to max_datasets
                    plottable_datasets = plottable_datasets[:max_datasets]
                    
                    # Calculate subplot grid
                    n_plots = len(plottable_datasets)
                    n_cols = min(2, n_plots)
                    n_rows = (n_plots + n_cols - 1) // n_cols
                    
                    # Create figure and subplots
                    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, dpi=dpi)
                    
                    # Make sure axes is always a 2D array
                    if n_plots == 1:
                        axes = np.array([[axes]])
                    elif n_rows == 1:
                        axes = axes.reshape(1, -1)
                    
                    # Plot each dataset
                    for i, (dataset_path, dataset, _) in enumerate(plottable_datasets):
                        row = i // n_cols
                        col = i % n_cols
                        ax = axes[row, col]
                        
                        try:
                            self._plot_dataset(dataset_path, dataset, fig, ax, colormap)
                        except Exception as e:
                            ax.text(0.5, 0.5, f"Error plotting {dataset_path}: {str(e)}",
                                   horizontalalignment='center', verticalalignment='center')
                    
                    # Hide unused subplots
                    for i in range(n_plots, n_rows * n_cols):
                        row = i // n_cols
                        col = i % n_cols
                        axes[row, col].set_visible(False)
                
                # Add title with filename
                fig.suptitle(os.path.basename(file_path), fontsize=12)
                
                # Adjust layout
                fig.tight_layout(rect=[0, 0, 1, 0.95])  # Leave room for suptitle
                
                # Save or return the figure
                if output_path:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Save to the specified path
                    fig.savefig(output_path, format='png', dpi=dpi)
                    plt.close(fig)
                    return output_path
                else:
                    # Return the image data as bytes
                    img_byte_arr = io.BytesIO()
                    fig.savefig(img_byte_arr, format='png', dpi=dpi)
                    plt.close(fig)
                    return img_byte_arr.getvalue()
        except Exception as e:
            # Return error information
            return {'error': str(e)}
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the HDF5 file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
        # For thumbnails, use a simpler preview with just one dataset
        kwargs['max_datasets_to_preview'] = 1
        kwargs['preview_dpi'] = 72
        
        # Generate the preview with the specified width and height
        return self.generate_preview(
            file_path=file_path,
            output_path=output_path,
            width=width,
            height=height,
            **kwargs
        )
    
    def get_preview_formats(self) -> List[str]:
        """
        Get a list of preview formats supported by this interpreter.
        
        Returns:
            List of supported preview formats.
        """
        return ['image/png']
    
    def extract_structured_data(self, file_path: str, data_type: str, **kwargs) -> Any:
        """
        Extract structured data from the HDF5 file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'dataset', 'group', 'attribute').
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        if not H5PY_AVAILABLE:
            return {'error': "h5py library not available"}
        
        try:
            with h5py.File(file_path, 'r') as h5f:
                if data_type == 'dataset':
                    # Extract a specific dataset
                    dataset_path = kwargs.get('dataset_path')
                    if not dataset_path or dataset_path not in h5f:
                        return {'error': f"Dataset '{dataset_path}' not found"}
                    
                    dataset = h5f[dataset_path]
                    if not isinstance(dataset, h5py.Dataset):
                        return {'error': f"'{dataset_path}' is not a dataset"}
                    
                    # Get dataset data
                    data = dataset[()]
                    if isinstance(data, np.ndarray):
                        data = data.tolist()  # Convert to Python native types
                    
                    # Get dataset attributes
                    attributes = self._extract_attributes(dataset)
                    
                    return {
                        'path': dataset_path,
                        'shape': dataset.shape,
                        'dtype': str(dataset.dtype),
                        'attributes': attributes,
                        'data': data
                    }
                
                elif data_type == 'group':
                    # Extract a specific group
                    group_path = kwargs.get('group_path', '/')
                    if group_path not in h5f:
                        return {'error': f"Group '{group_path}' not found"}
                    
                    group = h5f[group_path]
                    if not isinstance(group, h5py.Group):
                        return {'error': f"'{group_path}' is not a group"}
                    
                    # Get group attributes
                    attributes = self._extract_attributes(group)
                    
                    # Get group items (without data)
                    items = {}
                    for name, obj in group.items():
                        if isinstance(obj, h5py.Dataset):
                            items[name] = {
                                'type': 'dataset',
                                'shape': obj.shape,
                                'dtype': str(obj.dtype)
                            }
                        elif isinstance(obj, h5py.Group):
                            items[name] = {
                                'type': 'group'
                            }
                        else:
                            items[name] = {
                                'type': 'other',
                                'object_type': str(type(obj))
                            }
                    
                    return {
                        'path': group_path,
                        'attributes': attributes,
                        'items': items
                    }
                
                elif data_type == 'attribute':
                    # Extract attributes from a specific object
                    object_path = kwargs.get('object_path', '/')
                    if object_path not in h5f:
                        return {'error': f"Object '{object_path}' not found"}
                    
                    obj = h5f[object_path]
                    
                    # Get object attributes
                    attributes = self._extract_attributes(obj)
                    
                    return {
                        'path': object_path,
                        'attributes': attributes
                    }
                
                elif data_type == 'structure':
                    # Extract the overall structure (limited to max_depth and max_items_per_group)
                    max_depth = kwargs.get('max_depth', 5)
                    max_items = kwargs.get('max_items_per_group', 100)
                    
                    return self._extract_group_metadata(h5f, "", max_depth, 0, max_items)
                
                else:
                    return {'error': f"Unsupported data type: {data_type}"}
        except Exception as e:
            return {'error': str(e)}
    
    def get_supported_data_types(self) -> List[str]:
        """
        Get a list of structured data types supported by this interpreter.
        
        Returns:
            List of supported data types.
        """
        return ['dataset', 'group', 'attribute', 'structure']
"""
NetCDF File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for NetCDF files,
with a focus on extracting metadata and generating previews of scientific data.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes
import json

# NetCDF libraries
try:
    import netCDF4
    from netCDF4 import Dataset
    NETCDF4_AVAILABLE = True
except ImportError:
    NETCDF4_AVAILABLE = False

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
class NetCDFFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                           ThumbnailGenerationCapability, StructuredDataExtractionCapability):
    """
    File interpreter plugin for NetCDF files.
    
    This plugin can interpret NetCDF files, extract metadata,
    generate previews and thumbnails, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the NetCDF file interpreter."""
        super().__init__()
        self.supported_extensions = ['.nc', '.nc4', '.cdf', '.netcdf']
        self.supported_mime_types = [
            'application/x-netcdf', 
            'application/netcdf',
            'application/x-netcdf4'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = NETCDF4_AVAILABLE
        self.can_generate_preview = NETCDF4_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="NetCDF File Interpreter",
            description="Interprets NetCDF files, extracts metadata, and generates previews of scientific data",
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
                "max_variables_to_preview": {
                    "type": "integer",
                    "description": "Maximum number of variables to include in preview",
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
        if not NETCDF4_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file with netCDF4 as a last resort
        try:
            with Dataset(file_path, 'r') as nc:
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
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the NetCDF file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not NETCDF4_AVAILABLE:
            metadata['error'] = "netCDF4 library not available"
            return metadata
        
        try:
            with Dataset(file_path, 'r') as nc:
                # Extract global attributes
                global_attrs = {}
                for attr_name in nc.ncattrs():
                    attr_value = nc.getncattr(attr_name)
                    # Convert numpy types to Python native types for JSON serialization
                    if hasattr(attr_value, 'item') and callable(getattr(attr_value, 'item')):
                        attr_value = attr_value.item()
                    global_attrs[attr_name] = attr_value
                
                # Add global attributes to metadata
                if global_attrs:
                    metadata['global_attributes'] = global_attrs
                
                # Extract dimensions
                dimensions = {}
                for dim_name, dim in nc.dimensions.items():
                    dimensions[dim_name] = {
                        'size': len(dim),
                        'unlimited': dim.isunlimited()
                    }
                
                # Add dimensions to metadata
                if dimensions:
                    metadata['dimensions'] = dimensions
                
                # Extract variables
                variables = {}
                for var_name, var in nc.variables.items():
                    var_info = {
                        'dimensions': var.dimensions,
                        'shape': var.shape,
                        'dtype': str(var.dtype),
                        'attributes': {}
                    }
                    
                    # Extract variable attributes
                    for attr_name in var.ncattrs():
                        attr_value = var.getncattr(attr_name)
                        # Convert numpy types to Python native types for JSON serialization
                        if hasattr(attr_value, 'item') and callable(getattr(attr_value, 'item')):
                            attr_value = attr_value.item()
                        var_info['attributes'][attr_name] = attr_value
                    
                    # Add variable statistics if it's a numeric type and not too large
                    if var.dtype.kind in 'iufc' and var.size < 1e6:
                        try:
                            var_data = var[:]
                            var_info['statistics'] = {
                                'min': float(var_data.min()),
                                'max': float(var_data.max()),
                                'mean': float(var_data.mean()),
                                'std': float(var_data.std())
                            }
                        except Exception:
                            pass
                    
                    variables[var_name] = var_info
                
                # Add variables to metadata
                if variables:
                    metadata['variables'] = variables
                
                # Add NetCDF format information
                metadata['format'] = nc.data_model
                
                return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def _get_plottable_variables(self, nc: 'Dataset') -> List[Tuple[str, int]]:
        """
        Get a list of variables that can be plotted, sorted by priority.
        
        Args:
            nc: NetCDF Dataset object.
            
        Returns:
            List of (variable_name, priority) tuples, sorted by priority.
        """
        plottable_vars = []
        
        for var_name, var in nc.variables.items():
            # Skip coordinate variables (usually 1D variables with the same name as a dimension)
            if var_name in nc.dimensions and len(var.dimensions) == 1 and var.dimensions[0] == var_name:
                continue
            
            # Skip variables with string data type
            if var.dtype.kind in 'SU':
                continue
            
            # Calculate priority based on dimensions and attributes
            priority = 0
            
            # Higher priority for 2D variables (good for heatmaps)
            if len(var.dimensions) == 2:
                priority += 10
            # Medium priority for 1D variables (good for line plots)
            elif len(var.dimensions) == 1:
                priority += 5
            # Lower priority for higher-dimensional variables
            else:
                priority += 1
            
            # Higher priority for variables with standard_name or long_name attributes
            if hasattr(var, 'standard_name') or hasattr(var, 'long_name'):
                priority += 3
            
            # Higher priority for variables with units attribute
            if hasattr(var, 'units'):
                priority += 2
            
            # Add to list if variable has data
            if var.size > 0:
                plottable_vars.append((var_name, priority))
        
        # Sort by priority (descending)
        plottable_vars.sort(key=lambda x: x[1], reverse=True)
        
        return plottable_vars
    
    def _plot_variable(self, nc: 'Dataset', var_name: str, fig: 'Figure', ax: Any, 
                      colormap: str = 'viridis') -> None:
        """
        Plot a variable from the NetCDF file.
        
        Args:
            nc: NetCDF Dataset object.
            var_name: Name of the variable to plot.
            fig: Matplotlib Figure object.
            ax: Matplotlib Axes object.
            colormap: Colormap to use for 2D plots.
        """
        var = nc.variables[var_name]
        
        # Get variable data
        data = var[:]
        
        # Get variable attributes for title and labels
        title = var_name
        if hasattr(var, 'long_name'):
            title = var.long_name
        elif hasattr(var, 'standard_name'):
            title = var.standard_name
        
        units = ''
        if hasattr(var, 'units'):
            units = f" [{var.units}]"
        
        # Plot based on dimensions
        if len(var.dimensions) == 1:
            # 1D plot (line plot)
            x = range(len(data))
            x_label = var.dimensions[0]
            
            # Try to get coordinate variable for x-axis
            if var.dimensions[0] in nc.variables:
                x = nc.variables[var.dimensions[0]][:]
                if hasattr(nc.variables[var.dimensions[0]], 'long_name'):
                    x_label = nc.variables[var.dimensions[0]].long_name
                elif hasattr(nc.variables[var.dimensions[0]], 'standard_name'):
                    x_label = nc.variables[var.dimensions[0]].standard_name
                
                if hasattr(nc.variables[var.dimensions[0]], 'units'):
                    x_label += f" [{nc.variables[var.dimensions[0]].units}]"
            
            ax.plot(x, data)
            ax.set_xlabel(x_label)
            ax.set_ylabel(f"{title}{units}")
            
        elif len(var.dimensions) == 2:
            # 2D plot (heatmap)
            im = ax.imshow(data, cmap=colormap, aspect='auto')
            ax.set_xlabel(var.dimensions[1])
            ax.set_ylabel(var.dimensions[0])
            fig.colorbar(im, ax=ax, label=f"{title}{units}")
            
        else:
            # For higher dimensions, plot a slice
            # For 3D, take the middle slice along the first dimension
            if len(var.dimensions) == 3:
                middle_idx = data.shape[0] // 2
                slice_data = data[middle_idx, :, :]
                im = ax.imshow(slice_data, cmap=colormap, aspect='auto')
                ax.set_xlabel(var.dimensions[2])
                ax.set_ylabel(var.dimensions[1])
                ax.set_title(f"{title}{units} (Slice at {var.dimensions[0]}={middle_idx})")
                fig.colorbar(im, ax=ax)
            else:
                # For 4D+, just show text
                ax.text(0.5, 0.5, f"{var_name}: {data.shape} (too many dimensions to plot)",
                       horizontalalignment='center', verticalalignment='center')
        
        ax.set_title(title)
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the NetCDF file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview in pixels.
            height: Optional height for the preview in pixels.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not (NETCDF4_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE):
            return {'error': "Required libraries not available"}
        
        try:
            # Get parameters from kwargs or use defaults
            max_vars = kwargs.get('max_variables_to_preview', 4)
            dpi = kwargs.get('preview_dpi', 100)
            colormap = kwargs.get('colormap', 'viridis')
            
            # Calculate figure size based on width/height if provided
            figsize = (10, 8)  # default size in inches
            if width and height:
                figsize = (width / dpi, height / dpi)
            elif width:
                figsize = (width / dpi, figsize[1])
            elif height:
                figsize = (figsize[0], height / dpi)
            
            # Create figure and subplots
            with Dataset(file_path, 'r') as nc:
                # Get plottable variables
                plottable_vars = self._get_plottable_variables(nc)
                
                if not plottable_vars:
                    # No plottable variables found, create a text-only preview
                    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                    ax.text(0.5, 0.5, "No plottable variables found in this NetCDF file",
                           horizontalalignment='center', verticalalignment='center')
                    ax.set_axis_off()
                else:
                    # Limit to max_vars
                    plottable_vars = plottable_vars[:max_vars]
                    
                    # Calculate subplot grid
                    n_plots = len(plottable_vars)
                    n_cols = min(2, n_plots)
                    n_rows = (n_plots + n_cols - 1) // n_cols
                    
                    # Create figure and subplots
                    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, dpi=dpi)
                    
                    # Make sure axes is always a 2D array
                    if n_plots == 1:
                        axes = np.array([[axes]])
                    elif n_rows == 1:
                        axes = axes.reshape(1, -1)
                    
                    # Plot each variable
                    for i, (var_name, _) in enumerate(plottable_vars):
                        row = i // n_cols
                        col = i % n_cols
                        ax = axes[row, col]
                        
                        try:
                            self._plot_variable(nc, var_name, fig, ax, colormap)
                        except Exception as e:
                            ax.text(0.5, 0.5, f"Error plotting {var_name}: {str(e)}",
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
        Generate a thumbnail for the NetCDF file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
        # For thumbnails, use a simpler preview with just one variable
        kwargs['max_variables_to_preview'] = 1
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
        Extract structured data from the NetCDF file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'variable', 'dimension').
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        if not NETCDF4_AVAILABLE:
            return {'error': "netCDF4 library not available"}
        
        try:
            with Dataset(file_path, 'r') as nc:
                if data_type == 'variable':
                    # Extract a specific variable
                    var_name = kwargs.get('variable_name')
                    if not var_name or var_name not in nc.variables:
                        return {'error': f"Variable '{var_name}' not found"}
                    
                    var = nc.variables[var_name]
                    
                    # Get variable data
                    data = var[:].tolist()  # Convert to Python native types
                    
                    # Get variable attributes
                    attributes = {}
                    for attr_name in var.ncattrs():
                        attr_value = var.getncattr(attr_name)
                        # Convert numpy types to Python native types
                        if hasattr(attr_value, 'item') and callable(getattr(attr_value, 'item')):
                            attr_value = attr_value.item()
                        attributes[attr_name] = attr_value
                    
                    return {
                        'name': var_name,
                        'dimensions': var.dimensions,
                        'shape': var.shape,
                        'dtype': str(var.dtype),
                        'attributes': attributes,
                        'data': data
                    }
                
                elif data_type == 'dimension':
                    # Extract a specific dimension
                    dim_name = kwargs.get('dimension_name')
                    if not dim_name or dim_name not in nc.dimensions:
                        return {'error': f"Dimension '{dim_name}' not found"}
                    
                    dim = nc.dimensions[dim_name]
                    
                    return {
                        'name': dim_name,
                        'size': len(dim),
                        'unlimited': dim.isunlimited()
                    }
                
                elif data_type == 'global_attributes':
                    # Extract all global attributes
                    attributes = {}
                    for attr_name in nc.ncattrs():
                        attr_value = nc.getncattr(attr_name)
                        # Convert numpy types to Python native types
                        if hasattr(attr_value, 'item') and callable(getattr(attr_value, 'item')):
                            attr_value = attr_value.item()
                        attributes[attr_name] = attr_value
                    
                    return attributes
                
                elif data_type == 'structure':
                    # Extract the overall structure (dimensions and variables)
                    structure = {
                        'dimensions': {},
                        'variables': {}
                    }
                    
                    # Extract dimensions
                    for dim_name, dim in nc.dimensions.items():
                        structure['dimensions'][dim_name] = {
                            'size': len(dim),
                            'unlimited': dim.isunlimited()
                        }
                    
                    # Extract variables (without data)
                    for var_name, var in nc.variables.items():
                        var_info = {
                            'dimensions': var.dimensions,
                            'shape': var.shape,
                            'dtype': str(var.dtype),
                            'attributes': {}
                        }
                        
                        # Extract variable attributes
                        for attr_name in var.ncattrs():
                            attr_value = var.getncattr(attr_name)
                            # Convert numpy types to Python native types
                            if hasattr(attr_value, 'item') and callable(getattr(attr_value, 'item')):
                                attr_value = attr_value.item()
                            var_info['attributes'][attr_name] = attr_value
                        
                        structure['variables'][var_name] = var_info
                    
                    return structure
                
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
        return ['variable', 'dimension', 'global_attributes', 'structure']
"""
FITS File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for FITS (Flexible Image Transport System) files,
with a focus on extracting metadata and generating previews of astronomical data.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes
import json

# FITS libraries
try:
    from astropy.io import fits
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False

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
class FITSFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                         ThumbnailGenerationCapability, StructuredDataExtractionCapability):
    """
    File interpreter plugin for FITS files.
    
    This plugin can interpret FITS (Flexible Image Transport System) files, extract metadata,
    generate previews and thumbnails, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the FITS file interpreter."""
        super().__init__()
        self.supported_extensions = ['.fits', '.fit', '.fts']
        self.supported_mime_types = [
            'application/fits', 
            'image/fits',
            'application/x-fits'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = ASTROPY_AVAILABLE
        self.can_generate_preview = ASTROPY_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="FITS File Interpreter",
            description="Interprets FITS files, extracts metadata, and generates previews of astronomical data",
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
                "max_hdus_to_preview": {
                    "type": "integer",
                    "description": "Maximum number of HDUs to include in preview",
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
        if not ASTROPY_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file with astropy as a last resort
        try:
            with fits.open(file_path) as hdul:
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
        Extract metadata from the FITS file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not ASTROPY_AVAILABLE:
            metadata['error'] = "astropy library not available"
            return metadata
        
        try:
            with fits.open(file_path) as hdul:
                # Add FITS format information
                metadata['format'] = 'FITS'
                metadata['num_hdus'] = len(hdul)
                
                # Extract HDU information
                hdus = []
                for i, hdu in enumerate(hdul):
                    hdu_info = {
                        'index': i,
                        'name': hdu.name,
                        'type': hdu.__class__.__name__,
                        'header': {}
                    }
                    
                    # Extract header information
                    for key in hdu.header:
                        # Skip history and comment entries
                        if key not in ('HISTORY', 'COMMENT'):
                            value = hdu.header[key]
                            # Convert non-serializable types to strings
                            if not isinstance(value, (str, int, float, bool, type(None))):
                                value = str(value)
                            hdu_info['header'][key] = value
                    
                    # Add data shape information if available
                    if hasattr(hdu, 'data') and hdu.data is not None:
                        hdu_info['data_shape'] = hdu.data.shape
                        hdu_info['data_type'] = str(hdu.data.dtype)
                        
                        # Add basic statistics for image data
                        if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
                            if hdu.data.size > 0 and hdu.data.ndim >= 2:
                                try:
                                    hdu_info['statistics'] = {
                                        'min': float(np.nanmin(hdu.data)),
                                        'max': float(np.nanmax(hdu.data)),
                                        'mean': float(np.nanmean(hdu.data)),
                                        'std': float(np.nanstd(hdu.data))
                                    }
                                except Exception:
                                    pass
                        
                        # Add table information for table data
                        elif isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
                            hdu_info['columns'] = [
                                {
                                    'name': col.name,
                                    'format': col.format,
                                    'unit': col.unit if hasattr(col, 'unit') else None
                                }
                                for col in hdu.columns
                            ]
                            hdu_info['num_rows'] = hdu.data.shape[0] if hdu.data is not None else 0
                    
                    hdus.append(hdu_info)
                
                # Add HDUs to metadata
                metadata['hdus'] = hdus
                
                # Extract common astronomical metadata
                primary_header = hdul[0].header
                astro_metadata = {}
                
                # Common FITS keywords for astronomical data
                astro_keywords = [
                    'TELESCOP', 'INSTRUME', 'OBJECT', 'OBSERVER',
                    'DATE-OBS', 'EXPTIME', 'FILTER', 'AIRMASS',
                    'RA', 'DEC', 'EQUINOX', 'RADECSYS',
                    'WCSAXES', 'CRVAL1', 'CRVAL2', 'CRPIX1', 'CRPIX2',
                    'CTYPE1', 'CTYPE2', 'CD1_1', 'CD1_2', 'CD2_1', 'CD2_2'
                ]
                
                for keyword in astro_keywords:
                    if keyword in primary_header:
                        value = primary_header[keyword]
                        # Convert non-serializable types to strings
                        if not isinstance(value, (str, int, float, bool, type(None))):
                            value = str(value)
                        astro_metadata[keyword] = value
                
                # Add astronomical metadata if any was found
                if astro_metadata:
                    metadata['astronomical_metadata'] = astro_metadata
                
                return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def _get_plottable_hdus(self, hdul: 'fits.HDUList') -> List[Tuple[int, str, int]]:
        """
        Get a list of HDUs that can be plotted, sorted by priority.
        
        Args:
            hdul: FITS HDUList object.
            
        Returns:
            List of (hdu_index, hdu_name, priority) tuples, sorted by priority.
        """
        plottable_hdus = []
        
        for i, hdu in enumerate(hdul):
            # Skip HDUs without data
            if not hasattr(hdu, 'data') or hdu.data is None:
                continue
            
            # Calculate priority based on HDU type and data shape
            priority = 0
            
            # Higher priority for image HDUs
            if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
                # Check if it's an actual image (at least 2D)
                if hdu.data.ndim >= 2:
                    priority += 10
                    
                    # Higher priority for 2D images (easier to visualize)
                    if hdu.data.ndim == 2:
                        priority += 5
                    
                    # Higher priority for primary HDU
                    if i == 0:
                        priority += 3
                    
                    # Add to list
                    plottable_hdus.append((i, hdu.name, priority))
            
            # Medium priority for table HDUs
            elif isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
                priority += 5
                
                # Add to list
                plottable_hdus.append((i, hdu.name, priority))
        
        # Sort by priority (descending)
        plottable_hdus.sort(key=lambda x: x[2], reverse=True)
        
        return plottable_hdus
    
    def _plot_hdu(self, hdu: 'fits.HDU', fig: 'Figure', ax: Any, 
                 colormap: str = 'viridis') -> None:
        """
        Plot an HDU from the FITS file.
        
        Args:
            hdu: FITS HDU object.
            fig: Matplotlib Figure object.
            ax: Matplotlib Axes object.
            colormap: Colormap to use for image plots.
        """
        # Skip HDUs without data
        if not hasattr(hdu, 'data') or hdu.data is None:
            ax.text(0.5, 0.5, f"{hdu.name}: No data",
                   horizontalalignment='center', verticalalignment='center')
            return
        
        # Get title from OBJECT keyword if available
        title = hdu.name
        if 'OBJECT' in hdu.header:
            title = f"{hdu.header['OBJECT']} ({hdu.name})"
        
        # Plot based on HDU type
        if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
            # Image HDU
            if hdu.data.ndim == 2:
                # 2D image
                im = ax.imshow(hdu.data, cmap=colormap, origin='lower')
                fig.colorbar(im, ax=ax)
            elif hdu.data.ndim > 2:
                # Higher dimensional image, take a slice
                slice_indices = tuple([0] * (hdu.data.ndim - 2) + [slice(None), slice(None)])
                slice_data = hdu.data[slice_indices]
                im = ax.imshow(slice_data, cmap=colormap, origin='lower')
                fig.colorbar(im, ax=ax)
                ax.set_title(f"{title} (First 2D slice)")
            else:
                # 1D data
                ax.plot(hdu.data)
                ax.set_xlabel('Pixel')
                ax.set_ylabel('Value')
        
        elif isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
            # Table HDU
            # For tables, show a summary of the columns
            column_names = [col.name for col in hdu.columns]
            
            # Create a text representation of the table structure
            table_text = f"Table with {len(column_names)} columns and {len(hdu.data)} rows\n\n"
            table_text += "Columns:\n"
            for col in hdu.columns:
                col_info = f"- {col.name} ({col.format})"
                if hasattr(col, 'unit') and col.unit:
                    col_info += f" [{col.unit}]"
                table_text += col_info + "\n"
            
            # Display the text
            ax.text(0.5, 0.5, table_text,
                   horizontalalignment='center', verticalalignment='center',
                   fontsize=9, family='monospace')
            ax.set_axis_off()
        
        else:
            # Other HDU types
            ax.text(0.5, 0.5, f"{hdu.name}: {type(hdu).__name__}\nData shape: {hdu.data.shape}",
                   horizontalalignment='center', verticalalignment='center')
        
        # Set title if not already set
        if not ax.get_title():
            ax.set_title(title)
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the FITS file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview in pixels.
            height: Optional height for the preview in pixels.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not (ASTROPY_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE):
            return {'error': "Required libraries not available"}
        
        try:
            # Get parameters from kwargs or use defaults
            max_hdus = kwargs.get('max_hdus_to_preview', 4)
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
            with fits.open(file_path) as hdul:
                # Get plottable HDUs
                plottable_hdus = self._get_plottable_hdus(hdul)
                
                if not plottable_hdus:
                    # No plottable HDUs found, create a text-only preview
                    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                    ax.text(0.5, 0.5, "No plottable data found in this FITS file",
                           horizontalalignment='center', verticalalignment='center')
                    ax.set_axis_off()
                else:
                    # Limit to max_hdus
                    plottable_hdus = plottable_hdus[:max_hdus]
                    
                    # Calculate subplot grid
                    n_plots = len(plottable_hdus)
                    n_cols = min(2, n_plots)
                    n_rows = (n_plots + n_cols - 1) // n_cols
                    
                    # Create figure and subplots
                    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, dpi=dpi)
                    
                    # Make sure axes is always a 2D array
                    if n_plots == 1:
                        axes = np.array([[axes]])
                    elif n_rows == 1:
                        axes = axes.reshape(1, -1)
                    
                    # Plot each HDU
                    for i, (hdu_index, hdu_name, _) in enumerate(plottable_hdus):
                        row = i // n_cols
                        col = i % n_cols
                        ax = axes[row, col]
                        
                        try:
                            self._plot_hdu(hdul[hdu_index], fig, ax, colormap)
                        except Exception as e:
                            ax.text(0.5, 0.5, f"Error plotting {hdu_name}: {str(e)}",
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
        Generate a thumbnail for the FITS file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
        # For thumbnails, use a simpler preview with just one HDU
        kwargs['max_hdus_to_preview'] = 1
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
        Extract structured data from the FITS file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'hdu', 'header', 'image', 'table').
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        if not ASTROPY_AVAILABLE:
            return {'error': "astropy library not available"}
        
        try:
            with fits.open(file_path) as hdul:
                if data_type == 'hdu':
                    # Extract a specific HDU
                    hdu_index = kwargs.get('hdu_index', 0)
                    if hdu_index < 0 or hdu_index >= len(hdul):
                        return {'error': f"HDU index {hdu_index} out of range"}
                    
                    hdu = hdul[hdu_index]
                    
                    # Create HDU info
                    hdu_info = {
                        'index': hdu_index,
                        'name': hdu.name,
                        'type': hdu.__class__.__name__,
                        'header': {}
                    }
                    
                    # Extract header information
                    for key in hdu.header:
                        # Skip history and comment entries
                        if key not in ('HISTORY', 'COMMENT'):
                            value = hdu.header[key]
                            # Convert non-serializable types to strings
                            if not isinstance(value, (str, int, float, bool, type(None))):
                                value = str(value)
                            hdu_info['header'][key] = value
                    
                    # Add data information if available
                    if hasattr(hdu, 'data') and hdu.data is not None:
                        hdu_info['data_shape'] = hdu.data.shape
                        hdu_info['data_type'] = str(hdu.data.dtype)
                        
                        # Include data if requested and not too large
                        include_data = kwargs.get('include_data', False)
                        max_data_size = kwargs.get('max_data_size', 1e6)
                        
                        if include_data and hdu.data.size <= max_data_size:
                            # Convert data to a serializable format
                            if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
                                # For image data, convert to list
                                hdu_info['data'] = hdu.data.tolist()
                            elif isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
                                # For table data, convert to records
                                records = []
                                for row in hdu.data:
                                    record = {}
                                    for i, col in enumerate(hdu.columns):
                                        value = row[i]
                                        # Convert non-serializable types
                                        if hasattr(value, 'item') and callable(getattr(value, 'item')):
                                            value = value.item()
                                        record[col.name] = value
                                    records.append(record)
                                hdu_info['data'] = records
                    
                    return hdu_info
                
                elif data_type == 'header':
                    # Extract a specific header
                    hdu_index = kwargs.get('hdu_index', 0)
                    if hdu_index < 0 or hdu_index >= len(hdul):
                        return {'error': f"HDU index {hdu_index} out of range"}
                    
                    header = hdul[hdu_index].header
                    
                    # Convert header to dictionary
                    header_dict = {}
                    for key in header:
                        # Skip history and comment entries
                        if key not in ('HISTORY', 'COMMENT'):
                            value = header[key]
                            # Convert non-serializable types to strings
                            if not isinstance(value, (str, int, float, bool, type(None))):
                                value = str(value)
                            header_dict[key] = value
                    
                    return header_dict
                
                elif data_type == 'image':
                    # Extract image data from a specific HDU
                    hdu_index = kwargs.get('hdu_index', 0)
                    if hdu_index < 0 or hdu_index >= len(hdul):
                        return {'error': f"HDU index {hdu_index} out of range"}
                    
                    hdu = hdul[hdu_index]
                    
                    # Check if HDU has image data
                    if not hasattr(hdu, 'data') or hdu.data is None:
                        return {'error': f"HDU {hdu_index} has no data"}
                    
                    if not isinstance(hdu, fits.ImageHDU) and not isinstance(hdu, fits.PrimaryHDU):
                        return {'error': f"HDU {hdu_index} is not an image HDU"}
                    
                    # Get image data
                    image_data = hdu.data
                    
                    # For higher dimensional data, take a slice if requested
                    if image_data.ndim > 2:
                        slice_indices = kwargs.get('slice_indices')
                        if slice_indices:
                            try:
                                image_data = image_data[tuple(slice_indices)]
                            except Exception as e:
                                return {'error': f"Error slicing data: {str(e)}"}
                        else:
                            # Default to first 2D slice
                            slice_indices = tuple([0] * (image_data.ndim - 2) + [slice(None), slice(None)])
                            image_data = image_data[slice_indices]
                    
                    # Check if resulting data is 2D
                    if image_data.ndim != 2:
                        return {'error': f"Resulting data is not 2D (shape: {image_data.shape})"}
                    
                    # Get image statistics
                    stats = {
                        'min': float(np.nanmin(image_data)),
                        'max': float(np.nanmax(image_data)),
                        'mean': float(np.nanmean(image_data)),
                        'std': float(np.nanstd(image_data))
                    }
                    
                    # Return image data and statistics
                    return {
                        'shape': image_data.shape,
                        'dtype': str(image_data.dtype),
                        'statistics': stats,
                        'data': image_data.tolist() if kwargs.get('include_data', False) else None
                    }
                
                elif data_type == 'table':
                    # Extract table data from a specific HDU
                    hdu_index = kwargs.get('hdu_index', 1)  # Default to first extension
                    if hdu_index < 0 or hdu_index >= len(hdul):
                        return {'error': f"HDU index {hdu_index} out of range"}
                    
                    hdu = hdul[hdu_index]
                    
                    # Check if HDU has table data
                    if not hasattr(hdu, 'data') or hdu.data is None:
                        return {'error': f"HDU {hdu_index} has no data"}
                    
                    if not isinstance(hdu, fits.BinTableHDU) and not isinstance(hdu, fits.TableHDU):
                        return {'error': f"HDU {hdu_index} is not a table HDU"}
                    
                    # Get table information
                    columns = [
                        {
                            'name': col.name,
                            'format': col.format,
                            'unit': col.unit if hasattr(col, 'unit') else None
                        }
                        for col in hdu.columns
                    ]
                    
                    # Get table data if requested
                    include_data = kwargs.get('include_data', False)
                    max_rows = kwargs.get('max_rows', 100)
                    
                    table_data = None
                    if include_data:
                        # Limit number of rows
                        num_rows = min(len(hdu.data), max_rows)
                        
                        # Convert to records
                        records = []
                        for i in range(num_rows):
                            record = {}
                            for j, col in enumerate(hdu.columns):
                                value = hdu.data[i][j]
                                # Convert non-serializable types
                                if hasattr(value, 'item') and callable(getattr(value, 'item')):
                                    value = value.item()
                                record[col.name] = value
                            records.append(record)
                        
                        table_data = records
                    
                    # Return table information
                    return {
                        'num_rows': len(hdu.data),
                        'num_columns': len(columns),
                        'columns': columns,
                        'data': table_data
                    }
                
                elif data_type == 'structure':
                    # Extract the overall structure of the FITS file
                    structure = {
                        'num_hdus': len(hdul),
                        'hdus': []
                    }
                    
                    # Extract basic information for each HDU
                    for i, hdu in enumerate(hdul):
                        hdu_info = {
                            'index': i,
                            'name': hdu.name,
                            'type': hdu.__class__.__name__
                        }
                        
                        # Add data information if available
                        if hasattr(hdu, 'data') and hdu.data is not None:
                            hdu_info['data_shape'] = hdu.data.shape
                            hdu_info['data_type'] = str(hdu.data.dtype)
                            
                            # Add specific information based on HDU type
                            if isinstance(hdu, fits.ImageHDU) or isinstance(hdu, fits.PrimaryHDU):
                                hdu_info['data_kind'] = 'image'
                            elif isinstance(hdu, fits.BinTableHDU) or isinstance(hdu, fits.TableHDU):
                                hdu_info['data_kind'] = 'table'
                                hdu_info['num_rows'] = len(hdu.data)
                                hdu_info['num_columns'] = len(hdu.columns)
                        
                        # Add key header keywords
                        key_keywords = ['EXTNAME', 'EXTVER', 'OBJECT', 'DATE-OBS', 'TELESCOP', 'INSTRUME']
                        header_info = {}
                        for keyword in key_keywords:
                            if keyword in hdu.header:
                                value = hdu.header[keyword]
                                # Convert non-serializable types to strings
                                if not isinstance(value, (str, int, float, bool, type(None))):
                                    value = str(value)
                                header_info[keyword] = value
                        
                        if header_info:
                            hdu_info['key_header_keywords'] = header_info
                        
                        structure['hdus'].append(hdu_info)
                    
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
        return ['hdu', 'header', 'image', 'table', 'structure']
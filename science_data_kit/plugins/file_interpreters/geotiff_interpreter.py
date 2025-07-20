"""
GeoTIFF File Interpreter Plugin for Science Data Kit.

This module provides a plugin for interpreting GeoTIFF files, extracting
geospatial metadata, and generating previews.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes

# GeoTIFF libraries
try:
    import rasterio
    from rasterio.plot import show
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

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
class GeoTIFFFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                           ThumbnailGenerationCapability, StructuredDataExtractionCapability):
    """
    File interpreter plugin for GeoTIFF files.
    
    This plugin can interpret GeoTIFF files, extract geospatial metadata,
    generate previews and thumbnails, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the GeoTIFF file interpreter."""
        super().__init__()
        self.supported_extensions = ['.tif', '.tiff']
        self.supported_mime_types = [
            'image/tiff',
            'image/geotiff',
            'application/geotiff',
            'application/x-geotiff'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = RASTERIO_AVAILABLE
        self.can_generate_preview = RASTERIO_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="GeoTIFF File Interpreter",
            description="Interprets GeoTIFF files, extracts geospatial metadata, and generates previews",
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
        if not RASTERIO_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            # Try to open the file with rasterio to check if it's a GeoTIFF
            try:
                with rasterio.open(file_path) as src:
                    # Check if the file has geospatial metadata
                    return src.crs is not None
            except Exception:
                # If rasterio can't open it as a GeoTIFF, defer to the regular image interpreter
                return False
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
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
        Extract metadata from the GeoTIFF file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not RASTERIO_AVAILABLE:
            metadata['error'] = "rasterio library not available"
            return metadata
        
        try:
            with rasterio.open(file_path) as src:
                # Add GeoTIFF format information
                metadata['format'] = 'GeoTIFF'
                
                # Add basic raster information
                metadata.update({
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,  # Number of bands
                    'dtype': str(src.dtypes[0]),
                    'driver': src.driver,
                    'transform': src.transform.to_gdal() if src.transform else None,
                    'nodata': src.nodata
                })
                
                # Add coordinate reference system information
                if src.crs:
                    metadata['crs'] = {
                        'proj4': src.crs.to_proj4(),
                        'wkt': src.crs.to_wkt(),
                        'epsg': src.crs.to_epsg()
                    }
                
                # Add bounds information
                if src.bounds:
                    metadata['bounds'] = {
                        'left': src.bounds.left,
                        'bottom': src.bounds.bottom,
                        'right': src.bounds.right,
                        'top': src.bounds.top
                    }
                
                # Add resolution information
                if src.res:
                    metadata['resolution'] = {
                        'x': src.res[0],
                        'y': src.res[1]
                    }
                
                # Add band information
                bands = []
                for i in range(1, src.count + 1):
                    band_info = {
                        'index': i,
                        'description': src.descriptions[i-1] or f"Band {i}",
                        'dtype': str(src.dtypes[i-1])
                    }
                    
                    # Add band statistics
                    try:
                        band_data = src.read(i)
                        if band_data.size > 0:
                            band_info['statistics'] = {
                                'min': float(np.nanmin(band_data)),
                                'max': float(np.nanmax(band_data)),
                                'mean': float(np.nanmean(band_data)),
                                'std': float(np.nanstd(band_data))
                            }
                    except Exception:
                        pass
                    
                    bands.append(band_info)
                
                metadata['bands'] = bands
                
                # Add tags/metadata from the GeoTIFF
                if src.tags():
                    metadata['tags'] = src.tags()
                
                return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, width: Optional[int] = None, height: Optional[int] = None, **kwargs) -> Any:
        """
        Generate a preview for the GeoTIFF file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview or the preview data.
        """
        if not self.can_generate_preview:
            return None
        
        # Get configuration
        colormap = kwargs.get('colormap', 'viridis')
        dpi = kwargs.get('preview_dpi', 100)
        
        # Create a temporary file if output_path is not provided
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            temp_file = True
        else:
            temp_file = False
        
        try:
            with rasterio.open(file_path) as src:
                # Determine figure size based on aspect ratio
                aspect_ratio = src.height / src.width
                if width and height:
                    figsize = (width / dpi, height / dpi)
                elif width:
                    figsize = (width / dpi, width * aspect_ratio / dpi)
                elif height:
                    figsize = (height / aspect_ratio / dpi, height / dpi)
                else:
                    # Default size
                    max_size = kwargs.get('max_preview_size', 1024)
                    if src.width > src.height:
                        figsize = (max_size / dpi, max_size * aspect_ratio / dpi)
                    else:
                        figsize = (max_size / aspect_ratio / dpi, max_size / dpi)
                
                # Create figure and plot
                fig = Figure(figsize=figsize, dpi=dpi)
                canvas = FigureCanvas(fig)
                ax = fig.add_subplot(111)
                
                # Read the data
                if src.count == 1:
                    # Single band - plot as grayscale or with colormap
                    data = src.read(1)
                    show(data, ax=ax, cmap=colormap, title=f"GeoTIFF Preview: {os.path.basename(file_path)}")
                elif src.count == 3:
                    # Three bands - plot as RGB
                    data = src.read((1, 2, 3))
                    # Normalize data for RGB display
                    data = np.transpose(data, (1, 2, 0))
                    data = (data - data.min()) / (data.max() - data.min())
                    ax.imshow(data)
                    ax.set_title(f"GeoTIFF Preview: {os.path.basename(file_path)}")
                else:
                    # Multiple bands - plot first band with colormap
                    data = src.read(1)
                    show(data, ax=ax, cmap=colormap, title=f"GeoTIFF Preview (Band 1): {os.path.basename(file_path)}")
                
                # Add colorbar
                if src.count == 1 or src.count > 3:
                    plt.colorbar(ax.get_images()[0], ax=ax)
                
                # Remove axis ticks for cleaner preview
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Add coordinate reference system information
                if src.crs:
                    ax.text(0.01, 0.01, f"CRS: {src.crs.to_string()}", transform=ax.transAxes, 
                            fontsize=8, verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
                
                # Save the figure
                fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
                
                if temp_file:
                    # Read the file and return the data
                    with open(output_path, 'rb') as f:
                        data = f.read()
                    os.unlink(output_path)
                    return data
                else:
                    return output_path
        except Exception as e:
            if temp_file and os.path.exists(output_path):
                os.unlink(output_path)
            raise e
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None, width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the GeoTIFF file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail.
            height: Height for the thumbnail.
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail or the thumbnail data.
        """
        # For thumbnails, we'll use the same method as for previews but with smaller dimensions
        return self.generate_preview(
            file_path=file_path,
            output_path=output_path,
            width=width,
            height=height,
            **kwargs
        )
    
    def get_preview_formats(self) -> List[str]:
        """
        Get a list of supported preview formats.
        
        Returns:
            List of supported preview formats.
        """
        return ['png', 'jpg', 'svg']
    
    def extract_structured_data(self, file_path: str, data_type: str, **kwargs) -> Any:
        """
        Extract structured data from the GeoTIFF file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract.
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        if not RASTERIO_AVAILABLE:
            return None
        
        try:
            with rasterio.open(file_path) as src:
                if data_type == 'raster_data':
                    # Extract raster data
                    band = kwargs.get('band', 1)
                    if band > src.count:
                        band = 1
                    
                    # Read the data
                    data = src.read(band)
                    
                    # Convert to list for JSON serialization
                    return {
                        'data': data.tolist(),
                        'band': band,
                        'width': src.width,
                        'height': src.height,
                        'dtype': str(data.dtype),
                        'nodata': src.nodata
                    }
                
                elif data_type == 'metadata':
                    # Return metadata as structured data
                    return self.extract_metadata(file_path)
                
                elif data_type == 'bounds':
                    # Return bounds information
                    if src.bounds:
                        return {
                            'left': src.bounds.left,
                            'bottom': src.bounds.bottom,
                            'right': src.bounds.right,
                            'top': src.bounds.top,
                            'crs': src.crs.to_string() if src.crs else None
                        }
                    return None
                
                elif data_type == 'statistics':
                    # Calculate statistics for each band
                    stats = []
                    for i in range(1, src.count + 1):
                        band_data = src.read(i)
                        if band_data.size > 0:
                            stats.append({
                                'band': i,
                                'min': float(np.nanmin(band_data)),
                                'max': float(np.nanmax(band_data)),
                                'mean': float(np.nanmean(band_data)),
                                'std': float(np.nanstd(band_data)),
                                'median': float(np.nanmedian(band_data)),
                                'histogram': np.histogram(band_data[~np.isnan(band_data)], bins=10)[0].tolist()
                            })
                    return stats
                
                return None
        except Exception:
            return None
    
    def get_supported_data_types(self) -> List[str]:
        """
        Get a list of structured data types supported by this interpreter.
        
        Returns:
            List of supported data types.
        """
        return ['raster_data', 'metadata', 'bounds', 'statistics']
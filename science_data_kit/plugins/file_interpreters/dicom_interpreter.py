"""
DICOM File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for DICOM (Digital Imaging and Communications in Medicine) files,
with a focus on extracting metadata and generating previews of medical imaging data.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes
import json

# DICOM libraries
try:
    import pydicom
    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False

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
class DICOMFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                          ThumbnailGenerationCapability, StructuredDataExtractionCapability):
    """
    File interpreter plugin for DICOM files.
    
    This plugin can interpret DICOM (Digital Imaging and Communications in Medicine) files, extract metadata,
    generate previews and thumbnails, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the DICOM file interpreter."""
        super().__init__()
        self.supported_extensions = ['.dcm', '.dicom', '.dic']
        self.supported_mime_types = [
            'application/dicom', 
            'image/dicom',
            'application/x-dicom'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = PYDICOM_AVAILABLE
        self.can_generate_preview = PYDICOM_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="DICOM File Interpreter",
            description="Interprets DICOM files, extracts metadata, and generates previews of medical imaging data",
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
                    "default": "gray"
                },
                "window_center": {
                    "type": "integer",
                    "description": "Window center for DICOM image display",
                    "default": None
                },
                "window_width": {
                    "type": "integer",
                    "description": "Window width for DICOM image display",
                    "default": None
                },
                "fhir_viewer_url": {
                    "type": "string",
                    "description": "URL for FHIR viewer integration",
                    "default": "https://ohif-viewer-url/viewer/"
                }
            }
        )
    
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        # Add DICOM MIME type to the system
        mimetypes.add_type('application/dicom', '.dcm')
        mimetypes.add_type('application/dicom', '.dicom')
        mimetypes.add_type('application/dicom', '.dic')
        
        return True
    
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise.
        """
        return True
    
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
        if not PYDICOM_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file with pydicom as a last resort
        try:
            pydicom.dcmread(file_path)
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
        Extract metadata from the DICOM file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not PYDICOM_AVAILABLE:
            metadata['error'] = "pydicom library not available"
            return metadata
        
        try:
            # Read DICOM file
            ds = pydicom.dcmread(file_path)
            
            # Add DICOM format information
            metadata['format'] = 'DICOM'
            
            # Extract DICOM metadata
            dicom_metadata = {}
            
            # Common DICOM elements to extract
            common_elements = [
                # Patient information
                'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex', 'PatientAge',
                # Study information
                'StudyInstanceUID', 'StudyID', 'StudyDate', 'StudyTime', 'StudyDescription',
                # Series information
                'SeriesInstanceUID', 'SeriesNumber', 'SeriesDate', 'SeriesTime', 'SeriesDescription',
                # Image information
                'SOPInstanceUID', 'SOPClassUID', 'InstanceNumber', 'ImageType', 'ImageComments',
                # Acquisition information
                'Modality', 'Manufacturer', 'ManufacturerModelName', 'SoftwareVersions',
                # Technical parameters
                'KVP', 'ExposureTime', 'XRayTubeCurrent', 'Exposure', 'ExposureInuAs',
                # Image dimensions
                'Rows', 'Columns', 'PixelSpacing', 'SliceThickness', 'SpacingBetweenSlices',
                # Window settings
                'WindowCenter', 'WindowWidth',
                # Other
                'InstitutionName', 'ReferringPhysicianName', 'PerformingPhysicianName'
            ]
            
            # Extract common elements
            for element in common_elements:
                if hasattr(ds, element):
                    value = getattr(ds, element)
                    # Convert non-serializable types to strings
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        value = str(value)
                    dicom_metadata[element] = value
            
            # Add image dimensions if available
            if hasattr(ds, 'pixel_array'):
                dicom_metadata['ImageDimensions'] = {
                    'Rows': int(ds.Rows) if hasattr(ds, 'Rows') else None,
                    'Columns': int(ds.Columns) if hasattr(ds, 'Columns') else None,
                    'NumberOfFrames': int(ds.NumberOfFrames) if hasattr(ds, 'NumberOfFrames') else 1
                }
            
            # Add DICOM metadata to overall metadata
            metadata['dicom_metadata'] = dicom_metadata
            
            # Add FHIR viewer URL if available
            if hasattr(ds, 'StudyInstanceUID'):
                metadata['fhir_viewer_url'] = f"https://ohif-viewer-url/viewer/{ds.StudyInstanceUID}"
            
            return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the DICOM file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview in pixels.
            height: Optional height for the preview in pixels.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not (PYDICOM_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE):
            return {'error': "Required libraries not available"}
        
        try:
            # Get parameters from kwargs or use defaults
            dpi = kwargs.get('preview_dpi', 100)
            colormap = kwargs.get('colormap', 'gray')
            window_center = kwargs.get('window_center', None)
            window_width = kwargs.get('window_width', None)
            
            # Calculate figure size based on width/height if provided
            figsize = (10, 8)  # default size in inches
            if width and height:
                figsize = (width / dpi, height / dpi)
            elif width:
                figsize = (width / dpi, figsize[1])
            elif height:
                figsize = (figsize[0], height / dpi)
            
            # Read DICOM file
            ds = pydicom.dcmread(file_path)
            
            # Create figure
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            
            # Check if pixel data is available
            if hasattr(ds, 'pixel_array'):
                # Get pixel array
                pixel_array = ds.pixel_array
                
                # Handle multi-frame images
                if len(pixel_array.shape) > 2:
                    # For multi-frame images, display the middle frame
                    frame_index = pixel_array.shape[0] // 2
                    pixel_array = pixel_array[frame_index]
                
                # Apply window center/width if provided
                if window_center is not None and window_width is not None:
                    # Convert to float for calculations
                    pixel_array = pixel_array.astype(float)
                    
                    # Apply window
                    min_value = window_center - window_width // 2
                    max_value = window_center + window_width // 2
                    
                    # Clip values outside the window
                    pixel_array = np.clip(pixel_array, min_value, max_value)
                    
                    # Normalize to 0-1 range
                    pixel_array = (pixel_array - min_value) / (max_value - min_value)
                else:
                    # Auto-window by normalizing to 0-1 range
                    min_value = np.min(pixel_array)
                    max_value = np.max(pixel_array)
                    
                    if min_value != max_value:
                        pixel_array = (pixel_array - min_value) / (max_value - min_value)
                    else:
                        # Handle case where all pixels have the same value
                        pixel_array = np.zeros_like(pixel_array)
                
                # Display the image
                im = ax.imshow(pixel_array, cmap=colormap)
                fig.colorbar(im, ax=ax)
                
                # Add title with patient and study information
                title = "DICOM Image"
                if hasattr(ds, 'PatientName'):
                    title = f"{ds.PatientName}"
                if hasattr(ds, 'StudyDescription'):
                    title += f" - {ds.StudyDescription}"
                elif hasattr(ds, 'SeriesDescription'):
                    title += f" - {ds.SeriesDescription}"
                
                ax.set_title(title)
            else:
                # No pixel data available
                ax.text(0.5, 0.5, "No image data available in this DICOM file",
                       horizontalalignment='center', verticalalignment='center')
                ax.set_axis_off()
            
            # Add DICOM information as text
            info_text = ""
            if hasattr(ds, 'Modality'):
                info_text += f"Modality: {ds.Modality}\n"
            if hasattr(ds, 'StudyDate'):
                info_text += f"Study Date: {ds.StudyDate}\n"
            if hasattr(ds, 'SeriesNumber'):
                info_text += f"Series: {ds.SeriesNumber}\n"
            if hasattr(ds, 'InstanceNumber'):
                info_text += f"Instance: {ds.InstanceNumber}\n"
            
            # Add text to bottom left corner
            if info_text:
                ax.text(0.01, 0.01, info_text, transform=ax.transAxes,
                       fontsize=8, verticalalignment='bottom', horizontalalignment='left',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
            
            # Add FHIR viewer link information
            if hasattr(ds, 'StudyInstanceUID'):
                fhir_text = "FHIR Viewer Available"
                ax.text(0.99, 0.01, fhir_text, transform=ax.transAxes,
                       fontsize=8, verticalalignment='bottom', horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            # Adjust layout
            fig.tight_layout()
            
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
        Generate a thumbnail for the DICOM file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
        # For thumbnails, use a simpler preview with just the image
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
        Extract structured data from the DICOM file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'image', 'metadata', 'fhir').
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        if not PYDICOM_AVAILABLE:
            return {'error': "pydicom library not available"}
        
        try:
            # Read DICOM file
            ds = pydicom.dcmread(file_path)
            
            if data_type == 'image':
                # Extract image data
                if not hasattr(ds, 'pixel_array'):
                    return {'error': "No image data available in this DICOM file"}
                
                # Get pixel array
                pixel_array = ds.pixel_array
                
                # Handle multi-frame images
                if len(pixel_array.shape) > 2:
                    # For multi-frame images, get the specified frame or default to middle frame
                    frame_index = kwargs.get('frame_index', pixel_array.shape[0] // 2)
                    if frame_index < 0 or frame_index >= pixel_array.shape[0]:
                        return {'error': f"Frame index {frame_index} out of range"}
                    
                    pixel_array = pixel_array[frame_index]
                
                # Apply window center/width if provided
                window_center = kwargs.get('window_center')
                window_width = kwargs.get('window_width')
                
                if window_center is not None and window_width is not None:
                    # Convert to float for calculations
                    pixel_array = pixel_array.astype(float)
                    
                    # Apply window
                    min_value = window_center - window_width // 2
                    max_value = window_center + window_width // 2
                    
                    # Clip values outside the window
                    pixel_array = np.clip(pixel_array, min_value, max_value)
                    
                    # Normalize to 0-1 range
                    pixel_array = (pixel_array - min_value) / (max_value - min_value)
                
                # Get image statistics
                stats = {
                    'min': float(np.min(pixel_array)),
                    'max': float(np.max(pixel_array)),
                    'mean': float(np.mean(pixel_array)),
                    'std': float(np.std(pixel_array))
                }
                
                # Return image data and statistics
                return {
                    'shape': pixel_array.shape,
                    'dtype': str(pixel_array.dtype),
                    'statistics': stats,
                    'data': pixel_array.tolist() if kwargs.get('include_data', False) else None
                }
            
            elif data_type == 'metadata':
                # Extract all DICOM metadata
                metadata = {}
                
                # Iterate through all DICOM elements
                for elem in ds:
                    # Skip pixel data
                    if elem.tag == pydicom.tag.Tag('PixelData'):
                        continue
                    
                    # Get element name and value
                    name = elem.name
                    value = elem.value
                    
                    # Convert non-serializable types to strings
                    if not isinstance(value, (str, int, float, bool, type(None), list, dict)):
                        value = str(value)
                    
                    metadata[name] = value
                
                return metadata
            
            elif data_type == 'fhir':
                # Extract data for FHIR integration
                fhir_data = {
                    'resourceType': 'ImagingStudy',
                    'id': str(ds.StudyInstanceUID) if hasattr(ds, 'StudyInstanceUID') else None,
                    'status': 'available',
                    'subject': {
                        'reference': f"Patient/{ds.PatientID}" if hasattr(ds, 'PatientID') else None,
                        'display': str(ds.PatientName) if hasattr(ds, 'PatientName') else None
                    },
                    'started': f"{ds.StudyDate}T{ds.StudyTime}" if hasattr(ds, 'StudyDate') and hasattr(ds, 'StudyTime') else None,
                    'description': ds.StudyDescription if hasattr(ds, 'StudyDescription') else None,
                    'series': [
                        {
                            'uid': str(ds.SeriesInstanceUID) if hasattr(ds, 'SeriesInstanceUID') else None,
                            'number': int(ds.SeriesNumber) if hasattr(ds, 'SeriesNumber') else None,
                            'modality': {
                                'code': ds.Modality if hasattr(ds, 'Modality') else None
                            },
                            'description': ds.SeriesDescription if hasattr(ds, 'SeriesDescription') else None,
                            'numberOfInstances': 1,
                            'instance': [
                                {
                                    'uid': str(ds.SOPInstanceUID) if hasattr(ds, 'SOPInstanceUID') else None,
                                    'number': int(ds.InstanceNumber) if hasattr(ds, 'InstanceNumber') else None,
                                    'sopClass': {
                                        'system': 'urn:ietf:rfc:3986',
                                        'code': str(ds.SOPClassUID) if hasattr(ds, 'SOPClassUID') else None
                                    }
                                }
                            ]
                        }
                    ]
                }
                
                # Add OHIF viewer URL
                fhir_viewer_url = kwargs.get('fhir_viewer_url', 'https://ohif-viewer-url/viewer/')
                if hasattr(ds, 'StudyInstanceUID'):
                    fhir_data['viewerUrl'] = f"{fhir_viewer_url}{ds.StudyInstanceUID}"
                
                return fhir_data
            
            elif data_type == 'structure':
                # Extract the overall structure of the DICOM file
                structure = {
                    'format': 'DICOM',
                    'transfer_syntax': str(ds.file_meta.TransferSyntaxUID) if hasattr(ds, 'file_meta') and hasattr(ds.file_meta, 'TransferSyntaxUID') else None,
                    'sop_class': str(ds.file_meta.MediaStorageSOPClassUID) if hasattr(ds, 'file_meta') and hasattr(ds.file_meta, 'MediaStorageSOPClassUID') else None,
                    'modality': ds.Modality if hasattr(ds, 'Modality') else None,
                    'patient_info': {
                        'name': str(ds.PatientName) if hasattr(ds, 'PatientName') else None,
                        'id': ds.PatientID if hasattr(ds, 'PatientID') else None,
                        'birth_date': ds.PatientBirthDate if hasattr(ds, 'PatientBirthDate') else None,
                        'sex': ds.PatientSex if hasattr(ds, 'PatientSex') else None
                    },
                    'study_info': {
                        'uid': str(ds.StudyInstanceUID) if hasattr(ds, 'StudyInstanceUID') else None,
                        'id': ds.StudyID if hasattr(ds, 'StudyID') else None,
                        'date': ds.StudyDate if hasattr(ds, 'StudyDate') else None,
                        'time': ds.StudyTime if hasattr(ds, 'StudyTime') else None,
                        'description': ds.StudyDescription if hasattr(ds, 'StudyDescription') else None
                    },
                    'series_info': {
                        'uid': str(ds.SeriesInstanceUID) if hasattr(ds, 'SeriesInstanceUID') else None,
                        'number': int(ds.SeriesNumber) if hasattr(ds, 'SeriesNumber') else None,
                        'date': ds.SeriesDate if hasattr(ds, 'SeriesDate') else None,
                        'time': ds.SeriesTime if hasattr(ds, 'SeriesTime') else None,
                        'description': ds.SeriesDescription if hasattr(ds, 'SeriesDescription') else None
                    },
                    'image_info': {
                        'uid': str(ds.SOPInstanceUID) if hasattr(ds, 'SOPInstanceUID') else None,
                        'number': int(ds.InstanceNumber) if hasattr(ds, 'InstanceNumber') else None,
                        'type': ds.ImageType if hasattr(ds, 'ImageType') else None,
                        'rows': int(ds.Rows) if hasattr(ds, 'Rows') else None,
                        'columns': int(ds.Columns) if hasattr(ds, 'Columns') else None,
                        'frames': int(ds.NumberOfFrames) if hasattr(ds, 'NumberOfFrames') else 1
                    },
                    'has_pixel_data': hasattr(ds, 'pixel_array')
                }
                
                # Add FHIR viewer URL
                if hasattr(ds, 'StudyInstanceUID'):
                    structure['fhir_viewer_url'] = f"https://ohif-viewer-url/viewer/{ds.StudyInstanceUID}"
                
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
        return ['image', 'metadata', 'fhir', 'structure']
"""
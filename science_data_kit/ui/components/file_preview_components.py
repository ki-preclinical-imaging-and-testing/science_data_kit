"""
File preview components for the Science Data Kit.

This module contains UI components for previewing different types of files,
including images, documents, and other file types. These components use
the file interpreter plugins to extract metadata and generate previews.
"""

import os
import io
import base64
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import streamlit as st
import pandas as pd
from PIL import Image

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PluginRegistry
)


def get_file_interpreter(file_path: str) -> Optional[FileInterpreterPlugin]:
    """
    Get the appropriate file interpreter for a file.

    Args:
        file_path: Path to the file.

    Returns:
        FileInterpreterPlugin instance if an interpreter is found, None otherwise.
    """
    try:
        registry = PluginRegistry()
        interpreter = registry.get_file_interpreter_for_file(file_path)
        return interpreter
    except Exception as e:
        st.error(f"Error getting file interpreter: {str(e)}")
        return None


def render_metadata_section(metadata: Dict[str, Any], title: str = "Metadata"):
    """
    Render a metadata section with grouped metadata.

    Args:
        metadata: Dictionary of metadata key-value pairs.
        title: Title for the metadata section.
    """
    st.subheader(title)

    # Group metadata into categories
    basic_info = {}
    file_info = {}
    format_info = {}
    content_info = {}
    other_info = {}

    # Basic file info
    basic_keys = ['name', 'extension', 'size', 'created', 'modified', 'accessed']
    for key in basic_keys:
        if key in metadata:
            basic_info[key] = metadata[key]

    # Format-specific info
    format_keys = ['format', 'mime_type', 'encoding', 'version']
    for key in format_keys:
        if key in metadata:
            format_info[key] = metadata[key]

    # Content-specific info
    content_keys = ['width', 'height', 'duration', 'bitrate', 'channels', 'sample_rate', 
                    'frame_rate', 'codec', 'resolution']
    for key in content_keys:
        if key in metadata:
            content_info[key] = metadata[key]

    # Nested metadata (like EXIF, ID3, etc.)
    nested_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, dict):
            nested_metadata[key] = value
        elif key not in basic_keys + format_keys + content_keys:
            other_info[key] = value

    # Display basic info
    if basic_info:
        with st.expander("Basic Information", expanded=True):
            for key, value in basic_info.items():
                if key == 'size' and isinstance(value, int):
                    # Format size in human-readable format
                    if value < 1024:
                        formatted_value = f"{value} B"
                    elif value < 1024 * 1024:
                        formatted_value = f"{value / 1024:.1f} KB"
                    elif value < 1024 * 1024 * 1024:
                        formatted_value = f"{value / (1024 * 1024):.1f} MB"
                    else:
                        formatted_value = f"{value / (1024 * 1024 * 1024):.1f} GB"
                    st.write(f"**{key.capitalize()}:** {formatted_value}")
                elif key in ['created', 'modified', 'accessed'] and value:
                    # Format timestamps
                    try:
                        from datetime import datetime
                        if isinstance(value, (int, float)):
                            dt = datetime.fromtimestamp(value)
                            formatted_value = dt.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            formatted_value = str(value)
                        st.write(f"**{key.capitalize()}:** {formatted_value}")
                    except:
                        st.write(f"**{key.capitalize()}:** {value}")
                else:
                    st.write(f"**{key.capitalize()}:** {value}")

    # Display format info
    if format_info:
        with st.expander("Format Information", expanded=True):
            for key, value in format_info.items():
                st.write(f"**{key.capitalize()}:** {value}")

    # Display content info
    if content_info:
        with st.expander("Content Information", expanded=True):
            for key, value in content_info.items():
                st.write(f"**{key.capitalize()}:** {value}")

    # Display nested metadata
    for category, data in nested_metadata.items():
        with st.expander(f"{category.capitalize()} Metadata", expanded=False):
            if isinstance(data, dict):
                for key, value in data.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.write(data)

    # Display other info
    if other_info:
        with st.expander("Other Information", expanded=False):
            for key, value in other_info.items():
                st.write(f"**{key.capitalize()}:** {value}")


def render_image_preview(file_path: str, interpreter: Optional[FileInterpreterPlugin] = None):
    """
    Render a preview for an image file.

    Args:
        file_path: Path to the image file.
        interpreter: Optional FileInterpreterPlugin instance. If not provided,
                    the function will try to get an appropriate interpreter.
    """
    if interpreter is None:
        interpreter = get_file_interpreter(file_path)

    if interpreter is None:
        st.error("No interpreter found for this file type")
        return

    try:
        # Extract metadata
        metadata = interpreter.extract_metadata(file_path)

        # Display image
        st.subheader("Image Preview")

        try:
            # Try to open the image with PIL
            img = Image.open(file_path)
            st.image(img, use_column_width=True)

            # Display image dimensions
            width, height = img.size
            st.write(f"Dimensions: {width} × {height} pixels")

            # Display image format
            st.write(f"Format: {img.format}")

            # Display image mode
            st.write(f"Mode: {img.mode}")

            # If it's an animated GIF, show animation info
            if hasattr(img, 'is_animated') and img.is_animated:
                st.write(f"Animated GIF with {img.n_frames} frames")
        except Exception as e:
            # If PIL fails, try to use the interpreter's preview generation
            st.error(f"Error displaying image with PIL: {str(e)}")
            st.write("Trying to generate preview with interpreter...")

            # Generate preview using the interpreter
            preview_data = interpreter.generate_preview(file_path)
            if isinstance(preview_data, str) and os.path.exists(preview_data):
                # If the preview is a file path, open it
                img = Image.open(preview_data)
                st.image(img, use_column_width=True)
            elif isinstance(preview_data, bytes):
                # If the preview is bytes, convert to base64 and display
                b64 = base64.b64encode(preview_data).decode()
                st.markdown(f'<img src="data:image/png;base64,{b64}" style="max-width: 100%;">', unsafe_allow_html=True)
            else:
                st.error(f"Unable to display image preview: {preview_data}")

        # Display metadata
        render_metadata_section(metadata)

    except Exception as e:
        st.error(f"Error rendering image preview: {str(e)}")


def render_document_preview(file_path: str, interpreter: Optional[FileInterpreterPlugin] = None):
    """
    Render a preview for a document file (PDF, DOCX, XLSX, etc.).

    Args:
        file_path: Path to the document file.
        interpreter: Optional FileInterpreterPlugin instance. If not provided,
                    the function will try to get an appropriate interpreter.
    """
    if interpreter is None:
        interpreter = get_file_interpreter(file_path)

    if interpreter is None:
        st.error("No interpreter found for this file type")
        return

    try:
        # Extract metadata
        metadata = interpreter.extract_metadata(file_path)

        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()

        # Display document preview based on file type
        st.subheader("Document Preview")

        if ext == '.pdf':
            # For PDF files, display using PDF viewer
            try:
                # Generate preview using the interpreter
                preview_path = interpreter.generate_preview(file_path)

                if isinstance(preview_path, str) and os.path.exists(preview_path):
                    # If the preview is a file path, display it using PDF viewer
                    with open(preview_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                    # Display PDF using iframe
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    # If preview generation failed, display a message
                    st.warning("PDF preview not available. Try downloading the file to view it.")

                    # Try to extract text if available
                    if hasattr(interpreter, 'extract_text'):
                        text = interpreter.extract_text(file_path)
                        if text:
                            with st.expander("Document Text", expanded=True):
                                st.text(text[:10000] + ("..." if len(text) > 10000 else ""))
            except Exception as e:
                st.error(f"Error displaying PDF preview: {str(e)}")

        elif ext in ['.docx', '.doc']:
            # For DOCX files, try to extract text and display it
            try:
                if hasattr(interpreter, 'extract_text'):
                    text = interpreter.extract_text(file_path)
                    if text:
                        with st.expander("Document Text", expanded=True):
                            st.text(text[:10000] + ("..." if len(text) > 10000 else ""))
                    else:
                        st.warning("Text extraction not available for this document.")

                # Try to generate preview
                preview_path = interpreter.generate_preview(file_path)
                if isinstance(preview_path, str) and os.path.exists(preview_path):
                    # If the preview is a file path, display it as an image
                    img = Image.open(preview_path)
                    st.image(img, use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying DOCX preview: {str(e)}")

        elif ext in ['.xlsx', '.xls']:
            # For XLSX files, try to extract structured data and display it
            try:
                if hasattr(interpreter, 'extract_structured_data'):
                    data = interpreter.extract_structured_data(file_path, 'table')
                    if isinstance(data, dict):
                        # Display each sheet as a separate tab
                        sheet_names = list(data.keys())
                        if sheet_names:
                            selected_sheet = st.selectbox("Select Sheet", sheet_names)
                            sheet_data = data[selected_sheet]

                            if isinstance(sheet_data, list) and sheet_data:
                                if isinstance(sheet_data[0], dict):
                                    # Convert list of dicts to DataFrame
                                    df = pd.DataFrame(sheet_data)
                                    st.dataframe(df)
                                elif isinstance(sheet_data[0], list):
                                    # Convert list of lists to DataFrame
                                    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0] if sheet_data else None)
                                    st.dataframe(df)
                                else:
                                    st.write(sheet_data)
                            else:
                                st.write(sheet_data)
                    else:
                        st.warning("Structured data extraction not available for this spreadsheet.")

                # Try to generate preview
                preview_path = interpreter.generate_preview(file_path)
                if isinstance(preview_path, str) and os.path.exists(preview_path):
                    # If the preview is a file path, display it as an image
                    with st.expander("Spreadsheet Preview Image", expanded=False):
                        img = Image.open(preview_path)
                        st.image(img, use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying XLSX preview: {str(e)}")

        else:
            # For other document types, display a generic message
            st.warning(f"Preview not available for {ext} files. Try downloading the file to view it.")

            # Try to extract text if available
            if hasattr(interpreter, 'extract_text'):
                text = interpreter.extract_text(file_path)
                if text:
                    with st.expander("Document Text", expanded=True):
                        st.text(text[:10000] + ("..." if len(text) > 10000 else ""))

        # Display metadata
        render_metadata_section(metadata)

    except Exception as e:
        st.error(f"Error rendering document preview: {str(e)}")


def render_scientific_data_preview(file_path: str, interpreter: Optional[FileInterpreterPlugin] = None):
    """
    Render a preview for a scientific data file (NetCDF, HDF5, FITS, GeoTIFF, etc.).

    Args:
        file_path: Path to the scientific data file.
        interpreter: Optional FileInterpreterPlugin instance. If not provided,
                    the function will try to get an appropriate interpreter.
    """
    if interpreter is None:
        interpreter = get_file_interpreter(file_path)

    if interpreter is None:
        st.error("No interpreter found for this file type")
        return

    try:
        # Extract metadata
        metadata = interpreter.extract_metadata(file_path)

        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()

        # Display scientific data preview
        st.subheader("Scientific Data Preview")

        # Generate and display preview image
        try:
            preview_path = interpreter.generate_preview(file_path)
            if isinstance(preview_path, bytes):
                # If preview is returned as bytes, display it directly
                st.image(preview_path, use_column_width=True)
            elif isinstance(preview_path, str) and os.path.exists(preview_path):
                # If preview is returned as a file path, open and display it
                img = Image.open(preview_path)
                st.image(img, use_column_width=True)
        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")

        # Display file-specific information based on type
        if ext in ['.nc', '.nc4', '.netcdf']:
            # NetCDF specific display
            if 'dimensions' in metadata:
                with st.expander("Dimensions", expanded=True):
                    for dim_name, dim_size in metadata.get('dimensions', {}).items():
                        st.write(f"**{dim_name}:** {dim_size}")

            if 'variables' in metadata:
                with st.expander("Variables", expanded=True):
                    for var_name, var_info in metadata.get('variables', {}).items():
                        st.write(f"**{var_name}**")
                        st.write(f"  Dimensions: {', '.join(var_info.get('dimensions', []))}")
                        st.write(f"  Type: {var_info.get('dtype', 'Unknown')}")
                        if 'attributes' in var_info:
                            st.write("  Attributes:")
                            for attr_name, attr_value in var_info.get('attributes', {}).items():
                                st.write(f"    {attr_name}: {attr_value}")

        elif ext in ['.h5', '.hdf5', '.he5']:
            # HDF5 specific display
            if 'groups' in metadata:
                with st.expander("Groups", expanded=True):
                    for group_name, group_info in metadata.get('groups', {}).items():
                        st.write(f"**{group_name}**")
                        if 'datasets' in group_info:
                            st.write("  Datasets:")
                            for dataset_name, dataset_info in group_info.get('datasets', {}).items():
                                st.write(f"    {dataset_name}: {dataset_info.get('shape', 'Unknown shape')}, {dataset_info.get('dtype', 'Unknown type')}")

        elif ext in ['.fits', '.fit', '.fts']:
            # FITS specific display
            if 'hdus' in metadata:
                with st.expander("HDUs (Header Data Units)", expanded=True):
                    for hdu in metadata.get('hdus', []):
                        st.write(f"**{hdu.get('name', 'Unnamed')} (Type: {hdu.get('type', 'Unknown')})**")
                        if 'data_shape' in hdu:
                            st.write(f"  Shape: {hdu.get('data_shape', 'Unknown')}")
                        if 'statistics' in hdu:
                            stats = hdu.get('statistics', {})
                            st.write(f"  Min: {stats.get('min', 'N/A')}, Max: {stats.get('max', 'N/A')}")
                            st.write(f"  Mean: {stats.get('mean', 'N/A')}, Std: {stats.get('std', 'N/A')}")

            if 'astronomical_metadata' in metadata:
                with st.expander("Astronomical Metadata", expanded=True):
                    for key, value in metadata.get('astronomical_metadata', {}).items():
                        st.write(f"**{key}:** {value}")

        elif ext in ['.tif', '.tiff'] and 'crs' in metadata:
            # GeoTIFF specific display
            if 'crs' in metadata:
                with st.expander("Coordinate Reference System", expanded=True):
                    crs = metadata.get('crs', {})
                    st.write(f"**EPSG:** {crs.get('epsg', 'Unknown')}")
                    st.write(f"**Proj4:** {crs.get('proj4', 'Unknown')}")

            if 'bounds' in metadata:
                with st.expander("Bounds", expanded=True):
                    bounds = metadata.get('bounds', {})
                    st.write(f"**Left:** {bounds.get('left', 'Unknown')}")
                    st.write(f"**Bottom:** {bounds.get('bottom', 'Unknown')}")
                    st.write(f"**Right:** {bounds.get('right', 'Unknown')}")
                    st.write(f"**Top:** {bounds.get('top', 'Unknown')}")

            if 'resolution' in metadata:
                with st.expander("Resolution", expanded=True):
                    resolution = metadata.get('resolution', {})
                    st.write(f"**X Resolution:** {resolution.get('x', 'Unknown')}")
                    st.write(f"**Y Resolution:** {resolution.get('y', 'Unknown')}")

            if 'bands' in metadata:
                with st.expander("Bands", expanded=True):
                    for band in metadata.get('bands', []):
                        st.write(f"**Band {band.get('index', 'Unknown')}:** {band.get('description', 'No description')}")
                        if 'statistics' in band:
                            stats = band.get('statistics', {})
                            st.write(f"  Min: {stats.get('min', 'N/A')}, Max: {stats.get('max', 'N/A')}")
                            st.write(f"  Mean: {stats.get('mean', 'N/A')}, Std: {stats.get('std', 'N/A')}")

        elif ext in ['.csv', '.tsv']:
            # CSV/TSV specific display
            try:
                # Try to extract structured data
                data = interpreter.extract_structured_data(file_path, 'table_data')
                if data and 'data' in data:
                    # Convert to pandas DataFrame for display
                    df = pd.DataFrame(data['data'])
                    if 'columns' in data and len(data['columns']) == len(df.columns):
                        df.columns = data['columns']

                    # Display the data table
                    with st.expander("Data Preview", expanded=True):
                        st.dataframe(df.head(100))

                        # Display basic statistics
                        if len(df) > 0:
                            st.write(f"Rows: {len(df)}, Columns: {len(df.columns)}")

                            # Try to display numeric column statistics
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            if len(numeric_cols) > 0:
                                st.write("Numeric Column Statistics:")
                                st.dataframe(df[numeric_cols].describe())
            except Exception as e:
                st.error(f"Error displaying CSV/TSV data: {str(e)}")

        # Display metadata
        render_metadata_section(metadata)

    except Exception as e:
        st.error(f"Error rendering scientific data preview: {str(e)}")


def render_media_preview(file_path: str, interpreter: Optional[FileInterpreterPlugin] = None):
    """
    Render a preview for a media file (audio or video).

    Args:
        file_path: Path to the media file.
        interpreter: Optional FileInterpreterPlugin instance. If not provided,
                    the function will try to get an appropriate interpreter.
    """
    if interpreter is None:
        interpreter = get_file_interpreter(file_path)

    if interpreter is None:
        st.error("No interpreter found for this file type")
        return

    try:
        # Extract metadata
        metadata = interpreter.extract_metadata(file_path)

        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()

        # Display media preview based on file type
        st.subheader("Media Preview")

        if ext in ['.mp3', '.wav', '.ogg']:
            # For audio files, display using audio player
            try:
                with open(file_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format=f'audio/{ext[1:]}')

                # Display audio metadata
                if 'length' in metadata:
                    st.write(f"Duration: {metadata['length']:.2f} seconds")
                if 'bitrate' in metadata:
                    st.write(f"Bitrate: {metadata['bitrate'] / 1000:.0f} kbps")
                if 'sample_rate' in metadata:
                    st.write(f"Sample Rate: {metadata['sample_rate']} Hz")
                if 'channels' in metadata:
                    st.write(f"Channels: {metadata['channels']}")

                # Display ID3 tags if available
                if 'id3' in metadata and isinstance(metadata['id3'], dict):
                    with st.expander("ID3 Tags", expanded=True):
                        for key, value in metadata['id3'].items():
                            st.write(f"**{key.capitalize()}:** {value}")
            except Exception as e:
                st.error(f"Error displaying audio preview: {str(e)}")

        elif ext in ['.mp4', '.webm', '.avi', '.mov']:
            # For video files, display using video player
            try:
                with open(file_path, "rb") as f:
                    video_bytes = f.read()
                st.video(video_bytes, format=f'video/{ext[1:]}')

                # Display video metadata
                if 'length' in metadata:
                    st.write(f"Duration: {metadata['length']:.2f} seconds")
                if 'video_info' in metadata and isinstance(metadata['video_info'], dict):
                    with st.expander("Video Information", expanded=True):
                        for key, value in metadata['video_info'].items():
                            st.write(f"**{key.capitalize()}:** {value}")
            except Exception as e:
                st.error(f"Error displaying video preview: {str(e)}")

                # Try to display a thumbnail
                try:
                    thumbnail_path = interpreter.generate_thumbnail(file_path)
                    if isinstance(thumbnail_path, str) and os.path.exists(thumbnail_path):
                        st.write("Video Thumbnail:")
                        img = Image.open(thumbnail_path)
                        st.image(img, use_column_width=True)
                except Exception as thumb_error:
                    st.error(f"Error generating thumbnail: {str(thumb_error)}")

        else:
            # For other media types, display a generic message
            st.warning(f"Preview not available for {ext} files. Try downloading the file to view it.")

            # Try to display a thumbnail
            try:
                thumbnail_path = interpreter.generate_thumbnail(file_path)
                if isinstance(thumbnail_path, str) and os.path.exists(thumbnail_path):
                    st.write("Media Thumbnail:")
                    img = Image.open(thumbnail_path)
                    st.image(img, use_column_width=True)
            except Exception as thumb_error:
                st.warning(f"Thumbnail not available: {str(thumb_error)}")

        # Display metadata
        render_metadata_section(metadata)

    except Exception as e:
        st.error(f"Error rendering media preview: {str(e)}")


def render_file_preview(file_path: str):
    """
    Render a preview for a file based on its type.

    Args:
        file_path: Path to the file.
    """
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return

    # Get file extension
    ext = os.path.splitext(file_path)[1].lower()

    # Get file interpreter
    interpreter = get_file_interpreter(file_path)

    if interpreter is None:
        st.warning("No specialized interpreter found for this file type. Displaying basic information.")

        # Display basic file info
        file_info = {
            'name': os.path.basename(file_path),
            'extension': ext,
            'size': os.path.getsize(file_path),
            'created': os.path.getctime(file_path),
            'modified': os.path.getmtime(file_path),
            'accessed': os.path.getatime(file_path)
        }

        render_metadata_section(file_info, title="File Information")

        # Try to display content for text files
        if ext in ['.txt', '.md', '.py', '.json', '.csv', '.html', '.xml', '.yml', '.yaml']:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                st.subheader("File Content")
                st.text(content[:10000] + ("..." if len(content) > 10000 else ""))
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

        return

    # Determine file type category
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    document_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.md', '.json', '.xml', '.html']
    media_extensions = ['.mp3', '.wav', '.ogg', '.mp4', '.webm', '.avi', '.mov']
    scientific_data_extensions = ['.nc', '.nc4', '.netcdf', '.h5', '.hdf5', '.he5', '.fits', '.fit', '.fts', '.csv', '.tsv']

    # Check if it's a GeoTIFF (TIFF with geospatial metadata)
    is_geotiff = False
    if ext in ['.tif', '.tiff']:
        try:
            metadata = interpreter.extract_metadata(file_path)
            if 'crs' in metadata:
                is_geotiff = True
        except Exception:
            pass

    # Render preview based on file type
    if is_geotiff or ext in scientific_data_extensions:
        render_scientific_data_preview(file_path, interpreter)
    elif ext in image_extensions or (ext in ['.tif', '.tiff'] and not is_geotiff):
        render_image_preview(file_path, interpreter)
    elif ext in document_extensions:
        render_document_preview(file_path, interpreter)
    elif ext in media_extensions:
        render_media_preview(file_path, interpreter)
    else:
        # For other file types, display metadata and basic info
        st.subheader("File Preview")
        st.warning(f"No specialized preview available for {ext} files.")

        # Extract and display metadata
        metadata = interpreter.extract_metadata(file_path)
        render_metadata_section(metadata)

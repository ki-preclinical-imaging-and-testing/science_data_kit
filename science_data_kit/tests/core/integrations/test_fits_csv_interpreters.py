"""
Tests for FITS and CSV/TSV file interpreters.

This module contains tests for the FITS and CSV/TSV file interpreters,
ensuring they correctly interpret files, extract metadata, and generate previews.
"""

import os
import sys
import unittest
import tempfile
import csv
from pathlib import Path

from science_data_kit.core.integrations.plugin_architecture import (
    get_plugin_registry,
    FileInterpreterPlugin
)

# Check if required libraries are available
try:
    from astropy.io import fits
    import numpy as np
    ASTROPY_AVAILABLE = True
except ImportError:
    ASTROPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class TestFITSInterpreter(unittest.TestCase):
    """Test the FITS file interpreter."""

    @unittest.skipIf(not ASTROPY_AVAILABLE, "astropy not available")
    def setUp(self):
        """Set up the test by creating a sample FITS file."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create a sample FITS file
        self.fits_file = self.test_dir / "test.fits"

        # Create a simple FITS file with a primary HDU and an image HDU
        primary_hdu = fits.PrimaryHDU()
        primary_hdu.header['TELESCOP'] = 'Test Telescope'
        primary_hdu.header['INSTRUME'] = 'Test Instrument'
        primary_hdu.header['OBJECT'] = 'Test Object'

        # Create a simple 2D image
        image_data = np.random.rand(100, 100)
        image_hdu = fits.ImageHDU(data=image_data)
        image_hdu.header['EXTNAME'] = 'TEST_IMAGE'

        # Create a simple table
        col1 = fits.Column(name='id', format='J', array=np.arange(10))
        col2 = fits.Column(name='value', format='E', array=np.random.rand(10))
        table_hdu = fits.BinTableHDU.from_columns([col1, col2])
        table_hdu.header['EXTNAME'] = 'TEST_TABLE'

        # Create HDUList and write to file
        hdul = fits.HDUList([primary_hdu, image_hdu, table_hdu])
        hdul.writeto(self.fits_file, overwrite=True)

        # Get the plugin registry
        self.registry = get_plugin_registry()

    @unittest.skipIf(not ASTROPY_AVAILABLE, "astropy not available")
    def tearDown(self):
        """Clean up after the test."""
        self.temp_dir.cleanup()

    @unittest.skipIf(not ASTROPY_AVAILABLE, "astropy not available")
    def test_fits_interpreter_registration(self):
        """Test that the FITS interpreter is registered."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the FITS interpreter
        fits_interpreter = None
        for interpreter in interpreters:
            if "FITS" in interpreter.metadata.name:
                fits_interpreter = interpreter
                break

        # Check that the FITS interpreter was found
        self.assertIsNotNone(fits_interpreter, "FITS interpreter not found in registry")

        # Check that it's a FileInterpreterPlugin
        self.assertIsInstance(fits_interpreter, FileInterpreterPlugin)

        # Check that it supports FITS files
        self.assertTrue(fits_interpreter.can_interpret(str(self.fits_file)))

        # Check supported extensions
        self.assertIn('.fits', fits_interpreter.get_supported_extensions())

        # Check supported MIME types
        self.assertIn('application/fits', fits_interpreter.get_supported_mime_types())

    @unittest.skipIf(not ASTROPY_AVAILABLE, "astropy not available")
    def test_fits_metadata_extraction(self):
        """Test that the FITS interpreter can extract metadata."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the FITS interpreter
        fits_interpreter = None
        for interpreter in interpreters:
            if "FITS" in interpreter.metadata.name:
                fits_interpreter = interpreter
                break

        # Extract metadata
        metadata = fits_interpreter.extract_metadata(str(self.fits_file))

        # Check basic metadata
        self.assertEqual(metadata['format'], 'FITS')
        self.assertEqual(metadata['num_hdus'], 3)

        # Check HDU information
        self.assertEqual(len(metadata['hdus']), 3)
        self.assertEqual(metadata['hdus'][0]['type'], 'PrimaryHDU')
        self.assertEqual(metadata['hdus'][1]['type'], 'ImageHDU')
        self.assertEqual(metadata['hdus'][2]['type'], 'BinTableHDU')

        # Check astronomical metadata
        self.assertIn('astronomical_metadata', metadata)
        self.assertEqual(metadata['astronomical_metadata']['TELESCOP'], 'Test Telescope')
        self.assertEqual(metadata['astronomical_metadata']['INSTRUME'], 'Test Instrument')
        self.assertEqual(metadata['astronomical_metadata']['OBJECT'], 'Test Object')

    @unittest.skipIf(not (ASTROPY_AVAILABLE and np and 'matplotlib.pyplot' in sys.modules), 
                    "astropy, numpy, or matplotlib not available")
    def test_fits_preview_generation(self):
        """Test that the FITS interpreter can generate previews."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the FITS interpreter
        fits_interpreter = None
        for interpreter in interpreters:
            if "FITS" in interpreter.metadata.name:
                fits_interpreter = interpreter
                break

        # Generate preview
        preview_file = self.test_dir / "preview.png"
        result = fits_interpreter.generate_preview(str(self.fits_file), str(preview_file))

        # Check that the preview was generated
        self.assertEqual(result, str(preview_file))
        self.assertTrue(os.path.exists(preview_file))

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(preview_file), 0)

    @unittest.skipIf(not ASTROPY_AVAILABLE, "astropy not available")
    def test_fits_structured_data_extraction(self):
        """Test that the FITS interpreter can extract structured data."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the FITS interpreter
        fits_interpreter = None
        for interpreter in interpreters:
            if "FITS" in interpreter.metadata.name:
                fits_interpreter = interpreter
                break

        # Extract structure
        structure = fits_interpreter.extract_structured_data(str(self.fits_file), 'structure')

        # Check structure
        self.assertEqual(structure['num_hdus'], 3)
        self.assertEqual(len(structure['hdus']), 3)
        self.assertEqual(structure['hdus'][0]['type'], 'PrimaryHDU')
        self.assertEqual(structure['hdus'][1]['type'], 'ImageHDU')
        self.assertEqual(structure['hdus'][2]['type'], 'BinTableHDU')

        # Extract image data
        image_data = fits_interpreter.extract_structured_data(
            str(self.fits_file), 'image', hdu_index=1
        )

        # Check image data
        self.assertIn('shape', image_data)
        self.assertEqual(image_data['shape'], (100, 100))
        self.assertIn('statistics', image_data)

        # Extract table data
        table_data = fits_interpreter.extract_structured_data(
            str(self.fits_file), 'table', hdu_index=2
        )

        # Check table data
        self.assertEqual(table_data['num_rows'], 10)
        self.assertEqual(table_data['num_columns'], 2)
        self.assertEqual(table_data['columns'][0]['name'], 'id')
        self.assertEqual(table_data['columns'][1]['name'], 'value')


class TestCSVInterpreter(unittest.TestCase):
    """Test the CSV/TSV file interpreter."""

    def setUp(self):
        """Set up the test by creating sample CSV and TSV files."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create a sample CSV file
        self.csv_file = self.test_dir / "test.csv"
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'value'])
            for i in range(10):
                writer.writerow([i, f'Item {i}', i * 2.5])

        # Create a sample TSV file
        self.tsv_file = self.test_dir / "test.tsv"
        with open(self.tsv_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['id', 'name', 'value'])
            for i in range(10):
                writer.writerow([i, f'Item {i}', i * 2.5])

        # Get the plugin registry
        self.registry = get_plugin_registry()

    def tearDown(self):
        """Clean up after the test."""
        self.temp_dir.cleanup()

    def test_csv_interpreter_registration(self):
        """Test that the CSV interpreter is registered."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the CSV interpreter
        csv_interpreter = None
        for interpreter in interpreters:
            if "CSV" in interpreter.metadata.name:
                csv_interpreter = interpreter
                break

        # Check that the CSV interpreter was found
        self.assertIsNotNone(csv_interpreter, "CSV interpreter not found in registry")

        # Check that it's a FileInterpreterPlugin
        self.assertIsInstance(csv_interpreter, FileInterpreterPlugin)

        # Check that it supports CSV files
        self.assertTrue(csv_interpreter.can_interpret(str(self.csv_file)))

        # Check that it supports TSV files
        self.assertTrue(csv_interpreter.can_interpret(str(self.tsv_file)))

        # Check supported extensions
        self.assertIn('.csv', csv_interpreter.get_supported_extensions())
        self.assertIn('.tsv', csv_interpreter.get_supported_extensions())

        # Check supported MIME types
        self.assertIn('text/csv', csv_interpreter.get_supported_mime_types())
        self.assertIn('text/tab-separated-values', csv_interpreter.get_supported_mime_types())

    def test_csv_metadata_extraction(self):
        """Test that the CSV interpreter can extract metadata."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the CSV interpreter
        csv_interpreter = None
        for interpreter in interpreters:
            if "CSV" in interpreter.metadata.name:
                csv_interpreter = interpreter
                break

        # Extract metadata from CSV file
        csv_metadata = csv_interpreter.extract_metadata(str(self.csv_file))

        # Check basic metadata
        self.assertEqual(csv_metadata['delimiter'], ',')
        self.assertTrue(csv_metadata['has_header'])
        self.assertEqual(csv_metadata['num_columns'], 3)
        self.assertEqual(csv_metadata['num_rows'], 10)
        self.assertEqual(csv_metadata['columns'], ['id', 'name', 'value'])

        # Extract metadata from TSV file
        tsv_metadata = csv_interpreter.extract_metadata(str(self.tsv_file))

        # Check basic metadata
        self.assertEqual(tsv_metadata['delimiter'], '\t')
        self.assertTrue(tsv_metadata['has_header'])
        self.assertEqual(tsv_metadata['num_columns'], 3)
        self.assertEqual(tsv_metadata['num_rows'], 10)
        self.assertEqual(tsv_metadata['columns'], ['id', 'name', 'value'])

    def test_csv_text_extraction(self):
        """Test that the CSV interpreter can extract text."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the CSV interpreter
        csv_interpreter = None
        for interpreter in interpreters:
            if "CSV" in interpreter.metadata.name:
                csv_interpreter = interpreter
                break

        # Extract text from CSV file
        csv_text = csv_interpreter.extract_text(str(self.csv_file))

        # Check that the text contains the header and data
        self.assertIn('id,name,value', csv_text)
        self.assertIn('0,Item 0,0.0', csv_text)

        # Extract text from TSV file
        tsv_text = csv_interpreter.extract_text(str(self.tsv_file))

        # Check that the text contains the header and data
        self.assertIn('id\tname\tvalue', tsv_text)
        self.assertIn('0\tItem 0\t0.0', tsv_text)

    @unittest.skipIf(not (PANDAS_AVAILABLE and np and 'matplotlib.pyplot' in sys.modules), 
                    "pandas, numpy, or matplotlib not available")
    def test_csv_preview_generation(self):
        """Test that the CSV interpreter can generate previews."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the CSV interpreter
        csv_interpreter = None
        for interpreter in interpreters:
            if "CSV" in interpreter.metadata.name:
                csv_interpreter = interpreter
                break

        # Generate preview for CSV file
        csv_preview_file = self.test_dir / "csv_preview.png"
        csv_result = csv_interpreter.generate_preview(str(self.csv_file), str(csv_preview_file))

        # Check that the preview was generated
        self.assertEqual(csv_result, str(csv_preview_file))
        self.assertTrue(os.path.exists(csv_preview_file))

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(csv_preview_file), 0)

        # Generate preview for TSV file
        tsv_preview_file = self.test_dir / "tsv_preview.png"
        tsv_result = csv_interpreter.generate_preview(str(self.tsv_file), str(tsv_preview_file))

        # Check that the preview was generated
        self.assertEqual(tsv_result, str(tsv_preview_file))
        self.assertTrue(os.path.exists(tsv_preview_file))

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(tsv_preview_file), 0)

    def test_csv_structured_data_extraction(self):
        """Test that the CSV interpreter can extract structured data."""
        # Get all file interpreters
        interpreters = self.registry.get_plugins_by_category("FILE_INTERPRETER")

        # Find the CSV interpreter
        csv_interpreter = None
        for interpreter in interpreters:
            if "CSV" in interpreter.metadata.name:
                csv_interpreter = interpreter
                break

        # Extract table data from CSV file
        csv_table = csv_interpreter.extract_structured_data(str(self.csv_file), 'table')

        # Check table data
        self.assertEqual(csv_table['num_rows'], 10)
        self.assertEqual(csv_table['num_columns'], 3)
        self.assertEqual(csv_table['columns'], ['id', 'name', 'value'])
        self.assertEqual(len(csv_table['data']), 10)

        # Extract column information from CSV file
        csv_columns = csv_interpreter.extract_structured_data(str(self.csv_file), 'columns')

        # Check column information
        self.assertEqual(len(csv_columns), 3)
        self.assertEqual(csv_columns[0]['name'], 'id')
        self.assertEqual(csv_columns[1]['name'], 'name')
        self.assertEqual(csv_columns[2]['name'], 'value')

        # Extract table data from TSV file
        tsv_table = csv_interpreter.extract_structured_data(str(self.tsv_file), 'table')

        # Check table data
        self.assertEqual(tsv_table['num_rows'], 10)
        self.assertEqual(tsv_table['num_columns'], 3)
        self.assertEqual(tsv_table['columns'], ['id', 'name', 'value'])
        self.assertEqual(len(tsv_table['data']), 10)


if __name__ == '__main__':
    unittest.main()

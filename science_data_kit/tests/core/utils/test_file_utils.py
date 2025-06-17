"""
Unit tests for the file_utils module.

This module contains tests for the file utilities defined in science_data_kit.core.utils.file_utils.
"""

import os
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

from science_data_kit.core.utils.file_utils import FileOrganizer, organize_files


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as source_dir, \
         tempfile.TemporaryDirectory() as symlink_dir, \
         tempfile.TemporaryDirectory() as export_dir:
        yield source_dir, symlink_dir, export_dir


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        f.write("filepath,col1,col2,col3\n")
        f.write("file1.txt,category1,subcategory1,group1\n")
        f.write("file2.txt,category1,subcategory2,group2\n")
        f.write("file3.txt,category2,subcategory1,group1\n")
        csv_path = f.name
    
    yield csv_path
    
    # Clean up
    if os.path.exists(csv_path):
        os.unlink(csv_path)


@pytest.fixture
def sample_files(temp_dirs):
    """Create sample files for testing."""
    source_dir, _, _ = temp_dirs
    
    # Create sample files
    for i in range(1, 4):
        file_path = os.path.join(source_dir, f"file{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"This is test file {i}")
    
    return source_dir


@pytest.mark.unit
class TestFileOrganizer:
    """Tests for the FileOrganizer class."""
    
    def test_init(self, temp_dirs, sample_csv_file):
        """Test initializing a FileOrganizer instance."""
        source_dir, symlink_dir, export_dir = temp_dirs
        
        # Mock the pandas read_csv function
        with patch('pandas.read_csv') as mock_read_csv:
            mock_df = MagicMock()
            mock_df.__len__.return_value = 3
            mock_read_csv.return_value = mock_df
            
            organizer = FileOrganizer(
                csv_file=sample_csv_file,
                source_dir=source_dir,
                symlink_dir=symlink_dir,
                final_export_dir=export_dir
            )
            
            assert organizer.csv_file == sample_csv_file
            assert organizer.source_dir == source_dir.rstrip('/')
            assert organizer.symlink_dir == symlink_dir.rstrip('/')
            assert organizer.final_export_dir == export_dir.rstrip('/')
            assert organizer.total_files == 3
            mock_read_csv.assert_called_once_with(sample_csv_file)
    
    def test_create_symlinks(self, temp_dirs, sample_csv_file, sample_files):
        """Test creating symlinks."""
        source_dir, symlink_dir, _ = temp_dirs
        
        # Create a real CSV file
        df = pd.DataFrame({
            'filepath': ['file1.txt', 'file2.txt', 'file3.txt'],
            'col1': ['category1', 'category1', 'category2'],
            'col2': ['subcategory1', 'subcategory2', 'subcategory1'],
            'col3': ['group1', 'group2', 'group1']
        })
        csv_path = os.path.join(source_dir, 'test.csv')
        df.to_csv(csv_path, index=False)
        
        # Create the organizer and run create_symlinks
        organizer = FileOrganizer(
            csv_file=csv_path,
            source_dir=source_dir,
            symlink_dir=symlink_dir,
            final_export_dir='not_used'
        )
        
        with patch('tqdm.tqdm') as mock_tqdm:
            mock_tqdm.return_value = df.iterrows()
            organizer.create_symlinks()
        
        # Check that symlinks were created with the correct structure
        expected_paths = [
            os.path.join(symlink_dir, 'category1', 'subcategory1', 'group1', 'file1.txt'),
            os.path.join(symlink_dir, 'category1', 'subcategory2', 'group2', 'file2.txt'),
            os.path.join(symlink_dir, 'category2', 'subcategory1', 'group1', 'file3.txt')
        ]
        
        for path in expected_paths:
            assert os.path.exists(path)
            assert os.path.islink(path)
    
    def test_run_rsync(self, temp_dirs, sample_csv_file):
        """Test running rsync."""
        source_dir, symlink_dir, export_dir = temp_dirs
        
        # Create the organizer
        organizer = FileOrganizer(
            csv_file=sample_csv_file,
            source_dir=source_dir,
            symlink_dir=symlink_dir,
            final_export_dir=export_dir
        )
        
        # Mock subprocess.Popen
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ['line1', 'line2', '']
        mock_process.wait.return_value = 0
        
        with patch('subprocess.Popen', return_value=mock_process) as mock_popen, \
             patch('os.walk', return_value=[('', [], ['file1', 'file2'])]) as mock_walk, \
             patch('tqdm.tqdm') as mock_tqdm:
            
            return_code = organizer.run_rsync()
            
            assert return_code == 0
            mock_popen.assert_called_once()
            # Check that rsync command was called with the correct arguments
            args, _ = mock_popen.call_args
            assert args[0][0] == 'rsync'
            assert args[0][1:3] == ['-av', '--copy-links']
            assert args[0][3].startswith(symlink_dir)
            assert args[0][4].startswith(export_dir)


@pytest.mark.unit
class TestOrganizeFiles:
    """Tests for the organize_files function."""
    
    def test_organize_files_with_symlinks(self, temp_dirs, sample_csv_file):
        """Test organizing files with symlinks."""
        source_dir, output_dir, _ = temp_dirs
        
        with patch('science_data_kit.core.utils.file_utils.FileOrganizer') as mock_organizer_class:
            mock_organizer = MagicMock()
            mock_organizer_class.return_value = mock_organizer
            
            organize_files(
                csv_file=sample_csv_file,
                source_dir=source_dir,
                output_dir=output_dir,
                use_symlinks=True
            )
            
            mock_organizer_class.assert_called_once_with(
                csv_file=sample_csv_file,
                source_dir=source_dir,
                symlink_dir=output_dir,
                final_export_dir=output_dir
            )
            mock_organizer.create_symlinks.assert_called_once()
            mock_organizer.execute.assert_not_called()
    
    def test_organize_files_with_copying(self, temp_dirs, sample_csv_file):
        """Test organizing files with copying."""
        source_dir, _, output_dir = temp_dirs
        
        with patch('science_data_kit.core.utils.file_utils.FileOrganizer') as mock_organizer_class, \
             patch('shutil.rmtree') as mock_rmtree:
            
            mock_organizer = MagicMock()
            mock_organizer_class.return_value = mock_organizer
            
            organize_files(
                csv_file=sample_csv_file,
                source_dir=source_dir,
                output_dir=output_dir,
                use_symlinks=False
            )
            
            # Check that FileOrganizer was created with the correct arguments
            mock_organizer_class.assert_called_once()
            args, kwargs = mock_organizer_class.call_args
            assert kwargs['csv_file'] == sample_csv_file
            assert kwargs['source_dir'] == source_dir
            assert kwargs['symlink_dir'].endswith('.temp_symlinks')
            assert kwargs['final_export_dir'] == output_dir
            
            # Check that execute was called with the correct arguments
            mock_organizer.execute.assert_called_once_with(
                hierarchy_columns=None,
                file_path_column='filepath',
                rsync_options=None,
                prompt_before_rsync=False
            )
            
            # Check that the temporary directory was cleaned up
            mock_rmtree.assert_called_once()
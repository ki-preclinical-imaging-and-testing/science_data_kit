"""
Tests for the file_clustering module.

This module contains unit tests for the file_clustering module, which provides
functionality for clustering files based on various criteria such as content
similarity, metadata similarity, and file type.
"""

import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import numpy as np
from pathlib import Path

from science_data_kit.core.file_handling.file_clustering import (
    ClusteringAlgorithm,
    ClusteringCriterion,
    ClusteringOptions,
    FileCluster,
    ClusteringResult,
    FileClustering,
    cluster_files,
    visualize_file_clusters,
    generate_cluster_report
)


class TestClusteringOptions(unittest.TestCase):
    """Tests for the ClusteringOptions class."""
    
    def test_default_options(self):
        """Test default clustering options."""
        options = ClusteringOptions()
        self.assertEqual(options.algorithm, ClusteringAlgorithm.DBSCAN)
        self.assertEqual(options.criterion, ClusteringCriterion.CONTENT)
        self.assertEqual(options.eps, 0.5)
        self.assertEqual(options.min_samples, 5)
        self.assertEqual(options.n_clusters, 5)
        self.assertEqual(options.linkage, "ward")
        self.assertIsNone(options.distance_threshold)
        self.assertEqual(options.n_components, 10)
        self.assertIsNotNone(options.content_analysis_options)
        self.assertIsNotNone(options.similarity_options)
        self.assertTrue(options.group_by_extension)
        self.assertTrue(options.apply_dimensionality_reduction)
        self.assertTrue(options.include_file_details)
    
    def test_custom_options(self):
        """Test custom clustering options."""
        options = ClusteringOptions(
            algorithm=ClusteringAlgorithm.KMEANS,
            criterion=ClusteringCriterion.METADATA,
            eps=0.3,
            min_samples=3,
            n_clusters=10,
            linkage="complete",
            distance_threshold=0.5,
            n_components=5,
            group_by_extension=False,
            apply_dimensionality_reduction=False,
            include_file_details=False
        )
        self.assertEqual(options.algorithm, ClusteringAlgorithm.KMEANS)
        self.assertEqual(options.criterion, ClusteringCriterion.METADATA)
        self.assertEqual(options.eps, 0.3)
        self.assertEqual(options.min_samples, 3)
        self.assertEqual(options.n_clusters, 10)
        self.assertEqual(options.linkage, "complete")
        self.assertEqual(options.distance_threshold, 0.5)
        self.assertEqual(options.n_components, 5)
        self.assertFalse(options.group_by_extension)
        self.assertFalse(options.apply_dimensionality_reduction)
        self.assertFalse(options.include_file_details)


class TestFileCluster(unittest.TestCase):
    """Tests for the FileCluster class."""
    
    def test_file_cluster_creation(self):
        """Test creating a file cluster."""
        cluster = FileCluster(
            id=1,
            files=["file1.txt", "file2.txt", "file3.txt"],
            centroid="file1.txt",
            similarity_scores={"file2.txt": 0.8, "file3.txt": 0.7},
            metadata={"criterion": "content", "algorithm": "dbscan"}
        )
        self.assertEqual(cluster.id, 1)
        self.assertEqual(len(cluster.files), 3)
        self.assertEqual(cluster.centroid, "file1.txt")
        self.assertEqual(cluster.similarity_scores["file2.txt"], 0.8)
        self.assertEqual(cluster.similarity_scores["file3.txt"], 0.7)
        self.assertEqual(cluster.metadata["criterion"], "content")
        self.assertEqual(cluster.metadata["algorithm"], "dbscan")


class TestClusteringResult(unittest.TestCase):
    """Tests for the ClusteringResult class."""
    
    def test_clustering_result_creation(self):
        """Test creating a clustering result."""
        cluster1 = FileCluster(
            id=1,
            files=["file1.txt", "file2.txt"],
            centroid="file1.txt",
            metadata={"criterion": "content"}
        )
        cluster2 = FileCluster(
            id=2,
            files=["file3.txt", "file4.txt"],
            centroid="file3.txt",
            metadata={"criterion": "content"}
        )
        result = ClusteringResult(
            clusters=[cluster1, cluster2],
            noise=["file5.txt"],
            total_files=5,
            total_clusters=2,
            algorithm="dbscan",
            criterion="content",
            execution_time=1.5
        )
        self.assertEqual(len(result.clusters), 2)
        self.assertEqual(len(result.noise), 1)
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.total_clusters, 2)
        self.assertEqual(result.algorithm, "dbscan")
        self.assertEqual(result.criterion, "content")
        self.assertEqual(result.execution_time, 1.5)
        self.assertIsNone(result.visualization_data)
        self.assertIsNone(result.error_message)


class TestFileClustering(unittest.TestCase):
    """Tests for the FileClustering class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_files = [
            "file1.txt",
            "file2.txt",
            "file3.txt",
            "file4.pdf",
            "file5.pdf",
            "file6.jpg"
        ]
    
    @patch('science_data_kit.core.file_handling.file_clustering.ContentAnalyzer')
    def test_cluster_by_content(self, mock_content_analyzer):
        """Test clustering files by content."""
        # Mock the content analyzer
        mock_analyzer_instance = MagicMock()
        mock_content_analyzer.return_value = mock_analyzer_instance
        
        # Mock the extract_features method
        mock_result = MagicMock()
        mock_result.files = self.test_files
        mock_result.clusters = [0, 0, 0, 1, 1, -1]  # 3 files in cluster 0, 2 in cluster 1, 1 noise
        mock_result.similarity_matrix = np.ones((6, 6))  # All similarities are 1.0
        mock_analyzer_instance.extract_features.return_value = mock_result
        
        # Create clustering options
        options = ClusteringOptions(
            algorithm=ClusteringAlgorithm.DBSCAN,
            criterion=ClusteringCriterion.CONTENT,
            group_by_extension=False  # Don't group by extension for this test
        )
        
        # Create clustering object and cluster files
        clustering = FileClustering(options)
        result = clustering.cluster_files(self.test_files)
        
        # Check that the content analyzer was called
        mock_content_analyzer.assert_called_once()
        mock_analyzer_instance.extract_features.assert_called_once_with(self.test_files)
        
        # Check the clustering result
        self.assertEqual(len(result.clusters), 2)
        self.assertEqual(len(result.noise), 1)
        self.assertEqual(result.total_files, 6)
        self.assertEqual(result.total_clusters, 2)
        self.assertEqual(result.algorithm, "dbscan")
        self.assertEqual(result.criterion, "content")
        
        # Check the clusters
        cluster0 = next(c for c in result.clusters if c.id == 0)
        cluster1 = next(c for c in result.clusters if c.id == 1)
        self.assertEqual(len(cluster0.files), 3)
        self.assertEqual(len(cluster1.files), 2)
        self.assertEqual(result.noise, ["file6.jpg"])
    
    @patch('science_data_kit.core.file_handling.file_clustering.calculate_metadata_similarity')
    @patch('science_data_kit.core.file_handling.file_clustering.DBSCAN')
    def test_cluster_by_metadata(self, mock_dbscan, mock_calculate_metadata_similarity):
        """Test clustering files by metadata."""
        # Mock the DBSCAN clusterer
        mock_dbscan_instance = MagicMock()
        mock_dbscan.return_value = mock_dbscan_instance
        mock_dbscan_instance.fit_predict.return_value = [0, 0, 0, 1, 1, -1]  # 3 files in cluster 0, 2 in cluster 1, 1 noise
        
        # Mock the metadata similarity calculation
        mock_calculate_metadata_similarity.return_value = 0.8  # All similarities are 0.8
        
        # Create clustering options
        options = ClusteringOptions(
            algorithm=ClusteringAlgorithm.DBSCAN,
            criterion=ClusteringCriterion.METADATA,
            group_by_extension=False  # Don't group by extension for this test
        )
        
        # Create clustering object and cluster files
        clustering = FileClustering(options)
        result = clustering.cluster_files(self.test_files)
        
        # Check that the DBSCAN clusterer was called
        mock_dbscan.assert_called_once()
        mock_dbscan_instance.fit_predict.assert_called_once()
        
        # Check that the metadata similarity calculation was called
        self.assertGreater(mock_calculate_metadata_similarity.call_count, 0)
        
        # Check the clustering result
        self.assertEqual(len(result.clusters), 2)
        self.assertEqual(len(result.noise), 1)
        self.assertEqual(result.total_files, 6)
        self.assertEqual(result.total_clusters, 2)
        self.assertEqual(result.algorithm, "dbscan")
        self.assertEqual(result.criterion, "metadata")
        
        # Check the clusters
        cluster0 = next(c for c in result.clusters if c.id == 0)
        cluster1 = next(c for c in result.clusters if c.id == 1)
        self.assertEqual(len(cluster0.files), 3)
        self.assertEqual(len(cluster1.files), 2)
        self.assertEqual(result.noise, ["file6.jpg"])
    
    def test_cluster_by_file_type(self):
        """Test clustering files by file type."""
        # Create clustering options
        options = ClusteringOptions(
            criterion=ClusteringCriterion.FILE_TYPE,
            group_by_extension=True
        )
        
        # Create clustering object and cluster files
        clustering = FileClustering(options)
        result = clustering.cluster_files(self.test_files)
        
        # Check the clustering result
        self.assertEqual(len(result.clusters), 3)  # 3 file types: .txt, .pdf, .jpg
        self.assertEqual(len(result.noise), 0)  # No noise in file type clustering
        self.assertEqual(result.total_files, 6)
        self.assertEqual(result.total_clusters, 3)
        self.assertEqual(result.algorithm, "file_type")
        self.assertEqual(result.criterion, "file_type")
        
        # Check the clusters
        txt_cluster = next(c for c in result.clusters if c.metadata["extension"] == ".txt")
        pdf_cluster = next(c for c in result.clusters if c.metadata["extension"] == ".pdf")
        jpg_cluster = next(c for c in result.clusters if c.metadata["extension"] == ".jpg")
        self.assertEqual(len(txt_cluster.files), 3)
        self.assertEqual(len(pdf_cluster.files), 2)
        self.assertEqual(len(jpg_cluster.files), 1)
    
    @patch('science_data_kit.core.file_handling.file_clustering.detect_similar_files')
    def test_cluster_by_combined(self, mock_detect_similar_files):
        """Test clustering files by combined criteria."""
        # Mock the detect_similar_files function
        mock_result = MagicMock()
        mock_result.duplicate_groups = [
            MagicMock(files=["file1.txt", "file2.txt"], reference_file="file1.txt", similarity_score=0.9, detection_method="combined"),
            MagicMock(files=["file4.pdf", "file5.pdf"], reference_file="file4.pdf", similarity_score=0.8, detection_method="combined")
        ]
        mock_detect_similar_files.return_value = mock_result
        
        # Create clustering options
        options = ClusteringOptions(
            criterion=ClusteringCriterion.COMBINED,
            group_by_extension=True
        )
        
        # Create clustering object and cluster files
        clustering = FileClustering(options)
        result = clustering.cluster_files(self.test_files)
        
        # Check that the detect_similar_files function was called
        self.assertEqual(mock_detect_similar_files.call_count, 2)  # Called for .txt and .pdf groups
        
        # Check the clustering result
        self.assertEqual(len(result.clusters), 2)
        self.assertEqual(result.total_files, 6)
        self.assertEqual(result.total_clusters, 2)
        self.assertEqual(result.algorithm, "combined")
        self.assertEqual(result.criterion, "combined")
        
        # Check the clusters
        txt_cluster = next(c for c in result.clusters if c.metadata["extension"] == ".txt")
        pdf_cluster = next(c for c in result.clusters if c.metadata["extension"] == ".pdf")
        self.assertEqual(len(txt_cluster.files), 2)
        self.assertEqual(len(pdf_cluster.files), 2)
        self.assertEqual(len(result.noise), 2)  # file3.txt and file6.jpg
    
    def test_group_files_by_extension(self):
        """Test grouping files by extension."""
        clustering = FileClustering()
        extension_groups = clustering._group_files_by_extension(self.test_files)
        
        self.assertEqual(len(extension_groups), 3)  # 3 file types: .txt, .pdf, .jpg
        self.assertEqual(len(extension_groups[".txt"]), 3)
        self.assertEqual(len(extension_groups[".pdf"]), 2)
        self.assertEqual(len(extension_groups[".jpg"]), 1)
        self.assertIn("file1.txt", extension_groups[".txt"])
        self.assertIn("file4.pdf", extension_groups[".pdf"])
        self.assertIn("file6.jpg", extension_groups[".jpg"])


class TestClusteringFunctions(unittest.TestCase):
    """Tests for the clustering functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_files = [
            "file1.txt",
            "file2.txt",
            "file3.pdf",
            "file4.jpg"
        ]
        self.cluster1 = FileCluster(
            id=1,
            files=["file1.txt", "file2.txt"],
            centroid="file1.txt",
            metadata={"criterion": "content"}
        )
        self.cluster2 = FileCluster(
            id=2,
            files=["file3.pdf"],
            metadata={"criterion": "content"}
        )
        self.result = ClusteringResult(
            clusters=[self.cluster1, self.cluster2],
            noise=["file4.jpg"],
            total_files=4,
            total_clusters=2,
            algorithm="dbscan",
            criterion="content",
            execution_time=1.5
        )
    
    @patch('science_data_kit.core.file_handling.file_clustering.FileClustering')
    def test_cluster_files(self, mock_file_clustering):
        """Test the cluster_files function."""
        # Mock the FileClustering class
        mock_clustering_instance = MagicMock()
        mock_file_clustering.return_value = mock_clustering_instance
        mock_clustering_instance.cluster_files.return_value = self.result
        
        # Call the cluster_files function
        options = ClusteringOptions()
        result = cluster_files(self.test_files, options)
        
        # Check that the FileClustering class was called
        mock_file_clustering.assert_called_once_with(options)
        mock_clustering_instance.cluster_files.assert_called_once_with(self.test_files)
        
        # Check the result
        self.assertEqual(result, self.result)
    
    @patch('science_data_kit.core.file_handling.file_clustering.plt')
    def test_visualize_file_clusters(self, mock_plt):
        """Test the visualize_file_clusters function."""
        # Add visualization data to the result
        self.result.visualization_data = {
            "method": "t-SNE",
            "coordinates": [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]],
            "files": self.test_files,
            "clusters": [1, 1, 2, -1]
        }
        
        # Call the visualize_file_clusters function
        output_file = "test_visualization.png"
        result = visualize_file_clusters(self.result, output_file)
        
        # Check that matplotlib was called
        mock_plt.figure.assert_called_once()
        mock_plt.scatter.assert_called()
        mock_plt.annotate.assert_called()
        mock_plt.title.assert_called_once()
        mock_plt.xlabel.assert_called_once()
        mock_plt.ylabel.assert_called_once()
        mock_plt.savefig.assert_called_once_with(output_file, dpi=300, bbox_inches='tight')
        mock_plt.close.assert_called_once()
        
        # Check the result
        self.assertEqual(result, self.result.visualization_data)
    
    def test_generate_cluster_report_text(self):
        """Test generating a text cluster report."""
        # Call the generate_cluster_report function
        report = generate_cluster_report(self.result, 'text')
        
        # Check the report
        self.assertIn("File Clustering Report", report)
        self.assertIn("Total files analyzed: 4", report)
        self.assertIn("Total clusters found: 2", report)
        self.assertIn("Clustering algorithm: dbscan", report)
        self.assertIn("Clustering criterion: content", report)
        self.assertIn("Cluster 1: 2 files", report)
        self.assertIn("Centroid: file1.txt", report)
        self.assertIn("Cluster 2: 1 files", report)
        self.assertIn("Noise: 1 files", report)
        self.assertIn("file4.jpg", report)
    
    def test_generate_cluster_report_json(self):
        """Test generating a JSON cluster report."""
        # Call the generate_cluster_report function
        report = generate_cluster_report(self.result, 'json')
        
        # Check the report
        self.assertIn('"total_files": 4', report)
        self.assertIn('"total_clusters": 2', report)
        self.assertIn('"algorithm": "dbscan"', report)
        self.assertIn('"criterion": "content"', report)
        self.assertIn('"id": 1', report)
        self.assertIn('"files": ["file1.txt", "file2.txt"]', report)
        self.assertIn('"centroid": "file1.txt"', report)
        self.assertIn('"noise": ["file4.jpg"]', report)
    
    def test_generate_cluster_report_html(self):
        """Test generating an HTML cluster report."""
        # Call the generate_cluster_report function
        report = generate_cluster_report(self.result, 'html')
        
        # Check the report
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("<title>File Clustering Report</title>", report)
        self.assertIn("Total files analyzed: 4", report)
        self.assertIn("Total clusters found: 2", report)
        self.assertIn("Clustering algorithm: dbscan", report)
        self.assertIn("Clustering criterion: content", report)
        self.assertIn("Cluster 1: 2 files", report)
        self.assertIn("Centroid: file1.txt", report)
        self.assertIn("Cluster 2: 1 files", report)
        self.assertIn("Noise: 1 files", report)
        self.assertIn("file4.jpg", report)
    
    def test_generate_cluster_report_invalid_format(self):
        """Test generating a report with an invalid format."""
        # Call the generate_cluster_report function with an invalid format
        with self.assertRaises(ValueError):
            generate_cluster_report(self.result, 'invalid')


if __name__ == '__main__':
    unittest.main()
"""
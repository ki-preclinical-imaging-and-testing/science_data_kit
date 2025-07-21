"""
Unit tests for the similarity visualization module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from science_data_kit.core.file_handling.similarity_visualization import (
    VisualizationType,
    VisualizationOptions,
    VisualizationResult,
    SimilarityVisualizer,
    visualize_file_similarities,
    visualize_similarity_matrix,
    save_visualization
)


class TestVisualizationOptions(unittest.TestCase):
    """Test cases for VisualizationOptions."""
    
    def test_default_options(self):
        """Test default options."""
        options = VisualizationOptions()
        self.assertEqual(options.visualization_type, VisualizationType.FORCE_DIRECTED_GRAPH)
        self.assertEqual(options.title, "File Similarity Visualization")
        self.assertEqual(options.width, 800)
        self.assertEqual(options.height, 600)
        self.assertEqual(options.similarity_threshold, 0.3)
        self.assertIsNone(options.similarity_options)
        self.assertIsNone(options.content_analysis_options)
        self.assertTrue(options.node_size_by_degree)
        self.assertTrue(options.edge_width_by_similarity)
        self.assertTrue(options.use_community_detection)
        self.assertTrue(options.show_file_names)
        self.assertEqual(options.colormap, "viridis")
        self.assertEqual(options.n_components, 2)
        self.assertEqual(options.perplexity, 30)
        self.assertEqual(options.output_format, "html")
        self.assertTrue(options.include_interactive_elements)


class TestVisualizationResult(unittest.TestCase):
    """Test cases for VisualizationResult."""
    
    def test_result_creation(self):
        """Test creating a visualization result."""
        result = VisualizationResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={
                "nodes": [{"id": 0, "name": "file1.txt"}, {"id": 1, "name": "file2.txt"}],
                "edges": [{"source": 0, "target": 1, "similarity": 0.8}]
            },
            html_output="<html>...</html>",
            image_output="data:image/png;base64,...",
            metadata={"num_files": 2, "num_edges": 1}
        )
        self.assertEqual(len(result.files), 2)
        self.assertEqual(result.visualization_type, VisualizationType.FORCE_DIRECTED_GRAPH)
        self.assertEqual(len(result.visualization_data["nodes"]), 2)
        self.assertEqual(len(result.visualization_data["edges"]), 1)
        self.assertEqual(result.html_output, "<html>...</html>")
        self.assertTrue(result.image_output.startswith("data:image/png;base64,"))
        self.assertEqual(result.metadata, {"num_files": 2, "num_edges": 1})


class TestSimilarityVisualizer(unittest.TestCase):
    """Test cases for SimilarityVisualizer."""
    
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._calculate_similarity_matrix')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.scatter')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._get_image_data')
    def test_tsne_visualization(self, mock_get_image, mock_close, mock_tight_layout, mock_title, 
                               mock_scatter, mock_figure, mock_calc_matrix):
        """Test t-SNE visualization."""
        # Mock the content analyzer
        with patch('science_data_kit.core.file_handling.similarity_visualization.ContentAnalyzer') as MockAnalyzer:
            # Create mock content result
            mock_result = MagicMock()
            mock_result.features = [
                MagicMock(features=np.array([0.1, 0.2, 0.3])),
                MagicMock(features=np.array([0.4, 0.5, 0.6]))
            ]
            
            # Set up the mock analyzer
            mock_analyzer_instance = MockAnalyzer.return_value
            mock_analyzer_instance.extract_features.return_value = mock_result
            
            # Mock the TSNE class
            with patch('sklearn.manifold.TSNE') as MockTSNE:
                # Set up the mock TSNE
                mock_tsne_instance = MockTSNE.return_value
                mock_tsne_instance.fit_transform.return_value = np.array([[1.0, 2.0], [3.0, 4.0]])
                
                # Set up the mock image data
                mock_get_image.return_value = "data:image/png;base64,..."
                
                # Create visualizer with t-SNE visualization type
                options = VisualizationOptions(visualization_type=VisualizationType.TSNE)
                visualizer = SimilarityVisualizer(options)
                
                # Generate visualization
                result = visualizer.visualize_file_similarities([
                    "/path/to/file1.txt",
                    "/path/to/file2.txt"
                ])
                
                # Verify results
                self.assertEqual(result.visualization_type, VisualizationType.TSNE)
                self.assertEqual(len(result.files), 2)
                self.assertEqual(result.visualization_data["coordinates"], [[1.0, 2.0], [3.0, 4.0]])
                self.assertEqual(result.visualization_data["file_names"], ["file1.txt", "file2.txt"])
                self.assertEqual(result.image_output, "data:image/png;base64,...")
                
                # Verify method calls
                MockAnalyzer.assert_called_once()
                mock_analyzer_instance.extract_features.assert_called_once()
                MockTSNE.assert_called_once_with(n_components=2, perplexity=1, random_state=42)
                mock_tsne_instance.fit_transform.assert_called_once()
                mock_figure.assert_called_once()
                mock_scatter.assert_called_once()
                mock_title.assert_called_once()
                mock_tight_layout.assert_called_once()
                mock_close.assert_called_once()
                mock_get_image.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._calculate_similarity_matrix')
    def test_empty_file_list(self, mock_calc_matrix):
        """Test visualization with empty file list."""
        visualizer = SimilarityVisualizer()
        result = visualizer.visualize_file_similarities([])
        
        self.assertEqual(result.files, [])
        self.assertEqual(result.visualization_data, {})
        mock_calc_matrix.assert_not_called()
    
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._visualize_force_directed_graph')
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._visualize_heatmap')
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._visualize_tsne')
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._visualize_pca')
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._visualize_umap')
    def test_visualization_type_selection(self, mock_umap, mock_pca, mock_tsne, mock_heatmap, mock_force):
        """Test selection of visualization type."""
        file_paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
        
        # Set up mock return values
        mock_result = VisualizationResult(
            files=file_paths,
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={}
        )
        mock_force.return_value = mock_result
        mock_heatmap.return_value = mock_result
        mock_tsne.return_value = mock_result
        mock_pca.return_value = mock_result
        mock_umap.return_value = mock_result
        
        # Test force-directed graph
        visualizer = SimilarityVisualizer(VisualizationOptions(
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH
        ))
        visualizer.visualize_file_similarities(file_paths)
        mock_force.assert_called_once()
        
        # Test heatmap
        visualizer = SimilarityVisualizer(VisualizationOptions(
            visualization_type=VisualizationType.HEATMAP
        ))
        visualizer.visualize_file_similarities(file_paths)
        mock_heatmap.assert_called_once()
        
        # Test t-SNE
        visualizer = SimilarityVisualizer(VisualizationOptions(
            visualization_type=VisualizationType.TSNE
        ))
        visualizer.visualize_file_similarities(file_paths)
        mock_tsne.assert_called_once()
        
        # Test PCA
        visualizer = SimilarityVisualizer(VisualizationOptions(
            visualization_type=VisualizationType.PCA
        ))
        visualizer.visualize_file_similarities(file_paths)
        mock_pca.assert_called_once()
        
        # Test UMAP
        visualizer = SimilarityVisualizer(VisualizationOptions(
            visualization_type=VisualizationType.UMAP
        ))
        visualizer.visualize_file_similarities(file_paths)
        mock_umap.assert_called_once()
        
        # Test unsupported type
        visualizer = SimilarityVisualizer(VisualizationOptions(
            visualization_type=VisualizationType.CUSTOM
        ))
        result = visualizer.visualize_file_similarities(file_paths)
        self.assertEqual(result.visualization_type, VisualizationType.CUSTOM)
        self.assertEqual(result.visualization_data, {})
    
    @patch('science_data_kit.core.file_handling.similarity_visualization.compare_files')
    def test_calculate_similarity_matrix(self, mock_compare):
        """Test calculation of similarity matrix."""
        # Mock the compare_files function
        mock_compare.return_value = MagicMock(similarity_score=0.8)
        
        # Create visualizer
        visualizer = SimilarityVisualizer()
        
        # Calculate similarity matrix
        file_paths = ["/path/to/file1.txt", "/path/to/file2.txt"]
        matrix = visualizer._calculate_similarity_matrix(file_paths)
        
        # Verify results
        self.assertEqual(matrix.shape, (2, 2))
        self.assertEqual(matrix[0, 0], 1.0)  # Self-similarity
        self.assertEqual(matrix[1, 1], 1.0)  # Self-similarity
        self.assertEqual(matrix[0, 1], 0.8)  # Similarity between files
        self.assertEqual(matrix[1, 0], 0.8)  # Similarity between files
        
        # Verify method calls
        self.assertEqual(mock_compare.call_count, 1)  # Only called once for the pair (0,1)


class TestVisualizationFunctions(unittest.TestCase):
    """Test cases for visualization functions."""
    
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer.visualize_file_similarities')
    def test_visualize_file_similarities_function(self, mock_visualize):
        """Test visualize_file_similarities function."""
        # Mock the visualizer's method
        mock_result = VisualizationResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={}
        )
        mock_visualize.return_value = mock_result
        
        # Call the function
        result = visualize_file_similarities(
            file_paths=["/path/to/file1.txt", "/path/to/file2.txt"]
        )
        
        # Verify result
        self.assertEqual(result, mock_result)
    
    @patch('matplotlib.pyplot.figure')
    @patch('seaborn.heatmap')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('science_data_kit.core.file_handling.similarity_visualization.SimilarityVisualizer._get_image_data')
    def test_visualize_similarity_matrix_function(self, mock_get_image, mock_close, mock_tight_layout, 
                                                mock_title, mock_heatmap, mock_figure):
        """Test visualize_similarity_matrix function."""
        # Mock the image data
        mock_get_image.return_value = "data:image/png;base64,..."
        
        # Create similarity matrix
        similarity_matrix = np.array([[1.0, 0.8], [0.8, 1.0]])
        file_names = ["file1.txt", "file2.txt"]
        
        # Call the function
        result = visualize_similarity_matrix(similarity_matrix, file_names)
        
        # Verify results
        self.assertEqual(result.visualization_type, VisualizationType.HEATMAP)
        self.assertEqual(result.visualization_data["similarity_matrix"], similarity_matrix.tolist())
        self.assertEqual(result.visualization_data["file_names"], file_names)
        self.assertEqual(result.image_output, "data:image/png;base64,...")
        
        # Verify method calls
        mock_figure.assert_called_once()
        mock_heatmap.assert_called_once()
        mock_title.assert_called_once()
        mock_tight_layout.assert_called_once()
        mock_close.assert_called_once()
        mock_get_image.assert_called_once()
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_visualization_html(self, mock_open):
        """Test saving visualization as HTML."""
        # Create visualization result
        result = VisualizationResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={},
            html_output="<html>...</html>"
        )
        
        # Save visualization
        success = save_visualization(result, "/path/to/output.html")
        
        # Verify results
        self.assertTrue(success)
        mock_open.assert_called_once_with("/path/to/output.html", 'w', encoding='utf-8')
        mock_open().write.assert_called_once_with("<html>...</html>")
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('base64.b64decode')
    def test_save_visualization_image(self, mock_b64decode, mock_open):
        """Test saving visualization as image."""
        # Mock base64 decode
        mock_b64decode.return_value = b"image data"
        
        # Create visualization result
        result = VisualizationResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={},
            image_output="data:image/png;base64,aW1hZ2UgZGF0YQ=="
        )
        
        # Save visualization
        success = save_visualization(result, "/path/to/output.png")
        
        # Verify results
        self.assertTrue(success)
        mock_b64decode.assert_called_once_with("aW1hZ2UgZGF0YQ==")
        mock_open.assert_called_once_with("/path/to/output.png", 'wb')
        mock_open().write.assert_called_once_with(b"image data")
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_save_visualization_json(self, mock_json_dump, mock_open):
        """Test saving visualization as JSON."""
        # Create visualization result
        result = VisualizationResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={"nodes": [], "edges": []}
        )
        
        # Save visualization
        success = save_visualization(result, "/path/to/output.json")
        
        # Verify results
        self.assertTrue(success)
        mock_open.assert_called_once_with("/path/to/output.json", 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
        self.assertEqual(mock_json_dump.call_args[0][0], {"nodes": [], "edges": []})
    
    def test_save_visualization_unsupported_format(self):
        """Test saving visualization with unsupported format."""
        # Create visualization result
        result = VisualizationResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
            visualization_data={}
        )
        
        # Save visualization
        success = save_visualization(result, "/path/to/output.xyz")
        
        # Verify results
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
"""
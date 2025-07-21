"""
Similarity visualization module for visualizing file similarities.

This module provides functionality for visualizing the similarities between files
using various visualization techniques such as force-directed graphs, heatmaps,
and dimensionality reduction plots. It builds on the existing similarity analysis
and content analysis modules to provide intuitive visualizations of file relationships.

The module includes:
- Visualization options class for configuring visualizations
- Visualization result class for storing visualization data
- Functions for generating different types of visualizations
- Utilities for exporting visualizations to various formats
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from science_data_kit.core.file_handling.similarity_analysis import (
    SimilarityOptions,
    SimilarityResult,
    compare_files,
    find_similar_files
)
from science_data_kit.core.file_handling.content_analysis import (
    ContentAnalysisOptions,
    ContentAnalyzer,
    analyze_content
)

logger = logging.getLogger(__name__)


class VisualizationType(Enum):
    """Enumeration of visualization types."""
    FORCE_DIRECTED_GRAPH = "force_directed_graph"
    HEATMAP = "heatmap"
    TSNE = "tsne"
    PCA = "pca"
    UMAP = "umap"
    CUSTOM = "custom"


@dataclass
class VisualizationOptions:
    """Options for similarity visualization."""
    # General options
    visualization_type: VisualizationType = VisualizationType.FORCE_DIRECTED_GRAPH
    title: str = "File Similarity Visualization"
    width: int = 800
    height: int = 600
    
    # Similarity options
    similarity_threshold: float = 0.3
    similarity_options: Optional[SimilarityOptions] = None
    content_analysis_options: Optional[ContentAnalysisOptions] = None
    
    # Force-directed graph options
    node_size_by_degree: bool = True
    edge_width_by_similarity: bool = True
    use_community_detection: bool = True
    
    # Heatmap options
    show_file_names: bool = True
    colormap: str = "viridis"
    
    # Dimensionality reduction options
    n_components: int = 2
    perplexity: int = 30  # for t-SNE
    
    # Output options
    output_format: str = "html"
    include_interactive_elements: bool = True


@dataclass
class VisualizationResult:
    """Result of a similarity visualization."""
    files: List[str]
    visualization_type: VisualizationType
    visualization_data: Dict[str, Any]
    html_output: Optional[str] = None
    image_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimilarityVisualizer:
    """Class for visualizing file similarities."""
    
    def __init__(self, options: Optional[VisualizationOptions] = None):
        """
        Initialize the similarity visualizer.
        
        Args:
            options: Visualization options
        """
        self.options = options or VisualizationOptions()
    
    def visualize_file_similarities(self, file_paths: List[str]) -> VisualizationResult:
        """
        Visualize similarities between files.
        
        Args:
            file_paths: List of file paths to visualize
            
        Returns:
            VisualizationResult object containing the visualization data
        """
        if not file_paths:
            logger.warning("Empty file list for visualization")
            return VisualizationResult(
                files=[],
                visualization_type=self.options.visualization_type,
                visualization_data={}
            )
        
        # Generate visualization based on the selected type
        if self.options.visualization_type == VisualizationType.FORCE_DIRECTED_GRAPH:
            return self._visualize_force_directed_graph(file_paths)
        elif self.options.visualization_type == VisualizationType.HEATMAP:
            return self._visualize_heatmap(file_paths)
        elif self.options.visualization_type == VisualizationType.TSNE:
            return self._visualize_tsne(file_paths)
        elif self.options.visualization_type == VisualizationType.PCA:
            return self._visualize_pca(file_paths)
        elif self.options.visualization_type == VisualizationType.UMAP:
            return self._visualize_umap(file_paths)
        else:
            logger.warning(f"Unsupported visualization type: {self.options.visualization_type}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=self.options.visualization_type,
                visualization_data={}
            )
    
    def _calculate_similarity_matrix(self, file_paths: List[str]) -> np.ndarray:
        """
        Calculate similarity matrix for a list of files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Similarity matrix as numpy array
        """
        n_files = len(file_paths)
        similarity_matrix = np.zeros((n_files, n_files))
        
        # Use content analysis if available
        if self.options.content_analysis_options is not None:
            # Analyze content
            analyzer = ContentAnalyzer(self.options.content_analysis_options)
            result = analyzer.extract_features(file_paths)
            
            if result.similarity_matrix is not None:
                return result.similarity_matrix
        
        # Otherwise, calculate pairwise similarities
        similarity_options = self.options.similarity_options or SimilarityOptions(
            threshold=self.options.similarity_threshold
        )
        
        for i in range(n_files):
            for j in range(i, n_files):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                else:
                    result = compare_files(file_paths[i], file_paths[j], similarity_options)
                    similarity_matrix[i, j] = result.similarity_score
                    similarity_matrix[j, i] = result.similarity_score
        
        return similarity_matrix
    
    def _visualize_force_directed_graph(self, file_paths: List[str]) -> VisualizationResult:
        """
        Create a force-directed graph visualization of file similarities.
        
        Args:
            file_paths: List of file paths to visualize
            
        Returns:
            VisualizationResult object containing the visualization data
        """
        try:
            # Try to import visualization libraries
            import networkx as nx
            import matplotlib.pyplot as plt
            from matplotlib.colors import Normalize
            from matplotlib.cm import ScalarMappable
            
            # Calculate similarity matrix
            similarity_matrix = self._calculate_similarity_matrix(file_paths)
            
            # Create graph
            G = nx.Graph()
            
            # Add nodes
            for i, file_path in enumerate(file_paths):
                G.add_node(i, name=os.path.basename(file_path), path=file_path)
            
            # Add edges for similarities above threshold
            for i in range(len(file_paths)):
                for j in range(i+1, len(file_paths)):
                    similarity = similarity_matrix[i, j]
                    if similarity >= self.options.similarity_threshold:
                        G.add_edge(i, j, weight=similarity)
            
            # Apply community detection if requested
            if self.options.use_community_detection:
                try:
                    from community import best_partition
                    partition = best_partition(G)
                    nx.set_node_attributes(G, partition, 'community')
                except ImportError:
                    logger.warning("python-louvain package not installed. Community detection disabled.")
                    partition = {i: 0 for i in range(len(file_paths))}
            else:
                partition = {i: 0 for i in range(len(file_paths))}
            
            # Create visualization
            plt.figure(figsize=(self.options.width/100, self.options.height/100), dpi=100)
            
            # Set node sizes based on degree if requested
            if self.options.node_size_by_degree:
                node_sizes = [300 * (1 + G.degree(n)) for n in G.nodes()]
            else:
                node_sizes = [300] * len(G.nodes())
            
            # Set edge widths based on similarity if requested
            if self.options.edge_width_by_similarity:
                edge_widths = [2 * G[u][v]['weight'] for u, v in G.edges()]
            else:
                edge_widths = [1] * len(G.edges())
            
            # Set node colors based on community
            node_colors = [partition[n] for n in G.nodes()]
            
            # Create layout
            pos = nx.spring_layout(G, k=0.3, iterations=50)
            
            # Draw graph
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8, cmap=plt.cm.tab10)
            nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5)
            
            # Add labels if not too many nodes
            if len(G.nodes()) <= 20:
                nx.draw_networkx_labels(G, pos, {n: G.nodes[n]['name'] for n in G.nodes()}, font_size=8)
            
            plt.title(self.options.title)
            plt.axis('off')
            
            # Save visualization
            html_output = None
            image_output = None
            
            if self.options.output_format == 'html' and self.options.include_interactive_elements:
                try:
                    import mpld3
                    html_output = mpld3.fig_to_html(plt.gcf())
                except ImportError:
                    logger.warning("mpld3 package not installed. Falling back to static image.")
                    image_output = self._get_image_data(plt.gcf())
            else:
                image_output = self._get_image_data(plt.gcf())
            
            # Close the plot to free memory
            plt.close()
            
            # Create visualization data
            visualization_data = {
                "nodes": [
                    {
                        "id": n,
                        "name": G.nodes[n]['name'],
                        "path": G.nodes[n]['path'],
                        "community": partition[n],
                        "degree": G.degree(n)
                    } for n in G.nodes()
                ],
                "edges": [
                    {
                        "source": u,
                        "target": v,
                        "similarity": G[u][v]['weight']
                    } for u, v in G.edges()
                ],
                "communities": len(set(partition.values()))
            }
            
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
                visualization_data=visualization_data,
                html_output=html_output,
                image_output=image_output,
                metadata={
                    "num_files": len(file_paths),
                    "num_edges": len(G.edges()),
                    "avg_similarity": np.mean([G[u][v]['weight'] for u, v in G.edges()]) if G.edges() else 0,
                    "num_communities": len(set(partition.values()))
                }
            )
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
                visualization_data={}
            )
        
        except Exception as e:
            logger.error(f"Error creating force-directed graph visualization: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.FORCE_DIRECTED_GRAPH,
                visualization_data={}
            )
    
    def _visualize_heatmap(self, file_paths: List[str]) -> VisualizationResult:
        """
        Create a heatmap visualization of file similarities.
        
        Args:
            file_paths: List of file paths to visualize
            
        Returns:
            VisualizationResult object containing the visualization data
        """
        try:
            # Try to import visualization libraries
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Calculate similarity matrix
            similarity_matrix = self._calculate_similarity_matrix(file_paths)
            
            # Create visualization
            plt.figure(figsize=(self.options.width/100, self.options.height/100), dpi=100)
            
            # Create heatmap
            ax = sns.heatmap(
                similarity_matrix,
                cmap=self.options.colormap,
                vmin=0,
                vmax=1,
                annot=False,
                square=True,
                linewidths=0.5
            )
            
            # Add labels if requested and not too many files
            if self.options.show_file_names and len(file_paths) <= 20:
                file_names = [os.path.basename(f) for f in file_paths]
                ax.set_xticks(np.arange(len(file_names)) + 0.5)
                ax.set_yticks(np.arange(len(file_names)) + 0.5)
                ax.set_xticklabels(file_names, rotation=45, ha='right')
                ax.set_yticklabels(file_names)
            
            plt.title(self.options.title)
            plt.tight_layout()
            
            # Save visualization
            html_output = None
            image_output = None
            
            if self.options.output_format == 'html' and self.options.include_interactive_elements:
                try:
                    import mpld3
                    html_output = mpld3.fig_to_html(plt.gcf())
                except ImportError:
                    logger.warning("mpld3 package not installed. Falling back to static image.")
                    image_output = self._get_image_data(plt.gcf())
            else:
                image_output = self._get_image_data(plt.gcf())
            
            # Close the plot to free memory
            plt.close()
            
            # Create visualization data
            visualization_data = {
                "similarity_matrix": similarity_matrix.tolist(),
                "file_names": [os.path.basename(f) for f in file_paths]
            }
            
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.HEATMAP,
                visualization_data=visualization_data,
                html_output=html_output,
                image_output=image_output,
                metadata={
                    "num_files": len(file_paths),
                    "avg_similarity": np.mean(similarity_matrix),
                    "max_similarity": np.max(similarity_matrix) if similarity_matrix.size > 0 else 0,
                    "min_similarity": np.min(similarity_matrix) if similarity_matrix.size > 0 else 0
                }
            )
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.HEATMAP,
                visualization_data={}
            )
        
        except Exception as e:
            logger.error(f"Error creating heatmap visualization: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.HEATMAP,
                visualization_data={}
            )
    
    def _visualize_tsne(self, file_paths: List[str]) -> VisualizationResult:
        """
        Create a t-SNE visualization of file similarities.
        
        Args:
            file_paths: List of file paths to visualize
            
        Returns:
            VisualizationResult object containing the visualization data
        """
        try:
            # Try to import visualization libraries
            import matplotlib.pyplot as plt
            from sklearn.manifold import TSNE
            
            # Use content analysis to get features
            analyzer = ContentAnalyzer(self.options.content_analysis_options)
            content_result = analyzer.extract_features(file_paths)
            
            if not content_result.features:
                logger.warning("No features extracted for t-SNE visualization")
                return VisualizationResult(
                    files=file_paths,
                    visualization_type=VisualizationType.TSNE,
                    visualization_data={}
                )
            
            # Get feature matrix
            feature_matrix = np.vstack([f.features for f in content_result.features])
            
            # Apply t-SNE
            tsne = TSNE(
                n_components=self.options.n_components,
                perplexity=min(self.options.perplexity, len(file_paths) - 1),
                random_state=42
            )
            tsne_result = tsne.fit_transform(feature_matrix)
            
            # Create visualization
            plt.figure(figsize=(self.options.width/100, self.options.height/100), dpi=100)
            
            # Plot points
            plt.scatter(tsne_result[:, 0], tsne_result[:, 1])
            
            # Add labels if not too many files
            if len(file_paths) <= 20:
                for i, file_path in enumerate(file_paths):
                    plt.annotate(
                        os.path.basename(file_path),
                        (tsne_result[i, 0], tsne_result[i, 1]),
                        fontsize=8
                    )
            
            plt.title(self.options.title)
            plt.tight_layout()
            
            # Save visualization
            html_output = None
            image_output = None
            
            if self.options.output_format == 'html' and self.options.include_interactive_elements:
                try:
                    import mpld3
                    html_output = mpld3.fig_to_html(plt.gcf())
                except ImportError:
                    logger.warning("mpld3 package not installed. Falling back to static image.")
                    image_output = self._get_image_data(plt.gcf())
            else:
                image_output = self._get_image_data(plt.gcf())
            
            # Close the plot to free memory
            plt.close()
            
            # Create visualization data
            visualization_data = {
                "coordinates": tsne_result.tolist(),
                "file_names": [os.path.basename(f) for f in file_paths]
            }
            
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.TSNE,
                visualization_data=visualization_data,
                html_output=html_output,
                image_output=image_output,
                metadata={
                    "num_files": len(file_paths),
                    "perplexity": min(self.options.perplexity, len(file_paths) - 1),
                    "n_components": self.options.n_components
                }
            )
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.TSNE,
                visualization_data={}
            )
        
        except Exception as e:
            logger.error(f"Error creating t-SNE visualization: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.TSNE,
                visualization_data={}
            )
    
    def _visualize_pca(self, file_paths: List[str]) -> VisualizationResult:
        """
        Create a PCA visualization of file similarities.
        
        Args:
            file_paths: List of file paths to visualize
            
        Returns:
            VisualizationResult object containing the visualization data
        """
        try:
            # Try to import visualization libraries
            import matplotlib.pyplot as plt
            from sklearn.decomposition import PCA
            
            # Use content analysis to get features
            analyzer = ContentAnalyzer(self.options.content_analysis_options)
            content_result = analyzer.extract_features(file_paths)
            
            if not content_result.features:
                logger.warning("No features extracted for PCA visualization")
                return VisualizationResult(
                    files=file_paths,
                    visualization_type=VisualizationType.PCA,
                    visualization_data={}
                )
            
            # Get feature matrix
            feature_matrix = np.vstack([f.features for f in content_result.features])
            
            # Apply PCA
            n_components = min(self.options.n_components, feature_matrix.shape[0], feature_matrix.shape[1])
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(feature_matrix)
            
            # Create visualization
            plt.figure(figsize=(self.options.width/100, self.options.height/100), dpi=100)
            
            # Plot points
            plt.scatter(pca_result[:, 0], pca_result[:, 1])
            
            # Add labels if not too many files
            if len(file_paths) <= 20:
                for i, file_path in enumerate(file_paths):
                    plt.annotate(
                        os.path.basename(file_path),
                        (pca_result[i, 0], pca_result[i, 1]),
                        fontsize=8
                    )
            
            plt.title(self.options.title)
            plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.2%})")
            plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.2%})")
            plt.tight_layout()
            
            # Save visualization
            html_output = None
            image_output = None
            
            if self.options.output_format == 'html' and self.options.include_interactive_elements:
                try:
                    import mpld3
                    html_output = mpld3.fig_to_html(plt.gcf())
                except ImportError:
                    logger.warning("mpld3 package not installed. Falling back to static image.")
                    image_output = self._get_image_data(plt.gcf())
            else:
                image_output = self._get_image_data(plt.gcf())
            
            # Close the plot to free memory
            plt.close()
            
            # Create visualization data
            visualization_data = {
                "coordinates": pca_result.tolist(),
                "file_names": [os.path.basename(f) for f in file_paths],
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist()
            }
            
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.PCA,
                visualization_data=visualization_data,
                html_output=html_output,
                image_output=image_output,
                metadata={
                    "num_files": len(file_paths),
                    "n_components": n_components,
                    "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
                    "total_explained_variance": sum(pca.explained_variance_ratio_)
                }
            )
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.PCA,
                visualization_data={}
            )
        
        except Exception as e:
            logger.error(f"Error creating PCA visualization: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.PCA,
                visualization_data={}
            )
    
    def _visualize_umap(self, file_paths: List[str]) -> VisualizationResult:
        """
        Create a UMAP visualization of file similarities.
        
        Args:
            file_paths: List of file paths to visualize
            
        Returns:
            VisualizationResult object containing the visualization data
        """
        try:
            # Try to import visualization libraries
            import matplotlib.pyplot as plt
            import umap
            
            # Use content analysis to get features
            analyzer = ContentAnalyzer(self.options.content_analysis_options)
            content_result = analyzer.extract_features(file_paths)
            
            if not content_result.features:
                logger.warning("No features extracted for UMAP visualization")
                return VisualizationResult(
                    files=file_paths,
                    visualization_type=VisualizationType.UMAP,
                    visualization_data={}
                )
            
            # Get feature matrix
            feature_matrix = np.vstack([f.features for f in content_result.features])
            
            # Apply UMAP
            reducer = umap.UMAP(n_components=self.options.n_components)
            umap_result = reducer.fit_transform(feature_matrix)
            
            # Create visualization
            plt.figure(figsize=(self.options.width/100, self.options.height/100), dpi=100)
            
            # Plot points
            plt.scatter(umap_result[:, 0], umap_result[:, 1])
            
            # Add labels if not too many files
            if len(file_paths) <= 20:
                for i, file_path in enumerate(file_paths):
                    plt.annotate(
                        os.path.basename(file_path),
                        (umap_result[i, 0], umap_result[i, 1]),
                        fontsize=8
                    )
            
            plt.title(self.options.title)
            plt.tight_layout()
            
            # Save visualization
            html_output = None
            image_output = None
            
            if self.options.output_format == 'html' and self.options.include_interactive_elements:
                try:
                    import mpld3
                    html_output = mpld3.fig_to_html(plt.gcf())
                except ImportError:
                    logger.warning("mpld3 package not installed. Falling back to static image.")
                    image_output = self._get_image_data(plt.gcf())
            else:
                image_output = self._get_image_data(plt.gcf())
            
            # Close the plot to free memory
            plt.close()
            
            # Create visualization data
            visualization_data = {
                "coordinates": umap_result.tolist(),
                "file_names": [os.path.basename(f) for f in file_paths]
            }
            
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.UMAP,
                visualization_data=visualization_data,
                html_output=html_output,
                image_output=image_output,
                metadata={
                    "num_files": len(file_paths),
                    "n_components": self.options.n_components
                }
            )
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.UMAP,
                visualization_data={}
            )
        
        except Exception as e:
            logger.error(f"Error creating UMAP visualization: {e}")
            return VisualizationResult(
                files=file_paths,
                visualization_type=VisualizationType.UMAP,
                visualization_data={}
            )
    
    def _get_image_data(self, fig) -> str:
        """
        Get image data as base64 string.
        
        Args:
            fig: Matplotlib figure
            
        Returns:
            Base64-encoded image data
        """
        try:
            import io
            import base64
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            img_data = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_data}"
        
        except Exception as e:
            logger.error(f"Error getting image data: {e}")
            return ""


def visualize_file_similarities(file_paths: List[str], 
                              options: Optional[VisualizationOptions] = None) -> VisualizationResult:
    """
    Visualize similarities between files.
    
    Args:
        file_paths: List of file paths to visualize
        options: Visualization options
        
    Returns:
        VisualizationResult object containing the visualization data
    """
    visualizer = SimilarityVisualizer(options)
    return visualizer.visualize_file_similarities(file_paths)


def visualize_similarity_matrix(similarity_matrix: np.ndarray, file_names: List[str],
                              options: Optional[VisualizationOptions] = None) -> VisualizationResult:
    """
    Visualize a pre-computed similarity matrix.
    
    Args:
        similarity_matrix: Pre-computed similarity matrix
        file_names: List of file names corresponding to the matrix
        options: Visualization options
        
    Returns:
        VisualizationResult object containing the visualization data
    """
    try:
        # Try to import visualization libraries
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Create options if not provided
        if options is None:
            options = VisualizationOptions(visualization_type=VisualizationType.HEATMAP)
        
        # Create visualization
        plt.figure(figsize=(options.width/100, options.height/100), dpi=100)
        
        # Create heatmap
        ax = sns.heatmap(
            similarity_matrix,
            cmap=options.colormap,
            vmin=0,
            vmax=1,
            annot=False,
            square=True,
            linewidths=0.5
        )
        
        # Add labels if requested and not too many files
        if options.show_file_names and len(file_names) <= 20:
            ax.set_xticks(np.arange(len(file_names)) + 0.5)
            ax.set_yticks(np.arange(len(file_names)) + 0.5)
            ax.set_xticklabels(file_names, rotation=45, ha='right')
            ax.set_yticklabels(file_names)
        
        plt.title(options.title)
        plt.tight_layout()
        
        # Save visualization
        html_output = None
        image_output = None
        
        if options.output_format == 'html' and options.include_interactive_elements:
            try:
                import mpld3
                html_output = mpld3.fig_to_html(plt.gcf())
            except ImportError:
                logger.warning("mpld3 package not installed. Falling back to static image.")
                image_output = SimilarityVisualizer()._get_image_data(plt.gcf())
        else:
            image_output = SimilarityVisualizer()._get_image_data(plt.gcf())
        
        # Close the plot to free memory
        plt.close()
        
        # Create visualization data
        visualization_data = {
            "similarity_matrix": similarity_matrix.tolist(),
            "file_names": file_names
        }
        
        return VisualizationResult(
            files=[],  # No actual files, just names
            visualization_type=VisualizationType.HEATMAP,
            visualization_data=visualization_data,
            html_output=html_output,
            image_output=image_output,
            metadata={
                "num_files": len(file_names),
                "avg_similarity": np.mean(similarity_matrix),
                "max_similarity": np.max(similarity_matrix) if similarity_matrix.size > 0 else 0,
                "min_similarity": np.min(similarity_matrix) if similarity_matrix.size > 0 else 0
            }
        )
    
    except ImportError as e:
        logger.error(f"Error importing visualization libraries: {e}")
        return VisualizationResult(
            files=[],
            visualization_type=VisualizationType.HEATMAP,
            visualization_data={}
        )
    
    except Exception as e:
        logger.error(f"Error creating heatmap visualization: {e}")
        return VisualizationResult(
            files=[],
            visualization_type=VisualizationType.HEATMAP,
            visualization_data={}
        )


def save_visualization(result: VisualizationResult, output_path: str) -> bool:
    """
    Save visualization to a file.
    
    Args:
        result: VisualizationResult object containing the visualization data
        output_path: Path to save the visualization
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Determine output format based on file extension
        _, ext = os.path.splitext(output_path)
        ext = ext.lower()
        
        if ext == '.html' and result.html_output:
            # Save HTML output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.html_output)
            logger.info(f"Visualization saved to {output_path}")
            return True
        
        elif ext in ['.png', '.jpg', '.jpeg', '.svg', '.pdf'] and result.image_output:
            # Save image output
            if result.image_output.startswith('data:image/png;base64,'):
                import base64
                img_data = result.image_output.split(',')[1]
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                logger.info(f"Visualization saved to {output_path}")
                return True
            else:
                logger.error(f"Invalid image data format")
                return False
        
        elif ext == '.json':
            # Save visualization data as JSON
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.visualization_data, f, indent=2)
            logger.info(f"Visualization data saved to {output_path}")
            return True
        
        else:
            logger.error(f"Unsupported output format: {ext}")
            return False
    
    except Exception as e:
        logger.error(f"Error saving visualization: {e}")
        return False
"""
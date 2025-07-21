"""
File Clustering for Science Data Kit

This module provides functionality for clustering files based on various criteria
such as content similarity, metadata similarity, and file type. It builds on the
existing similarity analysis, content analysis, and duplicate detection modules
to provide more advanced clustering capabilities.

The module includes:
1. Functions for clustering files based on different criteria
2. Support for various clustering algorithms (DBSCAN, K-means, hierarchical)
3. Visualization and reporting capabilities
4. Integration with existing similarity analysis and duplicate detection code
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import numpy as np
from pathlib import Path

from science_data_kit.core.file_handling.similarity_analysis import (
    calculate_content_similarity, calculate_metadata_similarity,
    SimilarityMetricType, SimilarityOptions, SimilarityResult
)
from science_data_kit.core.file_handling.content_analysis import (
    ContentAnalysisOptions, ContentAnalysisResult, ContentAnalyzer,
    ContentFeatureType, cluster_documents_by_content
)
from science_data_kit.core.file_handling.duplicate_detection import (
    DuplicateDetectionStrategy, DuplicateGroup, DuplicateDetectionResult,
    detect_duplicates, detect_similar_files, group_duplicates_by_directory
)

# Set up logging
logger = logging.getLogger(__name__)


class ClusteringAlgorithm(Enum):
    """Enumeration of clustering algorithms."""
    DBSCAN = "dbscan"  # Density-based clustering
    KMEANS = "kmeans"  # K-means clustering
    HIERARCHICAL = "hierarchical"  # Hierarchical clustering
    SPECTRAL = "spectral"  # Spectral clustering


class ClusteringCriterion(Enum):
    """Enumeration of clustering criteria."""
    CONTENT = "content"  # Cluster by content similarity
    METADATA = "metadata"  # Cluster by metadata similarity
    FILE_TYPE = "file_type"  # Cluster by file type
    COMBINED = "combined"  # Cluster by a combination of criteria
    CUSTOM = "custom"  # Cluster by custom criteria


@dataclass
class ClusteringOptions:
    """Options for file clustering."""
    # Clustering algorithm options
    algorithm: ClusteringAlgorithm = ClusteringAlgorithm.DBSCAN
    criterion: ClusteringCriterion = ClusteringCriterion.CONTENT
    
    # DBSCAN options
    eps: float = 0.5  # DBSCAN epsilon parameter
    min_samples: int = 5  # DBSCAN min_samples parameter
    
    # K-means options
    n_clusters: int = 5  # Number of clusters for K-means
    
    # Hierarchical options
    linkage: str = "ward"  # Linkage method for hierarchical clustering
    distance_threshold: Optional[float] = None  # Distance threshold for hierarchical clustering
    
    # Spectral options
    n_components: int = 10  # Number of components for spectral clustering
    
    # Content analysis options
    content_analysis_options: Optional[ContentAnalysisOptions] = None
    
    # Similarity options
    similarity_options: Optional[SimilarityOptions] = None
    
    # File type options
    group_by_extension: bool = True  # Group files by extension before clustering
    
    # Visualization options
    apply_dimensionality_reduction: bool = True  # Apply dimensionality reduction for visualization
    
    # Reporting options
    include_file_details: bool = True  # Include detailed file information in reports
    
    def __post_init__(self):
        """Validate options and set defaults."""
        # Set default content analysis options if not provided
        if self.content_analysis_options is None:
            self.content_analysis_options = ContentAnalysisOptions(
                feature_type=ContentFeatureType.TFIDF,
                apply_clustering=True,
                apply_dimensionality_reduction=self.apply_dimensionality_reduction,
                eps=self.eps,
                min_samples=self.min_samples
            )
        
        # Set default similarity options if not provided
        if self.similarity_options is None:
            self.similarity_options = SimilarityOptions(
                metric_type=SimilarityMetricType.COSINE,
                threshold=0.7
            )


@dataclass
class FileCluster:
    """A cluster of files."""
    id: int
    files: List[str]
    centroid: Optional[str] = None  # Representative file (closest to cluster center)
    similarity_scores: Dict[str, float] = field(default_factory=dict)  # Similarity to centroid
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusteringResult:
    """Result of a file clustering operation."""
    clusters: List[FileCluster]
    noise: List[str]  # Files not assigned to any cluster
    total_files: int
    total_clusters: int
    algorithm: str
    criterion: str
    execution_time: float = 0.0
    visualization_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class FileClustering:
    """Class for clustering files based on various criteria."""
    
    def __init__(self, options: Optional[ClusteringOptions] = None):
        """
        Initialize the file clustering object.
        
        Args:
            options: Clustering options
        """
        self.options = options or ClusteringOptions()
        self.content_analyzer = None
        self.clusterer = None
    
    def cluster_files(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on the specified criterion and algorithm.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        import time
        start_time = time.time()
        
        try:
            # Group files by extension if requested
            if self.options.group_by_extension:
                extension_groups = self._group_files_by_extension(file_paths)
                
                # Cluster each extension group separately
                all_clusters = []
                all_noise = []
                cluster_id_counter = 0
                
                for extension, group_files in extension_groups.items():
                    if len(group_files) <= 1:
                        # Add single files to noise
                        all_noise.extend(group_files)
                        continue
                    
                    # Cluster files in this extension group
                    result = self._cluster_files_by_criterion(group_files)
                    
                    # Update cluster IDs to ensure uniqueness
                    for cluster in result.clusters:
                        cluster.id += cluster_id_counter
                        cluster.metadata["extension"] = extension
                        all_clusters.append(cluster)
                    
                    all_noise.extend(result.noise)
                    cluster_id_counter += len(result.clusters)
                
                # Create combined result
                result = ClusteringResult(
                    clusters=all_clusters,
                    noise=all_noise,
                    total_files=len(file_paths),
                    total_clusters=len(all_clusters),
                    algorithm=self.options.algorithm.value,
                    criterion=self.options.criterion.value,
                    execution_time=time.time() - start_time
                )
                
                # Add visualization data if requested
                if self.options.apply_dimensionality_reduction:
                    result.visualization_data = self._create_visualization_data(file_paths, result)
                
                return result
            
            else:
                # Cluster all files together
                result = self._cluster_files_by_criterion(file_paths)
                result.execution_time = time.time() - start_time
                
                # Add visualization data if requested
                if self.options.apply_dimensionality_reduction:
                    result.visualization_data = self._create_visualization_data(file_paths, result)
                
                return result
        
        except Exception as e:
            logger.error(f"Error clustering files: {str(e)}")
            return ClusteringResult(
                clusters=[],
                noise=file_paths,
                total_files=len(file_paths),
                total_clusters=0,
                algorithm=self.options.algorithm.value,
                criterion=self.options.criterion.value,
                execution_time=time.time() - start_time,
                error_message=f"Error clustering files: {str(e)}"
            )
    
    def _cluster_files_by_criterion(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on the specified criterion.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        if self.options.criterion == ClusteringCriterion.CONTENT:
            return self._cluster_by_content(file_paths)
        elif self.options.criterion == ClusteringCriterion.METADATA:
            return self._cluster_by_metadata(file_paths)
        elif self.options.criterion == ClusteringCriterion.FILE_TYPE:
            return self._cluster_by_file_type(file_paths)
        elif self.options.criterion == ClusteringCriterion.COMBINED:
            return self._cluster_by_combined(file_paths)
        elif self.options.criterion == ClusteringCriterion.CUSTOM:
            return self._cluster_by_custom(file_paths)
        else:
            raise ValueError(f"Unknown clustering criterion: {self.options.criterion}")
    
    def _cluster_by_content(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on content similarity.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        # Use content analyzer to extract features and cluster
        self.content_analyzer = ContentAnalyzer(self.options.content_analysis_options)
        content_result = self.content_analyzer.extract_features(file_paths)
        
        # Check if clustering was successful
        if content_result.clusters is None:
            logger.warning("Content clustering failed, falling back to document clustering")
            # Fall back to document clustering
            doc_clusters = cluster_documents_by_content(
                file_paths, self.options.content_analysis_options
            )
            
            # Convert to ClusteringResult
            clusters = []
            noise = []
            
            for cluster_id, cluster_files in doc_clusters.items():
                if cluster_id == -1:
                    # Noise points
                    noise.extend(cluster_files)
                else:
                    # Create cluster
                    clusters.append(FileCluster(
                        id=cluster_id,
                        files=cluster_files,
                        metadata={
                            "criterion": "content",
                            "algorithm": "dbscan"
                        }
                    ))
            
            return ClusteringResult(
                clusters=clusters,
                noise=noise,
                total_files=len(file_paths),
                total_clusters=len(clusters),
                algorithm=self.options.algorithm.value,
                criterion=self.options.criterion.value
            )
        
        # Convert ContentAnalysisResult to ClusteringResult
        clusters = []
        noise = []
        
        # Group files by cluster
        for i, cluster_id in enumerate(content_result.clusters):
            if cluster_id == -1:
                # Noise points
                noise.append(content_result.files[i])
            else:
                # Find or create cluster
                cluster = next((c for c in clusters if c.id == cluster_id), None)
                if cluster is None:
                    cluster = FileCluster(
                        id=cluster_id,
                        files=[],
                        metadata={
                            "criterion": "content",
                            "algorithm": "dbscan"
                        }
                    )
                    clusters.append(cluster)
                
                # Add file to cluster
                cluster.files.append(content_result.files[i])
        
        # Find centroids for each cluster
        if content_result.similarity_matrix is not None:
            for cluster in clusters:
                # Get indices of files in this cluster
                indices = [content_result.files.index(f) for f in cluster.files]
                
                # Calculate average similarity to all other files in cluster
                avg_similarities = {}
                for i, idx in enumerate(indices):
                    avg_sim = 0.0
                    for j, other_idx in enumerate(indices):
                        if idx != other_idx:
                            avg_sim += content_result.similarity_matrix[idx, other_idx]
                    
                    if len(indices) > 1:
                        avg_sim /= (len(indices) - 1)
                    
                    avg_similarities[cluster.files[i]] = avg_sim
                
                # Find centroid (file with highest average similarity)
                if avg_similarities:
                    cluster.centroid = max(avg_similarities.items(), key=lambda x: x[1])[0]
                    cluster.similarity_scores = avg_similarities
        
        return ClusteringResult(
            clusters=clusters,
            noise=noise,
            total_files=len(file_paths),
            total_clusters=len(clusters),
            algorithm=self.options.algorithm.value,
            criterion=self.options.criterion.value
        )
    
    def _cluster_by_metadata(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on metadata similarity.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        try:
            # Import scikit-learn for clustering
            from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering, SpectralClustering
            from sklearn.preprocessing import normalize
            
            # Calculate metadata similarity matrix
            similarity_matrix = np.zeros((len(file_paths), len(file_paths)))
            
            for i in range(len(file_paths)):
                for j in range(i, len(file_paths)):
                    if i == j:
                        similarity_matrix[i, j] = 1.0  # Self-similarity is 1.0
                    else:
                        # Calculate metadata similarity
                        similarity = calculate_metadata_similarity(
                            file_paths[i], file_paths[j],
                            options=self.options.similarity_options
                        )
                        similarity_matrix[i, j] = similarity
                        similarity_matrix[j, i] = similarity  # Symmetric matrix
            
            # Convert similarity matrix to distance matrix (1 - similarity)
            distance_matrix = 1.0 - similarity_matrix
            
            # Apply clustering algorithm
            if self.options.algorithm == ClusteringAlgorithm.DBSCAN:
                self.clusterer = DBSCAN(
                    eps=self.options.eps,
                    min_samples=self.options.min_samples,
                    metric='precomputed'
                )
                cluster_labels = self.clusterer.fit_predict(distance_matrix)
            
            elif self.options.algorithm == ClusteringAlgorithm.KMEANS:
                # K-means requires feature vectors, not distance matrix
                # Use multidimensional scaling to convert distance matrix to feature vectors
                from sklearn.manifold import MDS
                mds = MDS(n_components=min(10, len(file_paths) - 1), dissimilarity='precomputed', random_state=42)
                features = mds.fit_transform(distance_matrix)
                
                self.clusterer = KMeans(
                    n_clusters=min(self.options.n_clusters, len(file_paths)),
                    random_state=42
                )
                cluster_labels = self.clusterer.fit_predict(features)
            
            elif self.options.algorithm == ClusteringAlgorithm.HIERARCHICAL:
                self.clusterer = AgglomerativeClustering(
                    n_clusters=None if self.options.distance_threshold else min(self.options.n_clusters, len(file_paths)),
                    distance_threshold=self.options.distance_threshold,
                    linkage=self.options.linkage,
                    affinity='precomputed'
                )
                cluster_labels = self.clusterer.fit_predict(distance_matrix)
            
            elif self.options.algorithm == ClusteringAlgorithm.SPECTRAL:
                # Spectral clustering works with similarity matrix, not distance matrix
                self.clusterer = SpectralClustering(
                    n_clusters=min(self.options.n_clusters, len(file_paths)),
                    affinity='precomputed',
                    random_state=42
                )
                cluster_labels = self.clusterer.fit_predict(similarity_matrix)
            
            else:
                raise ValueError(f"Unknown clustering algorithm: {self.options.algorithm}")
            
            # Convert cluster labels to ClusteringResult
            clusters = []
            noise = []
            
            # Group files by cluster
            for i, cluster_id in enumerate(cluster_labels):
                if cluster_id == -1:
                    # Noise points
                    noise.append(file_paths[i])
                else:
                    # Find or create cluster
                    cluster = next((c for c in clusters if c.id == cluster_id), None)
                    if cluster is None:
                        cluster = FileCluster(
                            id=cluster_id,
                            files=[],
                            metadata={
                                "criterion": "metadata",
                                "algorithm": self.options.algorithm.value
                            }
                        )
                        clusters.append(cluster)
                    
                    # Add file to cluster
                    cluster.files.append(file_paths[i])
            
            # Find centroids for each cluster
            for cluster in clusters:
                # Get indices of files in this cluster
                indices = [file_paths.index(f) for f in cluster.files]
                
                # Calculate average similarity to all other files in cluster
                avg_similarities = {}
                for i, idx in enumerate(indices):
                    avg_sim = 0.0
                    for j, other_idx in enumerate(indices):
                        if idx != other_idx:
                            avg_sim += similarity_matrix[idx, other_idx]
                    
                    if len(indices) > 1:
                        avg_sim /= (len(indices) - 1)
                    
                    avg_similarities[cluster.files[i]] = avg_sim
                
                # Find centroid (file with highest average similarity)
                if avg_similarities:
                    cluster.centroid = max(avg_similarities.items(), key=lambda x: x[1])[0]
                    cluster.similarity_scores = avg_similarities
            
            return ClusteringResult(
                clusters=clusters,
                noise=noise,
                total_files=len(file_paths),
                total_clusters=len(clusters),
                algorithm=self.options.algorithm.value,
                criterion=self.options.criterion.value
            )
        
        except ImportError as e:
            logger.error(f"Error importing scikit-learn: {str(e)}")
            return ClusteringResult(
                clusters=[],
                noise=file_paths,
                total_files=len(file_paths),
                total_clusters=0,
                algorithm=self.options.algorithm.value,
                criterion=self.options.criterion.value,
                error_message=f"Error importing scikit-learn: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Error clustering by metadata: {str(e)}")
            return ClusteringResult(
                clusters=[],
                noise=file_paths,
                total_files=len(file_paths),
                total_clusters=0,
                algorithm=self.options.algorithm.value,
                criterion=self.options.criterion.value,
                error_message=f"Error clustering by metadata: {str(e)}"
            )
    
    def _cluster_by_file_type(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on file type.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        # Group files by extension
        extension_groups = self._group_files_by_extension(file_paths)
        
        # Convert to ClusteringResult
        clusters = []
        cluster_id = 0
        
        for extension, group_files in extension_groups.items():
            if len(group_files) > 0:
                # Create cluster for this extension
                clusters.append(FileCluster(
                    id=cluster_id,
                    files=group_files,
                    metadata={
                        "criterion": "file_type",
                        "extension": extension
                    }
                ))
                cluster_id += 1
        
        return ClusteringResult(
            clusters=clusters,
            noise=[],  # No noise in file type clustering
            total_files=len(file_paths),
            total_clusters=len(clusters),
            algorithm="file_type",
            criterion="file_type"
        )
    
    def _cluster_by_combined(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on a combination of content and metadata similarity.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        # First, group files by extension
        extension_groups = self._group_files_by_extension(file_paths)
        
        # Then, for each extension group, cluster by content and metadata
        all_clusters = []
        all_noise = []
        cluster_id_counter = 0
        
        for extension, group_files in extension_groups.items():
            if len(group_files) <= 1:
                # Add single files to noise
                all_noise.extend(group_files)
                continue
            
            # Use duplicate detection with combined strategy
            duplicate_result = detect_similar_files(
                group_files,
                threshold=self.options.similarity_options.threshold if self.options.similarity_options else 0.7,
                strategy=DuplicateDetectionStrategy.COMBINED
            )
            
            # Convert duplicate groups to clusters
            for group in duplicate_result.duplicate_groups:
                cluster = FileCluster(
                    id=cluster_id_counter,
                    files=group.files,
                    centroid=group.reference_file,
                    metadata={
                        "criterion": "combined",
                        "extension": extension,
                        "similarity_score": group.similarity_score,
                        "detection_method": group.detection_method
                    }
                )
                
                # Add similarity scores
                if group.reference_file:
                    for file_path in group.files:
                        if file_path != group.reference_file:
                            cluster.similarity_scores[file_path] = group.similarity_score
                
                all_clusters.append(cluster)
                cluster_id_counter += 1
            
            # Add files not in any group to noise
            group_files_set = set(group_files)
            duplicate_files_set = set()
            for group in duplicate_result.duplicate_groups:
                duplicate_files_set.update(group.files)
            
            noise_files = group_files_set - duplicate_files_set
            all_noise.extend(noise_files)
        
        return ClusteringResult(
            clusters=all_clusters,
            noise=all_noise,
            total_files=len(file_paths),
            total_clusters=len(all_clusters),
            algorithm="combined",
            criterion="combined"
        )
    
    def _cluster_by_custom(self, file_paths: List[str]) -> ClusteringResult:
        """
        Cluster files based on custom criteria.
        This is a placeholder for custom clustering implementations.
        
        Args:
            file_paths: List of file paths to cluster
            
        Returns:
            ClusteringResult object containing the clustering results
        """
        logger.warning("Custom clustering not implemented, falling back to combined clustering")
        return self._cluster_by_combined(file_paths)
    
    def _group_files_by_extension(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Group files by their extension.
        
        Args:
            file_paths: List of file paths to group
            
        Returns:
            Dictionary mapping extensions to lists of file paths
        """
        extension_groups: Dict[str, List[str]] = {}
        
        for file_path in file_paths:
            # Get file extension (lowercase)
            extension = os.path.splitext(file_path)[1].lower()
            
            if extension in extension_groups:
                extension_groups[extension].append(file_path)
            else:
                extension_groups[extension] = [file_path]
        
        return extension_groups
    
    def _create_visualization_data(self, file_paths: List[str], result: ClusteringResult) -> Dict[str, Any]:
        """
        Create visualization data for the clustering result.
        
        Args:
            file_paths: List of file paths
            result: ClusteringResult object
            
        Returns:
            Dictionary with visualization data
        """
        try:
            # Import visualization libraries
            from sklearn.manifold import TSNE
            from sklearn.decomposition import PCA
            import matplotlib.pyplot as plt
            
            # Create a mapping from file paths to cluster IDs
            file_to_cluster = {}
            for cluster in result.clusters:
                for file_path in cluster.files:
                    file_to_cluster[file_path] = cluster.id
            
            # Create feature matrix based on criterion
            if self.options.criterion == ClusteringCriterion.CONTENT and hasattr(self, 'content_analyzer') and self.content_analyzer:
                # Use content features if available
                content_result = self.content_analyzer.extract_features(file_paths)
                if content_result.reduced_features is not None:
                    features = content_result.reduced_features
                elif content_result.features:
                    features = np.vstack([f.features for f in content_result.features])
                else:
                    # Fall back to PCA on similarity matrix
                    similarity_matrix = np.zeros((len(file_paths), len(file_paths)))
                    for i in range(len(file_paths)):
                        for j in range(i, len(file_paths)):
                            if i == j:
                                similarity_matrix[i, j] = 1.0
                            else:
                                similarity = calculate_content_similarity(
                                    file_paths[i], file_paths[j],
                                    options=self.options.similarity_options
                                )
                                similarity_matrix[i, j] = similarity
                                similarity_matrix[j, i] = similarity
                    
                    # Apply PCA to similarity matrix
                    pca = PCA(n_components=min(10, len(file_paths) - 1))
                    features = pca.fit_transform(similarity_matrix)
            
            else:
                # Create similarity matrix
                similarity_matrix = np.zeros((len(file_paths), len(file_paths)))
                for i in range(len(file_paths)):
                    for j in range(i, len(file_paths)):
                        if i == j:
                            similarity_matrix[i, j] = 1.0
                        else:
                            # Use appropriate similarity calculation based on criterion
                            if self.options.criterion == ClusteringCriterion.METADATA:
                                similarity = calculate_metadata_similarity(
                                    file_paths[i], file_paths[j],
                                    options=self.options.similarity_options
                                )
                            elif self.options.criterion == ClusteringCriterion.COMBINED:
                                content_sim = calculate_content_similarity(
                                    file_paths[i], file_paths[j],
                                    options=self.options.similarity_options
                                )
                                metadata_sim = calculate_metadata_similarity(
                                    file_paths[i], file_paths[j],
                                    options=self.options.similarity_options
                                )
                                similarity = (0.7 * content_sim) + (0.3 * metadata_sim)
                            else:
                                # Default to content similarity
                                similarity = calculate_content_similarity(
                                    file_paths[i], file_paths[j],
                                    options=self.options.similarity_options
                                )
                            
                            similarity_matrix[i, j] = similarity
                            similarity_matrix[j, i] = similarity
                
                # Apply PCA to similarity matrix
                pca = PCA(n_components=min(10, len(file_paths) - 1))
                features = pca.fit_transform(similarity_matrix)
            
            # Apply t-SNE for visualization
            tsne = TSNE(n_components=2, random_state=42)
            vis_data = tsne.fit_transform(features)
            
            # Create visualization data
            visualization_data = {
                "method": "t-SNE",
                "coordinates": vis_data.tolist(),
                "files": file_paths,
                "clusters": [file_to_cluster.get(f, -1) for f in file_paths]
            }
            
            return visualization_data
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {str(e)}")
            return {}
        
        except Exception as e:
            logger.error(f"Error creating visualization data: {str(e)}")
            return {}


def cluster_files(file_paths: List[str], options: Optional[ClusteringOptions] = None) -> ClusteringResult:
    """
    Cluster files based on the specified options.
    
    Args:
        file_paths: List of file paths to cluster
        options: Clustering options
        
    Returns:
        ClusteringResult object containing the clustering results
    """
    clustering = FileClustering(options)
    return clustering.cluster_files(file_paths)


def visualize_file_clusters(result: ClusteringResult, output_file: str) -> Dict[str, Any]:
    """
    Visualize file clusters.
    
    Args:
        result: ClusteringResult object
        output_file: Path to save the visualization
        
    Returns:
        Dictionary with visualization data
    """
    try:
        # Import visualization libraries
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Check if visualization data is available
        if not result.visualization_data or "coordinates" not in result.visualization_data:
            logger.warning("Visualization data not available")
            return {}
        
        # Extract visualization data
        coordinates = np.array(result.visualization_data["coordinates"])
        files = result.visualization_data["files"]
        clusters = result.visualization_data["clusters"]
        
        # Create visualization
        plt.figure(figsize=(12, 10))
        
        # Plot points colored by cluster
        unique_clusters = set(clusters)
        for cluster_id in unique_clusters:
            if cluster_id == -1:
                # Plot noise points as gray x's
                mask = np.array(clusters) == cluster_id
                plt.scatter(
                    coordinates[mask, 0], coordinates[mask, 1],
                    marker='x', color='gray', label='Noise'
                )
            else:
                # Plot cluster points with a unique color
                mask = np.array(clusters) == cluster_id
                plt.scatter(
                    coordinates[mask, 0], coordinates[mask, 1],
                    label=f'Cluster {cluster_id}'
                )
        
        # Add file names as annotations
        for i, file_path in enumerate(files):
            plt.annotate(
                os.path.basename(file_path),
                (coordinates[i, 0], coordinates[i, 1]),
                fontsize=8
            )
        
        plt.title(f'File Clustering Visualization ({result.criterion} - {result.algorithm})')
        plt.xlabel('t-SNE dimension 1')
        plt.ylabel('t-SNE dimension 2')
        
        if len(unique_clusters) > 1:
            plt.legend()
        
        # Save to file
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Visualization saved to {output_file}")
        
        # Close the plot to free memory
        plt.close()
        
        return result.visualization_data
    
    except ImportError as e:
        logger.error(f"Error importing visualization libraries: {str(e)}")
        return {}
    
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        return {}


def generate_cluster_report(result: ClusteringResult, format: str = 'text') -> str:
    """
    Generate a report of file clusters.
    
    Args:
        result: ClusteringResult object
        format: Report format ('text', 'json', or 'html')
        
    Returns:
        Report string in the specified format
    """
    if format == 'text':
        return _generate_text_cluster_report(result)
    elif format == 'json':
        return _generate_json_cluster_report(result)
    elif format == 'html':
        return _generate_html_cluster_report(result)
    else:
        raise ValueError(f"Unknown report format: {format}")


def _generate_text_cluster_report(result: ClusteringResult) -> str:
    """Generate a text report of file clusters."""
    import textwrap
    
    lines = []
    lines.append("File Clustering Report")
    lines.append("=====================")
    lines.append(f"Total files analyzed: {result.total_files}")
    lines.append(f"Total clusters found: {result.total_clusters}")
    lines.append(f"Clustering algorithm: {result.algorithm}")
    lines.append(f"Clustering criterion: {result.criterion}")
    lines.append(f"Execution time: {result.execution_time:.2f} seconds")
    lines.append("")
    
    if result.error_message:
        lines.append(f"ERROR: {result.error_message}")
        lines.append("")
    
    if not result.clusters:
        lines.append("No clusters found.")
        return "\n".join(lines)
    
    # Report clusters
    for i, cluster in enumerate(result.clusters, 1):
        lines.append(f"Cluster {cluster.id}: {len(cluster.files)} files")
        lines.append("-" * len(f"Cluster {cluster.id}: {len(cluster.files)} files"))
        
        if cluster.centroid:
            lines.append(f"  Centroid: {os.path.basename(cluster.centroid)}")
        
        for file_path in cluster.files:
            if file_path != cluster.centroid:
                similarity = cluster.similarity_scores.get(file_path, "N/A")
                if isinstance(similarity, float):
                    similarity = f"{similarity:.2f}"
                lines.append(f"  - {os.path.basename(file_path)} (similarity: {similarity})")
        
        lines.append("")
    
    # Report noise points
    if result.noise:
        lines.append(f"Noise: {len(result.noise)} files")
        lines.append("-" * len(f"Noise: {len(result.noise)} files"))
        for file_path in result.noise:
            lines.append(f"  - {os.path.basename(file_path)}")
        lines.append("")
    
    return "\n".join(lines)


def _generate_json_cluster_report(result: ClusteringResult) -> str:
    """Generate a JSON report of file clusters."""
    import json
    
    # Convert result to dictionary
    result_dict = {
        "total_files": result.total_files,
        "total_clusters": result.total_clusters,
        "algorithm": result.algorithm,
        "criterion": result.criterion,
        "execution_time": result.execution_time,
        "error_message": result.error_message,
        "clusters": [],
        "noise": [os.path.basename(f) for f in result.noise]
    }
    
    # Add clusters
    for cluster in result.clusters:
        cluster_dict = {
            "id": cluster.id,
            "files": [os.path.basename(f) for f in cluster.files],
            "centroid": os.path.basename(cluster.centroid) if cluster.centroid else None,
            "similarity_scores": {os.path.basename(f): s for f, s in cluster.similarity_scores.items()},
            "metadata": cluster.metadata
        }
        result_dict["clusters"].append(cluster_dict)
    
    return json.dumps(result_dict, indent=2)


def _generate_html_cluster_report(result: ClusteringResult) -> str:
    """Generate an HTML report of file clusters."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("  <title>File Clustering Report</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
    html.append("    h1 { color: #333; }")
    html.append("    h2 { color: #666; margin-top: 20px; }")
    html.append("    .summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
    html.append("    .cluster { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }")
    html.append("    .centroid { font-weight: bold; color: #007bff; }")
    html.append("    .file { margin-left: 20px; }")
    html.append("    .noise { color: #999; }")
    html.append("    .error { color: red; font-weight: bold; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("  <h1>File Clustering Report</h1>")
    html.append("  <div class='summary'>")
    html.append(f"    <p>Total files analyzed: {result.total_files}</p>")
    html.append(f"    <p>Total clusters found: {result.total_clusters}</p>")
    html.append(f"    <p>Clustering algorithm: {result.algorithm}</p>")
    html.append(f"    <p>Clustering criterion: {result.criterion}</p>")
    html.append(f"    <p>Execution time: {result.execution_time:.2f} seconds</p>")
    html.append("  </div>")
    
    if result.error_message:
        html.append(f"  <p class='error'>ERROR: {result.error_message}</p>")
    
    if not result.clusters:
        html.append("  <p>No clusters found.</p>")
    else:
        # Report clusters
        for cluster in result.clusters:
            html.append(f"  <div class='cluster'>")
            html.append(f"    <h2>Cluster {cluster.id}: {len(cluster.files)} files</h2>")
            
            if cluster.centroid:
                html.append(f"    <p class='centroid'>Centroid: {os.path.basename(cluster.centroid)}</p>")
            
            html.append("    <ul>")
            for file_path in cluster.files:
                if file_path != cluster.centroid:
                    similarity = cluster.similarity_scores.get(file_path, "N/A")
                    if isinstance(similarity, float):
                        similarity = f"{similarity:.2f}"
                    html.append(f"      <li class='file'>{os.path.basename(file_path)} (similarity: {similarity})</li>")
            html.append("    </ul>")
            html.append("  </div>")
    
    # Report noise points
    if result.noise:
        html.append("  <div class='noise'>")
        html.append(f"    <h2>Noise: {len(result.noise)} files</h2>")
        html.append("    <ul>")
        for file_path in result.noise:
            html.append(f"      <li>{os.path.basename(file_path)}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)
"""
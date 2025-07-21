"""
Content analysis module for analyzing and comparing file content.

This module provides functionality for analyzing the content of files,
extracting features, and comparing files based on their content. It builds
on the similarity_analysis module but provides more advanced content-specific
analysis capabilities.

The module includes:
- Content feature extraction (TF-IDF, word embeddings, etc.)
- Content-based similarity analysis
- Content clustering and classification
- Content visualization utilities
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from science_data_kit.core.file_handling.similarity_analysis import (
    SimilarityMetricType,
    SimilarityOptions,
    SimilarityResult,
    calculate_content_similarity,
    compare_files
)
from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions,
    TextExtractionResult,
    extract_text_from_file
)

logger = logging.getLogger(__name__)


class ContentFeatureType(Enum):
    """Enumeration of content feature types."""
    TFIDF = "tfidf"
    WORD_EMBEDDINGS = "word_embeddings"
    DOC_EMBEDDINGS = "doc_embeddings"
    CUSTOM = "custom"


@dataclass
class ContentAnalysisOptions:
    """Options for content analysis."""
    # Feature extraction options
    feature_type: ContentFeatureType = ContentFeatureType.TFIDF
    max_features: int = 1000
    ngram_range: Tuple[int, int] = (1, 2)  # Unigrams and bigrams
    min_df: int = 2  # Minimum document frequency
    max_df: float = 0.9  # Maximum document frequency
    
    # Text preprocessing options
    lowercase: bool = True
    remove_stopwords: bool = True
    stemming: bool = False
    lemmatization: bool = False
    
    # Dimensionality reduction options
    apply_dimensionality_reduction: bool = False
    n_components: int = 100
    
    # Clustering options
    apply_clustering: bool = False
    eps: float = 0.5  # DBSCAN epsilon
    min_samples: int = 5  # DBSCAN min_samples
    
    # Similarity options
    similarity_metric: SimilarityMetricType = SimilarityMetricType.COSINE
    similarity_threshold: float = 0.7
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class ContentFeatures:
    """Content features extracted from a file."""
    file_path: str
    feature_type: ContentFeatureType
    features: Union[np.ndarray, List[float], Dict[str, float]]
    vocabulary: Optional[Dict[str, int]] = None
    feature_names: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert features to numpy array if needed."""
        if isinstance(self.features, list):
            self.features = np.array(self.features)
        elif isinstance(self.features, dict):
            # Convert dict to array if needed
            if self.vocabulary:
                array_features = np.zeros(len(self.vocabulary))
                for term, value in self.features.items():
                    if term in self.vocabulary:
                        array_features[self.vocabulary[term]] = value
                self.features = array_features


@dataclass
class ContentAnalysisResult:
    """Result of content analysis on a collection of files."""
    files: List[str]
    features: List[ContentFeatures]
    feature_type: ContentFeatureType
    similarity_matrix: Optional[np.ndarray] = None
    clusters: Optional[List[int]] = None
    reduced_features: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentAnalyzer:
    """Class for analyzing and comparing file content."""
    
    def __init__(self, options: Optional[ContentAnalysisOptions] = None):
        """
        Initialize the content analyzer.
        
        Args:
            options: Content analysis options
        """
        self.options = options or ContentAnalysisOptions()
        self.vectorizer = None
        self.svd = None
        self.clusterer = None
    
    def extract_features(self, file_paths: List[str]) -> ContentAnalysisResult:
        """
        Extract features from a list of files.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            ContentAnalysisResult object containing the extracted features
        """
        # Extract text from files
        text_extraction_options = self.options.text_extraction_options or TextExtractionOptions()
        texts = []
        valid_files = []
        
        for file_path in file_paths:
            try:
                text_result = extract_text_from_file(file_path, text_extraction_options)
                if text_result and text_result.text:
                    texts.append(text_result.text)
                    valid_files.append(file_path)
                else:
                    logger.warning(f"Could not extract text from file: {file_path}")
            except Exception as e:
                logger.error(f"Error extracting text from file {file_path}: {e}")
        
        if not texts:
            logger.warning("No valid texts extracted from files")
            return ContentAnalysisResult(
                files=[],
                features=[],
                feature_type=self.options.feature_type
            )
        
        # Extract features based on feature type
        if self.options.feature_type == ContentFeatureType.TFIDF:
            return self._extract_tfidf_features(texts, valid_files)
        elif self.options.feature_type == ContentFeatureType.WORD_EMBEDDINGS:
            return self._extract_word_embedding_features(texts, valid_files)
        elif self.options.feature_type == ContentFeatureType.DOC_EMBEDDINGS:
            return self._extract_doc_embedding_features(texts, valid_files)
        else:
            logger.warning(f"Unsupported feature type: {self.options.feature_type}")
            return ContentAnalysisResult(
                files=valid_files,
                features=[],
                feature_type=self.options.feature_type
            )
    
    def _extract_tfidf_features(self, texts: List[str], file_paths: List[str]) -> ContentAnalysisResult:
        """
        Extract TF-IDF features from texts.
        
        Args:
            texts: List of text strings
            file_paths: List of file paths corresponding to the texts
            
        Returns:
            ContentAnalysisResult object containing the TF-IDF features
        """
        try:
            # Create and fit the TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=self.options.max_features,
                ngram_range=self.options.ngram_range,
                min_df=self.options.min_df,
                max_df=self.options.max_df,
                lowercase=self.options.lowercase,
                stop_words='english' if self.options.remove_stopwords else None
            )
            
            # Transform texts to TF-IDF features
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Get feature names and vocabulary
            feature_names = self.vectorizer.get_feature_names_out()
            vocabulary = self.vectorizer.vocabulary_
            
            # Create ContentFeatures objects
            features = []
            for i, file_path in enumerate(file_paths):
                features.append(ContentFeatures(
                    file_path=file_path,
                    feature_type=ContentFeatureType.TFIDF,
                    features=tfidf_matrix[i].toarray()[0],
                    vocabulary=vocabulary,
                    feature_names=feature_names,
                    metadata={
                        "num_features": len(feature_names),
                        "sparsity": 1.0 - (np.count_nonzero(tfidf_matrix[i]) / len(feature_names))
                    }
                ))
            
            # Create result object
            result = ContentAnalysisResult(
                files=file_paths,
                features=features,
                feature_type=ContentFeatureType.TFIDF,
                metadata={
                    "num_documents": len(file_paths),
                    "num_features": len(feature_names),
                    "vocabulary_size": len(vocabulary)
                }
            )
            
            # Apply dimensionality reduction if requested
            if self.options.apply_dimensionality_reduction:
                result = self._apply_dimensionality_reduction(result)
            
            # Apply clustering if requested
            if self.options.apply_clustering:
                result = self._apply_clustering(result)
            
            # Calculate similarity matrix
            result.similarity_matrix = self._calculate_similarity_matrix(
                np.vstack([f.features for f in features])
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error extracting TF-IDF features: {e}")
            return ContentAnalysisResult(
                files=file_paths,
                features=[],
                feature_type=ContentFeatureType.TFIDF
            )
    
    def _extract_word_embedding_features(self, texts: List[str], file_paths: List[str]) -> ContentAnalysisResult:
        """
        Extract word embedding features from texts.
        
        Args:
            texts: List of text strings
            file_paths: List of file paths corresponding to the texts
            
        Returns:
            ContentAnalysisResult object containing the word embedding features
        """
        try:
            # Try to import spaCy
            import spacy
            
            # Load spaCy model
            try:
                nlp = spacy.load("en_core_web_md")
            except OSError:
                logger.warning("en_core_web_md not found. Using en_core_web_sm instead.")
                try:
                    nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.error("No spaCy model found. Please install one with: python -m spacy download en_core_web_md")
                    raise ImportError("No spaCy model found")
            
            # Process texts and extract embeddings
            features = []
            for i, (text, file_path) in enumerate(zip(texts, file_paths)):
                # Process text with spaCy
                doc = nlp(text)
                
                # Get document embedding (average of word embeddings)
                if doc.vector.size > 0:
                    embedding = doc.vector
                else:
                    # Fallback for empty documents or models without vectors
                    embedding = np.zeros(nlp.meta["vectors"]["width"])
                
                features.append(ContentFeatures(
                    file_path=file_path,
                    feature_type=ContentFeatureType.WORD_EMBEDDINGS,
                    features=embedding,
                    metadata={
                        "embedding_size": embedding.size,
                        "model": nlp.meta["name"]
                    }
                ))
            
            # Create result object
            result = ContentAnalysisResult(
                files=file_paths,
                features=features,
                feature_type=ContentFeatureType.WORD_EMBEDDINGS,
                metadata={
                    "num_documents": len(file_paths),
                    "embedding_size": features[0].features.size if features else 0,
                    "model": nlp.meta["name"] if features else ""
                }
            )
            
            # Apply dimensionality reduction if requested
            if self.options.apply_dimensionality_reduction:
                result = self._apply_dimensionality_reduction(result)
            
            # Apply clustering if requested
            if self.options.apply_clustering:
                result = self._apply_clustering(result)
            
            # Calculate similarity matrix
            result.similarity_matrix = self._calculate_similarity_matrix(
                np.vstack([f.features for f in features])
            )
            
            return result
        
        except ImportError as e:
            logger.error(f"Error importing spaCy: {e}")
            logger.warning("Falling back to TF-IDF features")
            return self._extract_tfidf_features(texts, file_paths)
        
        except Exception as e:
            logger.error(f"Error extracting word embedding features: {e}")
            return ContentAnalysisResult(
                files=file_paths,
                features=[],
                feature_type=ContentFeatureType.WORD_EMBEDDINGS
            )
    
    def _extract_doc_embedding_features(self, texts: List[str], file_paths: List[str]) -> ContentAnalysisResult:
        """
        Extract document embedding features from texts using sentence transformers.
        
        Args:
            texts: List of text strings
            file_paths: List of file paths corresponding to the texts
            
        Returns:
            ContentAnalysisResult object containing the document embedding features
        """
        try:
            # Try to import sentence-transformers
            from sentence_transformers import SentenceTransformer
            
            # Load model
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Encode texts
            embeddings = model.encode(texts)
            
            # Create ContentFeatures objects
            features = []
            for i, (embedding, file_path) in enumerate(zip(embeddings, file_paths)):
                features.append(ContentFeatures(
                    file_path=file_path,
                    feature_type=ContentFeatureType.DOC_EMBEDDINGS,
                    features=embedding,
                    metadata={
                        "embedding_size": embedding.size,
                        "model": model.get_sentence_embedding_dimension()
                    }
                ))
            
            # Create result object
            result = ContentAnalysisResult(
                files=file_paths,
                features=features,
                feature_type=ContentFeatureType.DOC_EMBEDDINGS,
                metadata={
                    "num_documents": len(file_paths),
                    "embedding_size": embeddings[0].size if len(embeddings) > 0 else 0,
                    "model": "all-MiniLM-L6-v2"
                }
            )
            
            # Apply dimensionality reduction if requested
            if self.options.apply_dimensionality_reduction:
                result = self._apply_dimensionality_reduction(result)
            
            # Apply clustering if requested
            if self.options.apply_clustering:
                result = self._apply_clustering(result)
            
            # Calculate similarity matrix
            result.similarity_matrix = self._calculate_similarity_matrix(embeddings)
            
            return result
        
        except ImportError as e:
            logger.error(f"Error importing sentence-transformers: {e}")
            logger.warning("Falling back to word embedding features")
            return self._extract_word_embedding_features(texts, file_paths)
        
        except Exception as e:
            logger.error(f"Error extracting document embedding features: {e}")
            return ContentAnalysisResult(
                files=file_paths,
                features=[],
                feature_type=ContentFeatureType.DOC_EMBEDDINGS
            )
    
    def _apply_dimensionality_reduction(self, result: ContentAnalysisResult) -> ContentAnalysisResult:
        """
        Apply dimensionality reduction to the features.
        
        Args:
            result: ContentAnalysisResult object containing the features
            
        Returns:
            ContentAnalysisResult object with reduced features
        """
        try:
            if not result.features:
                return result
            
            # Stack features into a matrix
            feature_matrix = np.vstack([f.features for f in result.features])
            
            # Apply SVD for dimensionality reduction
            n_components = min(self.options.n_components, feature_matrix.shape[0], feature_matrix.shape[1])
            self.svd = TruncatedSVD(n_components=n_components)
            reduced_features = self.svd.fit_transform(feature_matrix)
            
            # Update result with reduced features
            result.reduced_features = reduced_features
            result.metadata["dimensionality_reduction"] = {
                "method": "TruncatedSVD",
                "n_components": n_components,
                "explained_variance_ratio": self.svd.explained_variance_ratio_.sum()
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error applying dimensionality reduction: {e}")
            return result
    
    def _apply_clustering(self, result: ContentAnalysisResult) -> ContentAnalysisResult:
        """
        Apply clustering to the features.
        
        Args:
            result: ContentAnalysisResult object containing the features
            
        Returns:
            ContentAnalysisResult object with cluster assignments
        """
        try:
            if not result.features:
                return result
            
            # Use reduced features if available, otherwise use original features
            if result.reduced_features is not None:
                feature_matrix = result.reduced_features
            else:
                feature_matrix = np.vstack([f.features for f in result.features])
            
            # Normalize features
            feature_matrix = normalize(feature_matrix)
            
            # Apply DBSCAN clustering
            self.clusterer = DBSCAN(
                eps=self.options.eps,
                min_samples=self.options.min_samples,
                metric='cosine'
            )
            clusters = self.clusterer.fit_predict(feature_matrix)
            
            # Update result with cluster assignments
            result.clusters = clusters.tolist()
            
            # Count number of clusters (excluding noise points labeled as -1)
            num_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
            
            result.metadata["clustering"] = {
                "method": "DBSCAN",
                "num_clusters": num_clusters,
                "noise_points": np.sum(clusters == -1),
                "eps": self.options.eps,
                "min_samples": self.options.min_samples
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error applying clustering: {e}")
            return result
    
    def _calculate_similarity_matrix(self, feature_matrix: np.ndarray) -> np.ndarray:
        """
        Calculate similarity matrix from feature matrix.
        
        Args:
            feature_matrix: Matrix of features (n_samples, n_features)
            
        Returns:
            Similarity matrix (n_samples, n_samples)
        """
        try:
            # Normalize features
            feature_matrix = normalize(feature_matrix)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(feature_matrix)
            
            return similarity_matrix
        
        except Exception as e:
            logger.error(f"Error calculating similarity matrix: {e}")
            return np.array([])
    
    def find_similar_documents(self, result: ContentAnalysisResult, 
                             target_index: int, threshold: Optional[float] = None) -> List[Tuple[int, float]]:
        """
        Find documents similar to a target document.
        
        Args:
            result: ContentAnalysisResult object containing the features
            target_index: Index of the target document
            threshold: Similarity threshold (default: self.options.similarity_threshold)
            
        Returns:
            List of tuples (document_index, similarity_score) sorted by similarity
        """
        if not result.similarity_matrix is not None:
            logger.warning("Similarity matrix not available")
            return []
        
        if target_index < 0 or target_index >= len(result.files):
            logger.error(f"Invalid target index: {target_index}")
            return []
        
        threshold = threshold or self.options.similarity_threshold
        
        # Get similarities to target document
        similarities = result.similarity_matrix[target_index]
        
        # Find similar documents (excluding self)
        similar_docs = []
        for i, sim in enumerate(similarities):
            if i != target_index and sim >= threshold:
                similar_docs.append((i, sim))
        
        # Sort by similarity (highest first)
        similar_docs.sort(key=lambda x: x[1], reverse=True)
        
        return similar_docs
    
    def get_important_terms(self, result: ContentAnalysisResult, 
                          document_index: int, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get the most important terms for a document.
        
        Args:
            result: ContentAnalysisResult object containing the features
            document_index: Index of the document
            top_n: Number of top terms to return
            
        Returns:
            List of tuples (term, importance_score) sorted by importance
        """
        if result.feature_type != ContentFeatureType.TFIDF:
            logger.warning("Important terms are only available for TF-IDF features")
            return []
        
        if document_index < 0 or document_index >= len(result.files):
            logger.error(f"Invalid document index: {document_index}")
            return []
        
        if not result.features or not result.features[document_index].feature_names:
            logger.warning("Feature names not available")
            return []
        
        # Get document features and feature names
        doc_features = result.features[document_index].features
        feature_names = result.features[document_index].feature_names
        
        # Get indices of top terms
        top_indices = np.argsort(doc_features)[-top_n:][::-1]
        
        # Get terms and scores
        important_terms = []
        for idx in top_indices:
            if doc_features[idx] > 0:  # Only include terms that are actually in the document
                important_terms.append((feature_names[idx], float(doc_features[idx])))
        
        return important_terms
    
    def visualize_document_similarity(self, result: ContentAnalysisResult, 
                                    output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Visualize document similarity using t-SNE.
        
        Args:
            result: ContentAnalysisResult object containing the features
            output_file: Path to save the visualization (if None, no file is saved)
            
        Returns:
            Dictionary with visualization data
        """
        try:
            # Try to import visualization libraries
            import matplotlib.pyplot as plt
            
            if not result.features:
                logger.warning("No features available for visualization")
                return {}
            
            # Use reduced features if available, otherwise use original features
            if result.reduced_features is not None:
                feature_matrix = result.reduced_features
            else:
                feature_matrix = np.vstack([f.features for f in result.features])
            
            # Normalize features
            feature_matrix = normalize(feature_matrix)
            
            # Apply t-SNE for visualization
            tsne = TSNE(n_components=2, random_state=42)
            vis_data = tsne.fit_transform(feature_matrix)
            
            # Create visualization
            plt.figure(figsize=(10, 8))
            
            # Use clusters if available, otherwise just plot points
            if result.clusters is not None:
                # Plot points colored by cluster
                unique_clusters = set(result.clusters)
                for cluster in unique_clusters:
                    if cluster == -1:
                        # Plot noise points as gray x's
                        mask = np.array(result.clusters) == cluster
                        plt.scatter(
                            vis_data[mask, 0], vis_data[mask, 1],
                            marker='x', color='gray', label='Noise'
                        )
                    else:
                        # Plot cluster points with a unique color
                        mask = np.array(result.clusters) == cluster
                        plt.scatter(
                            vis_data[mask, 0], vis_data[mask, 1],
                            label=f'Cluster {cluster}'
                        )
            else:
                # Just plot all points in blue
                plt.scatter(vis_data[:, 0], vis_data[:, 1], color='blue')
            
            # Add file names as annotations
            for i, file_path in enumerate(result.files):
                plt.annotate(
                    os.path.basename(file_path),
                    (vis_data[i, 0], vis_data[i, 1]),
                    fontsize=8
                )
            
            plt.title('Document Similarity Visualization')
            plt.xlabel('t-SNE dimension 1')
            plt.ylabel('t-SNE dimension 2')
            
            if result.clusters is not None and len(set(result.clusters)) > 1:
                plt.legend()
            
            # Save to file if requested
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"Visualization saved to {output_file}")
            
            # Close the plot to free memory
            plt.close()
            
            # Return visualization data
            return {
                "method": "t-SNE",
                "coordinates": vis_data.tolist(),
                "files": result.files,
                "clusters": result.clusters
            }
        
        except ImportError as e:
            logger.error(f"Error importing visualization libraries: {e}")
            return {}
        
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return {}


def analyze_content(file_paths: List[str], 
                  options: Optional[ContentAnalysisOptions] = None) -> ContentAnalysisResult:
    """
    Analyze the content of a list of files.
    
    Args:
        file_paths: List of file paths to analyze
        options: Content analysis options
        
    Returns:
        ContentAnalysisResult object containing the analysis results
    """
    analyzer = ContentAnalyzer(options)
    return analyzer.extract_features(file_paths)


def find_content_based_similar_files(target_file: str, file_list: List[str],
                                   options: Optional[ContentAnalysisOptions] = None) -> List[Tuple[str, float]]:
    """
    Find files with similar content to a target file.
    
    Args:
        target_file: Path to the target file
        file_list: List of file paths to compare against
        options: Content analysis options
        
    Returns:
        List of tuples (file_path, similarity_score) sorted by similarity
    """
    # Make sure target_file is in file_list
    if target_file not in file_list:
        file_list = [target_file] + file_list
    
    # Analyze content
    analyzer = ContentAnalyzer(options)
    result = analyzer.extract_features(file_list)
    
    if not result.features:
        logger.warning("No features extracted")
        return []
    
    # Find target file index
    target_index = result.files.index(target_file)
    
    # Find similar documents
    similar_docs = analyzer.find_similar_documents(result, target_index)
    
    # Convert to list of (file_path, similarity_score)
    similar_files = [(result.files[idx], score) for idx, score in similar_docs]
    
    return similar_files


def get_document_important_terms(file_path: str, top_n: int = 10,
                               options: Optional[ContentAnalysisOptions] = None) -> List[Tuple[str, float]]:
    """
    Get the most important terms for a document.
    
    Args:
        file_path: Path to the file
        top_n: Number of top terms to return
        options: Content analysis options
        
    Returns:
        List of tuples (term, importance_score) sorted by importance
    """
    # Create options with TF-IDF features
    if options is None:
        options = ContentAnalysisOptions(feature_type=ContentFeatureType.TFIDF)
    else:
        options.feature_type = ContentFeatureType.TFIDF
    
    # Analyze content
    analyzer = ContentAnalyzer(options)
    result = analyzer.extract_features([file_path])
    
    if not result.features:
        logger.warning("No features extracted")
        return []
    
    # Get important terms
    return analyzer.get_important_terms(result, 0, top_n)


def cluster_documents_by_content(file_paths: List[str],
                               options: Optional[ContentAnalysisOptions] = None) -> Dict[int, List[str]]:
    """
    Cluster documents based on their content.
    
    Args:
        file_paths: List of file paths to cluster
        options: Content analysis options
        
    Returns:
        Dictionary mapping cluster IDs to lists of file paths
    """
    # Create options with clustering enabled
    if options is None:
        options = ContentAnalysisOptions(apply_clustering=True)
    else:
        options.apply_clustering = True
    
    # Analyze content
    analyzer = ContentAnalyzer(options)
    result = analyzer.extract_features(file_paths)
    
    if not result.features or result.clusters is None:
        logger.warning("Clustering failed")
        return {}
    
    # Group files by cluster
    clusters = {}
    for i, cluster_id in enumerate(result.clusters):
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(result.files[i])
    
    return clusters


def visualize_document_clusters(file_paths: List[str], output_file: str,
                              options: Optional[ContentAnalysisOptions] = None) -> Dict[str, Any]:
    """
    Visualize document clusters based on content similarity.
    
    Args:
        file_paths: List of file paths to visualize
        output_file: Path to save the visualization
        options: Content analysis options
        
    Returns:
        Dictionary with visualization data
    """
    # Create options with clustering and dimensionality reduction enabled
    if options is None:
        options = ContentAnalysisOptions(
            apply_clustering=True,
            apply_dimensionality_reduction=True
        )
    else:
        options.apply_clustering = True
        options.apply_dimensionality_reduction = True
    
    # Analyze content
    analyzer = ContentAnalyzer(options)
    result = analyzer.extract_features(file_paths)
    
    if not result.features:
        logger.warning("Feature extraction failed")
        return {}
    
    # Create visualization
    return analyzer.visualize_document_similarity(result, output_file)
"""
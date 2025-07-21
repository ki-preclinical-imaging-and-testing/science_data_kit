"""
Similarity analysis module for comparing files based on content and metadata.

This module provides functionality for calculating similarity between files using
various metrics and algorithms. It supports content-based similarity (comparing
the actual content of files) and metadata-based similarity (comparing file metadata).

The module includes:
- Abstract base classes for similarity metrics
- Implementation of common similarity metrics (Jaccard, cosine, etc.)
- File comparison utilities that leverage these metrics
- Result classes for storing and analyzing similarity results
"""

import os
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractor, TextExtractionOptions, TextExtractionResult,
    find_text_extractor_for_file, extract_text_from_file
)
from science_data_kit.core.plugins.file_interpreter import get_file_interpreter_for_file

logger = logging.getLogger(__name__)


class SimilarityMetricType(Enum):
    """Enumeration of similarity metric types."""
    JACCARD = "jaccard"
    COSINE = "cosine"
    LEVENSHTEIN = "levenshtein"
    EUCLIDEAN = "euclidean"
    CUSTOM = "custom"


@dataclass
class SimilarityOptions:
    """Options for similarity analysis."""
    # General options
    metric_type: SimilarityMetricType = SimilarityMetricType.COSINE
    threshold: float = 0.7  # Similarity threshold (0.0 to 1.0)
    
    # Content-based options
    use_content: bool = True
    content_weight: float = 0.7  # Weight for content similarity (0.0 to 1.0)
    text_extraction_options: Optional[TextExtractionOptions] = None
    
    # Metadata-based options
    use_metadata: bool = True
    metadata_weight: float = 0.3  # Weight for metadata similarity (0.0 to 1.0)
    metadata_fields: List[str] = field(default_factory=list)  # Fields to compare, empty means all
    
    # Advanced options
    normalize_scores: bool = True
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Validate options after initialization."""
        if self.content_weight + self.metadata_weight != 1.0:
            logger.warning(
                f"Content weight ({self.content_weight}) and metadata weight "
                f"({self.metadata_weight}) do not sum to 1.0. Normalizing."
            )
            total = self.content_weight + self.metadata_weight
            self.content_weight /= total
            self.metadata_weight /= total
        
        if self.threshold < 0.0 or self.threshold > 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")


@dataclass
class SimilarityResult:
    """Result of a similarity comparison between two files."""
    file1_path: str
    file2_path: str
    similarity_score: float
    content_similarity: Optional[float] = None
    metadata_similarity: Optional[float] = None
    metric_type: SimilarityMetricType = SimilarityMetricType.COSINE
    comparison_details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_similar(self) -> bool:
        """Return True if the files are considered similar based on the threshold."""
        return self.similarity_score >= 0.7  # Default threshold
    
    def __str__(self) -> str:
        """Return a string representation of the similarity result."""
        return (
            f"Similarity between '{os.path.basename(self.file1_path)}' and "
            f"'{os.path.basename(self.file2_path)}': {self.similarity_score:.2f} "
            f"({self.metric_type.value})"
        )


class SimilarityMetric(ABC):
    """Abstract base class for similarity metrics."""
    
    @abstractmethod
    def calculate(self, data1: Any, data2: Any, options: Optional[SimilarityOptions] = None) -> float:
        """
        Calculate similarity between two data objects.
        
        Args:
            data1: First data object
            data2: Second data object
            options: Similarity options
            
        Returns:
            Similarity score between 0.0 (completely different) and 1.0 (identical)
        """
        pass
    
    @property
    @abstractmethod
    def metric_type(self) -> SimilarityMetricType:
        """Return the type of this similarity metric."""
        pass


class JaccardSimilarity(SimilarityMetric):
    """Jaccard similarity metric for comparing sets of tokens."""
    
    def calculate(self, data1: Union[str, Set], data2: Union[str, Set], 
                 options: Optional[SimilarityOptions] = None) -> float:
        """
        Calculate Jaccard similarity between two sets of tokens.
        
        Args:
            data1: First set of tokens or string to tokenize
            data2: Second set of tokens or string to tokenize
            options: Similarity options
            
        Returns:
            Jaccard similarity score between 0.0 and 1.0
        """
        if options is None:
            options = SimilarityOptions()
        
        # Convert strings to sets of tokens if needed
        if isinstance(data1, str):
            if not options.case_sensitive:
                data1 = data1.lower()
            data1 = set(data1.split())
        
        if isinstance(data2, str):
            if not options.case_sensitive:
                data2 = data2.lower()
            data2 = set(data2.split())
        
        # Calculate Jaccard similarity
        if not data1 and not data2:
            return 1.0  # Both empty sets are considered identical
        
        intersection = len(data1.intersection(data2))
        union = len(data1.union(data2))
        
        return intersection / union if union > 0 else 0.0
    
    @property
    def metric_type(self) -> SimilarityMetricType:
        """Return the type of this similarity metric."""
        return SimilarityMetricType.JACCARD


class CosineSimilarity(SimilarityMetric):
    """Cosine similarity metric for comparing text documents."""
    
    def calculate(self, data1: str, data2: str, 
                 options: Optional[SimilarityOptions] = None) -> float:
        """
        Calculate cosine similarity between two text documents.
        
        Args:
            data1: First text document
            data2: Second text document
            options: Similarity options
            
        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        if not data1 and not data2:
            return 1.0  # Both empty documents are considered identical
        
        if not data1 or not data2:
            return 0.0  # One empty document means no similarity
        
        if options is None:
            options = SimilarityOptions()
        
        # Preprocess text if needed
        if not options.case_sensitive:
            data1 = data1.lower()
            data2 = data2.lower()
        
        # Use TF-IDF vectorizer to convert text to vectors
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([data1, data2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    @property
    def metric_type(self) -> SimilarityMetricType:
        """Return the type of this similarity metric."""
        return SimilarityMetricType.COSINE


class LevenshteinSimilarity(SimilarityMetric):
    """Levenshtein (edit distance) similarity metric for comparing strings."""
    
    def calculate(self, data1: str, data2: str, 
                 options: Optional[SimilarityOptions] = None) -> float:
        """
        Calculate Levenshtein similarity between two strings.
        
        Args:
            data1: First string
            data2: Second string
            options: Similarity options
            
        Returns:
            Levenshtein similarity score between 0.0 and 1.0
        """
        if data1 == data2:
            return 1.0
        
        if not data1 and not data2:
            return 1.0  # Both empty strings are considered identical
        
        if not data1 or not data2:
            return 0.0  # One empty string means maximum distance
        
        if options is None:
            options = SimilarityOptions()
        
        # Preprocess strings if needed
        if not options.case_sensitive:
            data1 = data1.lower()
            data2 = data2.lower()
        
        # Calculate Levenshtein distance
        try:
            from Levenshtein import distance
            max_len = max(len(data1), len(data2))
            if max_len == 0:
                return 1.0
            
            dist = distance(data1, data2)
            similarity = 1.0 - (dist / max_len)
            return similarity
        except ImportError:
            logger.warning("Levenshtein package not installed. Falling back to Jaccard similarity.")
            return JaccardSimilarity().calculate(data1, data2, options)
    
    @property
    def metric_type(self) -> SimilarityMetricType:
        """Return the type of this similarity metric."""
        return SimilarityMetricType.LEVENSHTEIN


class EuclideanSimilarity(SimilarityMetric):
    """Euclidean distance similarity metric for comparing numeric vectors."""
    
    def calculate(self, data1: Union[List[float], np.ndarray], 
                 data2: Union[List[float], np.ndarray],
                 options: Optional[SimilarityOptions] = None) -> float:
        """
        Calculate Euclidean similarity between two numeric vectors.
        
        Args:
            data1: First numeric vector
            data2: Second numeric vector
            options: Similarity options
            
        Returns:
            Euclidean similarity score between 0.0 and 1.0
        """
        try:
            # Convert to numpy arrays if needed
            vec1 = np.array(data1, dtype=float)
            vec2 = np.array(data2, dtype=float)
            
            # Check if vectors have the same shape
            if vec1.shape != vec2.shape:
                logger.error(f"Vectors have different shapes: {vec1.shape} vs {vec2.shape}")
                return 0.0
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(vec1 - vec2)
            
            # Convert distance to similarity score (0.0 to 1.0)
            # Using a negative exponential transformation
            similarity = np.exp(-distance)
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating Euclidean similarity: {e}")
            return 0.0
    
    @property
    def metric_type(self) -> SimilarityMetricType:
        """Return the type of this similarity metric."""
        return SimilarityMetricType.EUCLIDEAN


def get_similarity_metric(metric_type: SimilarityMetricType) -> SimilarityMetric:
    """
    Get a similarity metric instance based on the metric type.
    
    Args:
        metric_type: Type of similarity metric to get
        
    Returns:
        Instance of a SimilarityMetric subclass
        
    Raises:
        ValueError: If the metric type is not supported
    """
    metric_map = {
        SimilarityMetricType.JACCARD: JaccardSimilarity(),
        SimilarityMetricType.COSINE: CosineSimilarity(),
        SimilarityMetricType.LEVENSHTEIN: LevenshteinSimilarity(),
        SimilarityMetricType.EUCLIDEAN: EuclideanSimilarity(),
    }
    
    if metric_type not in metric_map:
        raise ValueError(f"Unsupported similarity metric type: {metric_type}")
    
    return metric_map[metric_type]


def calculate_content_similarity(file1_path: str, file2_path: str, 
                               options: Optional[SimilarityOptions] = None) -> float:
    """
    Calculate content similarity between two files.
    
    Args:
        file1_path: Path to the first file
        file2_path: Path to the second file
        options: Similarity options
        
    Returns:
        Content similarity score between 0.0 and 1.0
    """
    if options is None:
        options = SimilarityOptions()
    
    # Extract text from files
    text_options = options.text_extraction_options or TextExtractionOptions()
    
    try:
        text1_result = extract_text_from_file(file1_path, text_options)
        text2_result = extract_text_from_file(file2_path, text_options)
        
        if not text1_result or not text2_result:
            logger.warning(f"Could not extract text from one or both files: {file1_path}, {file2_path}")
            return 0.0
        
        # Get the similarity metric
        metric = get_similarity_metric(options.metric_type)
        
        # Calculate similarity
        return metric.calculate(text1_result.text, text2_result.text, options)
    except Exception as e:
        logger.error(f"Error calculating content similarity: {e}")
        return 0.0


def calculate_metadata_similarity(file1_path: str, file2_path: str,
                                options: Optional[SimilarityOptions] = None) -> float:
    """
    Calculate metadata similarity between two files.
    
    Args:
        file1_path: Path to the first file
        file2_path: Path to the second file
        options: Similarity options
        
    Returns:
        Metadata similarity score between 0.0 and 1.0
    """
    if options is None:
        options = SimilarityOptions()
    
    try:
        # Get file interpreters
        interpreter1 = get_file_interpreter_for_file(file1_path)
        interpreter2 = get_file_interpreter_for_file(file2_path)
        
        if not interpreter1 or not interpreter2:
            logger.warning(f"Could not get file interpreters for one or both files: {file1_path}, {file2_path}")
            return 0.0
        
        # Extract metadata
        metadata1 = interpreter1.extract_metadata(file1_path)
        metadata2 = interpreter2.extract_metadata(file2_path)
        
        if not metadata1 or not metadata2:
            logger.warning(f"Could not extract metadata from one or both files: {file1_path}, {file2_path}")
            return 0.0
        
        # Filter metadata fields if specified
        if options.metadata_fields:
            metadata1 = {k: v for k, v in metadata1.items() if k in options.metadata_fields}
            metadata2 = {k: v for k, v in metadata2.items() if k in options.metadata_fields}
        
        # Calculate field-by-field similarity
        common_fields = set(metadata1.keys()).intersection(set(metadata2.keys()))
        if not common_fields:
            return 0.0
        
        field_similarities = []
        for field in common_fields:
            value1 = metadata1[field]
            value2 = metadata2[field]
            
            # Handle different value types
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                # Numeric values - use relative difference
                max_val = max(abs(value1), abs(value2))
                if max_val == 0:
                    field_sim = 1.0  # Both values are 0
                else:
                    field_sim = 1.0 - (abs(value1 - value2) / max_val)
                    field_sim = max(0.0, min(1.0, field_sim))  # Clamp to [0, 1]
            elif isinstance(value1, str) and isinstance(value2, str):
                # String values - use Levenshtein similarity
                field_sim = LevenshteinSimilarity().calculate(value1, value2, options)
            elif isinstance(value1, (list, tuple)) and isinstance(value2, (list, tuple)):
                # List values - use Jaccard similarity on sets
                field_sim = JaccardSimilarity().calculate(set(value1), set(value2), options)
            elif isinstance(value1, dict) and isinstance(value2, dict):
                # Dict values - recursive call with just these fields
                sub_options = SimilarityOptions(
                    metric_type=options.metric_type,
                    use_content=False,
                    use_metadata=True,
                    metadata_fields=[],
                    case_sensitive=options.case_sensitive
                )
                field_sim = calculate_metadata_similarity_for_dicts(value1, value2, sub_options)
            else:
                # Different types or unsupported types
                field_sim = 1.0 if value1 == value2 else 0.0
            
            field_similarities.append(field_sim)
        
        # Calculate overall metadata similarity as average of field similarities
        return sum(field_similarities) / len(field_similarities) if field_similarities else 0.0
    except Exception as e:
        logger.error(f"Error calculating metadata similarity: {e}")
        return 0.0


def calculate_metadata_similarity_for_dicts(dict1: Dict, dict2: Dict,
                                         options: Optional[SimilarityOptions] = None) -> float:
    """
    Calculate similarity between two metadata dictionaries.
    
    Args:
        dict1: First metadata dictionary
        dict2: Second metadata dictionary
        options: Similarity options
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if options is None:
        options = SimilarityOptions()
    
    # Calculate field-by-field similarity
    common_fields = set(dict1.keys()).intersection(set(dict2.keys()))
    if not common_fields:
        return 0.0
    
    field_similarities = []
    for field in common_fields:
        value1 = dict1[field]
        value2 = dict2[field]
        
        # Handle different value types
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            # Numeric values - use relative difference
            max_val = max(abs(value1), abs(value2))
            if max_val == 0:
                field_sim = 1.0  # Both values are 0
            else:
                field_sim = 1.0 - (abs(value1 - value2) / max_val)
                field_sim = max(0.0, min(1.0, field_sim))  # Clamp to [0, 1]
        elif isinstance(value1, str) and isinstance(value2, str):
            # String values - use Levenshtein similarity
            field_sim = LevenshteinSimilarity().calculate(value1, value2, options)
        elif isinstance(value1, (list, tuple)) and isinstance(value2, (list, tuple)):
            # List values - use Jaccard similarity on sets
            field_sim = JaccardSimilarity().calculate(set(value1), set(value2), options)
        elif isinstance(value1, dict) and isinstance(value2, dict):
            # Dict values - recursive call
            field_sim = calculate_metadata_similarity_for_dicts(value1, value2, options)
        else:
            # Different types or unsupported types
            field_sim = 1.0 if value1 == value2 else 0.0
        
        field_similarities.append(field_sim)
    
    # Calculate overall similarity as average of field similarities
    return sum(field_similarities) / len(field_similarities) if field_similarities else 0.0


def compare_files(file1_path: str, file2_path: str, 
                options: Optional[SimilarityOptions] = None) -> SimilarityResult:
    """
    Compare two files and calculate their similarity.
    
    Args:
        file1_path: Path to the first file
        file2_path: Path to the second file
        options: Similarity options
        
    Returns:
        SimilarityResult object containing the comparison results
    """
    if options is None:
        options = SimilarityOptions()
    
    content_similarity = None
    metadata_similarity = None
    comparison_details = {}
    
    # Calculate content similarity if enabled
    if options.use_content:
        content_similarity = calculate_content_similarity(file1_path, file2_path, options)
        comparison_details["content_similarity"] = content_similarity
    
    # Calculate metadata similarity if enabled
    if options.use_metadata:
        metadata_similarity = calculate_metadata_similarity(file1_path, file2_path, options)
        comparison_details["metadata_similarity"] = metadata_similarity
    
    # Calculate overall similarity score
    if options.use_content and options.use_metadata:
        similarity_score = (
            options.content_weight * content_similarity +
            options.metadata_weight * metadata_similarity
        )
    elif options.use_content:
        similarity_score = content_similarity
    elif options.use_metadata:
        similarity_score = metadata_similarity
    else:
        similarity_score = 0.0
        logger.warning("Neither content nor metadata similarity is enabled")
    
    return SimilarityResult(
        file1_path=file1_path,
        file2_path=file2_path,
        similarity_score=similarity_score,
        content_similarity=content_similarity,
        metadata_similarity=metadata_similarity,
        metric_type=options.metric_type,
        comparison_details=comparison_details
    )


def find_similar_files(target_file: str, file_list: List[str], 
                     options: Optional[SimilarityOptions] = None) -> List[SimilarityResult]:
    """
    Find files similar to a target file from a list of files.
    
    Args:
        target_file: Path to the target file
        file_list: List of file paths to compare against
        options: Similarity options
        
    Returns:
        List of SimilarityResult objects, sorted by similarity score (highest first)
    """
    if options is None:
        options = SimilarityOptions()
    
    results = []
    for file_path in file_list:
        if file_path == target_file:
            continue  # Skip comparing file to itself
        
        result = compare_files(target_file, file_path, options)
        if result.similarity_score >= options.threshold:
            results.append(result)
    
    # Sort results by similarity score (highest first)
    results.sort(key=lambda x: x.similarity_score, reverse=True)
    return results


def find_duplicate_files(file_list: List[str], 
                       options: Optional[SimilarityOptions] = None) -> List[List[str]]:
    """
    Find groups of duplicate or near-duplicate files from a list of files.
    
    Args:
        file_list: List of file paths to compare
        options: Similarity options
        
    Returns:
        List of lists, where each inner list contains paths to similar files
    """
    if options is None:
        options = SimilarityOptions(threshold=0.95)  # Higher threshold for duplicates
    
    # Compare all file pairs
    similarity_results = []
    for i, file1 in enumerate(file_list):
        for file2 in file_list[i+1:]:
            result = compare_files(file1, file2, options)
            if result.similarity_score >= options.threshold:
                similarity_results.append(result)
    
    # Group similar files
    if not similarity_results:
        return []
    
    # Use a simple clustering approach
    groups = []
    processed_files = set()
    
    for result in sorted(similarity_results, key=lambda x: x.similarity_score, reverse=True):
        file1 = result.file1_path
        file2 = result.file2_path
        
        # Find existing groups containing either file
        group1 = None
        group2 = None
        
        for i, group in enumerate(groups):
            if file1 in group:
                group1 = i
            if file2 in group:
                group2 = i
        
        if group1 is None and group2 is None:
            # Create a new group
            groups.append({file1, file2})
            processed_files.add(file1)
            processed_files.add(file2)
        elif group1 is not None and group2 is None:
            # Add file2 to group1
            groups[group1].add(file2)
            processed_files.add(file2)
        elif group1 is None and group2 is not None:
            # Add file1 to group2
            groups[group2].add(file1)
            processed_files.add(file1)
        elif group1 != group2:
            # Merge the two groups
            groups[group1].update(groups[group2])
            groups.pop(group2)
    
    # Add singleton groups for unprocessed files
    for file_path in file_list:
        if file_path not in processed_files:
            groups.append({file_path})
    
    # Convert sets to lists
    return [list(group) for group in groups if len(group) > 1]
"""
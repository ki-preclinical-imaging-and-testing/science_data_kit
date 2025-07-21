"""
Recommendation engine module for suggesting related files to users.

This module provides functionality for recommending files to users based on
content similarity, metadata similarity, usage patterns, and other factors.
It builds on the existing similarity analysis and content analysis modules
to provide intelligent file recommendations.

The module includes:
- Recommendation engine class for generating file recommendations
- Various recommendation strategies (content-based, metadata-based, hybrid)
- Recommendation result classes for storing and presenting recommendations
- Utilities for evaluating recommendation quality
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
    find_content_based_similar_files
)
from science_data_kit.core.file_handling.keyword_extraction import (
    extract_keywords_from_file,
    KeywordExtractionOptions,
    KeywordExtractionMethod
)

logger = logging.getLogger(__name__)


class RecommendationStrategy(Enum):
    """Enumeration of recommendation strategies."""
    CONTENT_BASED = "content_based"
    METADATA_BASED = "metadata_based"
    HYBRID = "hybrid"
    KEYWORD_BASED = "keyword_based"
    CUSTOM = "custom"


@dataclass
class RecommendationOptions:
    """Options for file recommendations."""
    # General options
    strategy: RecommendationStrategy = RecommendationStrategy.HYBRID
    max_recommendations: int = 10
    min_similarity_score: float = 0.3
    
    # Content-based options
    content_weight: float = 0.7
    content_analysis_options: Optional[ContentAnalysisOptions] = None
    
    # Metadata-based options
    metadata_weight: float = 0.3
    metadata_fields: List[str] = field(default_factory=list)
    
    # Keyword-based options
    use_keywords: bool = True
    keyword_extraction_options: Optional[KeywordExtractionOptions] = None
    keyword_weight: float = 0.5
    
    # Advanced options
    use_file_history: bool = False
    history_weight: float = 0.2
    
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


@dataclass
class Recommendation:
    """A single file recommendation."""
    file_path: str
    score: float
    reason: str
    similarity_details: Optional[Dict[str, Any]] = None
    keywords: Optional[List[Tuple[str, float]]] = None
    
    def __str__(self) -> str:
        """Return a string representation of the recommendation."""
        return f"Recommendation: {os.path.basename(self.file_path)} (score: {self.score:.2f}) - {self.reason}"


@dataclass
class RecommendationResult:
    """Result of a recommendation query."""
    target_file: Optional[str]
    recommendations: List[Recommendation]
    strategy: RecommendationStrategy
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the recommendation result."""
        if self.target_file:
            header = f"Recommendations for {os.path.basename(self.target_file)} using {self.strategy.value} strategy:"
        else:
            header = f"General recommendations using {self.strategy.value} strategy:"
        
        if not self.recommendations:
            return f"{header}\nNo recommendations found."
        
        recommendations_str = "\n".join([f"- {rec}" for rec in self.recommendations])
        return f"{header}\n{recommendations_str}"


class RecommendationEngine:
    """Class for generating file recommendations."""
    
    def __init__(self, options: Optional[RecommendationOptions] = None):
        """
        Initialize the recommendation engine.
        
        Args:
            options: Recommendation options
        """
        self.options = options or RecommendationOptions()
        self.content_analyzer = ContentAnalyzer(self.options.content_analysis_options)
    
    def recommend_similar_files(self, target_file: str, file_list: List[str]) -> RecommendationResult:
        """
        Recommend files similar to a target file.
        
        Args:
            target_file: Path to the target file
            file_list: List of file paths to consider for recommendations
            
        Returns:
            RecommendationResult object containing the recommendations
        """
        if target_file not in file_list:
            file_list = [f for f in file_list if f != target_file]
        
        if not file_list:
            logger.warning("Empty file list for recommendations")
            return RecommendationResult(
                target_file=target_file,
                recommendations=[],
                strategy=self.options.strategy
            )
        
        # Generate recommendations based on the selected strategy
        if self.options.strategy == RecommendationStrategy.CONTENT_BASED:
            return self._recommend_content_based(target_file, file_list)
        elif self.options.strategy == RecommendationStrategy.METADATA_BASED:
            return self._recommend_metadata_based(target_file, file_list)
        elif self.options.strategy == RecommendationStrategy.KEYWORD_BASED:
            return self._recommend_keyword_based(target_file, file_list)
        elif self.options.strategy == RecommendationStrategy.HYBRID:
            return self._recommend_hybrid(target_file, file_list)
        else:
            logger.warning(f"Unsupported recommendation strategy: {self.options.strategy}")
            return RecommendationResult(
                target_file=target_file,
                recommendations=[],
                strategy=self.options.strategy
            )
    
    def _recommend_content_based(self, target_file: str, file_list: List[str]) -> RecommendationResult:
        """
        Generate content-based recommendations.
        
        Args:
            target_file: Path to the target file
            file_list: List of file paths to consider for recommendations
            
        Returns:
            RecommendationResult object containing the recommendations
        """
        try:
            # Find similar files based on content
            similar_files = find_content_based_similar_files(
                target_file, 
                file_list, 
                self.options.content_analysis_options
            )
            
            # Create recommendations
            recommendations = []
            for file_path, score in similar_files:
                if score >= self.options.min_similarity_score:
                    recommendations.append(Recommendation(
                        file_path=file_path,
                        score=score,
                        reason="Content similarity",
                        similarity_details={"content_similarity": score}
                    ))
            
            # Limit number of recommendations
            recommendations = recommendations[:self.options.max_recommendations]
            
            return RecommendationResult(
                target_file=target_file,
                recommendations=recommendations,
                strategy=RecommendationStrategy.CONTENT_BASED,
                metadata={
                    "num_candidates": len(file_list),
                    "num_recommendations": len(recommendations)
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating content-based recommendations: {e}")
            return RecommendationResult(
                target_file=target_file,
                recommendations=[],
                strategy=RecommendationStrategy.CONTENT_BASED
            )
    
    def _recommend_metadata_based(self, target_file: str, file_list: List[str]) -> RecommendationResult:
        """
        Generate metadata-based recommendations.
        
        Args:
            target_file: Path to the target file
            file_list: List of file paths to consider for recommendations
            
        Returns:
            RecommendationResult object containing the recommendations
        """
        try:
            # Create similarity options focused on metadata
            similarity_options = SimilarityOptions(
                use_content=False,
                use_metadata=True,
                metadata_fields=self.options.metadata_fields,
                threshold=self.options.min_similarity_score
            )
            
            # Find similar files based on metadata
            similar_files = find_similar_files(target_file, file_list, similarity_options)
            
            # Create recommendations
            recommendations = []
            for result in similar_files:
                recommendations.append(Recommendation(
                    file_path=result.file2_path,
                    score=result.similarity_score,
                    reason="Metadata similarity",
                    similarity_details={"metadata_similarity": result.metadata_similarity}
                ))
            
            # Limit number of recommendations
            recommendations = recommendations[:self.options.max_recommendations]
            
            return RecommendationResult(
                target_file=target_file,
                recommendations=recommendations,
                strategy=RecommendationStrategy.METADATA_BASED,
                metadata={
                    "num_candidates": len(file_list),
                    "num_recommendations": len(recommendations)
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating metadata-based recommendations: {e}")
            return RecommendationResult(
                target_file=target_file,
                recommendations=[],
                strategy=RecommendationStrategy.METADATA_BASED
            )
    
    def _recommend_keyword_based(self, target_file: str, file_list: List[str]) -> RecommendationResult:
        """
        Generate keyword-based recommendations.
        
        Args:
            target_file: Path to the target file
            file_list: List of file paths to consider for recommendations
            
        Returns:
            RecommendationResult object containing the recommendations
        """
        try:
            # Extract keywords from target file
            keyword_options = self.options.keyword_extraction_options or KeywordExtractionOptions(
                method=KeywordExtractionMethod.RAKE,
                num_keywords=20
            )
            
            target_keywords = extract_keywords_from_file(target_file, keyword_options)
            if not target_keywords.keywords:
                logger.warning(f"No keywords extracted from target file: {target_file}")
                return RecommendationResult(
                    target_file=target_file,
                    recommendations=[],
                    strategy=RecommendationStrategy.KEYWORD_BASED
                )
            
            # Create a set of target keywords for faster lookup
            target_keyword_set = {kw.text.lower() for kw in target_keywords.keywords}
            
            # Calculate keyword overlap for each file
            recommendations = []
            for file_path in file_list:
                if file_path == target_file:
                    continue
                
                try:
                    # Extract keywords from candidate file
                    file_keywords = extract_keywords_from_file(file_path, keyword_options)
                    if not file_keywords.keywords:
                        continue
                    
                    # Calculate keyword overlap
                    file_keyword_set = {kw.text.lower() for kw in file_keywords.keywords}
                    common_keywords = target_keyword_set.intersection(file_keyword_set)
                    
                    if common_keywords:
                        # Calculate score based on keyword overlap
                        overlap_ratio = len(common_keywords) / max(len(target_keyword_set), len(file_keyword_set))
                        
                        # Get the actual keyword objects with scores for common keywords
                        common_keyword_objects = [
                            (kw.text, kw.score) for kw in file_keywords.keywords 
                            if kw.text.lower() in common_keywords
                        ]
                        
                        if overlap_ratio >= self.options.min_similarity_score:
                            recommendations.append(Recommendation(
                                file_path=file_path,
                                score=overlap_ratio,
                                reason=f"Keyword similarity ({len(common_keywords)} common keywords)",
                                keywords=common_keyword_objects
                            ))
                
                except Exception as e:
                    logger.error(f"Error processing file {file_path} for keyword-based recommendations: {e}")
            
            # Sort by score and limit number of recommendations
            recommendations.sort(key=lambda x: x.score, reverse=True)
            recommendations = recommendations[:self.options.max_recommendations]
            
            return RecommendationResult(
                target_file=target_file,
                recommendations=recommendations,
                strategy=RecommendationStrategy.KEYWORD_BASED,
                metadata={
                    "num_candidates": len(file_list),
                    "num_recommendations": len(recommendations),
                    "target_keywords": [(kw.text, kw.score) for kw in target_keywords.keywords]
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating keyword-based recommendations: {e}")
            return RecommendationResult(
                target_file=target_file,
                recommendations=[],
                strategy=RecommendationStrategy.KEYWORD_BASED
            )
    
    def _recommend_hybrid(self, target_file: str, file_list: List[str]) -> RecommendationResult:
        """
        Generate hybrid recommendations combining multiple strategies.
        
        Args:
            target_file: Path to the target file
            file_list: List of file paths to consider for recommendations
            
        Returns:
            RecommendationResult object containing the recommendations
        """
        try:
            # Get recommendations from different strategies
            content_results = self._recommend_content_based(target_file, file_list)
            metadata_results = self._recommend_metadata_based(target_file, file_list)
            
            # Combine recommendations
            file_scores = {}
            file_reasons = {}
            file_details = {}
            
            # Process content-based recommendations
            for rec in content_results.recommendations:
                file_scores[rec.file_path] = self.options.content_weight * rec.score
                file_reasons[rec.file_path] = ["Content similarity"]
                file_details[rec.file_path] = {
                    "content_similarity": rec.score
                }
            
            # Process metadata-based recommendations
            for rec in metadata_results.recommendations:
                if rec.file_path in file_scores:
                    file_scores[rec.file_path] += self.options.metadata_weight * rec.score
                    file_reasons[rec.file_path].append("Metadata similarity")
                    file_details[rec.file_path]["metadata_similarity"] = rec.score
                else:
                    file_scores[rec.file_path] = self.options.metadata_weight * rec.score
                    file_reasons[rec.file_path] = ["Metadata similarity"]
                    file_details[rec.file_path] = {
                        "metadata_similarity": rec.score
                    }
            
            # Add keyword-based recommendations if enabled
            if self.options.use_keywords:
                keyword_results = self._recommend_keyword_based(target_file, file_list)
                for rec in keyword_results.recommendations:
                    if rec.file_path in file_scores:
                        file_scores[rec.file_path] += self.options.keyword_weight * rec.score
                        file_reasons[rec.file_path].append("Keyword similarity")
                        file_details[rec.file_path]["keyword_similarity"] = rec.score
                        file_details[rec.file_path]["common_keywords"] = rec.keywords
                    else:
                        file_scores[rec.file_path] = self.options.keyword_weight * rec.score
                        file_reasons[rec.file_path] = ["Keyword similarity"]
                        file_details[rec.file_path] = {
                            "keyword_similarity": rec.score,
                            "common_keywords": rec.keywords
                        }
            
            # Create combined recommendations
            recommendations = []
            for file_path, score in file_scores.items():
                if score >= self.options.min_similarity_score:
                    reason = " and ".join(file_reasons[file_path])
                    recommendations.append(Recommendation(
                        file_path=file_path,
                        score=score,
                        reason=reason,
                        similarity_details=file_details[file_path],
                        keywords=file_details[file_path].get("common_keywords")
                    ))
            
            # Sort by score and limit number of recommendations
            recommendations.sort(key=lambda x: x.score, reverse=True)
            recommendations = recommendations[:self.options.max_recommendations]
            
            return RecommendationResult(
                target_file=target_file,
                recommendations=recommendations,
                strategy=RecommendationStrategy.HYBRID,
                metadata={
                    "num_candidates": len(file_list),
                    "num_recommendations": len(recommendations),
                    "strategies_used": ["content", "metadata"] + (["keyword"] if self.options.use_keywords else [])
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations: {e}")
            return RecommendationResult(
                target_file=target_file,
                recommendations=[],
                strategy=RecommendationStrategy.HYBRID
            )
    
    def recommend_for_directory(self, directory_path: str, max_files: int = 1000) -> Dict[str, RecommendationResult]:
        """
        Generate recommendations for all files in a directory.
        
        Args:
            directory_path: Path to the directory
            max_files: Maximum number of files to process
            
        Returns:
            Dictionary mapping file paths to RecommendationResult objects
        """
        try:
            # Get all files in the directory
            file_list = []
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
                    if len(file_list) >= max_files:
                        break
                if len(file_list) >= max_files:
                    break
            
            if not file_list:
                logger.warning(f"No files found in directory: {directory_path}")
                return {}
            
            # Generate recommendations for each file
            recommendations = {}
            for file_path in file_list:
                result = self.recommend_similar_files(file_path, file_list)
                recommendations[file_path] = result
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating recommendations for directory: {e}")
            return {}


def recommend_similar_files(target_file: str, file_list: List[str],
                          options: Optional[RecommendationOptions] = None) -> RecommendationResult:
    """
    Recommend files similar to a target file.
    
    Args:
        target_file: Path to the target file
        file_list: List of file paths to consider for recommendations
        options: Recommendation options
        
    Returns:
        RecommendationResult object containing the recommendations
    """
    engine = RecommendationEngine(options)
    return engine.recommend_similar_files(target_file, file_list)


def recommend_for_directory(directory_path: str, max_files: int = 1000,
                          options: Optional[RecommendationOptions] = None) -> Dict[str, RecommendationResult]:
    """
    Generate recommendations for all files in a directory.
    
    Args:
        directory_path: Path to the directory
        max_files: Maximum number of files to process
        options: Recommendation options
        
    Returns:
        Dictionary mapping file paths to RecommendationResult objects
    """
    engine = RecommendationEngine(options)
    return engine.recommend_for_directory(directory_path, max_files)
"""
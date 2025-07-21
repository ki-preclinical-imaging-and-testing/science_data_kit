"""
Tag suggestion module for automatically suggesting tags for files based on content.

This module provides functionality for suggesting tags for files based on their content,
metadata, and other factors. It builds on the existing keyword extraction, content analysis,
and entity recognition modules to provide intelligent tag suggestions.

The module includes:
- Tag suggestion engine class for generating tag suggestions
- Various suggestion strategies (keyword-based, entity-based, hybrid)
- Tag suggestion result classes for storing and presenting suggestions
- Utilities for evaluating suggestion quality
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from science_data_kit.core.file_handling.keyword_extraction import (
    extract_keywords_from_file,
    KeywordExtractionOptions,
    KeywordExtractionMethod,
    Keyword
)
from science_data_kit.core.file_handling.entity_recognition import (
    extract_entities_from_file,
    EntityExtractionOptions,
    EntityType
)
from science_data_kit.core.file_handling.content_analysis import (
    ContentAnalysisOptions,
    ContentAnalyzer,
    get_document_important_terms
)

logger = logging.getLogger(__name__)


class TagSuggestionStrategy(Enum):
    """Enumeration of tag suggestion strategies."""
    KEYWORD_BASED = "keyword_based"
    ENTITY_BASED = "entity_based"
    HYBRID = "hybrid"
    CUSTOM = "custom"


@dataclass
class TagSuggestionOptions:
    """Options for tag suggestions."""
    # General options
    strategy: TagSuggestionStrategy = TagSuggestionStrategy.HYBRID
    max_suggestions: int = 10
    min_score: float = 0.3
    
    # Keyword-based options
    keyword_weight: float = 0.6
    keyword_extraction_options: Optional[KeywordExtractionOptions] = None
    
    # Entity-based options
    entity_weight: float = 0.4
    entity_extraction_options: Optional[EntityExtractionOptions] = None
    entity_types: List[EntityType] = field(default_factory=list)  # Empty means all types
    
    # Content analysis options
    use_content_analysis: bool = True
    content_analysis_options: Optional[ContentAnalysisOptions] = None
    
    # Advanced options
    filter_common_words: bool = True
    common_words_file: Optional[str] = None
    use_stemming: bool = False
    
    def __post_init__(self):
        """Validate options after initialization."""
        if self.keyword_weight + self.entity_weight != 1.0:
            logger.warning(
                f"Keyword weight ({self.keyword_weight}) and entity weight "
                f"({self.entity_weight}) do not sum to 1.0. Normalizing."
            )
            total = self.keyword_weight + self.entity_weight
            self.keyword_weight /= total
            self.entity_weight /= total


@dataclass
class TagSuggestion:
    """A single tag suggestion."""
    tag: str
    score: float
    source: str
    details: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """Return a string representation of the tag suggestion."""
        return f"{self.tag} ({self.score:.2f}) - {self.source}"


@dataclass
class TagSuggestionResult:
    """Result of a tag suggestion query."""
    file_path: str
    suggestions: List[TagSuggestion]
    strategy: TagSuggestionStrategy
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the tag suggestion result."""
        header = f"Tag suggestions for {os.path.basename(self.file_path)} using {self.strategy.value} strategy:"
        
        if not self.suggestions:
            return f"{header}\nNo suggestions found."
        
        suggestions_str = "\n".join([f"- {sugg}" for sugg in self.suggestions])
        return f"{header}\n{suggestions_str}"
    
    def get_tags(self) -> List[str]:
        """Return just the tag strings."""
        return [sugg.tag for sugg in self.suggestions]


class TagSuggestionEngine:
    """Class for generating tag suggestions."""
    
    def __init__(self, options: Optional[TagSuggestionOptions] = None):
        """
        Initialize the tag suggestion engine.
        
        Args:
            options: Tag suggestion options
        """
        self.options = options or TagSuggestionOptions()
        self.common_words = self._load_common_words()
    
    def _load_common_words(self) -> Set[str]:
        """
        Load common words to filter out from suggestions.
        
        Returns:
            Set of common words
        """
        common_words = set()
        
        if self.options.filter_common_words:
            # Default common words
            default_common_words = {
                "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
                "at", "from", "by", "on", "off", "for", "in", "out", "over", "under",
                "again", "further", "then", "once", "here", "there", "when", "where", "why",
                "how", "all", "any", "both", "each", "few", "more", "most", "other",
                "some", "such", "no", "nor", "not", "only", "own", "same", "so",
                "than", "too", "very", "s", "t", "can", "will", "just", "don",
                "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren",
                "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma",
                "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn"
            }
            
            # Add default common words
            common_words.update(default_common_words)
            
            # Load custom common words if provided
            if self.options.common_words_file and os.path.exists(self.options.common_words_file):
                try:
                    with open(self.options.common_words_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            word = line.strip().lower()
                            if word and not word.startswith('#'):
                                common_words.add(word)
                except Exception as e:
                    logger.error(f"Error loading common words file: {e}")
        
        return common_words
    
    def suggest_tags(self, file_path: str) -> TagSuggestionResult:
        """
        Suggest tags for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            TagSuggestionResult object containing the suggestions
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=[],
                strategy=self.options.strategy
            )
        
        # Generate suggestions based on the selected strategy
        if self.options.strategy == TagSuggestionStrategy.KEYWORD_BASED:
            return self._suggest_keyword_based(file_path)
        elif self.options.strategy == TagSuggestionStrategy.ENTITY_BASED:
            return self._suggest_entity_based(file_path)
        elif self.options.strategy == TagSuggestionStrategy.HYBRID:
            return self._suggest_hybrid(file_path)
        else:
            logger.warning(f"Unsupported tag suggestion strategy: {self.options.strategy}")
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=[],
                strategy=self.options.strategy
            )
    
    def _suggest_keyword_based(self, file_path: str) -> TagSuggestionResult:
        """
        Generate keyword-based tag suggestions.
        
        Args:
            file_path: Path to the file
            
        Returns:
            TagSuggestionResult object containing the suggestions
        """
        try:
            # Extract keywords from file
            keyword_options = self.options.keyword_extraction_options or KeywordExtractionOptions(
                method=KeywordExtractionMethod.RAKE,
                num_keywords=self.options.max_suggestions * 2  # Extract more keywords than needed
            )
            
            keyword_result = extract_keywords_from_file(file_path, keyword_options)
            
            if not keyword_result.keywords:
                logger.warning(f"No keywords extracted from file: {file_path}")
                return TagSuggestionResult(
                    file_path=file_path,
                    suggestions=[],
                    strategy=TagSuggestionStrategy.KEYWORD_BASED
                )
            
            # Convert keywords to tag suggestions
            suggestions = []
            for keyword in keyword_result.keywords:
                # Skip common words if filtering is enabled
                if self.options.filter_common_words and keyword.text.lower() in self.common_words:
                    continue
                
                # Create tag suggestion
                if keyword.score >= self.options.min_score:
                    suggestions.append(TagSuggestion(
                        tag=keyword.text,
                        score=keyword.score,
                        source="Keyword extraction",
                        details={"method": keyword_result.method.value}
                    ))
            
            # Sort by score and limit number of suggestions
            suggestions.sort(key=lambda x: x.score, reverse=True)
            suggestions = suggestions[:self.options.max_suggestions]
            
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=suggestions,
                strategy=TagSuggestionStrategy.KEYWORD_BASED,
                metadata={
                    "num_keywords_extracted": len(keyword_result.keywords),
                    "num_suggestions": len(suggestions),
                    "extraction_method": keyword_result.method.value
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating keyword-based tag suggestions: {e}")
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=[],
                strategy=TagSuggestionStrategy.KEYWORD_BASED
            )
    
    def _suggest_entity_based(self, file_path: str) -> TagSuggestionResult:
        """
        Generate entity-based tag suggestions.
        
        Args:
            file_path: Path to the file
            
        Returns:
            TagSuggestionResult object containing the suggestions
        """
        try:
            # Extract entities from file
            entity_options = self.options.entity_extraction_options or EntityExtractionOptions(
                entity_types=self.options.entity_types or list(EntityType)
            )
            
            entity_result = extract_entities_from_file(file_path, entity_options)
            
            if not entity_result.entities:
                logger.warning(f"No entities extracted from file: {file_path}")
                return TagSuggestionResult(
                    file_path=file_path,
                    suggestions=[],
                    strategy=TagSuggestionStrategy.ENTITY_BASED
                )
            
            # Convert entities to tag suggestions
            suggestions = []
            for entity in entity_result.entities:
                # Skip common words if filtering is enabled
                if self.options.filter_common_words and entity.text.lower() in self.common_words:
                    continue
                
                # Create tag suggestion
                suggestions.append(TagSuggestion(
                    tag=entity.text,
                    score=1.0,  # Entities don't have scores, so use 1.0
                    source=f"Entity ({entity.entity_type.value})",
                    details={"entity_type": entity.entity_type.value}
                ))
            
            # Sort by entity type priority and limit number of suggestions
            # Priority: PERSON > ORGANIZATION > LOCATION > others
            type_priority = {
                EntityType.PERSON: 4,
                EntityType.ORGANIZATION: 3,
                EntityType.LOCATION: 2
            }
            
            suggestions.sort(key=lambda x: (
                type_priority.get(EntityType(x.details["entity_type"]), 1),
                x.score
            ), reverse=True)
            
            suggestions = suggestions[:self.options.max_suggestions]
            
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=suggestions,
                strategy=TagSuggestionStrategy.ENTITY_BASED,
                metadata={
                    "num_entities_extracted": len(entity_result.entities),
                    "num_suggestions": len(suggestions),
                    "entity_types": [e.entity_type.value for e in entity_result.entities]
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating entity-based tag suggestions: {e}")
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=[],
                strategy=TagSuggestionStrategy.ENTITY_BASED
            )
    
    def _suggest_hybrid(self, file_path: str) -> TagSuggestionResult:
        """
        Generate hybrid tag suggestions combining multiple strategies.
        
        Args:
            file_path: Path to the file
            
        Returns:
            TagSuggestionResult object containing the suggestions
        """
        try:
            # Get suggestions from different strategies
            keyword_results = self._suggest_keyword_based(file_path)
            entity_results = self._suggest_entity_based(file_path)
            
            # Combine suggestions
            tag_scores = {}
            tag_sources = {}
            tag_details = {}
            
            # Process keyword-based suggestions
            for sugg in keyword_results.suggestions:
                tag_scores[sugg.tag] = self.options.keyword_weight * sugg.score
                tag_sources[sugg.tag] = [sugg.source]
                tag_details[sugg.tag] = {"keyword_score": sugg.score}
            
            # Process entity-based suggestions
            for sugg in entity_results.suggestions:
                if sugg.tag in tag_scores:
                    tag_scores[sugg.tag] += self.options.entity_weight * sugg.score
                    tag_sources[sugg.tag].append(sugg.source)
                    tag_details[sugg.tag]["entity_score"] = sugg.score
                    tag_details[sugg.tag]["entity_type"] = sugg.details.get("entity_type")
                else:
                    tag_scores[sugg.tag] = self.options.entity_weight * sugg.score
                    tag_sources[sugg.tag] = [sugg.source]
                    tag_details[sugg.tag] = {
                        "entity_score": sugg.score,
                        "entity_type": sugg.details.get("entity_type")
                    }
            
            # Create combined suggestions
            suggestions = []
            for tag, score in tag_scores.items():
                if score >= self.options.min_score:
                    source = " and ".join(tag_sources[tag])
                    suggestions.append(TagSuggestion(
                        tag=tag,
                        score=score,
                        source=source,
                        details=tag_details[tag]
                    ))
            
            # Sort by score and limit number of suggestions
            suggestions.sort(key=lambda x: x.score, reverse=True)
            suggestions = suggestions[:self.options.max_suggestions]
            
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=suggestions,
                strategy=TagSuggestionStrategy.HYBRID,
                metadata={
                    "num_keyword_suggestions": len(keyword_results.suggestions),
                    "num_entity_suggestions": len(entity_results.suggestions),
                    "num_combined_suggestions": len(suggestions)
                }
            )
        
        except Exception as e:
            logger.error(f"Error generating hybrid tag suggestions: {e}")
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=[],
                strategy=TagSuggestionStrategy.HYBRID
            )
    
    def suggest_tags_for_directory(self, directory_path: str, max_files: int = 1000) -> Dict[str, TagSuggestionResult]:
        """
        Generate tag suggestions for all files in a directory.
        
        Args:
            directory_path: Path to the directory
            max_files: Maximum number of files to process
            
        Returns:
            Dictionary mapping file paths to TagSuggestionResult objects
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
            
            # Generate tag suggestions for each file
            suggestions = {}
            for file_path in file_list:
                result = self.suggest_tags(file_path)
                suggestions[file_path] = result
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Error generating tag suggestions for directory: {e}")
            return {}


def suggest_tags(file_path: str, options: Optional[TagSuggestionOptions] = None) -> TagSuggestionResult:
    """
    Suggest tags for a file.
    
    Args:
        file_path: Path to the file
        options: Tag suggestion options
        
    Returns:
        TagSuggestionResult object containing the suggestions
    """
    engine = TagSuggestionEngine(options)
    return engine.suggest_tags(file_path)


def suggest_tags_for_directory(directory_path: str, max_files: int = 1000,
                             options: Optional[TagSuggestionOptions] = None) -> Dict[str, TagSuggestionResult]:
    """
    Generate tag suggestions for all files in a directory.
    
    Args:
        directory_path: Path to the directory
        max_files: Maximum number of files to process
        options: Tag suggestion options
        
    Returns:
        Dictionary mapping file paths to TagSuggestionResult objects
    """
    engine = TagSuggestionEngine(options)
    return engine.suggest_tags_for_directory(directory_path, max_files)


def apply_tags_to_file(file_path: str, tags: List[str]) -> bool:
    """
    Apply tags to a file.
    
    This function is a placeholder for a system-specific implementation.
    Depending on the system, this might involve:
    - Adding tags to file metadata
    - Updating a database record
    - Modifying a knowledge graph
    
    Args:
        file_path: Path to the file
        tags: List of tags to apply
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Applying tags to file: {file_path}")
        logger.info(f"Tags: {tags}")
        
        # TODO: Implement system-specific tag application
        # This is a placeholder for actual implementation
        
        return True
    
    except Exception as e:
        logger.error(f"Error applying tags to file: {e}")
        return False
"""
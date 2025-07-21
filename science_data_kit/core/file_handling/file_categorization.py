"""
File categorization module for automatically categorizing files based on content.

This module provides functionality for automatically categorizing files based on
their content, metadata, and other attributes. It builds on the content_analysis,
topic_modeling, and keyword_extraction modules to provide a comprehensive system
for organizing files into meaningful categories.

The module includes:
- Predefined and custom category schemes
- Content-based categorization using machine learning
- Rule-based categorization using metadata and file attributes
- Category suggestion and confidence scoring
- Category hierarchy management
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

from science_data_kit.core.file_handling.content_analysis import (
    ContentAnalysisOptions,
    ContentAnalysisResult,
    ContentAnalyzer,
    ContentFeatureType,
    analyze_content
)
from science_data_kit.core.file_handling.keyword_extraction import (
    KeywordExtractionMethod,
    KeywordExtractionOptions,
    KeywordExtractor,
    extract_keywords_from_file
)
from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions,
    extract_text_from_file
)
from science_data_kit.core.file_handling.topic_modeling import (
    TopicModelingMethod,
    TopicModelingOptions,
    TopicModeler,
    extract_topics_from_files
)

logger = logging.getLogger(__name__)


class CategorizationMethod(Enum):
    """Enumeration of categorization methods."""
    SUPERVISED = "supervised"  # Requires labeled training data
    UNSUPERVISED = "unsupervised"  # Automatic clustering
    RULE_BASED = "rule_based"  # Based on predefined rules
    HYBRID = "hybrid"  # Combination of methods


class CategorizationAlgorithm(Enum):
    """Enumeration of categorization algorithms."""
    NAIVE_BAYES = "naive_bayes"
    RANDOM_FOREST = "random_forest"
    SVM = "svm"
    KMEANS = "kmeans"
    TOPIC_BASED = "topic_based"
    KEYWORD_BASED = "keyword_based"
    CUSTOM = "custom"


class CategoryScheme(Enum):
    """Enumeration of predefined category schemes."""
    DOCUMENT_TYPE = "document_type"  # PDF, DOCX, spreadsheet, etc.
    CONTENT_TYPE = "content_type"  # Text, image, audio, video, etc.
    SUBJECT_AREA = "subject_area"  # Science, engineering, medicine, etc.
    FILE_PURPOSE = "file_purpose"  # Data, report, presentation, etc.
    CUSTOM = "custom"  # User-defined categories


@dataclass
class Category:
    """Class representing a category."""
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the category."""
        return f"{self.name} ({self.id})"


@dataclass
class CategoryAssignment:
    """Class representing a category assignment for a file."""
    file_path: str
    category_id: str
    confidence: float
    method: CategorizationMethod
    algorithm: CategorizationAlgorithm
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the category assignment."""
        return f"{os.path.basename(self.file_path)} -> {self.category_id} ({self.confidence:.2f})"


@dataclass
class CategorizationOptions:
    """Options for file categorization."""
    # General options
    method: CategorizationMethod = CategorizationMethod.UNSUPERVISED
    algorithm: CategorizationAlgorithm = CategorizationAlgorithm.TOPIC_BASED
    category_scheme: CategoryScheme = CategoryScheme.CONTENT_TYPE
    min_confidence: float = 0.5
    max_categories_per_file: int = 3
    
    # Feature extraction options
    feature_type: ContentFeatureType = ContentFeatureType.TFIDF
    max_features: int = 1000
    ngram_range: Tuple[int, int] = (1, 2)
    
    # Supervised learning options
    test_size: float = 0.2
    random_state: int = 42
    
    # Unsupervised learning options
    num_clusters: int = 5
    
    # Topic-based options
    topic_method: TopicModelingMethod = TopicModelingMethod.LDA
    num_topics: int = 5
    
    # Keyword-based options
    keyword_method: KeywordExtractionMethod = KeywordExtractionMethod.TFIDF
    num_keywords: int = 10
    
    # Rule-based options
    rules: Dict[str, Any] = field(default_factory=dict)
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class CategorizationResult:
    """Result of file categorization."""
    file_paths: List[str]
    category_assignments: List[CategoryAssignment]
    categories: Dict[str, Category]
    method: CategorizationMethod
    algorithm: CategorizationAlgorithm
    model: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the categorization result."""
        return "\n".join([
            f"Method: {self.method.value}",
            f"Algorithm: {self.algorithm.value}",
            f"Files: {len(self.file_paths)}",
            f"Categories: {len(self.categories)}",
            f"Assignments: {len(self.category_assignments)}"
        ])
    
    def get_assignments_for_file(self, file_path: str) -> List[CategoryAssignment]:
        """Get category assignments for a specific file."""
        return [a for a in self.category_assignments if a.file_path == file_path]
    
    def get_files_in_category(self, category_id: str) -> List[str]:
        """Get files assigned to a specific category."""
        return [a.file_path for a in self.category_assignments if a.category_id == category_id]
    
    def get_category_distribution(self) -> Dict[str, int]:
        """Get the distribution of files across categories."""
        distribution = {}
        for category_id in self.categories:
            distribution[category_id] = len(self.get_files_in_category(category_id))
        return distribution


class FileCategorizer:
    """Class for categorizing files based on content and metadata."""
    
    def __init__(self, options: Optional[CategorizationOptions] = None):
        """
        Initialize the file categorizer.
        
        Args:
            options: Categorization options
        """
        self.options = options or CategorizationOptions()
        self.categories = {}
        self.model = None
        self.label_encoder = None
        self.vectorizer = None
    
    def categorize_files(self, file_paths: List[str], 
                        training_data: Optional[Dict[str, List[str]]] = None) -> CategorizationResult:
        """
        Categorize a list of files.
        
        Args:
            file_paths: List of file paths to categorize
            training_data: Dictionary mapping category IDs to lists of file paths (for supervised methods)
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        if not file_paths:
            logger.warning("No files provided for categorization")
            return CategorizationResult(
                file_paths=[],
                category_assignments=[],
                categories={},
                method=self.options.method,
                algorithm=self.options.algorithm
            )
        
        # Initialize categories based on the selected scheme
        self._initialize_categories()
        
        # Categorize files based on the selected method
        if self.options.method == CategorizationMethod.SUPERVISED:
            if not training_data:
                logger.error("Training data required for supervised categorization")
                return CategorizationResult(
                    file_paths=file_paths,
                    category_assignments=[],
                    categories=self.categories,
                    method=self.options.method,
                    algorithm=self.options.algorithm,
                    metadata={"error": "Training data required for supervised categorization"}
                )
            return self._categorize_supervised(file_paths, training_data)
        
        elif self.options.method == CategorizationMethod.UNSUPERVISED:
            return self._categorize_unsupervised(file_paths)
        
        elif self.options.method == CategorizationMethod.RULE_BASED:
            return self._categorize_rule_based(file_paths)
        
        elif self.options.method == CategorizationMethod.HYBRID:
            return self._categorize_hybrid(file_paths, training_data)
        
        else:
            logger.error(f"Unsupported categorization method: {self.options.method}")
            return CategorizationResult(
                file_paths=file_paths,
                category_assignments=[],
                categories=self.categories,
                method=self.options.method,
                algorithm=self.options.algorithm,
                metadata={"error": f"Unsupported categorization method: {self.options.method}"}
            )
    
    def _initialize_categories(self):
        """Initialize categories based on the selected scheme."""
        if self.options.category_scheme == CategoryScheme.DOCUMENT_TYPE:
            self.categories = {
                "pdf": Category(id="pdf", name="PDF Document", 
                              keywords=["pdf", "document", "portable document format"]),
                "docx": Category(id="docx", name="Word Document", 
                               keywords=["docx", "doc", "word", "microsoft word"]),
                "xlsx": Category(id="xlsx", name="Excel Spreadsheet", 
                               keywords=["xlsx", "xls", "excel", "spreadsheet"]),
                "pptx": Category(id="pptx", name="PowerPoint Presentation", 
                               keywords=["pptx", "ppt", "powerpoint", "presentation"]),
                "txt": Category(id="txt", name="Text File", 
                              keywords=["txt", "text", "plain text"]),
                "csv": Category(id="csv", name="CSV File", 
                              keywords=["csv", "comma separated", "tabular data"]),
                "json": Category(id="json", name="JSON File", 
                               keywords=["json", "javascript object notation"]),
                "xml": Category(id="xml", name="XML File", 
                              keywords=["xml", "extensible markup language"]),
                "html": Category(id="html", name="HTML File", 
                               keywords=["html", "hypertext markup language", "web page"]),
                "md": Category(id="md", name="Markdown File", 
                             keywords=["md", "markdown", "markup language"]),
                "other": Category(id="other", name="Other Document Type", 
                                keywords=["other", "unknown"])
            }
        
        elif self.options.category_scheme == CategoryScheme.CONTENT_TYPE:
            self.categories = {
                "text": Category(id="text", name="Text Content", 
                               keywords=["text", "document", "article", "report"]),
                "image": Category(id="image", name="Image Content", 
                                keywords=["image", "picture", "photo", "graphic"]),
                "audio": Category(id="audio", name="Audio Content", 
                                keywords=["audio", "sound", "music", "recording"]),
                "video": Category(id="video", name="Video Content", 
                                keywords=["video", "movie", "film", "recording"]),
                "data": Category(id="data", name="Data Content", 
                               keywords=["data", "dataset", "database", "statistics"]),
                "code": Category(id="code", name="Code Content", 
                               keywords=["code", "program", "script", "source"]),
                "mixed": Category(id="mixed", name="Mixed Content", 
                                keywords=["mixed", "multiple", "composite"]),
                "other": Category(id="other", name="Other Content Type", 
                                keywords=["other", "unknown"])
            }
        
        elif self.options.category_scheme == CategoryScheme.SUBJECT_AREA:
            self.categories = {
                "science": Category(id="science", name="Science", 
                                  keywords=["science", "scientific", "research"]),
                "engineering": Category(id="engineering", name="Engineering", 
                                      keywords=["engineering", "engineer", "technical"]),
                "medicine": Category(id="medicine", name="Medicine", 
                                   keywords=["medicine", "medical", "health", "clinical"]),
                "business": Category(id="business", name="Business", 
                                   keywords=["business", "finance", "management", "marketing"]),
                "arts": Category(id="arts", name="Arts and Humanities", 
                               keywords=["art", "humanities", "literature", "philosophy"]),
                "social": Category(id="social", name="Social Sciences", 
                                 keywords=["social", "psychology", "sociology", "economics"]),
                "computer": Category(id="computer", name="Computer Science", 
                                   keywords=["computer", "computing", "software", "programming"]),
                "math": Category(id="math", name="Mathematics", 
                               keywords=["math", "mathematics", "statistical", "calculation"]),
                "physics": Category(id="physics", name="Physics", 
                                  keywords=["physics", "physical", "quantum", "mechanics"]),
                "chemistry": Category(id="chemistry", name="Chemistry", 
                                    keywords=["chemistry", "chemical", "molecule", "compound"]),
                "biology": Category(id="biology", name="Biology", 
                                  keywords=["biology", "biological", "cell", "organism"]),
                "other": Category(id="other", name="Other Subject Area", 
                                keywords=["other", "unknown"])
            }
        
        elif self.options.category_scheme == CategoryScheme.FILE_PURPOSE:
            self.categories = {
                "data": Category(id="data", name="Data File", 
                               keywords=["data", "dataset", "raw data", "measurements"]),
                "report": Category(id="report", name="Report", 
                                 keywords=["report", "analysis", "findings", "results"]),
                "presentation": Category(id="presentation", name="Presentation", 
                                       keywords=["presentation", "slides", "talk"]),
                "documentation": Category(id="documentation", name="Documentation", 
                                        keywords=["documentation", "manual", "guide", "reference"]),
                "code": Category(id="code", name="Code", 
                               keywords=["code", "script", "program", "source"]),
                "notes": Category(id="notes", name="Notes", 
                                keywords=["notes", "memo", "minutes", "meeting"]),
                "paper": Category(id="paper", name="Research Paper", 
                                keywords=["paper", "article", "publication", "journal"]),
                "proposal": Category(id="proposal", name="Proposal", 
                                   keywords=["proposal", "plan", "project", "grant"]),
                "other": Category(id="other", name="Other Purpose", 
                                keywords=["other", "unknown"])
            }
        
        else:  # CategoryScheme.CUSTOM or other
            # Use empty dictionary for custom scheme
            if not self.categories:
                self.categories = {}
    
    def _categorize_supervised(self, file_paths: List[str], 
                             training_data: Dict[str, List[str]]) -> CategorizationResult:
        """
        Categorize files using supervised learning.
        
        Args:
            file_paths: List of file paths to categorize
            training_data: Dictionary mapping category IDs to lists of file paths
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        try:
            # Prepare training data
            train_files = []
            train_labels = []
            
            for category_id, category_files in training_data.items():
                for file_path in category_files:
                    train_files.append(file_path)
                    train_labels.append(category_id)
            
            # Extract features from training files
            train_features = self._extract_features(train_files)
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y_train = self.label_encoder.fit_transform(train_labels)
            
            # Split into training and validation sets
            X_train, X_val, y_train, y_val = train_test_split(
                train_features, y_train, 
                test_size=self.options.test_size, 
                random_state=self.options.random_state
            )
            
            # Train model based on selected algorithm
            if self.options.algorithm == CategorizationAlgorithm.NAIVE_BAYES:
                self.model = MultinomialNB()
            elif self.options.algorithm == CategorizationAlgorithm.RANDOM_FOREST:
                self.model = RandomForestClassifier(
                    n_estimators=100, 
                    random_state=self.options.random_state
                )
            elif self.options.algorithm == CategorizationAlgorithm.SVM:
                from sklearn.svm import SVC
                self.model = SVC(
                    probability=True, 
                    random_state=self.options.random_state
                )
            else:
                logger.warning(f"Unsupported algorithm for supervised learning: {self.options.algorithm}")
                logger.warning("Falling back to Naive Bayes")
                self.model = MultinomialNB()
            
            # Train the model
            self.model.fit(X_train, y_train)
            
            # Evaluate on validation set
            y_pred = self.model.predict(X_val)
            accuracy = accuracy_score(y_val, y_pred)
            report = classification_report(y_val, y_pred, target_names=self.label_encoder.classes_, output_dict=True)
            
            # Extract features from files to categorize
            features = self._extract_features(file_paths)
            
            # Predict categories
            y_pred = self.model.predict(features)
            y_prob = self.model.predict_proba(features)
            
            # Create category assignments
            category_assignments = []
            for i, file_path in enumerate(file_paths):
                category_id = self.label_encoder.inverse_transform([y_pred[i]])[0]
                
                # Get confidence score
                category_idx = list(self.label_encoder.classes_).index(category_id)
                confidence = y_prob[i, category_idx]
                
                if confidence >= self.options.min_confidence:
                    category_assignments.append(CategoryAssignment(
                        file_path=file_path,
                        category_id=category_id,
                        confidence=confidence,
                        method=CategorizationMethod.SUPERVISED,
                        algorithm=self.options.algorithm
                    ))
                
                # Check for additional categories if max_categories_per_file > 1
                if self.options.max_categories_per_file > 1:
                    # Get top categories by probability
                    top_indices = np.argsort(y_prob[i])[::-1]
                    
                    # Skip the first one (already added)
                    for j in range(1, min(self.options.max_categories_per_file, len(top_indices))):
                        idx = top_indices[j]
                        category_id = self.label_encoder.classes_[idx]
                        confidence = y_prob[i, idx]
                        
                        if confidence >= self.options.min_confidence:
                            category_assignments.append(CategoryAssignment(
                                file_path=file_path,
                                category_id=category_id,
                                confidence=confidence,
                                method=CategorizationMethod.SUPERVISED,
                                algorithm=self.options.algorithm
                            ))
            
            return CategorizationResult(
                file_paths=file_paths,
                category_assignments=category_assignments,
                categories=self.categories,
                method=CategorizationMethod.SUPERVISED,
                algorithm=self.options.algorithm,
                model=self.model,
                metadata={
                    "accuracy": accuracy,
                    "classification_report": report,
                    "num_training_files": len(train_files),
                    "num_categories": len(self.label_encoder.classes_)
                }
            )
        
        except Exception as e:
            logger.error(f"Error in supervised categorization: {e}")
            return CategorizationResult(
                file_paths=file_paths,
                category_assignments=[],
                categories=self.categories,
                method=CategorizationMethod.SUPERVISED,
                algorithm=self.options.algorithm,
                metadata={"error": str(e)}
            )
    
    def _categorize_unsupervised(self, file_paths: List[str]) -> CategorizationResult:
        """
        Categorize files using unsupervised learning.
        
        Args:
            file_paths: List of file paths to categorize
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        try:
            if self.options.algorithm == CategorizationAlgorithm.KMEANS:
                return self._categorize_kmeans(file_paths)
            elif self.options.algorithm == CategorizationAlgorithm.TOPIC_BASED:
                return self._categorize_topic_based(file_paths)
            elif self.options.algorithm == CategorizationAlgorithm.KEYWORD_BASED:
                return self._categorize_keyword_based(file_paths)
            else:
                logger.warning(f"Unsupported algorithm for unsupervised learning: {self.options.algorithm}")
                logger.warning("Falling back to K-means clustering")
                return self._categorize_kmeans(file_paths)
        
        except Exception as e:
            logger.error(f"Error in unsupervised categorization: {e}")
            return CategorizationResult(
                file_paths=file_paths,
                category_assignments=[],
                categories=self.categories,
                method=CategorizationMethod.UNSUPERVISED,
                algorithm=self.options.algorithm,
                metadata={"error": str(e)}
            )
    
    def _categorize_kmeans(self, file_paths: List[str]) -> CategorizationResult:
        """
        Categorize files using K-means clustering.
        
        Args:
            file_paths: List of file paths to categorize
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        # Extract features
        features = self._extract_features(file_paths)
        
        # Apply K-means clustering
        kmeans = KMeans(
            n_clusters=self.options.num_clusters,
            random_state=self.options.random_state
        )
        clusters = kmeans.fit_predict(features)
        
        # Calculate distances to cluster centers for confidence scores
        distances = kmeans.transform(features)
        
        # Create dynamic categories based on clusters
        self.categories = {}
        for i in range(self.options.num_clusters):
            # Get files in this cluster
            cluster_files = [file_paths[j] for j in range(len(file_paths)) if clusters[j] == i]
            
            # Extract keywords from cluster files to characterize the cluster
            cluster_keywords = self._extract_cluster_keywords(cluster_files)
            
            # Create category
            category_id = f"cluster_{i}"
            self.categories[category_id] = Category(
                id=category_id,
                name=f"Cluster {i}",
                description=f"Automatically generated cluster {i}",
                keywords=[kw for kw, _ in cluster_keywords[:5]]
            )
        
        # Create category assignments
        category_assignments = []
        for i, file_path in enumerate(file_paths):
            cluster_id = clusters[i]
            category_id = f"cluster_{cluster_id}"
            
            # Calculate confidence score (inverse of normalized distance)
            distance = distances[i, cluster_id]
            max_distance = np.max(distances[:, cluster_id])
            confidence = 1.0 - (distance / max_distance if max_distance > 0 else 0)
            
            if confidence >= self.options.min_confidence:
                category_assignments.append(CategoryAssignment(
                    file_path=file_path,
                    category_id=category_id,
                    confidence=confidence,
                    method=CategorizationMethod.UNSUPERVISED,
                    algorithm=CategorizationAlgorithm.KMEANS
                ))
        
        return CategorizationResult(
            file_paths=file_paths,
            category_assignments=category_assignments,
            categories=self.categories,
            method=CategorizationMethod.UNSUPERVISED,
            algorithm=CategorizationAlgorithm.KMEANS,
            model=kmeans,
            metadata={
                "inertia": kmeans.inertia_,
                "num_clusters": self.options.num_clusters,
                "cluster_sizes": {i: np.sum(clusters == i) for i in range(self.options.num_clusters)}
            }
        )
    
    def _categorize_topic_based(self, file_paths: List[str]) -> CategorizationResult:
        """
        Categorize files based on topics.
        
        Args:
            file_paths: List of file paths to categorize
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        # Create topic modeling options
        topic_options = TopicModelingOptions(
            method=self.options.topic_method,
            num_topics=self.options.num_topics,
            text_extraction_options=self.options.text_extraction_options
        )
        
        # Extract topics
        modeler = TopicModeler(topic_options)
        topic_result = modeler.extract_topics_from_files(file_paths)
        
        if not topic_result.topics:
            logger.warning("No topics extracted")
            return CategorizationResult(
                file_paths=file_paths,
                category_assignments=[],
                categories=self.categories,
                method=CategorizationMethod.UNSUPERVISED,
                algorithm=CategorizationAlgorithm.TOPIC_BASED,
                metadata={"error": "No topics extracted"}
            )
        
        # Create categories based on topics
        self.categories = {}
        for topic in topic_result.topics:
            category_id = f"topic_{topic.id}"
            
            # Get keywords as strings
            keywords = [word for word, _ in topic.keywords]
            
            self.categories[category_id] = Category(
                id=category_id,
                name=f"Topic {topic.id}",
                description=f"Automatically generated topic {topic.id}",
                keywords=keywords
            )
        
        # Create category assignments
        category_assignments = []
        
        if topic_result.document_topics:
            for i, file_path in enumerate(file_paths):
                if i < len(topic_result.document_topics):
                    doc_topics = topic_result.document_topics[i]
                    
                    # Assign categories based on topic probabilities
                    for j, (topic_id, probability) in enumerate(doc_topics):
                        if j >= self.options.max_categories_per_file:
                            break
                        
                        category_id = f"topic_{topic_id}"
                        
                        if probability >= self.options.min_confidence:
                            category_assignments.append(CategoryAssignment(
                                file_path=file_path,
                                category_id=category_id,
                                confidence=probability,
                                method=CategorizationMethod.UNSUPERVISED,
                                algorithm=CategorizationAlgorithm.TOPIC_BASED
                            ))
        
        return CategorizationResult(
            file_paths=file_paths,
            category_assignments=category_assignments,
            categories=self.categories,
            method=CategorizationMethod.UNSUPERVISED,
            algorithm=CategorizationAlgorithm.TOPIC_BASED,
            model=topic_result.model,
            metadata={
                "num_topics": len(topic_result.topics),
                "coherence_score": topic_result.coherence_score,
                "perplexity": topic_result.perplexity
            }
        )
    
    def _categorize_keyword_based(self, file_paths: List[str]) -> CategorizationResult:
        """
        Categorize files based on keywords.
        
        Args:
            file_paths: List of file paths to categorize
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        # Extract keywords from each file
        file_keywords = {}
        for file_path in file_paths:
            try:
                keywords = extract_keywords_from_file(
                    file_path,
                    method=self.options.keyword_method,
                    num_keywords=self.options.num_keywords
                )
                file_keywords[file_path] = keywords
            except Exception as e:
                logger.error(f"Error extracting keywords from {file_path}: {e}")
        
        # If no predefined categories, create them based on common keywords
        if not self.categories:
            self._create_categories_from_keywords(file_keywords)
        
        # Create category assignments
        category_assignments = []
        
        for file_path, keywords in file_keywords.items():
            # Calculate similarity to each category
            category_scores = {}
            
            for category_id, category in self.categories.items():
                score = self._calculate_keyword_category_similarity(keywords, category)
                category_scores[category_id] = score
            
            # Sort categories by score
            sorted_categories = sorted(
                category_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Assign top categories
            for i, (category_id, score) in enumerate(sorted_categories):
                if i >= self.options.max_categories_per_file:
                    break
                
                if score >= self.options.min_confidence:
                    category_assignments.append(CategoryAssignment(
                        file_path=file_path,
                        category_id=category_id,
                        confidence=score,
                        method=CategorizationMethod.UNSUPERVISED,
                        algorithm=CategorizationAlgorithm.KEYWORD_BASED
                    ))
        
        return CategorizationResult(
            file_paths=file_paths,
            category_assignments=category_assignments,
            categories=self.categories,
            method=CategorizationMethod.UNSUPERVISED,
            algorithm=CategorizationAlgorithm.KEYWORD_BASED,
            metadata={
                "num_categories": len(self.categories),
                "files_with_keywords": len(file_keywords)
            }
        )
    
    def _create_categories_from_keywords(self, file_keywords: Dict[str, List[Tuple[str, float]]]):
        """
        Create categories based on common keywords across files.
        
        Args:
            file_keywords: Dictionary mapping file paths to lists of (keyword, score) tuples
        """
        # Collect all keywords
        all_keywords = []
        for keywords in file_keywords.values():
            all_keywords.extend([kw for kw, _ in keywords])
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Use most common keywords as category seeds
        num_categories = min(self.options.num_clusters, len(keyword_counts))
        common_keywords = keyword_counts.most_common(num_categories)
        
        # Create categories
        self.categories = {}
        for i, (keyword, count) in enumerate(common_keywords):
            category_id = f"keyword_{i}"
            self.categories[category_id] = Category(
                id=category_id,
                name=f"Category: {keyword}",
                description=f"Automatically generated category based on keyword '{keyword}'",
                keywords=[keyword]
            )
    
    def _calculate_keyword_category_similarity(self, 
                                             keywords: List[Tuple[str, float]], 
                                             category: Category) -> float:
        """
        Calculate similarity between keywords and a category.
        
        Args:
            keywords: List of (keyword, score) tuples
            category: Category to compare against
            
        Returns:
            Similarity score between 0 and 1
        """
        if not keywords or not category.keywords:
            return 0.0
        
        # Extract keyword texts and scores
        keyword_dict = {kw: score for kw, score in keywords}
        
        # Calculate similarity based on keyword overlap
        total_score = 0.0
        matches = 0
        
        for cat_keyword in category.keywords:
            # Check for exact matches
            if cat_keyword in keyword_dict:
                total_score += keyword_dict[cat_keyword]
                matches += 1
                continue
            
            # Check for partial matches
            for kw in keyword_dict:
                if cat_keyword in kw or kw in cat_keyword:
                    total_score += keyword_dict[kw] * 0.5  # Half weight for partial matches
                    matches += 0.5
                    break
        
        # Normalize score
        if matches > 0:
            return total_score / matches
        else:
            return 0.0
    
    def _categorize_rule_based(self, file_paths: List[str]) -> CategorizationResult:
        """
        Categorize files using rule-based approach.
        
        Args:
            file_paths: List of file paths to categorize
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        # Ensure categories are initialized
        if not self.categories:
            logger.warning("No categories defined for rule-based categorization")
            return CategorizationResult(
                file_paths=file_paths,
                category_assignments=[],
                categories={},
                method=CategorizationMethod.RULE_BASED,
                algorithm=CategorizationAlgorithm.CUSTOM,
                metadata={"error": "No categories defined"}
            )
        
        # Apply rules to each file
        category_assignments = []
        
        for file_path in file_paths:
            # Extract file metadata
            file_metadata = self._extract_file_metadata(file_path)
            
            # Apply rules for each category
            for category_id, category in self.categories.items():
                if not category.rules:
                    continue
                
                # Check if file matches the category rules
                match, confidence = self._apply_category_rules(file_path, file_metadata, category)
                
                if match and confidence >= self.options.min_confidence:
                    category_assignments.append(CategoryAssignment(
                        file_path=file_path,
                        category_id=category_id,
                        confidence=confidence,
                        method=CategorizationMethod.RULE_BASED,
                        algorithm=CategorizationAlgorithm.CUSTOM
                    ))
        
        return CategorizationResult(
            file_paths=file_paths,
            category_assignments=category_assignments,
            categories=self.categories,
            method=CategorizationMethod.RULE_BASED,
            algorithm=CategorizationAlgorithm.CUSTOM,
            metadata={
                "num_categories": len(self.categories),
                "num_assignments": len(category_assignments)
            }
        )
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "extension": os.path.splitext(file_path)[1].lower().lstrip('.'),
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "directory": os.path.dirname(file_path)
        }
        
        # Try to extract text and get additional metadata
        try:
            text_result = extract_text_from_file(
                file_path, 
                options=self.options.text_extraction_options
            )
            if text_result:
                metadata.update(text_result.metadata)
                
                # Add text length
                if text_result.text:
                    metadata["text_length"] = len(text_result.text)
                    metadata["word_count"] = len(text_result.text.split())
        except Exception as e:
            logger.warning(f"Error extracting text metadata from {file_path}: {e}")
        
        return metadata
    
    def _apply_category_rules(self, file_path: str, 
                            file_metadata: Dict[str, Any], 
                            category: Category) -> Tuple[bool, float]:
        """
        Apply category rules to a file.
        
        Args:
            file_path: Path to the file
            file_metadata: File metadata
            category: Category to check
            
        Returns:
            Tuple of (match, confidence)
        """
        if not category.rules:
            return False, 0.0
        
        # Track rule matches and confidences
        rule_matches = 0
        total_confidence = 0.0
        
        for rule_type, rule_value in category.rules.items():
            if rule_type == "extension":
                # Check file extension
                if file_metadata.get("extension") == rule_value:
                    rule_matches += 1
                    total_confidence += 1.0
            
            elif rule_type == "filename_contains":
                # Check if filename contains the value
                if rule_value.lower() in file_metadata.get("filename", "").lower():
                    rule_matches += 1
                    total_confidence += 0.8
            
            elif rule_type == "size_range":
                # Check if file size is within range
                min_size, max_size = rule_value
                size = file_metadata.get("size", 0)
                if min_size <= size <= max_size:
                    rule_matches += 1
                    total_confidence += 0.7
            
            elif rule_type == "keyword_match":
                # Check if file contains keywords
                try:
                    keywords = extract_keywords_from_file(
                        file_path,
                        method=self.options.keyword_method,
                        num_keywords=20  # Get more keywords for better matching
                    )
                    
                    keyword_texts = [kw for kw, _ in keywords]
                    matches = [kw for kw in rule_value if kw.lower() in keyword_texts]
                    
                    if matches:
                        match_ratio = len(matches) / len(rule_value)
                        rule_matches += 1
                        total_confidence += 0.9 * match_ratio
                except Exception as e:
                    logger.warning(f"Error checking keyword match for {file_path}: {e}")
            
            elif rule_type == "content_contains":
                # Check if file content contains the value
                try:
                    text_result = extract_text_from_file(
                        file_path, 
                        options=self.options.text_extraction_options
                    )
                    if text_result and text_result.text:
                        if rule_value.lower() in text_result.text.lower():
                            rule_matches += 1
                            total_confidence += 0.6
                except Exception as e:
                    logger.warning(f"Error checking content for {file_path}: {e}")
            
            elif rule_type == "custom_function":
                # Apply custom function
                if callable(rule_value):
                    try:
                        result, confidence = rule_value(file_path, file_metadata)
                        if result:
                            rule_matches += 1
                            total_confidence += confidence
                    except Exception as e:
                        logger.warning(f"Error applying custom function for {file_path}: {e}")
        
        # Calculate overall confidence
        if rule_matches > 0:
            avg_confidence = total_confidence / rule_matches
            return True, avg_confidence
        else:
            return False, 0.0
    
    def _categorize_hybrid(self, file_paths: List[str], 
                         training_data: Optional[Dict[str, List[str]]] = None) -> CategorizationResult:
        """
        Categorize files using a hybrid approach.
        
        Args:
            file_paths: List of file paths to categorize
            training_data: Dictionary mapping category IDs to lists of file paths (for supervised methods)
            
        Returns:
            CategorizationResult object containing the categorization results
        """
        # First try rule-based categorization
        rule_result = self._categorize_rule_based(file_paths)
        
        # Get files that weren't categorized by rules
        categorized_files = set(a.file_path for a in rule_result.category_assignments)
        uncategorized_files = [f for f in file_paths if f not in categorized_files]
        
        # If we have training data, use supervised learning for remaining files
        if training_data and uncategorized_files:
            # Save current categories
            rule_categories = self.categories.copy()
            
            # Categorize using supervised learning
            supervised_result = self._categorize_supervised(uncategorized_files, training_data)
            
            # Merge categories
            self.categories.update(supervised_result.categories)
            
            # Merge category assignments
            category_assignments = rule_result.category_assignments + supervised_result.category_assignments
        
        # Otherwise use unsupervised learning
        elif uncategorized_files:
            # Save current categories
            rule_categories = self.categories.copy()
            
            # Categorize using unsupervised learning
            unsupervised_result = self._categorize_unsupervised(uncategorized_files)
            
            # Merge categories
            self.categories.update(unsupervised_result.categories)
            
            # Merge category assignments
            category_assignments = rule_result.category_assignments + unsupervised_result.category_assignments
        
        else:
            # All files were categorized by rules
            category_assignments = rule_result.category_assignments
        
        return CategorizationResult(
            file_paths=file_paths,
            category_assignments=category_assignments,
            categories=self.categories,
            method=CategorizationMethod.HYBRID,
            algorithm=CategorizationAlgorithm.CUSTOM,
            metadata={
                "num_categories": len(self.categories),
                "num_assignments": len(category_assignments),
                "rule_based_assignments": len(rule_result.category_assignments),
                "other_assignments": len(category_assignments) - len(rule_result.category_assignments)
            }
        )
    
    def _extract_features(self, file_paths: List[str]) -> np.ndarray:
        """
        Extract features from files for categorization.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Feature matrix
        """
        # Extract text from files
        texts = []
        valid_files = []
        
        for file_path in file_paths:
            try:
                text_result = extract_text_from_file(
                    file_path, 
                    options=self.options.text_extraction_options
                )
                if text_result and text_result.text:
                    texts.append(text_result.text)
                    valid_files.append(file_path)
                else:
                    logger.warning(f"Could not extract text from file: {file_path}")
                    # Use empty text as fallback
                    texts.append("")
                    valid_files.append(file_path)
            except Exception as e:
                logger.error(f"Error extracting text from file {file_path}: {e}")
                # Use empty text as fallback
                texts.append("")
                valid_files.append(file_path)
        
        # Create TF-IDF features
        if not hasattr(self, 'vectorizer') or self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=self.options.max_features,
                ngram_range=self.options.ngram_range,
                stop_words='english'
            )
            features = self.vectorizer.fit_transform(texts).toarray()
        else:
            features = self.vectorizer.transform(texts).toarray()
        
        return features
    
    def _extract_cluster_keywords(self, file_paths: List[str]) -> List[Tuple[str, float]]:
        """
        Extract keywords that characterize a cluster of files.
        
        Args:
            file_paths: List of file paths in the cluster
            
        Returns:
            List of (keyword, score) tuples
        """
        if not file_paths:
            return []
        
        # Extract text from files
        texts = []
        for file_path in file_paths:
            try:
                text_result = extract_text_from_file(
                    file_path, 
                    options=self.options.text_extraction_options
                )
                if text_result and text_result.text:
                    texts.append(text_result.text)
            except Exception as e:
                logger.error(f"Error extracting text from file {file_path}: {e}")
        
        if not texts:
            return []
        
        # Combine texts
        combined_text = " ".join(texts)
        
        # Extract keywords
        keywords = extract_keywords(
            combined_text,
            method=self.options.keyword_method,
            num_keywords=10
        )
        
        return keywords
    
    def add_category(self, category: Category):
        """
        Add a new category to the categorizer.
        
        Args:
            category: Category to add
        """
        self.categories[category.id] = category
    
    def remove_category(self, category_id: str):
        """
        Remove a category from the categorizer.
        
        Args:
            category_id: ID of the category to remove
        """
        if category_id in self.categories:
            del self.categories[category_id]
    
    def categorize_file(self, file_path: str) -> List[CategoryAssignment]:
        """
        Categorize a single file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of CategoryAssignment objects
        """
        result = self.categorize_files([file_path])
        return result.category_assignments


def categorize_files(file_paths: List[str], 
                   method: CategorizationMethod = CategorizationMethod.UNSUPERVISED,
                   algorithm: CategorizationAlgorithm = CategorizationAlgorithm.TOPIC_BASED,
                   **kwargs) -> CategorizationResult:
    """
    Categorize a list of files.
    
    Args:
        file_paths: List of file paths to categorize
        method: Categorization method to use
        algorithm: Categorization algorithm to use
        **kwargs: Additional options for categorization
        
    Returns:
        CategorizationResult object containing the categorization results
    """
    options = CategorizationOptions(
        method=method,
        algorithm=algorithm,
        **kwargs
    )
    
    categorizer = FileCategorizer(options)
    return categorizer.categorize_files(file_paths)


def categorize_file(file_path: str,
                  method: CategorizationMethod = CategorizationMethod.UNSUPERVISED,
                  algorithm: CategorizationAlgorithm = CategorizationAlgorithm.TOPIC_BASED,
                  **kwargs) -> List[CategoryAssignment]:
    """
    Categorize a single file.
    
    Args:
        file_path: Path to the file
        method: Categorization method to use
        algorithm: Categorization algorithm to use
        **kwargs: Additional options for categorization
        
    Returns:
        List of CategoryAssignment objects
    """
    options = CategorizationOptions(
        method=method,
        algorithm=algorithm,
        **kwargs
    )
    
    categorizer = FileCategorizer(options)
    result = categorizer.categorize_files([file_path])
    return result.category_assignments


def suggest_categories_for_files(file_paths: List[str], 
                               num_categories: int = 5) -> Dict[str, List[str]]:
    """
    Suggest categories for a list of files.
    
    Args:
        file_paths: List of file paths
        num_categories: Number of categories to suggest
        
    Returns:
        Dictionary mapping category names to lists of file paths
    """
    # Use topic-based categorization to suggest categories
    options = CategorizationOptions(
        method=CategorizationMethod.UNSUPERVISED,
        algorithm=CategorizationAlgorithm.TOPIC_BASED,
        num_topics=num_categories
    )
    
    categorizer = FileCategorizer(options)
    result = categorizer.categorize_files(file_paths)
    
    # Group files by category
    categories = {}
    for category_id, category in result.categories.items():
        categories[category.name] = result.get_files_in_category(category_id)
    
    return categories


def create_category_hierarchy(categories: Dict[str, Category]) -> Dict[str, List[str]]:
    """
    Create a hierarchy of categories.
    
    Args:
        categories: Dictionary mapping category IDs to Category objects
        
    Returns:
        Dictionary mapping parent category IDs to lists of child category IDs
    """
    hierarchy = {}
    
    # Find root categories (those without parents)
    root_categories = [cat_id for cat_id, cat in categories.items() if not cat.parent_id]
    
    # Initialize hierarchy with root categories
    for cat_id in root_categories:
        hierarchy[cat_id] = []
    
    # Add child categories
    for cat_id, cat in categories.items():
        if cat.parent_id:
            if cat.parent_id in hierarchy:
                hierarchy[cat.parent_id].append(cat_id)
            else:
                hierarchy[cat.parent_id] = [cat_id]
    
    return hierarchy
"""
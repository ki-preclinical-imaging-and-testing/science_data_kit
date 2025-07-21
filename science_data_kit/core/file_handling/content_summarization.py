"""
Content summarization module for generating summaries of document content.

This module provides functionality for generating summaries of document content
using various summarization techniques, including extractive and abstractive methods.
It builds on the text_extraction module to extract text from various file types
and then applies summarization algorithms to generate concise summaries.

The module includes:
- Extractive summarization using statistical methods
- Abstractive summarization using machine learning models
- Multi-document summarization
- Summary evaluation metrics
- Customizable summarization parameters
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions,
    TextExtractionResult,
    extract_text_from_file
)

logger = logging.getLogger(__name__)


class SummarizationMethod(Enum):
    """Enumeration of summarization methods."""
    TFIDF = "tfidf"  # TF-IDF based extractive summarization
    TEXTRANK = "textrank"  # TextRank algorithm for extractive summarization
    LSA = "lsa"  # Latent Semantic Analysis for extractive summarization
    TRANSFORMER = "transformer"  # Transformer-based abstractive summarization
    CUSTOM = "custom"  # Custom summarization method


@dataclass
class SummarizationOptions:
    """Options for content summarization."""
    # General options
    method: SummarizationMethod = SummarizationMethod.TFIDF
    max_sentences: int = 5
    min_sentence_length: int = 10
    max_sentence_length: int = 200
    language: str = "english"
    
    # TF-IDF specific options
    tfidf_ngram_range: Tuple[int, int] = (1, 2)
    tfidf_min_df: int = 1
    tfidf_max_df: float = 0.9
    
    # TextRank specific options
    textrank_window_size: int = 4
    textrank_damping_factor: float = 0.85
    textrank_convergence_threshold: float = 0.0001
    textrank_max_iterations: int = 100
    
    # LSA specific options
    lsa_n_components: int = 5
    
    # Transformer specific options
    transformer_model: str = "t5-small"
    transformer_min_length: int = 50
    transformer_max_length: int = 200
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class SummarizationResult:
    """Result of content summarization."""
    original_text: str
    summary: str
    method: SummarizationMethod
    sentences: List[str] = field(default_factory=list)
    sentence_scores: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the summarization result."""
        return f"Summary ({self.method.value}):\n{self.summary}"


class ContentSummarizer:
    """Class for summarizing document content."""
    
    def __init__(self, options: Optional[SummarizationOptions] = None):
        """
        Initialize the content summarizer.
        
        Args:
            options: Summarization options
        """
        self.options = options or SummarizationOptions()
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> Set[str]:
        """
        Load stopwords for the specified language.
        
        Returns:
            Set of stopwords
        """
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words(self.options.language))
        except (ImportError, LookupError):
            logger.warning(f"NLTK stopwords not available for language '{self.options.language}'. Using a minimal set.")
            # Minimal set of English stopwords
            return {
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
                'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during',
                'to', 'from', 'in', 'on', 'by', 'at', 'with', 'between', 'after', 'before',
                'without', 'under', 'over', 'again', 'further', 'then', 'once', 'here',
                'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
                'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
                'just', 'should', 'now'
            }
    
    def summarize(self, text: str) -> SummarizationResult:
        """
        Summarize text content.
        
        Args:
            text: Text to summarize
            
        Returns:
            SummarizationResult object containing the summary
        """
        if not text:
            logger.warning("Empty text provided for summarization")
            return SummarizationResult(
                original_text="",
                summary="",
                method=self.options.method
            )
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        # Filter sentences by length
        filtered_sentences = []
        for sentence in sentences:
            if self.options.min_sentence_length <= len(sentence) <= self.options.max_sentence_length:
                filtered_sentences.append(sentence)
        
        if not filtered_sentences:
            logger.warning("No valid sentences found for summarization")
            return SummarizationResult(
                original_text=text,
                summary="",
                method=self.options.method
            )
        
        # Apply summarization method
        if self.options.method == SummarizationMethod.TFIDF:
            return self._summarize_tfidf(text, filtered_sentences)
        elif self.options.method == SummarizationMethod.TEXTRANK:
            return self._summarize_textrank(text, filtered_sentences)
        elif self.options.method == SummarizationMethod.LSA:
            return self._summarize_lsa(text, filtered_sentences)
        elif self.options.method == SummarizationMethod.TRANSFORMER:
            return self._summarize_transformer(text)
        else:
            logger.warning(f"Unsupported summarization method: {self.options.method}")
            return SummarizationResult(
                original_text=text,
                summary="",
                method=self.options.method
            )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        try:
            from nltk.tokenize import sent_tokenize
            return sent_tokenize(text, language=self.options.language)
        except (ImportError, LookupError):
            logger.warning("NLTK sentence tokenizer not available. Using a simple sentence splitter.")
            # Simple sentence splitting
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _summarize_tfidf(self, text: str, sentences: List[str]) -> SummarizationResult:
        """
        Summarize text using TF-IDF based extractive summarization.
        
        Args:
            text: Original text
            sentences: List of sentences
            
        Returns:
            SummarizationResult object containing the summary
        """
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                ngram_range=self.options.tfidf_ngram_range,
                min_df=self.options.tfidf_min_df,
                max_df=self.options.tfidf_max_df,
                stop_words=self.stopwords
            )
            
            # Create sentence-term matrix
            sentence_vectors = vectorizer.fit_transform(sentences)
            
            # Calculate sentence scores based on the sum of TF-IDF values
            sentence_scores = []
            for i in range(len(sentences)):
                score = sentence_vectors[i].sum()
                sentence_scores.append(float(score))
            
            # Get indices of top sentences
            top_indices = np.argsort(sentence_scores)[::-1][:self.options.max_sentences]
            
            # Sort indices by position in the original text
            top_indices = sorted(top_indices)
            
            # Create summary by joining top sentences
            summary_sentences = [sentences[i] for i in top_indices]
            summary = " ".join(summary_sentences)
            
            return SummarizationResult(
                original_text=text,
                summary=summary,
                method=SummarizationMethod.TFIDF,
                sentences=sentences,
                sentence_scores=sentence_scores,
                metadata={
                    "num_sentences": len(sentences),
                    "summary_sentences": len(summary_sentences),
                    "compression_ratio": len(summary) / len(text) if text else 0
                }
            )
        
        except Exception as e:
            logger.error(f"Error in TF-IDF summarization: {e}")
            return SummarizationResult(
                original_text=text,
                summary="",
                method=SummarizationMethod.TFIDF,
                metadata={"error": str(e)}
            )
    
    def _summarize_textrank(self, text: str, sentences: List[str]) -> SummarizationResult:
        """
        Summarize text using TextRank algorithm.
        
        Args:
            text: Original text
            sentences: List of sentences
            
        Returns:
            SummarizationResult object containing the summary
        """
        try:
            # Create similarity matrix
            similarity_matrix = self._create_similarity_matrix(sentences)
            
            # Apply TextRank algorithm
            sentence_scores = self._apply_textrank(similarity_matrix)
            
            # Get indices of top sentences
            top_indices = np.argsort(sentence_scores)[::-1][:self.options.max_sentences]
            
            # Sort indices by position in the original text
            top_indices = sorted(top_indices)
            
            # Create summary by joining top sentences
            summary_sentences = [sentences[i] for i in top_indices]
            summary = " ".join(summary_sentences)
            
            return SummarizationResult(
                original_text=text,
                summary=summary,
                method=SummarizationMethod.TEXTRANK,
                sentences=sentences,
                sentence_scores=sentence_scores,
                metadata={
                    "num_sentences": len(sentences),
                    "summary_sentences": len(summary_sentences),
                    "compression_ratio": len(summary) / len(text) if text else 0
                }
            )
        
        except Exception as e:
            logger.error(f"Error in TextRank summarization: {e}")
            return SummarizationResult(
                original_text=text,
                summary="",
                method=SummarizationMethod.TEXTRANK,
                metadata={"error": str(e)}
            )
    
    def _create_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """
        Create a similarity matrix for sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            Similarity matrix
        """
        # Create TF-IDF vectors for sentences
        vectorizer = TfidfVectorizer(stop_words=self.stopwords)
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Calculate cosine similarity between sentences
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        return similarity_matrix
    
    def _apply_textrank(self, similarity_matrix: np.ndarray) -> List[float]:
        """
        Apply TextRank algorithm to the similarity matrix.
        
        Args:
            similarity_matrix: Similarity matrix between sentences
            
        Returns:
            List of sentence scores
        """
        # Initialize scores
        num_sentences = similarity_matrix.shape[0]
        scores = np.ones(num_sentences) / num_sentences
        
        # Apply TextRank algorithm
        for _ in range(self.options.textrank_max_iterations):
            prev_scores = scores.copy()
            
            for i in range(num_sentences):
                # Sum weighted scores from all other sentences
                score_sum = 0.0
                for j in range(num_sentences):
                    if i != j:  # Skip self-loops
                        score_sum += similarity_matrix[i, j] * prev_scores[j]
                
                # Apply damping factor
                scores[i] = (1 - self.options.textrank_damping_factor) + self.options.textrank_damping_factor * score_sum
            
            # Check for convergence
            if np.sum(np.abs(scores - prev_scores)) < self.options.textrank_convergence_threshold:
                break
        
        return scores.tolist()
    
    def _summarize_lsa(self, text: str, sentences: List[str]) -> SummarizationResult:
        """
        Summarize text using Latent Semantic Analysis.
        
        Args:
            text: Original text
            sentences: List of sentences
            
        Returns:
            SummarizationResult object containing the summary
        """
        try:
            from sklearn.decomposition import TruncatedSVD
            
            # Create TF-IDF vectors for sentences
            vectorizer = TfidfVectorizer(stop_words=self.stopwords)
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Apply LSA
            n_components = min(self.options.lsa_n_components, tfidf_matrix.shape[0] - 1, tfidf_matrix.shape[1] - 1)
            if n_components < 1:
                n_components = 1
            
            svd = TruncatedSVD(n_components=n_components)
            lsa_matrix = svd.fit_transform(tfidf_matrix)
            
            # Calculate sentence scores
            sentence_scores = []
            for i in range(len(sentences)):
                # Use the magnitude of the sentence vector in the LSA space
                score = np.sqrt(np.sum(np.square(lsa_matrix[i, :])))
                sentence_scores.append(float(score))
            
            # Get indices of top sentences
            top_indices = np.argsort(sentence_scores)[::-1][:self.options.max_sentences]
            
            # Sort indices by position in the original text
            top_indices = sorted(top_indices)
            
            # Create summary by joining top sentences
            summary_sentences = [sentences[i] for i in top_indices]
            summary = " ".join(summary_sentences)
            
            return SummarizationResult(
                original_text=text,
                summary=summary,
                method=SummarizationMethod.LSA,
                sentences=sentences,
                sentence_scores=sentence_scores,
                metadata={
                    "num_sentences": len(sentences),
                    "summary_sentences": len(summary_sentences),
                    "compression_ratio": len(summary) / len(text) if text else 0,
                    "explained_variance": sum(svd.explained_variance_ratio_)
                }
            )
        
        except Exception as e:
            logger.error(f"Error in LSA summarization: {e}")
            return SummarizationResult(
                original_text=text,
                summary="",
                method=SummarizationMethod.LSA,
                metadata={"error": str(e)}
            )
    
    def _summarize_transformer(self, text: str) -> SummarizationResult:
        """
        Summarize text using transformer-based abstractive summarization.
        
        Args:
            text: Text to summarize
            
        Returns:
            SummarizationResult object containing the summary
        """
        try:
            # Try to import transformers
            from transformers import pipeline
            
            # Create summarization pipeline
            summarizer = pipeline(
                "summarization", 
                model=self.options.transformer_model,
                device=-1  # Use CPU
            )
            
            # Truncate text if it's too long for the model
            max_input_length = 1024  # Most models have a limit
            truncated_text = text[:max_input_length] if len(text) > max_input_length else text
            
            # Generate summary
            summary_output = summarizer(
                truncated_text,
                min_length=self.options.transformer_min_length,
                max_length=self.options.transformer_max_length,
                do_sample=False
            )
            
            # Extract summary text
            summary = summary_output[0]['summary_text'] if summary_output else ""
            
            return SummarizationResult(
                original_text=text,
                summary=summary,
                method=SummarizationMethod.TRANSFORMER,
                metadata={
                    "model": self.options.transformer_model,
                    "truncated": len(text) > max_input_length,
                    "compression_ratio": len(summary) / len(text) if text else 0
                }
            )
        
        except ImportError:
            logger.warning("Transformers library not available. Falling back to TF-IDF summarization.")
            return self._summarize_tfidf(text, self._split_into_sentences(text))
        
        except Exception as e:
            logger.error(f"Error in transformer-based summarization: {e}")
            logger.warning("Falling back to TF-IDF summarization.")
            return self._summarize_tfidf(text, self._split_into_sentences(text))
    
    def summarize_file(self, file_path: str) -> SummarizationResult:
        """
        Summarize the content of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SummarizationResult object containing the summary
        """
        # Extract text from file
        text_extraction_options = self.options.text_extraction_options or TextExtractionOptions()
        
        try:
            text_result = extract_text_from_file(file_path, text_extraction_options)
            if text_result and text_result.text:
                result = self.summarize(text_result.text)
                result.metadata["file_path"] = file_path
                result.metadata.update(text_result.metadata)
                return result
            else:
                logger.warning(f"Could not extract text from file: {file_path}")
                return SummarizationResult(
                    original_text="",
                    summary="",
                    method=self.options.method,
                    metadata={"file_path": file_path, "error": "Text extraction failed"}
                )
        except Exception as e:
            logger.error(f"Error summarizing file {file_path}: {e}")
            return SummarizationResult(
                original_text="",
                summary="",
                method=self.options.method,
                metadata={"file_path": file_path, "error": str(e)}
            )
    
    def summarize_multiple_files(self, file_paths: List[str]) -> SummarizationResult:
        """
        Generate a summary from multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            SummarizationResult object containing the summary
        """
        # Extract text from files
        text_extraction_options = self.options.text_extraction_options or TextExtractionOptions()
        
        all_text = []
        file_metadata = []
        
        for file_path in file_paths:
            try:
                text_result = extract_text_from_file(file_path, text_extraction_options)
                if text_result and text_result.text:
                    all_text.append(text_result.text)
                    file_metadata.append({
                        "file_path": file_path,
                        **text_result.metadata
                    })
                else:
                    logger.warning(f"Could not extract text from file: {file_path}")
            except Exception as e:
                logger.error(f"Error extracting text from file {file_path}: {e}")
        
        if not all_text:
            logger.warning("Could not extract text from any of the provided files")
            return SummarizationResult(
                original_text="",
                summary="",
                method=self.options.method,
                metadata={"file_paths": file_paths, "error": "Text extraction failed for all files"}
            )
        
        # Combine text from all files
        combined_text = "\n\n".join(all_text)
        
        # Summarize combined text
        result = self.summarize(combined_text)
        result.metadata["file_paths"] = file_paths
        result.metadata["file_metadata"] = file_metadata
        result.metadata["num_files"] = len(file_paths)
        
        return result


def summarize_text(text: str, method: SummarizationMethod = SummarizationMethod.TFIDF,
                 max_sentences: int = 5, **kwargs) -> str:
    """
    Summarize text using the specified method.
    
    Args:
        text: Text to summarize
        method: Summarization method to use
        max_sentences: Maximum number of sentences in the summary
        **kwargs: Additional options for summarization
        
    Returns:
        Summary text
    """
    options = SummarizationOptions(
        method=method,
        max_sentences=max_sentences,
        **kwargs
    )
    
    summarizer = ContentSummarizer(options)
    result = summarizer.summarize(text)
    
    return result.summary


def summarize_file(file_path: str, method: SummarizationMethod = SummarizationMethod.TFIDF,
                 max_sentences: int = 5, **kwargs) -> str:
    """
    Summarize the content of a file.
    
    Args:
        file_path: Path to the file
        method: Summarization method to use
        max_sentences: Maximum number of sentences in the summary
        **kwargs: Additional options for summarization
        
    Returns:
        Summary text
    """
    options = SummarizationOptions(
        method=method,
        max_sentences=max_sentences,
        **kwargs
    )
    
    summarizer = ContentSummarizer(options)
    result = summarizer.summarize_file(file_path)
    
    return result.summary


def compare_summarization_methods(text: str, max_sentences: int = 5) -> Dict[str, str]:
    """
    Compare different summarization methods on the same text.
    
    Args:
        text: Text to summarize
        max_sentences: Maximum number of sentences in the summary
        
    Returns:
        Dictionary mapping method names to summaries
    """
    results = {}
    
    for method in SummarizationMethod:
        try:
            summary = summarize_text(text, method=method, max_sentences=max_sentences)
            results[method.value] = summary
        except Exception as e:
            logger.error(f"Error summarizing with {method.value}: {e}")
            results[method.value] = f"Error: {str(e)}"
    
    return results


def evaluate_summary(original_text: str, summary: str) -> Dict[str, float]:
    """
    Evaluate the quality of a summary.
    
    Args:
        original_text: Original text
        summary: Summary text
        
    Returns:
        Dictionary of evaluation metrics
    """
    metrics = {}
    
    # Calculate compression ratio
    metrics["compression_ratio"] = len(summary) / len(original_text) if original_text else 0
    
    # Calculate lexical diversity
    original_words = set(re.findall(r'\b\w+\b', original_text.lower()))
    summary_words = set(re.findall(r'\b\w+\b', summary.lower()))
    
    if original_words:
        metrics["vocabulary_retention"] = len(summary_words) / len(original_words)
    else:
        metrics["vocabulary_retention"] = 0
    
    # Calculate content retention (overlap of important words)
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([original_text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top words from original text
        original_scores = tfidf_matrix.toarray()[0]
        top_indices = np.argsort(original_scores)[::-1][:50]  # Top 50 words
        top_words = {feature_names[i] for i in top_indices if original_scores[i] > 0}
        
        # Calculate overlap with summary
        if top_words:
            metrics["content_retention"] = len(top_words.intersection(summary_words)) / len(top_words)
        else:
            metrics["content_retention"] = 0
    except Exception as e:
        logger.error(f"Error calculating content retention: {e}")
        metrics["content_retention"] = 0
    
    return metrics
"""
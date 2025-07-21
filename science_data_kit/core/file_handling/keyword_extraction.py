"""
Keyword extraction module for automatically extracting keywords from text content.

This module provides functionality for extracting keywords and key phrases from
text content using various algorithms and techniques. It builds on the content_analysis
module but focuses specifically on identifying the most important terms in a document.

The module includes:
- Statistical keyword extraction (TF-IDF, TextRank, RAKE)
- Machine learning-based keyword extraction
- Domain-specific keyword extraction
- Keyword scoring and ranking
"""

import logging
import re
import string
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from science_data_kit.core.file_handling.content_analysis import (
    ContentAnalysisOptions,
    ContentFeatureType,
    get_document_important_terms
)
from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions,
    extract_text_from_file
)

logger = logging.getLogger(__name__)


class KeywordExtractionMethod(Enum):
    """Enumeration of keyword extraction methods."""
    TFIDF = "tfidf"
    TEXTRANK = "textrank"
    RAKE = "rake"
    YAKE = "yake"
    CUSTOM = "custom"


@dataclass
class KeywordExtractionOptions:
    """Options for keyword extraction."""
    # General options
    method: KeywordExtractionMethod = KeywordExtractionMethod.TFIDF
    num_keywords: int = 10
    min_word_length: int = 3
    include_ngrams: bool = True
    ngram_range: Tuple[int, int] = (1, 3)  # Unigrams, bigrams, and trigrams
    
    # Text preprocessing options
    lowercase: bool = True
    remove_punctuation: bool = True
    remove_stopwords: bool = True
    language: str = "english"
    
    # TF-IDF specific options
    min_df: int = 1  # Minimum document frequency
    max_df: float = 0.9  # Maximum document frequency
    
    # TextRank specific options
    window_size: int = 4
    damping_factor: float = 0.85
    convergence_threshold: float = 0.0001
    max_iterations: int = 100
    
    # RAKE specific options
    min_chars_per_word: int = 2
    max_words_per_phrase: int = 4
    min_phrase_frequency: int = 1
    
    # YAKE specific options
    max_ngram_size: int = 3
    deduplication_threshold: float = 0.9
    deduplication_function: str = "seqm"
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class Keyword:
    """A keyword or key phrase extracted from text."""
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the keyword."""
        return f"{self.text} ({self.score:.4f})"


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction on a text or document."""
    keywords: List[Keyword]
    method: KeywordExtractionMethod
    text_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the extraction result."""
        return "\n".join([
            f"Method: {self.method.value}",
            f"Keywords: {', '.join(str(kw) for kw in self.keywords[:5])}{'...' if len(self.keywords) > 5 else ''}",
            f"Total keywords: {len(self.keywords)}"
        ])


class KeywordExtractor:
    """Class for extracting keywords from text."""
    
    def __init__(self, options: Optional[KeywordExtractionOptions] = None):
        """
        Initialize the keyword extractor.
        
        Args:
            options: Keyword extraction options
        """
        self.options = options or KeywordExtractionOptions()
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
                'just', 'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our',
                'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it',
                'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
                'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would',
                'should', 'could', 'ought', 'i\'m', 'you\'re', 'he\'s', 'she\'s',
                'it\'s', 'we\'re', 'they\'re', 'i\'ve', 'you\'ve', 'we\'ve',
                'they\'ve', 'i\'d', 'you\'d', 'he\'d', 'she\'d', 'we\'d', 'they\'d',
                'i\'ll', 'you\'ll', 'he\'ll', 'she\'ll', 'we\'ll', 'they\'ll',
                'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'hasn\'t', 'haven\'t',
                'hadn\'t', 'doesn\'t', 'don\'t', 'didn\'t', 'won\'t', 'wouldn\'t',
                'shan\'t', 'shouldn\'t', 'can\'t', 'cannot', 'couldn\'t', 'mustn\'t',
                'let\'s', 'that\'s', 'who\'s', 'what\'s', 'here\'s', 'there\'s',
                'when\'s', 'where\'s', 'why\'s', 'how\'s'
            }
    
    def extract_keywords(self, text: str) -> KeywordExtractionResult:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            KeywordExtractionResult object containing the extracted keywords
        """
        if not text:
            logger.warning("Empty text provided for keyword extraction")
            return KeywordExtractionResult(
                keywords=[],
                method=self.options.method
            )
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Extract keywords based on method
        if self.options.method == KeywordExtractionMethod.TFIDF:
            return self._extract_keywords_tfidf(processed_text)
        elif self.options.method == KeywordExtractionMethod.TEXTRANK:
            return self._extract_keywords_textrank(processed_text)
        elif self.options.method == KeywordExtractionMethod.RAKE:
            return self._extract_keywords_rake(processed_text)
        elif self.options.method == KeywordExtractionMethod.YAKE:
            return self._extract_keywords_yake(processed_text)
        else:
            logger.warning(f"Unsupported keyword extraction method: {self.options.method}")
            return KeywordExtractionResult(
                keywords=[],
                method=self.options.method
            )
    
    def extract_keywords_from_file(self, file_path: str) -> KeywordExtractionResult:
        """
        Extract keywords from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            KeywordExtractionResult object containing the extracted keywords
        """
        # Extract text from file
        text_extraction_options = self.options.text_extraction_options or TextExtractionOptions()
        
        try:
            text_result = extract_text_from_file(file_path, text_extraction_options)
            if text_result and text_result.text:
                result = self.extract_keywords(text_result.text)
                result.metadata["file_path"] = file_path
                return result
            else:
                logger.warning(f"Could not extract text from file: {file_path}")
                return KeywordExtractionResult(
                    keywords=[],
                    method=self.options.method,
                    metadata={"file_path": file_path, "error": "Text extraction failed"}
                )
        except Exception as e:
            logger.error(f"Error extracting keywords from file {file_path}: {e}")
            return KeywordExtractionResult(
                keywords=[],
                method=self.options.method,
                metadata={"file_path": file_path, "error": str(e)}
            )
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for keyword extraction.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase if requested
        if self.options.lowercase:
            text = text.lower()
        
        # Remove punctuation if requested
        if self.options.remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        return text
    
    def _extract_keywords_tfidf(self, text: str) -> KeywordExtractionResult:
        """
        Extract keywords using TF-IDF.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            KeywordExtractionResult object containing the extracted keywords
        """
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                ngram_range=self.options.ngram_range if self.options.include_ngrams else (1, 1),
                min_df=self.options.min_df,
                max_df=self.options.max_df,
                stop_words=self.stopwords if self.options.remove_stopwords else None,
                token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z0-9_]{' + str(self.options.min_word_length - 1) + r',}\b'
            )
            
            # Transform text to TF-IDF features
            tfidf_matrix = vectorizer.fit_transform([text])
            
            # Get feature names and scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Create keywords
            keywords = []
            for idx in np.argsort(scores)[::-1]:
                if scores[idx] > 0:
                    keywords.append(Keyword(
                        text=feature_names[idx],
                        score=float(scores[idx])
                    ))
                
                if len(keywords) >= self.options.num_keywords:
                    break
            
            return KeywordExtractionResult(
                keywords=keywords,
                method=KeywordExtractionMethod.TFIDF,
                metadata={
                    "num_features": len(feature_names),
                    "max_score": float(np.max(scores)) if scores.size > 0 else 0.0
                }
            )
        
        except Exception as e:
            logger.error(f"Error extracting keywords using TF-IDF: {e}")
            return KeywordExtractionResult(
                keywords=[],
                method=KeywordExtractionMethod.TFIDF,
                metadata={"error": str(e)}
            )
    
    def _extract_keywords_textrank(self, text: str) -> KeywordExtractionResult:
        """
        Extract keywords using TextRank algorithm.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            KeywordExtractionResult object containing the extracted keywords
        """
        try:
            # Tokenize text into sentences and words
            sentences = self._split_into_sentences(text)
            
            # Create a graph of words
            word_graph = self._build_word_graph(sentences)
            
            # Apply TextRank algorithm
            word_scores = self._apply_textrank(word_graph)
            
            # Extract keywords based on scores
            keywords = []
            for word, score in sorted(word_scores.items(), key=lambda x: x[1], reverse=True):
                if len(word) >= self.options.min_word_length:
                    keywords.append(Keyword(
                        text=word,
                        score=score
                    ))
                
                if len(keywords) >= self.options.num_keywords:
                    break
            
            # If n-grams are enabled, extract key phrases
            if self.options.include_ngrams and self.options.ngram_range[1] > 1:
                keywords = self._extract_keyphrases(text, word_scores, keywords)
            
            return KeywordExtractionResult(
                keywords=keywords,
                method=KeywordExtractionMethod.TEXTRANK,
                metadata={
                    "num_words": len(word_scores),
                    "max_score": max(word_scores.values()) if word_scores else 0.0
                }
            )
        
        except Exception as e:
            logger.error(f"Error extracting keywords using TextRank: {e}")
            return KeywordExtractionResult(
                keywords=[],
                method=KeywordExtractionMethod.TEXTRANK,
                metadata={"error": str(e)}
            )
    
    def _split_into_sentences(self, text: str) -> List[List[str]]:
        """
        Split text into sentences and tokenize each sentence.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences, where each sentence is a list of words
        """
        try:
            from nltk.tokenize import sent_tokenize, word_tokenize
            
            # Split text into sentences
            sentences = sent_tokenize(text)
            
            # Tokenize each sentence into words
            tokenized_sentences = []
            for sentence in sentences:
                words = word_tokenize(sentence)
                
                # Filter words
                filtered_words = []
                for word in words:
                    # Skip short words
                    if len(word) < self.options.min_word_length:
                        continue
                    
                    # Skip stopwords
                    if self.options.remove_stopwords and word.lower() in self.stopwords:
                        continue
                    
                    # Skip punctuation
                    if self.options.remove_punctuation and all(c in string.punctuation for c in word):
                        continue
                    
                    filtered_words.append(word.lower() if self.options.lowercase else word)
                
                if filtered_words:
                    tokenized_sentences.append(filtered_words)
            
            return tokenized_sentences
        
        except ImportError:
            logger.warning("NLTK not available. Using a simple sentence splitter.")
            
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            
            # Tokenize each sentence into words
            tokenized_sentences = []
            for sentence in sentences:
                words = re.findall(r'\b\w+\b', sentence)
                
                # Filter words
                filtered_words = []
                for word in words:
                    # Skip short words
                    if len(word) < self.options.min_word_length:
                        continue
                    
                    # Skip stopwords
                    if self.options.remove_stopwords and word.lower() in self.stopwords:
                        continue
                    
                    filtered_words.append(word.lower() if self.options.lowercase else word)
                
                if filtered_words:
                    tokenized_sentences.append(filtered_words)
            
            return tokenized_sentences
    
    def _build_word_graph(self, sentences: List[List[str]]) -> Dict[str, Dict[str, float]]:
        """
        Build a graph of words based on co-occurrence within a window.
        
        Args:
            sentences: List of sentences, where each sentence is a list of words
            
        Returns:
            Graph represented as a dictionary of dictionaries
        """
        # Initialize graph
        graph = defaultdict(lambda: defaultdict(float))
        
        # Build graph based on co-occurrence within a window
        for sentence in sentences:
            for i, word in enumerate(sentence):
                # Consider words within the window
                window_start = max(0, i - self.options.window_size)
                window_end = min(len(sentence), i + self.options.window_size + 1)
                
                for j in range(window_start, window_end):
                    if i != j:  # Skip self-loops
                        other_word = sentence[j]
                        graph[word][other_word] += 1.0
        
        # Normalize edge weights
        for word, edges in graph.items():
            total_weight = sum(edges.values())
            for other_word in edges:
                graph[word][other_word] /= total_weight
        
        return graph
    
    def _apply_textrank(self, graph: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Apply TextRank algorithm to the word graph.
        
        Args:
            graph: Graph represented as a dictionary of dictionaries
            
        Returns:
            Dictionary mapping words to their TextRank scores
        """
        # Initialize scores
        scores = {word: 1.0 for word in graph}
        
        # Apply TextRank algorithm
        for _ in range(self.options.max_iterations):
            prev_scores = scores.copy()
            
            # Update scores
            for word in graph:
                score_sum = 0.0
                
                # Sum contributions from incoming edges
                for other_word, weight in graph.items():
                    if word in weight:  # If there's an edge from other_word to word
                        incoming_weight = weight[word]
                        outgoing_sum = sum(weight.values())
                        score_sum += incoming_weight * prev_scores[other_word] / outgoing_sum
                
                # Apply damping factor
                scores[word] = (1 - self.options.damping_factor) + self.options.damping_factor * score_sum
            
            # Check for convergence
            diff = sum(abs(scores[word] - prev_scores[word]) for word in graph)
            if diff < self.options.convergence_threshold:
                break
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 1.0
        for word in scores:
            scores[word] /= max_score
        
        return scores
    
    def _extract_keyphrases(self, text: str, word_scores: Dict[str, float], 
                          keywords: List[Keyword]) -> List[Keyword]:
        """
        Extract keyphrases based on word scores.
        
        Args:
            text: Original text
            word_scores: Dictionary mapping words to their scores
            keywords: List of keywords extracted so far
            
        Returns:
            Updated list of keywords including keyphrases
        """
        try:
            from nltk.tokenize import word_tokenize
            
            # Tokenize text
            words = word_tokenize(text)
            
            # Filter words
            filtered_words = []
            for word in words:
                # Skip short words
                if len(word) < self.options.min_word_length:
                    continue
                
                # Skip stopwords
                if self.options.remove_stopwords and word.lower() in self.stopwords:
                    continue
                
                # Skip punctuation
                if self.options.remove_punctuation and all(c in string.punctuation for c in word):
                    continue
                
                filtered_words.append(word.lower() if self.options.lowercase else word)
            
            # Extract n-grams
            max_n = min(self.options.ngram_range[1], 5)  # Limit to 5-grams
            
            for n in range(2, max_n + 1):
                for i in range(len(filtered_words) - n + 1):
                    ngram = filtered_words[i:i+n]
                    
                    # Skip n-grams with stopwords at the beginning or end
                    if (self.options.remove_stopwords and 
                        (ngram[0].lower() in self.stopwords or ngram[-1].lower() in self.stopwords)):
                        continue
                    
                    # Calculate score as average of word scores
                    score = sum(word_scores.get(word, 0.0) for word in ngram) / n
                    
                    if score > 0:
                        keywords.append(Keyword(
                            text=" ".join(ngram),
                            score=score
                        ))
            
            # Sort keywords by score and limit to num_keywords
            keywords.sort(key=lambda x: x.score, reverse=True)
            return keywords[:self.options.num_keywords]
        
        except ImportError:
            logger.warning("NLTK not available. Skipping keyphrase extraction.")
            return keywords
    
    def _extract_keywords_rake(self, text: str) -> KeywordExtractionResult:
        """
        Extract keywords using RAKE (Rapid Automatic Keyword Extraction) algorithm.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            KeywordExtractionResult object containing the extracted keywords
        """
        try:
            # Split text into phrases using stopwords and punctuation as delimiters
            if self.options.remove_stopwords:
                # Create a regex pattern for splitting
                stop_pattern = r'|'.join(r'\b' + re.escape(word) + r'\b' for word in self.stopwords)
                if self.options.remove_punctuation:
                    split_pattern = f"[{re.escape(string.punctuation)}]|{stop_pattern}"
                else:
                    split_pattern = stop_pattern
            else:
                split_pattern = f"[{re.escape(string.punctuation)}]" if self.options.remove_punctuation else r'\s+'
            
            # Split text into candidate phrases
            phrases = re.split(split_pattern, text)
            phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
            
            # Filter phrases
            filtered_phrases = []
            for phrase in phrases:
                # Skip short phrases
                if len(phrase) < self.options.min_chars_per_word:
                    continue
                
                # Skip phrases with too many words
                words = phrase.split()
                if len(words) > self.options.max_words_per_phrase:
                    continue
                
                # Skip phrases with short words
                if any(len(word) < self.options.min_word_length for word in words):
                    continue
                
                filtered_phrases.append(phrase.lower() if self.options.lowercase else phrase)
            
            # Count phrase frequencies
            phrase_frequencies = Counter(filtered_phrases)
            
            # Filter by minimum frequency
            phrase_frequencies = {phrase: freq for phrase, freq in phrase_frequencies.items() 
                               if freq >= self.options.min_phrase_frequency}
            
            # Calculate word frequencies
            word_frequencies = defaultdict(int)
            for phrase, freq in phrase_frequencies.items():
                for word in phrase.split():
                    word_frequencies[word] += freq
            
            # Calculate word degrees
            word_degrees = defaultdict(int)
            for phrase, freq in phrase_frequencies.items():
                words = phrase.split()
                for word in words:
                    word_degrees[word] += len(words) - 1
            
            # Calculate word scores
            word_scores = {}
            for word in word_frequencies:
                if word_degrees[word] > 0:
                    word_scores[word] = word_frequencies[word] / word_degrees[word]
                else:
                    word_scores[word] = 0.0
            
            # Calculate phrase scores
            phrase_scores = {}
            for phrase in phrase_frequencies:
                words = phrase.split()
                phrase_scores[phrase] = sum(word_scores.get(word, 0.0) for word in words)
            
            # Create keywords
            keywords = []
            for phrase, score in sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True):
                keywords.append(Keyword(
                    text=phrase,
                    score=score
                ))
                
                if len(keywords) >= self.options.num_keywords:
                    break
            
            return KeywordExtractionResult(
                keywords=keywords,
                method=KeywordExtractionMethod.RAKE,
                metadata={
                    "num_phrases": len(phrase_frequencies),
                    "max_score": max(phrase_scores.values()) if phrase_scores else 0.0
                }
            )
        
        except Exception as e:
            logger.error(f"Error extracting keywords using RAKE: {e}")
            return KeywordExtractionResult(
                keywords=[],
                method=KeywordExtractionMethod.RAKE,
                metadata={"error": str(e)}
            )
    
    def _extract_keywords_yake(self, text: str) -> KeywordExtractionResult:
        """
        Extract keywords using YAKE (Yet Another Keyword Extractor) algorithm.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            KeywordExtractionResult object containing the extracted keywords
        """
        try:
            # Try to import yake
            import yake
            
            # Create keyword extractor
            kw_extractor = yake.KeywordExtractor(
                lan=self.options.language,
                n=self.options.max_ngram_size,
                dedupLim=self.options.deduplication_threshold,
                dedupFunc=self.options.deduplication_function,
                windowsSize=self.options.window_size,
                top=self.options.num_keywords,
                features=None
            )
            
            # Extract keywords
            keywords_list = kw_extractor.extract_keywords(text)
            
            # Create keywords (note: YAKE scores are inverted - lower is better)
            keywords = []
            for keyword_text, score in keywords_list:
                # Invert score so higher is better (consistent with other methods)
                inverted_score = 1.0 / (1.0 + score) if score > 0 else 1.0
                
                keywords.append(Keyword(
                    text=keyword_text,
                    score=inverted_score
                ))
            
            return KeywordExtractionResult(
                keywords=keywords,
                method=KeywordExtractionMethod.YAKE,
                metadata={
                    "num_keywords": len(keywords),
                    "original_scores": {kw.text: 1.0/kw.score - 1.0 for kw in keywords}
                }
            )
        
        except ImportError:
            logger.warning("YAKE package not available. Falling back to TF-IDF.")
            return self._extract_keywords_tfidf(text)
        
        except Exception as e:
            logger.error(f"Error extracting keywords using YAKE: {e}")
            return KeywordExtractionResult(
                keywords=[],
                method=KeywordExtractionMethod.YAKE,
                metadata={"error": str(e)}
            )


def extract_keywords(text: str, method: KeywordExtractionMethod = KeywordExtractionMethod.TFIDF,
                   num_keywords: int = 10, **kwargs) -> List[Tuple[str, float]]:
    """
    Extract keywords from text using the specified method.
    
    Args:
        text: Text to extract keywords from
        method: Keyword extraction method to use
        num_keywords: Number of keywords to extract
        **kwargs: Additional options for keyword extraction
        
    Returns:
        List of tuples (keyword, score) sorted by score
    """
    # Create options with specified method and num_keywords
    options = KeywordExtractionOptions(
        method=method,
        num_keywords=num_keywords,
        **kwargs
    )
    
    # Extract keywords
    extractor = KeywordExtractor(options)
    result = extractor.extract_keywords(text)
    
    # Return keywords as list of tuples
    return [(kw.text, kw.score) for kw in result.keywords]


def extract_keywords_from_file(file_path: str, method: KeywordExtractionMethod = KeywordExtractionMethod.TFIDF,
                             num_keywords: int = 10, **kwargs) -> List[Tuple[str, float]]:
    """
    Extract keywords from a file using the specified method.
    
    Args:
        file_path: Path to the file
        method: Keyword extraction method to use
        num_keywords: Number of keywords to extract
        **kwargs: Additional options for keyword extraction
        
    Returns:
        List of tuples (keyword, score) sorted by score
    """
    # Create options with specified method and num_keywords
    options = KeywordExtractionOptions(
        method=method,
        num_keywords=num_keywords,
        **kwargs
    )
    
    # Extract keywords
    extractor = KeywordExtractor(options)
    result = extractor.extract_keywords_from_file(file_path)
    
    # Return keywords as list of tuples
    return [(kw.text, kw.score) for kw in result.keywords]


def compare_keyword_extraction_methods(text: str, num_keywords: int = 10) -> Dict[str, List[Tuple[str, float]]]:
    """
    Compare different keyword extraction methods on the same text.
    
    Args:
        text: Text to extract keywords from
        num_keywords: Number of keywords to extract
        
    Returns:
        Dictionary mapping method names to lists of (keyword, score) tuples
    """
    results = {}
    
    # Try each method
    for method in KeywordExtractionMethod:
        try:
            keywords = extract_keywords(text, method=method, num_keywords=num_keywords)
            results[method.value] = keywords
        except Exception as e:
            logger.error(f"Error extracting keywords using {method.value}: {e}")
            results[method.value] = []
    
    return results


def get_document_keywords(file_path: str, num_keywords: int = 10,
                        method: KeywordExtractionMethod = KeywordExtractionMethod.TFIDF) -> List[Tuple[str, float]]:
    """
    Get keywords from a document.
    
    This is a convenience function that combines text extraction and keyword extraction.
    
    Args:
        file_path: Path to the file
        num_keywords: Number of keywords to extract
        method: Keyword extraction method to use
        
    Returns:
        List of tuples (keyword, score) sorted by score
    """
    return extract_keywords_from_file(file_path, method=method, num_keywords=num_keywords)
"""
"""
Topic modeling module for extracting topics from documents.

This module provides functionality for extracting topics from documents using
various topic modeling algorithms, including Latent Dirichlet Allocation (LDA),
Non-negative Matrix Factorization (NMF), and Latent Semantic Analysis (LSA).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
import numpy as np

try:
    from sklearn.decomposition import LatentDirichletAllocation, NMF, TruncatedSVD
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import gensim
    from gensim.corpora import Dictionary
    from gensim.models import LdaModel, CoherenceModel
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions, extract_text_from_file, TextExtractionResult
)

logger = logging.getLogger(__name__)


class TopicModelingMethod(str, Enum):
    """Enum for topic modeling methods."""
    LDA = "lda"  # Latent Dirichlet Allocation
    NMF = "nmf"  # Non-negative Matrix Factorization
    LSA = "lsa"  # Latent Semantic Analysis
    GENSIM_LDA = "gensim_lda"  # Gensim implementation of LDA


@dataclass
class TopicModelingOptions:
    """Options for topic modeling."""
    method: TopicModelingMethod = TopicModelingMethod.LDA
    num_topics: int = 5
    num_words_per_topic: int = 10
    max_features: int = 1000
    min_df: Union[int, float] = 2
    max_df: Union[int, float] = 0.95
    ngram_range: Tuple[int, int] = (1, 1)
    stop_words: str = "english"
    random_state: int = 42
    
    # LDA specific options
    lda_learning_method: str = "online"
    lda_max_iter: int = 10
    lda_learning_decay: float = 0.7
    
    # NMF specific options
    nmf_beta_loss: str = "frobenius"
    nmf_solver: str = "cd"
    nmf_alpha: float = 0.1
    nmf_l1_ratio: float = 0.5
    
    # LSA specific options
    lsa_algorithm: str = "randomized"
    lsa_n_iter: int = 5
    
    # Gensim LDA specific options
    gensim_passes: int = 10
    gensim_iterations: int = 50
    gensim_alpha: str = "auto"
    gensim_eta: str = "auto"
    gensim_eval_every: int = 10
    gensim_minimum_probability: float = 0.01
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class Topic:
    """Class representing a topic with its keywords and weights."""
    id: int
    keywords: List[Tuple[str, float]]
    coherence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the topic."""
        keywords_str = ", ".join([f"{word} ({weight:.4f})" for word, weight in self.keywords])
        coherence_str = f" (Coherence: {self.coherence:.4f})" if self.coherence is not None else ""
        return f"Topic {self.id}{coherence_str}: {keywords_str}"


@dataclass
class TopicModelingResult:
    """Result of topic modeling."""
    topics: List[Topic]
    method: TopicModelingMethod
    document_topics: Optional[List[List[Tuple[int, float]]]] = None
    model: Any = None
    vectorizer: Any = None
    corpus: Any = None
    dictionary: Any = None
    coherence_score: Optional[float] = None
    perplexity: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the topic modeling result."""
        topics_str = "\n".join([str(topic) for topic in self.topics])
        coherence_str = f"Coherence score: {self.coherence_score:.4f}" if self.coherence_score is not None else ""
        perplexity_str = f"Perplexity: {self.perplexity:.4f}" if self.perplexity is not None else ""
        metrics_str = "\n".join(filter(None, [coherence_str, perplexity_str]))
        
        return "\n".join(filter(None, [
            f"Method: {self.method.value}",
            f"Number of topics: {len(self.topics)}",
            topics_str,
            metrics_str
        ]))


class TopicModeler:
    """Class for topic modeling."""
    
    def __init__(self, options: Optional[TopicModelingOptions] = None):
        """Initialize the topic modeler.
        
        Args:
            options: Options for topic modeling.
        """
        self.options = options or TopicModelingOptions()
        
        if not SKLEARN_AVAILABLE and self.options.method in [
            TopicModelingMethod.LDA, TopicModelingMethod.NMF, TopicModelingMethod.LSA
        ]:
            logger.warning(
                f"scikit-learn is not available. Cannot use {self.options.method.value} "
                "for topic modeling. Install scikit-learn with 'pip install scikit-learn'."
            )
        
        if not GENSIM_AVAILABLE and self.options.method == TopicModelingMethod.GENSIM_LDA:
            logger.warning(
                "gensim is not available. Cannot use gensim_lda for topic modeling. "
                "Install gensim with 'pip install gensim'."
            )
    
    def extract_topics(self, documents: List[str]) -> TopicModelingResult:
        """Extract topics from a list of documents.
        
        Args:
            documents: List of document texts.
            
        Returns:
            TopicModelingResult: Result of topic modeling.
        """
        if not documents:
            return TopicModelingResult(
                topics=[],
                method=self.options.method,
                document_topics=[],
                metadata={"error": "No documents provided"}
            )
        
        if self.options.method == TopicModelingMethod.LDA:
            if not SKLEARN_AVAILABLE:
                return self._handle_missing_dependency("scikit-learn")
            return self._extract_topics_lda(documents)
        
        elif self.options.method == TopicModelingMethod.NMF:
            if not SKLEARN_AVAILABLE:
                return self._handle_missing_dependency("scikit-learn")
            return self._extract_topics_nmf(documents)
        
        elif self.options.method == TopicModelingMethod.LSA:
            if not SKLEARN_AVAILABLE:
                return self._handle_missing_dependency("scikit-learn")
            return self._extract_topics_lsa(documents)
        
        elif self.options.method == TopicModelingMethod.GENSIM_LDA:
            if not GENSIM_AVAILABLE:
                return self._handle_missing_dependency("gensim")
            return self._extract_topics_gensim_lda(documents)
        
        else:
            return TopicModelingResult(
                topics=[],
                method=self.options.method,
                document_topics=[],
                metadata={"error": f"Unsupported topic modeling method: {self.options.method.value}"}
            )
    
    def _handle_missing_dependency(self, dependency: str) -> TopicModelingResult:
        """Handle missing dependency.
        
        Args:
            dependency: Name of the missing dependency.
            
        Returns:
            TopicModelingResult: Result with error message.
        """
        return TopicModelingResult(
            topics=[],
            method=self.options.method,
            document_topics=[],
            metadata={"error": f"{dependency} is not available. Install it with 'pip install {dependency}'."}
        )
    
    def _extract_topics_lda(self, documents: List[str]) -> TopicModelingResult:
        """Extract topics using Latent Dirichlet Allocation.
        
        Args:
            documents: List of document texts.
            
        Returns:
            TopicModelingResult: Result of topic modeling.
        """
        # Create document-term matrix
        vectorizer = CountVectorizer(
            max_features=self.options.max_features,
            min_df=self.options.min_df,
            max_df=self.options.max_df,
            ngram_range=self.options.ngram_range,
            stop_words=self.options.stop_words
        )
        X = vectorizer.fit_transform(documents)
        
        # Train LDA model
        lda = LatentDirichletAllocation(
            n_components=self.options.num_topics,
            learning_method=self.options.lda_learning_method,
            max_iter=self.options.lda_max_iter,
            learning_decay=self.options.lda_learning_decay,
            random_state=self.options.random_state
        )
        lda.fit(X)
        
        # Get topics
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[:-self.options.num_words_per_topic-1:-1]
            top_words = [(feature_names[i], topic[i]) for i in top_words_idx]
            topics.append(Topic(id=topic_idx, keywords=top_words))
        
        # Get document-topic distribution
        doc_topics = lda.transform(X)
        document_topics = []
        for doc_topic in doc_topics:
            # Get topic indices and probabilities, sorted by probability
            sorted_topics = sorted(
                [(i, p) for i, p in enumerate(doc_topic)],
                key=lambda x: x[1],
                reverse=True
            )
            document_topics.append(sorted_topics)
        
        # Calculate perplexity
        perplexity = lda.perplexity(X)
        
        return TopicModelingResult(
            topics=topics,
            method=TopicModelingMethod.LDA,
            document_topics=document_topics,
            model=lda,
            vectorizer=vectorizer,
            perplexity=perplexity
        )
    
    def _extract_topics_nmf(self, documents: List[str]) -> TopicModelingResult:
        """Extract topics using Non-negative Matrix Factorization.
        
        Args:
            documents: List of document texts.
            
        Returns:
            TopicModelingResult: Result of topic modeling.
        """
        # Create document-term matrix with TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=self.options.max_features,
            min_df=self.options.min_df,
            max_df=self.options.max_df,
            ngram_range=self.options.ngram_range,
            stop_words=self.options.stop_words
        )
        X = vectorizer.fit_transform(documents)
        
        # Train NMF model
        nmf = NMF(
            n_components=self.options.num_topics,
            random_state=self.options.random_state,
            beta_loss=self.options.nmf_beta_loss,
            solver=self.options.nmf_solver,
            alpha=self.options.nmf_alpha,
            l1_ratio=self.options.nmf_l1_ratio
        )
        nmf.fit(X)
        
        # Get topics
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(nmf.components_):
            top_words_idx = topic.argsort()[:-self.options.num_words_per_topic-1:-1]
            top_words = [(feature_names[i], topic[i]) for i in top_words_idx]
            topics.append(Topic(id=topic_idx, keywords=top_words))
        
        # Get document-topic distribution
        doc_topics = nmf.transform(X)
        document_topics = []
        for doc_topic in doc_topics:
            # Get topic indices and weights, sorted by weight
            sorted_topics = sorted(
                [(i, p) for i, p in enumerate(doc_topic)],
                key=lambda x: x[1],
                reverse=True
            )
            document_topics.append(sorted_topics)
        
        return TopicModelingResult(
            topics=topics,
            method=TopicModelingMethod.NMF,
            document_topics=document_topics,
            model=nmf,
            vectorizer=vectorizer
        )
    
    def _extract_topics_lsa(self, documents: List[str]) -> TopicModelingResult:
        """Extract topics using Latent Semantic Analysis.
        
        Args:
            documents: List of document texts.
            
        Returns:
            TopicModelingResult: Result of topic modeling.
        """
        # Create document-term matrix with TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=self.options.max_features,
            min_df=self.options.min_df,
            max_df=self.options.max_df,
            ngram_range=self.options.ngram_range,
            stop_words=self.options.stop_words
        )
        X = vectorizer.fit_transform(documents)
        
        # Train LSA model
        lsa = TruncatedSVD(
            n_components=self.options.num_topics,
            algorithm=self.options.lsa_algorithm,
            n_iter=self.options.lsa_n_iter,
            random_state=self.options.random_state
        )
        lsa.fit(X)
        
        # Get topics
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lsa.components_):
            top_words_idx = topic.argsort()[:-self.options.num_words_per_topic-1:-1]
            top_words = [(feature_names[i], topic[i]) for i in top_words_idx]
            topics.append(Topic(id=topic_idx, keywords=top_words))
        
        # Get document-topic distribution
        doc_topics = lsa.transform(X)
        document_topics = []
        for doc_topic in doc_topics:
            # Get topic indices and weights, sorted by absolute weight
            sorted_topics = sorted(
                [(i, p) for i, p in enumerate(doc_topic)],
                key=lambda x: abs(x[1]),
                reverse=True
            )
            document_topics.append(sorted_topics)
        
        return TopicModelingResult(
            topics=topics,
            method=TopicModelingMethod.LSA,
            document_topics=document_topics,
            model=lsa,
            vectorizer=vectorizer
        )
    
    def _extract_topics_gensim_lda(self, documents: List[str]) -> TopicModelingResult:
        """Extract topics using Gensim's implementation of LDA.
        
        Args:
            documents: List of document texts.
            
        Returns:
            TopicModelingResult: Result of topic modeling.
        """
        # Tokenize documents
        tokenized_docs = [doc.lower().split() for doc in documents]
        
        # Create dictionary
        dictionary = Dictionary(tokenized_docs)
        
        # Filter out extremes (words that appear in less than min_df documents or more than max_df% of documents)
        min_df = self.options.min_df
        max_df = self.options.max_df
        if isinstance(max_df, float):
            max_df = int(max_df * len(documents))
        
        dictionary.filter_extremes(no_below=min_df, no_above=max_df, keep_n=self.options.max_features)
        
        # Create corpus
        corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]
        
        # Train LDA model
        lda_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=self.options.num_topics,
            passes=self.options.gensim_passes,
            iterations=self.options.gensim_iterations,
            alpha=self.options.gensim_alpha,
            eta=self.options.gensim_eta,
            eval_every=self.options.gensim_eval_every,
            minimum_probability=self.options.gensim_minimum_probability,
            random_state=self.options.random_state
        )
        
        # Get topics
        topics = []
        for topic_idx in range(self.options.num_topics):
            top_words = lda_model.show_topic(topic_idx, self.options.num_words_per_topic)
            topics.append(Topic(id=topic_idx, keywords=top_words))
        
        # Get document-topic distribution
        document_topics = []
        for doc_bow in corpus:
            doc_topics = lda_model.get_document_topics(
                doc_bow, minimum_probability=self.options.gensim_minimum_probability
            )
            # Sort by probability
            sorted_topics = sorted(doc_topics, key=lambda x: x[1], reverse=True)
            document_topics.append(sorted_topics)
        
        # Calculate coherence score
        coherence_model = CoherenceModel(
            model=lda_model, texts=tokenized_docs, dictionary=dictionary, coherence='c_v'
        )
        coherence_score = coherence_model.get_coherence()
        
        # Calculate topic coherence scores
        for topic in topics:
            topic_words = [word for word, _ in topic.keywords]
            topic_coherence = CoherenceModel(
                topics=[topic_words], texts=tokenized_docs, dictionary=dictionary, coherence='c_v'
            ).get_coherence()
            topic.coherence = topic_coherence
        
        # Calculate perplexity
        perplexity = lda_model.log_perplexity(corpus)
        
        return TopicModelingResult(
            topics=topics,
            method=TopicModelingMethod.GENSIM_LDA,
            document_topics=document_topics,
            model=lda_model,
            corpus=corpus,
            dictionary=dictionary,
            coherence_score=coherence_score,
            perplexity=perplexity
        )
    
    def extract_topics_from_files(self, file_paths: List[str]) -> TopicModelingResult:
        """Extract topics from a list of files.
        
        Args:
            file_paths: List of file paths.
            
        Returns:
            TopicModelingResult: Result of topic modeling.
        """
        # Extract text from files
        documents = []
        file_metadata = []
        
        for file_path in file_paths:
            result = extract_text_from_file(
                file_path, options=self.options.text_extraction_options
            )
            if result:
                documents.append(result.text)
                file_metadata.append({
                    "file_path": file_path,
                    **result.metadata
                })
            else:
                logger.warning(f"Failed to extract text from {file_path}")
        
        if not documents:
            return TopicModelingResult(
                topics=[],
                method=self.options.method,
                document_topics=[],
                metadata={"error": "Failed to extract text from any of the provided files"}
            )
        
        # Extract topics
        result = self.extract_topics(documents)
        
        # Add file metadata
        result.metadata["files"] = file_metadata
        
        return result
    
    def get_document_topics(self, document: str, result: TopicModelingResult) -> List[Tuple[int, float]]:
        """Get topics for a new document using an existing topic model.
        
        Args:
            document: Document text.
            result: Result of previous topic modeling.
            
        Returns:
            List[Tuple[int, float]]: List of (topic_id, probability) tuples.
        """
        if not result.model or not result.vectorizer:
            logger.error("No model or vectorizer available in the result")
            return []
        
        if self.options.method in [TopicModelingMethod.LDA, TopicModelingMethod.NMF, TopicModelingMethod.LSA]:
            # Transform document using the vectorizer
            X = result.vectorizer.transform([document])
            
            # Get document-topic distribution
            doc_topics = result.model.transform(X)[0]
            
            # Sort by probability/weight
            sorted_topics = sorted(
                [(i, p) for i, p in enumerate(doc_topics)],
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_topics
        
        elif self.options.method == TopicModelingMethod.GENSIM_LDA:
            if not result.dictionary:
                logger.error("No dictionary available in the result")
                return []
            
            # Tokenize document
            tokenized_doc = document.lower().split()
            
            # Convert to bag of words
            bow = result.dictionary.doc2bow(tokenized_doc)
            
            # Get document-topic distribution
            doc_topics = result.model.get_document_topics(
                bow, minimum_probability=self.options.gensim_minimum_probability
            )
            
            # Sort by probability
            sorted_topics = sorted(doc_topics, key=lambda x: x[1], reverse=True)
            
            return sorted_topics
        
        else:
            logger.error(f"Unsupported topic modeling method: {self.options.method.value}")
            return []


def extract_topics(
    documents: List[str],
    method: TopicModelingMethod = TopicModelingMethod.LDA,
    num_topics: int = 5,
    num_words_per_topic: int = 10,
    **kwargs
) -> List[List[Tuple[str, float]]]:
    """Extract topics from a list of documents.
    
    Args:
        documents: List of document texts.
        method: Topic modeling method.
        num_topics: Number of topics to extract.
        num_words_per_topic: Number of words per topic.
        **kwargs: Additional options for topic modeling.
        
    Returns:
        List[List[Tuple[str, float]]]: List of topics, each containing a list of (word, weight) tuples.
    """
    options = TopicModelingOptions(
        method=method,
        num_topics=num_topics,
        num_words_per_topic=num_words_per_topic,
        **kwargs
    )
    
    modeler = TopicModeler(options)
    result = modeler.extract_topics(documents)
    
    return [topic.keywords for topic in result.topics]


def extract_topics_from_files(
    file_paths: List[str],
    method: TopicModelingMethod = TopicModelingMethod.LDA,
    num_topics: int = 5,
    num_words_per_topic: int = 10,
    **kwargs
) -> List[List[Tuple[str, float]]]:
    """Extract topics from a list of files.
    
    Args:
        file_paths: List of file paths.
        method: Topic modeling method.
        num_topics: Number of topics to extract.
        num_words_per_topic: Number of words per topic.
        **kwargs: Additional options for topic modeling.
        
    Returns:
        List[List[Tuple[str, float]]]: List of topics, each containing a list of (word, weight) tuples.
    """
    options = TopicModelingOptions(
        method=method,
        num_topics=num_topics,
        num_words_per_topic=num_words_per_topic,
        **kwargs
    )
    
    modeler = TopicModeler(options)
    result = modeler.extract_topics_from_files(file_paths)
    
    return [topic.keywords for topic in result.topics]


def compare_topic_modeling_methods(
    documents: List[str],
    num_topics: int = 5,
    num_words_per_topic: int = 10,
    **kwargs
) -> Dict[str, List[List[Tuple[str, float]]]]:
    """Compare different topic modeling methods on the same documents.
    
    Args:
        documents: List of document texts.
        num_topics: Number of topics to extract.
        num_words_per_topic: Number of words per topic.
        **kwargs: Additional options for topic modeling.
        
    Returns:
        Dict[str, List[List[Tuple[str, float]]]]: Dictionary mapping method names to lists of topics.
    """
    results = {}
    
    for method in TopicModelingMethod:
        try:
            if (method in [TopicModelingMethod.LDA, TopicModelingMethod.NMF, TopicModelingMethod.LSA] 
                and not SKLEARN_AVAILABLE):
                logger.warning(f"Skipping {method.value} as scikit-learn is not available")
                continue
            
            if method == TopicModelingMethod.GENSIM_LDA and not GENSIM_AVAILABLE:
                logger.warning(f"Skipping {method.value} as gensim is not available")
                continue
            
            options = TopicModelingOptions(
                method=method,
                num_topics=num_topics,
                num_words_per_topic=num_words_per_topic,
                **kwargs
            )
            
            modeler = TopicModeler(options)
            result = modeler.extract_topics(documents)
            
            results[method.value] = [topic.keywords for topic in result.topics]
        except Exception as e:
            logger.error(f"Error extracting topics with {method.value}: {e}")
            results[method.value] = []
    
    return results


def get_document_topics(
    document: str,
    model_result: TopicModelingResult,
    num_topics: int = None
) -> List[Tuple[int, float]]:
    """Get topics for a document using an existing topic model.
    
    Args:
        document: Document text.
        model_result: Result of previous topic modeling.
        num_topics: Maximum number of topics to return.
        
    Returns:
        List[Tuple[int, float]]: List of (topic_id, probability) tuples.
    """
    modeler = TopicModeler(TopicModelingOptions(method=model_result.method))
    topics = modeler.get_document_topics(document, model_result)
    
    if num_topics is not None:
        topics = topics[:num_topics]
    
    return topics
"""
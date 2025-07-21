"""
Tests for the topic_modeling module.
"""

import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from science_data_kit.core.file_handling.topic_modeling import (
    TopicModelingMethod,
    TopicModelingOptions,
    Topic,
    TopicModelingResult,
    TopicModeler,
    extract_topics,
    extract_topics_from_files,
    compare_topic_modeling_methods,
    get_document_topics
)
from science_data_kit.core.file_handling.text_extraction import TextExtractionResult


class TestTopicModelingOptions(unittest.TestCase):
    """Tests for the TopicModelingOptions class."""
    
    def test_default_initialization(self):
        """Test that default initialization works correctly."""
        options = TopicModelingOptions()
        self.assertEqual(options.method, TopicModelingMethod.LDA)
        self.assertEqual(options.num_topics, 5)
        self.assertEqual(options.num_words_per_topic, 10)
        self.assertEqual(options.max_features, 1000)
        self.assertEqual(options.min_df, 2)
        self.assertEqual(options.max_df, 0.95)
        self.assertEqual(options.ngram_range, (1, 1))
        self.assertEqual(options.stop_words, "english")
        self.assertEqual(options.random_state, 42)
        self.assertEqual(options.lda_learning_method, "online")
        self.assertEqual(options.lda_max_iter, 10)
        self.assertEqual(options.lda_learning_decay, 0.7)
        self.assertEqual(options.nmf_beta_loss, "frobenius")
        self.assertEqual(options.nmf_solver, "cd")
        self.assertEqual(options.nmf_alpha, 0.1)
        self.assertEqual(options.nmf_l1_ratio, 0.5)
        self.assertEqual(options.lsa_algorithm, "randomized")
        self.assertEqual(options.lsa_n_iter, 5)
        self.assertEqual(options.gensim_passes, 10)
        self.assertEqual(options.gensim_iterations, 50)
        self.assertEqual(options.gensim_alpha, "auto")
        self.assertEqual(options.gensim_eta, "auto")
        self.assertEqual(options.gensim_eval_every, 10)
        self.assertEqual(options.gensim_minimum_probability, 0.01)
        self.assertIsNone(options.text_extraction_options)


class TestTopic(unittest.TestCase):
    """Tests for the Topic class."""
    
    def test_initialization(self):
        """Test initialization."""
        keywords = [("word1", 0.8), ("word2", 0.5)]
        topic = Topic(id=1, keywords=keywords)
        self.assertEqual(topic.id, 1)
        self.assertEqual(topic.keywords, keywords)
        self.assertIsNone(topic.coherence)
        self.assertEqual(topic.metadata, {})
    
    def test_str_representation(self):
        """Test string representation."""
        keywords = [("word1", 0.8), ("word2", 0.5)]
        topic = Topic(id=1, keywords=keywords)
        expected_str = "Topic 1: word1 (0.8000), word2 (0.5000)"
        self.assertEqual(str(topic), expected_str)
        
        # Test with coherence
        topic.coherence = 0.75
        expected_str = "Topic 1 (Coherence: 0.7500): word1 (0.8000), word2 (0.5000)"
        self.assertEqual(str(topic), expected_str)


class TestTopicModelingResult(unittest.TestCase):
    """Tests for the TopicModelingResult class."""
    
    def test_initialization(self):
        """Test initialization."""
        topics = [
            Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
            Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
        ]
        result = TopicModelingResult(
            topics=topics,
            method=TopicModelingMethod.LDA
        )
        self.assertEqual(result.topics, topics)
        self.assertEqual(result.method, TopicModelingMethod.LDA)
        self.assertIsNone(result.document_topics)
        self.assertIsNone(result.model)
        self.assertIsNone(result.vectorizer)
        self.assertIsNone(result.corpus)
        self.assertIsNone(result.dictionary)
        self.assertIsNone(result.coherence_score)
        self.assertIsNone(result.perplexity)
        self.assertEqual(result.metadata, {})
    
    def test_str_representation(self):
        """Test string representation."""
        topics = [
            Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
            Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
        ]
        result = TopicModelingResult(
            topics=topics,
            method=TopicModelingMethod.LDA
        )
        expected_str = "\n".join([
            "Method: lda",
            "Number of topics: 2",
            "Topic 0: word1 (0.8000), word2 (0.5000)",
            "Topic 1: word3 (0.7000), word4 (0.4000)"
        ])
        self.assertEqual(str(result), expected_str)
        
        # Test with coherence and perplexity
        result.coherence_score = 0.75
        result.perplexity = 2.5
        expected_str = "\n".join([
            "Method: lda",
            "Number of topics: 2",
            "Topic 0: word1 (0.8000), word2 (0.5000)",
            "Topic 1: word3 (0.7000), word4 (0.4000)",
            "Coherence score: 0.7500",
            "Perplexity: 2.5000"
        ])
        self.assertEqual(str(result), expected_str)


class TestTopicModeler(unittest.TestCase):
    """Tests for the TopicModeler class."""
    
    def setUp(self):
        """Set up the test case."""
        self.modeler = TopicModeler()
    
    def test_initialization(self):
        """Test initialization."""
        self.assertIsInstance(self.modeler.options, TopicModelingOptions)
        self.assertEqual(self.modeler.options.method, TopicModelingMethod.LDA)
    
    def test_extract_topics_empty_documents(self):
        """Test extracting topics from empty documents."""
        result = self.modeler.extract_topics([])
        self.assertEqual(len(result.topics), 0)
        self.assertEqual(result.method, TopicModelingMethod.LDA)
        self.assertEqual(result.metadata, {"error": "No documents provided"})
    
    @patch('science_data_kit.core.file_handling.topic_modeling.SKLEARN_AVAILABLE', False)
    def test_extract_topics_missing_sklearn(self):
        """Test extracting topics when scikit-learn is not available."""
        with patch('science_data_kit.core.file_handling.topic_modeling.logger') as mock_logger:
            modeler = TopicModeler()
            result = modeler.extract_topics(["document1", "document2"])
            self.assertEqual(len(result.topics), 0)
            self.assertEqual(result.method, TopicModelingMethod.LDA)
            self.assertEqual(result.metadata, {"error": "scikit-learn is not available. Install it with 'pip install scikit-learn'."})
            mock_logger.warning.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.topic_modeling.GENSIM_AVAILABLE', False)
    def test_extract_topics_missing_gensim(self):
        """Test extracting topics when gensim is not available."""
        with patch('science_data_kit.core.file_handling.topic_modeling.logger') as mock_logger:
            modeler = TopicModeler(TopicModelingOptions(method=TopicModelingMethod.GENSIM_LDA))
            result = modeler.extract_topics(["document1", "document2"])
            self.assertEqual(len(result.topics), 0)
            self.assertEqual(result.method, TopicModelingMethod.GENSIM_LDA)
            self.assertEqual(result.metadata, {"error": "gensim is not available. Install it with 'pip install gensim'."})
            mock_logger.warning.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.topic_modeling.CountVectorizer')
    @patch('science_data_kit.core.file_handling.topic_modeling.LatentDirichletAllocation')
    def test_extract_topics_lda(self, mock_lda_class, mock_vectorizer_class):
        """Test extracting topics using LDA."""
        # Mock the vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Mock the LDA model
        mock_lda = MagicMock()
        mock_lda.components_ = np.array([[0.1, 0.5, 0.3], [0.2, 0.1, 0.4]])
        mock_lda.transform.return_value = np.array([[0.7, 0.3], [0.4, 0.6]])
        mock_lda.perplexity.return_value = 2.5
        mock_lda_class.return_value = mock_lda
        
        # Extract topics
        result = self.modeler.extract_topics(["document1", "document2"])
        
        # Check the result
        self.assertEqual(len(result.topics), 2)
        self.assertEqual(result.method, TopicModelingMethod.LDA)
        self.assertEqual(result.topics[0].id, 0)
        self.assertEqual(result.topics[0].keywords[0][0], "word2")  # Highest weight in first topic
        self.assertEqual(result.topics[0].keywords[0][1], 0.5)
        self.assertEqual(result.topics[1].id, 1)
        self.assertEqual(result.topics[1].keywords[0][0], "word3")  # Highest weight in second topic
        self.assertEqual(result.topics[1].keywords[0][1], 0.4)
        self.assertEqual(len(result.document_topics), 2)
        self.assertEqual(result.document_topics[0][0][0], 0)  # First document, highest probability topic
        self.assertEqual(result.document_topics[0][0][1], 0.7)
        self.assertEqual(result.document_topics[1][0][0], 1)  # Second document, highest probability topic
        self.assertEqual(result.document_topics[1][0][1], 0.6)
        self.assertEqual(result.perplexity, 2.5)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.TfidfVectorizer')
    @patch('science_data_kit.core.file_handling.topic_modeling.NMF')
    def test_extract_topics_nmf(self, mock_nmf_class, mock_vectorizer_class):
        """Test extracting topics using NMF."""
        # Set options to use NMF
        self.modeler.options.method = TopicModelingMethod.NMF
        
        # Mock the vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Mock the NMF model
        mock_nmf = MagicMock()
        mock_nmf.components_ = np.array([[0.1, 0.5, 0.3], [0.2, 0.1, 0.4]])
        mock_nmf.transform.return_value = np.array([[0.7, 0.3], [0.4, 0.6]])
        mock_nmf_class.return_value = mock_nmf
        
        # Extract topics
        result = self.modeler.extract_topics(["document1", "document2"])
        
        # Check the result
        self.assertEqual(len(result.topics), 2)
        self.assertEqual(result.method, TopicModelingMethod.NMF)
        self.assertEqual(result.topics[0].id, 0)
        self.assertEqual(result.topics[0].keywords[0][0], "word2")  # Highest weight in first topic
        self.assertEqual(result.topics[0].keywords[0][1], 0.5)
        self.assertEqual(result.topics[1].id, 1)
        self.assertEqual(result.topics[1].keywords[0][0], "word3")  # Highest weight in second topic
        self.assertEqual(result.topics[1].keywords[0][1], 0.4)
        self.assertEqual(len(result.document_topics), 2)
        self.assertEqual(result.document_topics[0][0][0], 0)  # First document, highest weight topic
        self.assertEqual(result.document_topics[0][0][1], 0.7)
        self.assertEqual(result.document_topics[1][0][0], 1)  # Second document, highest weight topic
        self.assertEqual(result.document_topics[1][0][1], 0.6)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.TfidfVectorizer')
    @patch('science_data_kit.core.file_handling.topic_modeling.TruncatedSVD')
    def test_extract_topics_lsa(self, mock_svd_class, mock_vectorizer_class):
        """Test extracting topics using LSA."""
        # Set options to use LSA
        self.modeler.options.method = TopicModelingMethod.LSA
        
        # Mock the vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Mock the SVD model
        mock_svd = MagicMock()
        mock_svd.components_ = np.array([[0.1, 0.5, 0.3], [0.2, 0.1, 0.4]])
        mock_svd.transform.return_value = np.array([[0.7, -0.3], [0.4, 0.6]])
        mock_svd_class.return_value = mock_svd
        
        # Extract topics
        result = self.modeler.extract_topics(["document1", "document2"])
        
        # Check the result
        self.assertEqual(len(result.topics), 2)
        self.assertEqual(result.method, TopicModelingMethod.LSA)
        self.assertEqual(result.topics[0].id, 0)
        self.assertEqual(result.topics[0].keywords[0][0], "word2")  # Highest weight in first topic
        self.assertEqual(result.topics[0].keywords[0][1], 0.5)
        self.assertEqual(result.topics[1].id, 1)
        self.assertEqual(result.topics[1].keywords[0][0], "word3")  # Highest weight in second topic
        self.assertEqual(result.topics[1].keywords[0][1], 0.4)
        self.assertEqual(len(result.document_topics), 2)
        self.assertEqual(result.document_topics[0][0][0], 0)  # First document, highest absolute weight topic
        self.assertEqual(result.document_topics[0][0][1], 0.7)
        self.assertEqual(result.document_topics[1][0][0], 1)  # Second document, highest absolute weight topic
        self.assertEqual(result.document_topics[1][0][1], 0.6)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.Dictionary')
    @patch('science_data_kit.core.file_handling.topic_modeling.LdaModel')
    @patch('science_data_kit.core.file_handling.topic_modeling.CoherenceModel')
    def test_extract_topics_gensim_lda(self, mock_coherence_model_class, mock_lda_model_class, mock_dictionary_class):
        """Test extracting topics using Gensim LDA."""
        # Set options to use Gensim LDA
        self.modeler.options.method = TopicModelingMethod.GENSIM_LDA
        
        # Mock the dictionary
        mock_dictionary = MagicMock()
        mock_dictionary.doc2bow.side_effect = lambda doc: [(0, 1), (1, 2), (2, 1)]
        mock_dictionary_class.return_value = mock_dictionary
        
        # Mock the LDA model
        mock_lda_model = MagicMock()
        mock_lda_model.show_topic.side_effect = lambda topic_idx, num_words: [
            ("word1", 0.5), ("word2", 0.3), ("word3", 0.2)
        ] if topic_idx == 0 else [
            ("word4", 0.6), ("word5", 0.3), ("word6", 0.1)
        ]
        mock_lda_model.get_document_topics.return_value = [(0, 0.7), (1, 0.3)]
        mock_lda_model.log_perplexity.return_value = 2.5
        mock_lda_model_class.return_value = mock_lda_model
        
        # Mock the coherence model
        mock_coherence_model = MagicMock()
        mock_coherence_model.get_coherence.return_value = 0.75
        mock_coherence_model_class.return_value = mock_coherence_model
        
        # Extract topics
        result = self.modeler.extract_topics(["document1 document2", "document3 document4"])
        
        # Check the result
        self.assertEqual(len(result.topics), 5)  # Default num_topics is 5
        self.assertEqual(result.method, TopicModelingMethod.GENSIM_LDA)
        self.assertEqual(result.topics[0].id, 0)
        self.assertEqual(result.topics[0].keywords[0][0], "word1")
        self.assertEqual(result.topics[0].keywords[0][1], 0.5)
        self.assertEqual(result.topics[1].id, 1)
        self.assertEqual(result.topics[1].keywords[0][0], "word4")
        self.assertEqual(result.topics[1].keywords[0][1], 0.6)
        self.assertEqual(len(result.document_topics), 2)
        self.assertEqual(result.document_topics[0][0][0], 0)  # First document, highest probability topic
        self.assertEqual(result.document_topics[0][0][1], 0.7)
        self.assertEqual(result.coherence_score, 0.75)
        self.assertEqual(result.perplexity, 2.5)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.extract_text_from_file')
    def test_extract_topics_from_files(self, mock_extract_text):
        """Test extracting topics from files."""
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="document1 text", metadata={"size": 100}),
            TextExtractionResult(text="document2 text", metadata={"size": 200}),
            None  # Failed extraction
        ]
        
        # Mock the extract_topics method
        with patch.object(self.modeler, 'extract_topics', return_value=TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=TopicModelingMethod.LDA
        )) as mock_extract_topics:
            result = self.modeler.extract_topics_from_files([
                "/path/to/file1.txt", "/path/to/file2.txt", "/path/to/file3.txt"
            ])
        
        # Check the result
        self.assertEqual(len(result.topics), 2)
        self.assertEqual(result.method, TopicModelingMethod.LDA)
        self.assertEqual(len(result.metadata["files"]), 2)  # Only 2 successful extractions
        self.assertEqual(result.metadata["files"][0]["file_path"], "/path/to/file1.txt")
        self.assertEqual(result.metadata["files"][0]["size"], 100)
        self.assertEqual(result.metadata["files"][1]["file_path"], "/path/to/file2.txt")
        self.assertEqual(result.metadata["files"][1]["size"], 200)
        
        # Check that extract_topics was called with the extracted texts
        mock_extract_topics.assert_called_once_with(["document1 text", "document2 text"])
    
    @patch('science_data_kit.core.file_handling.topic_modeling.extract_text_from_file')
    def test_extract_topics_from_files_all_failed(self, mock_extract_text):
        """Test extracting topics from files when all extractions fail."""
        # Mock the text extraction to fail for all files
        mock_extract_text.return_value = None
        
        # Extract topics from files
        result = self.modeler.extract_topics_from_files(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(len(result.topics), 0)
        self.assertEqual(result.method, TopicModelingMethod.LDA)
        self.assertEqual(result.metadata, {"error": "Failed to extract text from any of the provided files"})
    
    def test_get_document_topics_sklearn(self):
        """Test getting topics for a document using a scikit-learn model."""
        # Create a mock result with a scikit-learn model
        model = MagicMock()
        model.transform.return_value = np.array([[0.7, 0.3]])
        
        vectorizer = MagicMock()
        vectorizer.transform.return_value = np.array([[0.1, 0.2, 0.3]])
        
        result = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=TopicModelingMethod.LDA,
            model=model,
            vectorizer=vectorizer
        )
        
        # Get document topics
        topics = self.modeler.get_document_topics("new document", result)
        
        # Check the result
        self.assertEqual(len(topics), 2)
        self.assertEqual(topics[0][0], 0)  # Highest probability topic
        self.assertEqual(topics[0][1], 0.7)
        self.assertEqual(topics[1][0], 1)  # Second highest probability topic
        self.assertEqual(topics[1][1], 0.3)
    
    def test_get_document_topics_gensim(self):
        """Test getting topics for a document using a Gensim model."""
        # Set options to use Gensim LDA
        self.modeler.options.method = TopicModelingMethod.GENSIM_LDA
        
        # Create a mock result with a Gensim model
        model = MagicMock()
        model.get_document_topics.return_value = [(0, 0.7), (1, 0.3)]
        
        dictionary = MagicMock()
        dictionary.doc2bow.return_value = [(0, 1), (1, 2)]
        
        result = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=TopicModelingMethod.GENSIM_LDA,
            model=model,
            dictionary=dictionary
        )
        
        # Get document topics
        topics = self.modeler.get_document_topics("new document", result)
        
        # Check the result
        self.assertEqual(len(topics), 2)
        self.assertEqual(topics[0][0], 0)  # Highest probability topic
        self.assertEqual(topics[0][1], 0.7)
        self.assertEqual(topics[1][0], 1)  # Second highest probability topic
        self.assertEqual(topics[1][1], 0.3)
    
    def test_get_document_topics_no_model(self):
        """Test getting topics for a document when no model is available."""
        # Create a result with no model
        result = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=TopicModelingMethod.LDA
        )
        
        # Get document topics
        with patch('science_data_kit.core.file_handling.topic_modeling.logger') as mock_logger:
            topics = self.modeler.get_document_topics("new document", result)
        
        # Check the result
        self.assertEqual(len(topics), 0)
        mock_logger.error.assert_called_once()
    
    def test_get_document_topics_unsupported_method(self):
        """Test getting topics for a document with an unsupported method."""
        # Create a custom method
        class CustomMethod(str, Enum):
            CUSTOM = "custom"
        
        # Create a result with the custom method
        result = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=CustomMethod.CUSTOM,
            model=MagicMock(),
            vectorizer=MagicMock()
        )
        
        # Set options to use the custom method
        self.modeler.options.method = CustomMethod.CUSTOM
        
        # Get document topics
        with patch('science_data_kit.core.file_handling.topic_modeling.logger') as mock_logger:
            topics = self.modeler.get_document_topics("new document", result)
        
        # Check the result
        self.assertEqual(len(topics), 0)
        mock_logger.error.assert_called_once()


class TestHighLevelFunctions(unittest.TestCase):
    """Tests for the high-level functions."""
    
    @patch('science_data_kit.core.file_handling.topic_modeling.TopicModeler')
    def test_extract_topics(self, mock_modeler_class):
        """Test the extract_topics function."""
        # Mock the TopicModeler
        mock_modeler = MagicMock()
        mock_modeler.extract_topics.return_value = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=TopicModelingMethod.LDA
        )
        mock_modeler_class.return_value = mock_modeler
        
        # Extract topics
        topics = extract_topics(
            ["document1", "document2"],
            method=TopicModelingMethod.LDA,
            num_topics=2
        )
        
        # Check the result
        self.assertEqual(len(topics), 2)
        self.assertEqual(topics[0][0][0], "word1")
        self.assertEqual(topics[0][0][1], 0.8)
        self.assertEqual(topics[1][0][0], "word3")
        self.assertEqual(topics[1][0][1], 0.7)
        
        # Check that the modeler was created with the correct options
        mock_modeler_class.assert_called_once()
        options = mock_modeler_class.call_args[0][0]
        self.assertEqual(options.method, TopicModelingMethod.LDA)
        self.assertEqual(options.num_topics, 2)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.TopicModeler')
    def test_extract_topics_from_files(self, mock_modeler_class):
        """Test the extract_topics_from_files function."""
        # Mock the TopicModeler
        mock_modeler = MagicMock()
        mock_modeler.extract_topics_from_files.return_value = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
            ],
            method=TopicModelingMethod.LDA
        )
        mock_modeler_class.return_value = mock_modeler
        
        # Extract topics from files
        topics = extract_topics_from_files(
            ["/path/to/file1.txt", "/path/to/file2.txt"],
            method=TopicModelingMethod.LDA,
            num_topics=2
        )
        
        # Check the result
        self.assertEqual(len(topics), 2)
        self.assertEqual(topics[0][0][0], "word1")
        self.assertEqual(topics[0][0][1], 0.8)
        self.assertEqual(topics[1][0][0], "word3")
        self.assertEqual(topics[1][0][1], 0.7)
        
        # Check that the modeler was created with the correct options
        mock_modeler_class.assert_called_once()
        options = mock_modeler_class.call_args[0][0]
        self.assertEqual(options.method, TopicModelingMethod.LDA)
        self.assertEqual(options.num_topics, 2)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.TopicModeler')
    def test_compare_topic_modeling_methods(self, mock_modeler_class):
        """Test the compare_topic_modeling_methods function."""
        # Mock the TopicModeler
        mock_modeler = MagicMock()
        mock_modeler.extract_topics.side_effect = [
            # LDA result
            TopicModelingResult(
                topics=[
                    Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                    Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)])
                ],
                method=TopicModelingMethod.LDA
            ),
            # NMF result
            TopicModelingResult(
                topics=[
                    Topic(id=0, keywords=[("word5", 0.9), ("word6", 0.6)]),
                    Topic(id=1, keywords=[("word7", 0.8), ("word8", 0.5)])
                ],
                method=TopicModelingMethod.NMF
            ),
            # LSA result
            TopicModelingResult(
                topics=[
                    Topic(id=0, keywords=[("word9", 0.7), ("word10", 0.4)]),
                    Topic(id=1, keywords=[("word11", 0.6), ("word12", 0.3)])
                ],
                method=TopicModelingMethod.LSA
            ),
            # GENSIM_LDA result
            TopicModelingResult(
                topics=[
                    Topic(id=0, keywords=[("word13", 0.6), ("word14", 0.3)]),
                    Topic(id=1, keywords=[("word15", 0.5), ("word16", 0.2)])
                ],
                method=TopicModelingMethod.GENSIM_LDA
            )
        ]
        mock_modeler_class.return_value = mock_modeler
        
        # Mock the availability of scikit-learn and gensim
        with patch('science_data_kit.core.file_handling.topic_modeling.SKLEARN_AVAILABLE', True), \
             patch('science_data_kit.core.file_handling.topic_modeling.GENSIM_AVAILABLE', True):
            # Compare methods
            results = compare_topic_modeling_methods(
                ["document1", "document2"],
                num_topics=2
            )
        
        # Check the result
        self.assertIn("lda", results)
        self.assertIn("nmf", results)
        self.assertIn("lsa", results)
        self.assertIn("gensim_lda", results)
        self.assertEqual(len(results["lda"]), 2)
        self.assertEqual(results["lda"][0][0][0], "word1")
        self.assertEqual(results["lda"][0][0][1], 0.8)
        self.assertEqual(len(results["nmf"]), 2)
        self.assertEqual(results["nmf"][0][0][0], "word5")
        self.assertEqual(results["nmf"][0][0][1], 0.9)
        self.assertEqual(len(results["lsa"]), 2)
        self.assertEqual(results["lsa"][0][0][0], "word9")
        self.assertEqual(results["lsa"][0][0][1], 0.7)
        self.assertEqual(len(results["gensim_lda"]), 2)
        self.assertEqual(results["gensim_lda"][0][0][0], "word13")
        self.assertEqual(results["gensim_lda"][0][0][1], 0.6)
    
    @patch('science_data_kit.core.file_handling.topic_modeling.TopicModeler')
    def test_get_document_topics(self, mock_modeler_class):
        """Test the get_document_topics function."""
        # Mock the TopicModeler
        mock_modeler = MagicMock()
        mock_modeler.get_document_topics.return_value = [
            (0, 0.7), (1, 0.3), (2, 0.1)
        ]
        mock_modeler_class.return_value = mock_modeler
        
        # Create a result
        result = TopicModelingResult(
            topics=[
                Topic(id=0, keywords=[("word1", 0.8), ("word2", 0.5)]),
                Topic(id=1, keywords=[("word3", 0.7), ("word4", 0.4)]),
                Topic(id=2, keywords=[("word5", 0.6), ("word6", 0.3)])
            ],
            method=TopicModelingMethod.LDA
        )
        
        # Get document topics
        topics = get_document_topics("new document", result)
        
        # Check the result
        self.assertEqual(len(topics), 3)
        self.assertEqual(topics[0][0], 0)
        self.assertEqual(topics[0][1], 0.7)
        self.assertEqual(topics[1][0], 1)
        self.assertEqual(topics[1][1], 0.3)
        self.assertEqual(topics[2][0], 2)
        self.assertEqual(topics[2][1], 0.1)
        
        # Get document topics with limit
        topics = get_document_topics("new document", result, num_topics=2)
        
        # Check the result
        self.assertEqual(len(topics), 2)
        self.assertEqual(topics[0][0], 0)
        self.assertEqual(topics[0][1], 0.7)
        self.assertEqual(topics[1][0], 1)
        self.assertEqual(topics[1][1], 0.3)


if __name__ == '__main__':
    unittest.main()
"""
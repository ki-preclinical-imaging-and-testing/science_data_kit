"""
Tests for the content_analysis module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from science_data_kit.core.file_handling.content_analysis import (
    ContentFeatureType,
    ContentAnalysisOptions,
    ContentFeatures,
    ContentAnalysisResult,
    ContentAnalyzer,
    analyze_content,
    find_content_based_similar_files,
    get_document_important_terms,
    cluster_documents_by_content,
    visualize_document_clusters
)
from science_data_kit.core.file_handling.text_extraction import TextExtractionResult


class TestContentAnalysisOptions(unittest.TestCase):
    """Tests for the ContentAnalysisOptions class."""
    
    def test_default_initialization(self):
        """Test that default initialization works correctly."""
        options = ContentAnalysisOptions()
        self.assertEqual(options.feature_type, ContentFeatureType.TFIDF)
        self.assertEqual(options.max_features, 1000)
        self.assertEqual(options.ngram_range, (1, 2))
        self.assertEqual(options.min_df, 2)
        self.assertEqual(options.max_df, 0.9)
        self.assertTrue(options.lowercase)
        self.assertTrue(options.remove_stopwords)
        self.assertFalse(options.stemming)
        self.assertFalse(options.lemmatization)
        self.assertFalse(options.apply_dimensionality_reduction)
        self.assertEqual(options.n_components, 100)
        self.assertFalse(options.apply_clustering)
        self.assertEqual(options.eps, 0.5)
        self.assertEqual(options.min_samples, 5)
        self.assertIsNone(options.text_extraction_options)


class TestContentFeatures(unittest.TestCase):
    """Tests for the ContentFeatures class."""
    
    def test_initialization_with_array(self):
        """Test initialization with a numpy array."""
        features = np.array([0.1, 0.2, 0.3])
        content_features = ContentFeatures(
            file_path="/path/to/file.txt",
            feature_type=ContentFeatureType.TFIDF,
            features=features
        )
        
        self.assertEqual(content_features.file_path, "/path/to/file.txt")
        self.assertEqual(content_features.feature_type, ContentFeatureType.TFIDF)
        np.testing.assert_array_equal(content_features.features, features)
        self.assertIsNone(content_features.vocabulary)
        self.assertIsNone(content_features.feature_names)
        self.assertEqual(content_features.metadata, {})
    
    def test_initialization_with_list(self):
        """Test initialization with a list."""
        features = [0.1, 0.2, 0.3]
        content_features = ContentFeatures(
            file_path="/path/to/file.txt",
            feature_type=ContentFeatureType.WORD_EMBEDDINGS,
            features=features
        )
        
        self.assertEqual(content_features.file_path, "/path/to/file.txt")
        self.assertEqual(content_features.feature_type, ContentFeatureType.WORD_EMBEDDINGS)
        np.testing.assert_array_equal(content_features.features, np.array(features))
    
    def test_initialization_with_dict(self):
        """Test initialization with a dictionary."""
        features = {"term1": 0.1, "term2": 0.2, "term3": 0.3}
        vocabulary = {"term1": 0, "term2": 1, "term3": 2}
        
        content_features = ContentFeatures(
            file_path="/path/to/file.txt",
            feature_type=ContentFeatureType.TFIDF,
            features=features,
            vocabulary=vocabulary
        )
        
        self.assertEqual(content_features.file_path, "/path/to/file.txt")
        self.assertEqual(content_features.feature_type, ContentFeatureType.TFIDF)
        np.testing.assert_array_equal(content_features.features, np.array([0.1, 0.2, 0.3]))


class TestContentAnalysisResult(unittest.TestCase):
    """Tests for the ContentAnalysisResult class."""
    
    def test_initialization(self):
        """Test initialization."""
        files = ["/path/to/file1.txt", "/path/to/file2.txt"]
        features = [
            ContentFeatures(
                file_path="/path/to/file1.txt",
                feature_type=ContentFeatureType.TFIDF,
                features=np.array([0.1, 0.2, 0.3])
            ),
            ContentFeatures(
                file_path="/path/to/file2.txt",
                feature_type=ContentFeatureType.TFIDF,
                features=np.array([0.4, 0.5, 0.6])
            )
        ]
        
        result = ContentAnalysisResult(
            files=files,
            features=features,
            feature_type=ContentFeatureType.TFIDF
        )
        
        self.assertEqual(result.files, files)
        self.assertEqual(result.features, features)
        self.assertEqual(result.feature_type, ContentFeatureType.TFIDF)
        self.assertIsNone(result.similarity_matrix)
        self.assertIsNone(result.clusters)
        self.assertIsNone(result.reduced_features)
        self.assertEqual(result.metadata, {})


class TestContentAnalyzer(unittest.TestCase):
    """Tests for the ContentAnalyzer class."""
    
    def setUp(self):
        """Set up the test case."""
        self.analyzer = ContentAnalyzer()
    
    @patch('science_data_kit.core.file_handling.content_analysis.extract_text_from_file')
    def test_extract_features_no_valid_texts(self, mock_extract_text):
        """Test extracting features when no valid texts are found."""
        # Mock the text extraction to return None
        mock_extract_text.return_value = None
        
        # Extract features
        result = self.analyzer.extract_features(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result.files, [])
        self.assertEqual(result.features, [])
        self.assertEqual(result.feature_type, ContentFeatureType.TFIDF)
    
    @patch('science_data_kit.core.file_handling.content_analysis.extract_text_from_file')
    @patch('science_data_kit.core.file_handling.content_analysis.TfidfVectorizer')
    def test_extract_tfidf_features(self, mock_vectorizer_class, mock_extract_text):
        """Test extracting TF-IDF features."""
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            TextExtractionResult(text="This is file 2", metadata={})
        ]
        
        # Mock the TF-IDF vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer.vocabulary_ = {"word1": 0, "word2": 1, "word3": 2}
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Extract features
        result = self.analyzer.extract_features(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result.files, ["/path/to/file1.txt", "/path/to/file2.txt"])
        self.assertEqual(len(result.features), 2)
        self.assertEqual(result.feature_type, ContentFeatureType.TFIDF)
        self.assertIsNotNone(result.similarity_matrix)
    
    @patch('science_data_kit.core.file_handling.content_analysis.extract_text_from_file')
    @patch('science_data_kit.core.file_handling.content_analysis.TfidfVectorizer')
    def test_extract_tfidf_features_with_dimensionality_reduction(self, mock_vectorizer_class, mock_extract_text):
        """Test extracting TF-IDF features with dimensionality reduction."""
        # Set options with dimensionality reduction
        self.analyzer.options.apply_dimensionality_reduction = True
        self.analyzer.options.n_components = 2
        
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            TextExtractionResult(text="This is file 2", metadata={})
        ]
        
        # Mock the TF-IDF vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer.vocabulary_ = {"word1": 0, "word2": 1, "word3": 2}
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Extract features
        with patch('science_data_kit.core.file_handling.content_analysis.TruncatedSVD') as mock_svd_class:
            # Mock the SVD
            mock_svd = MagicMock()
            mock_svd.fit_transform.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
            mock_svd.explained_variance_ratio_ = np.array([0.8, 0.2])
            mock_svd_class.return_value = mock_svd
            
            result = self.analyzer.extract_features(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result.files, ["/path/to/file1.txt", "/path/to/file2.txt"])
        self.assertEqual(len(result.features), 2)
        self.assertEqual(result.feature_type, ContentFeatureType.TFIDF)
        self.assertIsNotNone(result.reduced_features)
        self.assertIsNotNone(result.similarity_matrix)
        self.assertIn("dimensionality_reduction", result.metadata)
    
    @patch('science_data_kit.core.file_handling.content_analysis.extract_text_from_file')
    @patch('science_data_kit.core.file_handling.content_analysis.TfidfVectorizer')
    def test_extract_tfidf_features_with_clustering(self, mock_vectorizer_class, mock_extract_text):
        """Test extracting TF-IDF features with clustering."""
        # Set options with clustering
        self.analyzer.options.apply_clustering = True
        
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            TextExtractionResult(text="This is file 2", metadata={})
        ]
        
        # Mock the TF-IDF vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer.vocabulary_ = {"word1": 0, "word2": 1, "word3": 2}
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Extract features
        with patch('science_data_kit.core.file_handling.content_analysis.DBSCAN') as mock_dbscan_class:
            # Mock the DBSCAN
            mock_dbscan = MagicMock()
            mock_dbscan.fit_predict.return_value = np.array([0, 1])
            mock_dbscan_class.return_value = mock_dbscan
            
            result = self.analyzer.extract_features(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result.files, ["/path/to/file1.txt", "/path/to/file2.txt"])
        self.assertEqual(len(result.features), 2)
        self.assertEqual(result.feature_type, ContentFeatureType.TFIDF)
        self.assertEqual(result.clusters, [0, 1])
        self.assertIsNotNone(result.similarity_matrix)
        self.assertIn("clustering", result.metadata)
    
    @patch('science_data_kit.core.file_handling.content_analysis.extract_text_from_file')
    def test_extract_word_embedding_features(self, mock_extract_text):
        """Test extracting word embedding features."""
        # Set options with word embeddings
        self.analyzer.options.feature_type = ContentFeatureType.WORD_EMBEDDINGS
        
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            TextExtractionResult(text="This is file 2", metadata={})
        ]
        
        # Mock spaCy
        with patch('science_data_kit.core.file_handling.content_analysis.spacy') as mock_spacy:
            # Mock the spaCy model
            mock_nlp = MagicMock()
            mock_doc1 = MagicMock()
            mock_doc1.vector = np.array([0.1, 0.2, 0.3])
            mock_doc2 = MagicMock()
            mock_doc2.vector = np.array([0.4, 0.5, 0.6])
            mock_nlp.side_effect = [mock_doc1, mock_doc2]
            mock_nlp.meta = {"name": "en_core_web_md", "vectors": {"width": 3}}
            mock_spacy.load.return_value = mock_nlp
            
            # Extract features
            result = self.analyzer.extract_features(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result.files, ["/path/to/file1.txt", "/path/to/file2.txt"])
        self.assertEqual(len(result.features), 2)
        self.assertEqual(result.feature_type, ContentFeatureType.WORD_EMBEDDINGS)
        self.assertIsNotNone(result.similarity_matrix)
    
    @patch('science_data_kit.core.file_handling.content_analysis.extract_text_from_file')
    def test_extract_doc_embedding_features(self, mock_extract_text):
        """Test extracting document embedding features."""
        # Set options with document embeddings
        self.analyzer.options.feature_type = ContentFeatureType.DOC_EMBEDDINGS
        
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            TextExtractionResult(text="This is file 2", metadata={})
        ]
        
        # Mock sentence-transformers
        with patch('science_data_kit.core.file_handling.content_analysis.SentenceTransformer', create=True) as mock_st_class:
            # Mock the SentenceTransformer model
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
            mock_model.get_sentence_embedding_dimension.return_value = 3
            mock_st_class.return_value = mock_model
            
            # Extract features
            result = self.analyzer.extract_features(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result.files, ["/path/to/file1.txt", "/path/to/file2.txt"])
        self.assertEqual(len(result.features), 2)
        self.assertEqual(result.feature_type, ContentFeatureType.DOC_EMBEDDINGS)
        self.assertIsNotNone(result.similarity_matrix)
    
    def test_find_similar_documents(self):
        """Test finding similar documents."""
        # Create a result with a similarity matrix
        similarity_matrix = np.array([
            [1.0, 0.8, 0.3],
            [0.8, 1.0, 0.6],
            [0.3, 0.6, 1.0]
        ])
        
        result = ContentAnalysisResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt", "/path/to/file3.txt"],
            features=[],
            feature_type=ContentFeatureType.TFIDF,
            similarity_matrix=similarity_matrix
        )
        
        # Find similar documents to file1
        similar_docs = self.analyzer.find_similar_documents(result, 0)
        
        # Check the result
        self.assertEqual(len(similar_docs), 1)  # Only file2 is above threshold
        self.assertEqual(similar_docs[0][0], 1)  # Index of file2
        self.assertEqual(similar_docs[0][1], 0.8)  # Similarity score
    
    def test_get_important_terms(self):
        """Test getting important terms."""
        # Create a result with TF-IDF features
        features = [
            ContentFeatures(
                file_path="/path/to/file1.txt",
                feature_type=ContentFeatureType.TFIDF,
                features=np.array([0.1, 0.5, 0.3]),
                feature_names=["word1", "word2", "word3"]
            )
        ]
        
        result = ContentAnalysisResult(
            files=["/path/to/file1.txt"],
            features=features,
            feature_type=ContentFeatureType.TFIDF
        )
        
        # Get important terms
        terms = self.analyzer.get_important_terms(result, 0, top_n=2)
        
        # Check the result
        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0][0], "word2")  # Highest TF-IDF score
        self.assertEqual(terms[0][1], 0.5)
        self.assertEqual(terms[1][0], "word3")  # Second highest TF-IDF score
        self.assertEqual(terms[1][1], 0.3)


class TestHighLevelFunctions(unittest.TestCase):
    """Tests for the high-level functions."""
    
    @patch('science_data_kit.core.file_handling.content_analysis.ContentAnalyzer')
    def test_analyze_content(self, mock_analyzer_class):
        """Test the analyze_content function."""
        # Mock the ContentAnalyzer
        mock_analyzer = MagicMock()
        mock_result = ContentAnalysisResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt"],
            features=[],
            feature_type=ContentFeatureType.TFIDF
        )
        mock_analyzer.extract_features.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer
        
        # Analyze content
        result = analyze_content(["/path/to/file1.txt", "/path/to/file2.txt"])
        
        # Check the result
        self.assertEqual(result, mock_result)
        mock_analyzer_class.assert_called_once()
        mock_analyzer.extract_features.assert_called_once_with(["/path/to/file1.txt", "/path/to/file2.txt"])
    
    @patch('science_data_kit.core.file_handling.content_analysis.ContentAnalyzer')
    def test_find_content_based_similar_files(self, mock_analyzer_class):
        """Test the find_content_based_similar_files function."""
        # Mock the ContentAnalyzer
        mock_analyzer = MagicMock()
        mock_result = ContentAnalysisResult(
            files=["/path/to/target.txt", "/path/to/file1.txt", "/path/to/file2.txt"],
            features=[],
            feature_type=ContentFeatureType.TFIDF
        )
        mock_analyzer.extract_features.return_value = mock_result
        mock_analyzer.find_similar_documents.return_value = [(1, 0.8), (2, 0.6)]
        mock_analyzer_class.return_value = mock_analyzer
        
        # Find similar files
        similar_files = find_content_based_similar_files(
            "/path/to/target.txt",
            ["/path/to/file1.txt", "/path/to/file2.txt"]
        )
        
        # Check the result
        self.assertEqual(len(similar_files), 2)
        self.assertEqual(similar_files[0][0], "/path/to/file1.txt")
        self.assertEqual(similar_files[0][1], 0.8)
        self.assertEqual(similar_files[1][0], "/path/to/file2.txt")
        self.assertEqual(similar_files[1][1], 0.6)
    
    @patch('science_data_kit.core.file_handling.content_analysis.ContentAnalyzer')
    def test_get_document_important_terms(self, mock_analyzer_class):
        """Test the get_document_important_terms function."""
        # Mock the ContentAnalyzer
        mock_analyzer = MagicMock()
        mock_result = ContentAnalysisResult(
            files=["/path/to/file.txt"],
            features=[],
            feature_type=ContentFeatureType.TFIDF
        )
        mock_analyzer.extract_features.return_value = mock_result
        mock_analyzer.get_important_terms.return_value = [("word1", 0.5), ("word2", 0.3)]
        mock_analyzer_class.return_value = mock_analyzer
        
        # Get important terms
        terms = get_document_important_terms("/path/to/file.txt")
        
        # Check the result
        self.assertEqual(terms, [("word1", 0.5), ("word2", 0.3)])
        mock_analyzer_class.assert_called_once()
        self.assertEqual(mock_analyzer_class.call_args[0][0].feature_type, ContentFeatureType.TFIDF)
    
    @patch('science_data_kit.core.file_handling.content_analysis.ContentAnalyzer')
    def test_cluster_documents_by_content(self, mock_analyzer_class):
        """Test the cluster_documents_by_content function."""
        # Mock the ContentAnalyzer
        mock_analyzer = MagicMock()
        mock_result = ContentAnalysisResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt", "/path/to/file3.txt"],
            features=[],
            feature_type=ContentFeatureType.TFIDF,
            clusters=[0, 0, 1]
        )
        mock_analyzer.extract_features.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer
        
        # Cluster documents
        clusters = cluster_documents_by_content([
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            "/path/to/file3.txt"
        ])
        
        # Check the result
        self.assertEqual(len(clusters), 2)
        self.assertEqual(set(clusters[0]), {"/path/to/file1.txt", "/path/to/file2.txt"})
        self.assertEqual(set(clusters[1]), {"/path/to/file3.txt"})
        mock_analyzer_class.assert_called_once()
        self.assertTrue(mock_analyzer_class.call_args[0][0].apply_clustering)
    
    @patch('science_data_kit.core.file_handling.content_analysis.ContentAnalyzer')
    def test_visualize_document_clusters(self, mock_analyzer_class):
        """Test the visualize_document_clusters function."""
        # Mock the ContentAnalyzer
        mock_analyzer = MagicMock()
        mock_result = ContentAnalysisResult(
            files=["/path/to/file1.txt", "/path/to/file2.txt", "/path/to/file3.txt"],
            features=[],
            feature_type=ContentFeatureType.TFIDF
        )
        mock_analyzer.extract_features.return_value = mock_result
        mock_analyzer.visualize_document_similarity.return_value = {
            "method": "t-SNE",
            "coordinates": [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
            "files": ["/path/to/file1.txt", "/path/to/file2.txt", "/path/to/file3.txt"],
            "clusters": [0, 0, 1]
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        # Visualize document clusters
        visualization_data = visualize_document_clusters(
            ["/path/to/file1.txt", "/path/to/file2.txt", "/path/to/file3.txt"],
            "/path/to/output.png"
        )
        
        # Check the result
        self.assertEqual(visualization_data["method"], "t-SNE")
        self.assertEqual(len(visualization_data["coordinates"]), 3)
        mock_analyzer_class.assert_called_once()
        self.assertTrue(mock_analyzer_class.call_args[0][0].apply_clustering)
        self.assertTrue(mock_analyzer_class.call_args[0][0].apply_dimensionality_reduction)


if __name__ == '__main__':
    unittest.main()
"""
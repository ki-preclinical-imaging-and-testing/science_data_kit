"""
Tests for the keyword_extraction module.
"""

import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from science_data_kit.core.file_handling.keyword_extraction import (
    KeywordExtractionMethod,
    KeywordExtractionOptions,
    Keyword,
    KeywordExtractionResult,
    KeywordExtractor,
    extract_keywords,
    extract_keywords_from_file,
    compare_keyword_extraction_methods,
    get_document_keywords
)
from science_data_kit.core.file_handling.text_extraction import TextExtractionResult


class TestKeywordExtractionOptions(unittest.TestCase):
    """Tests for the KeywordExtractionOptions class."""
    
    def test_default_initialization(self):
        """Test that default initialization works correctly."""
        options = KeywordExtractionOptions()
        self.assertEqual(options.method, KeywordExtractionMethod.TFIDF)
        self.assertEqual(options.num_keywords, 10)
        self.assertEqual(options.min_word_length, 3)
        self.assertTrue(options.include_ngrams)
        self.assertEqual(options.ngram_range, (1, 3))
        self.assertTrue(options.lowercase)
        self.assertTrue(options.remove_punctuation)
        self.assertTrue(options.remove_stopwords)
        self.assertEqual(options.language, "english")
        self.assertEqual(options.min_df, 1)
        self.assertEqual(options.max_df, 0.9)
        self.assertEqual(options.window_size, 4)
        self.assertEqual(options.damping_factor, 0.85)
        self.assertEqual(options.convergence_threshold, 0.0001)
        self.assertEqual(options.max_iterations, 100)
        self.assertEqual(options.min_chars_per_word, 2)
        self.assertEqual(options.max_words_per_phrase, 4)
        self.assertEqual(options.min_phrase_frequency, 1)
        self.assertEqual(options.max_ngram_size, 3)
        self.assertEqual(options.deduplication_threshold, 0.9)
        self.assertEqual(options.deduplication_function, "seqm")
        self.assertIsNone(options.text_extraction_options)


class TestKeyword(unittest.TestCase):
    """Tests for the Keyword class."""
    
    def test_initialization(self):
        """Test initialization."""
        keyword = Keyword(text="example", score=0.75)
        self.assertEqual(keyword.text, "example")
        self.assertEqual(keyword.score, 0.75)
        self.assertEqual(keyword.metadata, {})
    
    def test_str_representation(self):
        """Test string representation."""
        keyword = Keyword(text="example", score=0.75)
        self.assertEqual(str(keyword), "example (0.7500)")


class TestKeywordExtractionResult(unittest.TestCase):
    """Tests for the KeywordExtractionResult class."""
    
    def test_initialization(self):
        """Test initialization."""
        keywords = [
            Keyword(text="example", score=0.75),
            Keyword(text="test", score=0.5)
        ]
        result = KeywordExtractionResult(
            keywords=keywords,
            method=KeywordExtractionMethod.TFIDF
        )
        self.assertEqual(result.keywords, keywords)
        self.assertEqual(result.method, KeywordExtractionMethod.TFIDF)
        self.assertIsNone(result.text_summary)
        self.assertEqual(result.metadata, {})
    
    def test_str_representation(self):
        """Test string representation."""
        keywords = [
            Keyword(text="example", score=0.75),
            Keyword(text="test", score=0.5)
        ]
        result = KeywordExtractionResult(
            keywords=keywords,
            method=KeywordExtractionMethod.TFIDF
        )
        expected_str = "\n".join([
            "Method: tfidf",
            "Keywords: example (0.7500), test (0.5000)",
            "Total keywords: 2"
        ])
        self.assertEqual(str(result), expected_str)


class TestKeywordExtractor(unittest.TestCase):
    """Tests for the KeywordExtractor class."""
    
    def setUp(self):
        """Set up the test case."""
        self.extractor = KeywordExtractor()
    
    def test_load_stopwords(self):
        """Test loading stopwords."""
        stopwords = self.extractor._load_stopwords()
        self.assertIsInstance(stopwords, set)
        self.assertGreater(len(stopwords), 0)
        self.assertIn("the", stopwords)
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        text = "This is an Example Text with Punctuation!"
        processed_text = self.extractor._preprocess_text(text)
        self.assertEqual(processed_text, "this is an example text with punctuation")
        
        # Test with different options
        extractor = KeywordExtractor(KeywordExtractionOptions(
            lowercase=False,
            remove_punctuation=False
        ))
        processed_text = extractor._preprocess_text(text)
        self.assertEqual(processed_text, "This is an Example Text with Punctuation!")
    
    def test_extract_keywords_empty_text(self):
        """Test extracting keywords from empty text."""
        result = self.extractor.extract_keywords("")
        self.assertEqual(len(result.keywords), 0)
        self.assertEqual(result.method, KeywordExtractionMethod.TFIDF)
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.TfidfVectorizer')
    def test_extract_keywords_tfidf(self, mock_vectorizer_class):
        """Test extracting keywords using TF-IDF."""
        # Mock the TF-IDF vectorizer
        mock_vectorizer = MagicMock()
        mock_vectorizer.fit_transform.return_value = np.array([[0.1, 0.5, 0.3]])
        mock_vectorizer.get_feature_names_out.return_value = np.array(["word1", "word2", "word3"])
        mock_vectorizer_class.return_value = mock_vectorizer
        
        # Extract keywords
        result = self.extractor.extract_keywords("This is a test document")
        
        # Check the result
        self.assertEqual(len(result.keywords), 3)
        self.assertEqual(result.method, KeywordExtractionMethod.TFIDF)
        self.assertEqual(result.keywords[0].text, "word2")  # Highest score
        self.assertEqual(result.keywords[0].score, 0.5)
        self.assertEqual(result.keywords[1].text, "word3")  # Second highest score
        self.assertEqual(result.keywords[1].score, 0.3)
        self.assertEqual(result.keywords[2].text, "word1")  # Lowest score
        self.assertEqual(result.keywords[2].score, 0.1)
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.KeywordExtractor._split_into_sentences')
    @patch('science_data_kit.core.file_handling.keyword_extraction.KeywordExtractor._build_word_graph')
    @patch('science_data_kit.core.file_handling.keyword_extraction.KeywordExtractor._apply_textrank')
    def test_extract_keywords_textrank(self, mock_apply_textrank, mock_build_graph, mock_split_sentences):
        """Test extracting keywords using TextRank."""
        # Set options to use TextRank
        self.extractor.options.method = KeywordExtractionMethod.TEXTRANK
        
        # Mock the TextRank components
        mock_split_sentences.return_value = [["this", "is", "test"], ["another", "test"]]
        mock_build_graph.return_value = {"test": {"is": 0.5}, "is": {"test": 0.5}}
        mock_apply_textrank.return_value = {"test": 0.8, "is": 0.6, "another": 0.4}
        
        # Extract keywords
        result = self.extractor.extract_keywords("This is a test. Another test.")
        
        # Check the result
        self.assertEqual(len(result.keywords), 3)
        self.assertEqual(result.method, KeywordExtractionMethod.TEXTRANK)
        self.assertEqual(result.keywords[0].text, "test")  # Highest score
        self.assertEqual(result.keywords[0].score, 0.8)
        self.assertEqual(result.keywords[1].text, "is")  # Second highest score
        self.assertEqual(result.keywords[1].score, 0.6)
        self.assertEqual(result.keywords[2].text, "another")  # Lowest score
        self.assertEqual(result.keywords[2].score, 0.4)
    
    def test_split_into_sentences(self):
        """Test splitting text into sentences."""
        text = "This is a test. Another test with multiple words."
        sentences = self.extractor._split_into_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertIn("test", sentences[0])
        self.assertIn("another", sentences[1])
        
        # Test with stopwords removal
        self.extractor.options.remove_stopwords = True
        sentences = self.extractor._split_into_sentences(text)
        self.assertNotIn("is", sentences[0])  # "is" should be removed as a stopword
    
    def test_build_word_graph(self):
        """Test building a word graph."""
        sentences = [["this", "is", "test"], ["another", "test"]]
        graph = self.extractor._build_word_graph(sentences)
        self.assertIn("test", graph)
        self.assertIn("is", graph["test"])
        self.assertGreater(graph["test"]["is"], 0)
    
    def test_apply_textrank(self):
        """Test applying TextRank algorithm."""
        graph = {
            "test": {"is": 0.5, "another": 0.5},
            "is": {"test": 1.0},
            "another": {"test": 1.0}
        }
        scores = self.extractor._apply_textrank(graph)
        self.assertIn("test", scores)
        self.assertIn("is", scores)
        self.assertIn("another", scores)
        self.assertGreater(scores["test"], 0)
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.re.split')
    @patch('science_data_kit.core.file_handling.keyword_extraction.Counter')
    def test_extract_keywords_rake(self, mock_counter, mock_split):
        """Test extracting keywords using RAKE."""
        # Set options to use RAKE
        self.extractor.options.method = KeywordExtractionMethod.RAKE
        
        # Mock the RAKE components
        mock_split.return_value = ["keyword extraction", "test document"]
        mock_counter.return_value = {"keyword extraction": 1, "test document": 1}
        
        # Extract keywords
        with patch.object(self.extractor, '_extract_keywords_rake', return_value=KeywordExtractionResult(
            keywords=[
                Keyword(text="keyword extraction", score=0.8),
                Keyword(text="test document", score=0.6)
            ],
            method=KeywordExtractionMethod.RAKE
        )):
            result = self.extractor.extract_keywords("This is a test document for keyword extraction.")
        
        # Check the result
        self.assertEqual(len(result.keywords), 2)
        self.assertEqual(result.method, KeywordExtractionMethod.RAKE)
        self.assertEqual(result.keywords[0].text, "keyword extraction")
        self.assertEqual(result.keywords[0].score, 0.8)
        self.assertEqual(result.keywords[1].text, "test document")
        self.assertEqual(result.keywords[1].score, 0.6)
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.extract_text_from_file')
    def test_extract_keywords_from_file(self, mock_extract_text):
        """Test extracting keywords from a file."""
        # Mock the text extraction
        mock_extract_text.return_value = TextExtractionResult(
            text="This is a test document for keyword extraction.",
            metadata={}
        )
        
        # Extract keywords from file
        with patch.object(self.extractor, 'extract_keywords', return_value=KeywordExtractionResult(
            keywords=[
                Keyword(text="keyword", score=0.8),
                Keyword(text="extraction", score=0.7),
                Keyword(text="test", score=0.6)
            ],
            method=KeywordExtractionMethod.TFIDF
        )):
            result = self.extractor.extract_keywords_from_file("/path/to/file.txt")
        
        # Check the result
        self.assertEqual(len(result.keywords), 3)
        self.assertEqual(result.method, KeywordExtractionMethod.TFIDF)
        self.assertEqual(result.metadata["file_path"], "/path/to/file.txt")
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.extract_text_from_file')
    def test_extract_keywords_from_file_error(self, mock_extract_text):
        """Test extracting keywords from a file with an error."""
        # Mock the text extraction to fail
        mock_extract_text.return_value = None
        
        # Extract keywords from file
        result = self.extractor.extract_keywords_from_file("/path/to/file.txt")
        
        # Check the result
        self.assertEqual(len(result.keywords), 0)
        self.assertEqual(result.method, KeywordExtractionMethod.TFIDF)
        self.assertEqual(result.metadata["file_path"], "/path/to/file.txt")
        self.assertEqual(result.metadata["error"], "Text extraction failed")


class TestHighLevelFunctions(unittest.TestCase):
    """Tests for the high-level functions."""
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.KeywordExtractor')
    def test_extract_keywords(self, mock_extractor_class):
        """Test the extract_keywords function."""
        # Mock the KeywordExtractor
        mock_extractor = MagicMock()
        mock_extractor.extract_keywords.return_value = KeywordExtractionResult(
            keywords=[
                Keyword(text="keyword", score=0.8),
                Keyword(text="extraction", score=0.7)
            ],
            method=KeywordExtractionMethod.TFIDF
        )
        mock_extractor_class.return_value = mock_extractor
        
        # Extract keywords
        keywords = extract_keywords(
            "This is a test document for keyword extraction.",
            method=KeywordExtractionMethod.TFIDF,
            num_keywords=2
        )
        
        # Check the result
        self.assertEqual(len(keywords), 2)
        self.assertEqual(keywords[0][0], "keyword")
        self.assertEqual(keywords[0][1], 0.8)
        self.assertEqual(keywords[1][0], "extraction")
        self.assertEqual(keywords[1][1], 0.7)
        
        # Check that the extractor was created with the correct options
        mock_extractor_class.assert_called_once()
        options = mock_extractor_class.call_args[0][0]
        self.assertEqual(options.method, KeywordExtractionMethod.TFIDF)
        self.assertEqual(options.num_keywords, 2)
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.KeywordExtractor')
    def test_extract_keywords_from_file(self, mock_extractor_class):
        """Test the extract_keywords_from_file function."""
        # Mock the KeywordExtractor
        mock_extractor = MagicMock()
        mock_extractor.extract_keywords_from_file.return_value = KeywordExtractionResult(
            keywords=[
                Keyword(text="keyword", score=0.8),
                Keyword(text="extraction", score=0.7)
            ],
            method=KeywordExtractionMethod.TFIDF
        )
        mock_extractor_class.return_value = mock_extractor
        
        # Extract keywords from file
        keywords = extract_keywords_from_file(
            "/path/to/file.txt",
            method=KeywordExtractionMethod.TFIDF,
            num_keywords=2
        )
        
        # Check the result
        self.assertEqual(len(keywords), 2)
        self.assertEqual(keywords[0][0], "keyword")
        self.assertEqual(keywords[0][1], 0.8)
        self.assertEqual(keywords[1][0], "extraction")
        self.assertEqual(keywords[1][1], 0.7)
        
        # Check that the extractor was created with the correct options
        mock_extractor_class.assert_called_once()
        options = mock_extractor_class.call_args[0][0]
        self.assertEqual(options.method, KeywordExtractionMethod.TFIDF)
        self.assertEqual(options.num_keywords, 2)
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.extract_keywords')
    def test_compare_keyword_extraction_methods(self, mock_extract_keywords):
        """Test the compare_keyword_extraction_methods function."""
        # Mock the extract_keywords function
        mock_extract_keywords.side_effect = [
            [("keyword", 0.8), ("extraction", 0.7)],  # TFIDF
            [("extraction", 0.9), ("keyword", 0.6)],  # TextRank
            [("keyword extraction", 0.8)],  # RAKE
            Exception("YAKE error")  # YAKE (error)
        ]
        
        # Compare methods
        results = compare_keyword_extraction_methods(
            "This is a test document for keyword extraction.",
            num_keywords=2
        )
        
        # Check the result
        self.assertIn("tfidf", results)
        self.assertIn("textrank", results)
        self.assertIn("rake", results)
        self.assertIn("yake", results)
        self.assertEqual(len(results["tfidf"]), 2)
        self.assertEqual(len(results["textrank"]), 2)
        self.assertEqual(len(results["rake"]), 1)
        self.assertEqual(len(results["yake"]), 0)  # Error case
    
    @patch('science_data_kit.core.file_handling.keyword_extraction.extract_keywords_from_file')
    def test_get_document_keywords(self, mock_extract_keywords_from_file):
        """Test the get_document_keywords function."""
        # Mock the extract_keywords_from_file function
        mock_extract_keywords_from_file.return_value = [
            ("keyword", 0.8),
            ("extraction", 0.7)
        ]
        
        # Get document keywords
        keywords = get_document_keywords(
            "/path/to/file.txt",
            num_keywords=2,
            method=KeywordExtractionMethod.TFIDF
        )
        
        # Check the result
        self.assertEqual(len(keywords), 2)
        self.assertEqual(keywords[0][0], "keyword")
        self.assertEqual(keywords[0][1], 0.8)
        self.assertEqual(keywords[1][0], "extraction")
        self.assertEqual(keywords[1][1], 0.7)
        
        # Check that extract_keywords_from_file was called with the correct arguments
        mock_extract_keywords_from_file.assert_called_once_with(
            "/path/to/file.txt",
            method=KeywordExtractionMethod.TFIDF,
            num_keywords=2
        )


if __name__ == '__main__':
    unittest.main()
"""
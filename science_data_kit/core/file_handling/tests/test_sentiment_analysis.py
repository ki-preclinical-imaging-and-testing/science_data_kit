"""
Tests for the sentiment_analysis module.

This module contains unit tests for the sentiment_analysis module, which provides
functionality for analyzing sentiment in text content, integrating with the AI
service framework to leverage external sentiment analysis services.
"""

import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import json
from pathlib import Path

from science_data_kit.core.file_handling.sentiment_analysis import (
    SentimentPolarity,
    SentimentScore,
    SentenceSentiment,
    SentimentAnalysisResult,
    SentimentAnalysisOptions,
    analyze_sentiment,
    analyze_text_file_sentiment,
    visualize_sentiment,
    generate_sentiment_report
)
from science_data_kit.core.file_handling.ai_service_integration import (
    TextAnalysisResult
)


class TestSentimentPolarity(unittest.TestCase):
    """Tests for the SentimentPolarity enum."""

    def test_sentiment_polarity_values(self):
        """Test sentiment polarity enum values."""
        self.assertEqual(SentimentPolarity.VERY_NEGATIVE.value, "very_negative")
        self.assertEqual(SentimentPolarity.NEGATIVE.value, "negative")
        self.assertEqual(SentimentPolarity.NEUTRAL.value, "neutral")
        self.assertEqual(SentimentPolarity.POSITIVE.value, "positive")
        self.assertEqual(SentimentPolarity.VERY_POSITIVE.value, "very_positive")


class TestSentimentScore(unittest.TestCase):
    """Tests for the SentimentScore class."""

    def test_sentiment_score_creation(self):
        """Test creating a sentiment score."""
        score = SentimentScore(score=0.8, magnitude=1.5, polarity=SentimentPolarity.POSITIVE)
        self.assertEqual(score.score, 0.8)
        self.assertEqual(score.magnitude, 1.5)
        self.assertEqual(score.polarity, SentimentPolarity.POSITIVE)

    def test_sentiment_score_polarity_calculation(self):
        """Test that polarity is calculated correctly based on score."""
        # Very negative
        score = SentimentScore(score=-0.8, magnitude=1.0, polarity=SentimentPolarity.NEUTRAL)
        self.assertEqual(score.polarity, SentimentPolarity.VERY_NEGATIVE)

        # Negative
        score = SentimentScore(score=-0.5, magnitude=1.0, polarity=SentimentPolarity.NEUTRAL)
        self.assertEqual(score.polarity, SentimentPolarity.NEGATIVE)

        # Neutral
        score = SentimentScore(score=0.0, magnitude=1.0, polarity=SentimentPolarity.NEUTRAL)
        self.assertEqual(score.polarity, SentimentPolarity.NEUTRAL)

        # Positive
        score = SentimentScore(score=0.5, magnitude=1.0, polarity=SentimentPolarity.NEUTRAL)
        self.assertEqual(score.polarity, SentimentPolarity.POSITIVE)

        # Very positive
        score = SentimentScore(score=0.8, magnitude=1.0, polarity=SentimentPolarity.NEUTRAL)
        self.assertEqual(score.polarity, SentimentPolarity.VERY_POSITIVE)


class TestSentenceSentiment(unittest.TestCase):
    """Tests for the SentenceSentiment class."""

    def test_sentence_sentiment_creation(self):
        """Test creating a sentence sentiment."""
        sentence = SentenceSentiment(
            text="This is a test sentence.",
            score=0.6,
            magnitude=1.2,
            polarity=SentimentPolarity.POSITIVE,
            start_offset=10
        )
        self.assertEqual(sentence.text, "This is a test sentence.")
        self.assertEqual(sentence.score, 0.6)
        self.assertEqual(sentence.magnitude, 1.2)
        self.assertEqual(sentence.polarity, SentimentPolarity.POSITIVE)
        self.assertEqual(sentence.start_offset, 10)

    def test_sentence_sentiment_polarity_calculation(self):
        """Test that polarity is calculated correctly based on score."""
        # Very negative
        sentence = SentenceSentiment(text="Test", score=-0.8, magnitude=1.0, polarity=None)
        self.assertEqual(sentence.polarity, SentimentPolarity.VERY_NEGATIVE)

        # Negative
        sentence = SentenceSentiment(text="Test", score=-0.5, magnitude=1.0, polarity=None)
        self.assertEqual(sentence.polarity, SentimentPolarity.NEGATIVE)

        # Neutral
        sentence = SentenceSentiment(text="Test", score=0.0, magnitude=1.0, polarity=None)
        self.assertEqual(sentence.polarity, SentimentPolarity.NEUTRAL)

        # Positive
        sentence = SentenceSentiment(text="Test", score=0.5, magnitude=1.0, polarity=None)
        self.assertEqual(sentence.polarity, SentimentPolarity.POSITIVE)

        # Very positive
        sentence = SentenceSentiment(text="Test", score=0.8, magnitude=1.0, polarity=None)
        self.assertEqual(sentence.polarity, SentimentPolarity.VERY_POSITIVE)


class TestSentimentAnalysisResult(unittest.TestCase):
    """Tests for the SentimentAnalysisResult class."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_sentiment = SentimentScore(
            score=0.3,
            magnitude=1.5,
            polarity=SentimentPolarity.POSITIVE
        )

        self.sentences = [
            SentenceSentiment(
                text="This is a positive sentence.",
                score=0.8,
                magnitude=1.2,
                polarity=SentimentPolarity.VERY_POSITIVE,
                start_offset=0
            ),
            SentenceSentiment(
                text="This is a neutral sentence.",
                score=0.1,
                magnitude=0.5,
                polarity=SentimentPolarity.NEUTRAL,
                start_offset=28
            ),
            SentenceSentiment(
                text="This is a negative sentence.",
                score=-0.6,
                magnitude=1.0,
                polarity=SentimentPolarity.NEGATIVE,
                start_offset=56
            )
        ]

        self.result = SentimentAnalysisResult(
            text="This is a positive sentence. This is a neutral sentence. This is a negative sentence.",
            document_sentiment=self.document_sentiment,
            sentences=self.sentences,
            language="en",
            metadata={"text_length": 84, "sentence_count": 3}
        )

    def test_sentiment_analysis_result_creation(self):
        """Test creating a sentiment analysis result."""
        self.assertEqual(self.result.text, "This is a positive sentence. This is a neutral sentence. This is a negative sentence.")
        self.assertEqual(self.result.document_sentiment, self.document_sentiment)
        self.assertEqual(self.result.sentences, self.sentences)
        self.assertEqual(self.result.language, "en")
        self.assertEqual(self.result.metadata["text_length"], 84)
        self.assertEqual(self.result.metadata["sentence_count"], 3)

    def test_average_sentence_score(self):
        """Test calculating average sentence score."""
        # (0.8 + 0.1 + -0.6) / 3 = 0.1
        self.assertAlmostEqual(self.result.average_sentence_score, 0.1)

    def test_average_sentence_magnitude(self):
        """Test calculating average sentence magnitude."""
        # (1.2 + 0.5 + 1.0) / 3 = 0.9
        self.assertAlmostEqual(self.result.average_sentence_magnitude, 0.9)

    def test_sentiment_distribution(self):
        """Test getting sentiment distribution."""
        distribution = self.result.sentiment_distribution
        self.assertEqual(distribution[SentimentPolarity.VERY_NEGATIVE], 0)
        self.assertEqual(distribution[SentimentPolarity.NEGATIVE], 1)
        self.assertEqual(distribution[SentimentPolarity.NEUTRAL], 1)
        self.assertEqual(distribution[SentimentPolarity.POSITIVE], 0)
        self.assertEqual(distribution[SentimentPolarity.VERY_POSITIVE], 1)

    def test_most_positive_sentences(self):
        """Test getting most positive sentences."""
        positive_sentences = self.result.most_positive_sentences
        self.assertEqual(len(positive_sentences), 3)
        self.assertEqual(positive_sentences[0], self.sentences[0])  # score 0.8
        self.assertEqual(positive_sentences[1], self.sentences[1])  # score 0.1
        self.assertEqual(positive_sentences[2], self.sentences[2])  # score -0.6

    def test_most_negative_sentences(self):
        """Test getting most negative sentences."""
        negative_sentences = self.result.most_negative_sentences
        self.assertEqual(len(negative_sentences), 3)
        self.assertEqual(negative_sentences[0], self.sentences[2])  # score -0.6
        self.assertEqual(negative_sentences[1], self.sentences[1])  # score 0.1
        self.assertEqual(negative_sentences[2], self.sentences[0])  # score 0.8

    def test_most_emotional_sentences(self):
        """Test getting most emotional sentences."""
        emotional_sentences = self.result.most_emotional_sentences
        self.assertEqual(len(emotional_sentences), 3)
        self.assertEqual(emotional_sentences[0], self.sentences[0])  # magnitude 1.2
        self.assertEqual(emotional_sentences[1], self.sentences[2])  # magnitude 1.0
        self.assertEqual(emotional_sentences[2], self.sentences[1])  # magnitude 0.5


class TestSentimentAnalysisOptions(unittest.TestCase):
    """Tests for the SentimentAnalysisOptions class."""

    def test_sentiment_analysis_options_defaults(self):
        """Test default sentiment analysis options."""
        options = SentimentAnalysisOptions()
        self.assertIsNone(options.language)
        self.assertTrue(options.extract_sentences)
        self.assertEqual(options.min_text_length, 10)
        self.assertIsNone(options.text_extraction_options)

    def test_sentiment_analysis_options_custom(self):
        """Test custom sentiment analysis options."""
        options = SentimentAnalysisOptions(
            language="fr",
            extract_sentences=False,
            min_text_length=20
        )
        self.assertEqual(options.language, "fr")
        self.assertFalse(options.extract_sentences)
        self.assertEqual(options.min_text_length, 20)


class TestAnalyzeSentiment(unittest.TestCase):
    """Tests for the analyze_sentiment function."""

    @patch('science_data_kit.core.file_handling.sentiment_analysis.analyze_text')
    def test_analyze_sentiment(self, mock_analyze_text):
        """Test analyzing sentiment in text."""
        # Mock the analyze_text function
        mock_result = MagicMock(spec=TextAnalysisResult)
        mock_result.success = True
        mock_result.service_name = "test_service"
        mock_result.sentiment = {
            'score': 0.5,
            'magnitude': 1.0,
            'sentences': [
                {
                    'text': 'This is a test sentence.',
                    'score': 0.5,
                    'magnitude': 1.0,
                    'start': 0
                }
            ]
        }
        mock_result.language = {'language_code': 'en'}
        mock_analyze_text.return_value = mock_result

        # Call the analyze_sentiment function
        text = "This is a test sentence."
        result = analyze_sentiment(text)

        # Check that analyze_text was called
        mock_analyze_text.assert_called_once()

        # Check the result
        self.assertEqual(result.text, text)
        self.assertEqual(result.document_sentiment.score, 0.5)
        self.assertEqual(result.document_sentiment.magnitude, 1.0)
        self.assertEqual(result.document_sentiment.polarity, SentimentPolarity.POSITIVE)
        self.assertEqual(len(result.sentences), 1)
        self.assertEqual(result.sentences[0].text, 'This is a test sentence.')
        self.assertEqual(result.sentences[0].score, 0.5)
        self.assertEqual(result.sentences[0].magnitude, 1.0)
        self.assertEqual(result.sentences[0].polarity, SentimentPolarity.POSITIVE)
        self.assertEqual(result.language, 'en')
        self.assertEqual(result.metadata['service'], 'test_service')

    @patch('science_data_kit.core.file_handling.sentiment_analysis.analyze_text')
    def test_analyze_sentiment_with_language(self, mock_analyze_text):
        """Test analyzing sentiment with specified language."""
        # Mock the analyze_text function
        mock_result = MagicMock(spec=TextAnalysisResult)
        mock_result.success = True
        mock_result.service_name = "test_service"
        mock_result.sentiment = {
            'score': 0.5,
            'magnitude': 1.0
        }
        mock_analyze_text.return_value = mock_result

        # Call the analyze_sentiment function with language
        text = "C'est un test."
        options = SentimentAnalysisOptions(language="fr")
        analyze_sentiment(text, options)

        # Check that analyze_text was called with language
        mock_analyze_text.assert_called_once_with(text, ['sentiment'], language="fr")

    @patch('science_data_kit.core.file_handling.sentiment_analysis.analyze_text')
    def test_analyze_sentiment_without_sentences(self, mock_analyze_text):
        """Test analyzing sentiment without extracting sentences."""
        # Mock the analyze_text function
        mock_result = MagicMock(spec=TextAnalysisResult)
        mock_result.success = True
        mock_result.service_name = "test_service"
        mock_result.sentiment = {
            'score': 0.5,
            'magnitude': 1.0
        }
        mock_analyze_text.return_value = mock_result

        # Call the analyze_sentiment function with extract_sentences=False
        text = "This is a test sentence."
        options = SentimentAnalysisOptions(extract_sentences=False)
        result = analyze_sentiment(text, options)

        # Check the result
        self.assertEqual(result.text, text)
        self.assertEqual(result.document_sentiment.score, 0.5)
        self.assertEqual(result.document_sentiment.magnitude, 1.0)
        self.assertEqual(len(result.sentences), 0)

    def test_analyze_sentiment_text_too_short(self):
        """Test analyzing sentiment with text that is too short."""
        # Call the analyze_sentiment function with short text
        text = "Short"
        options = SentimentAnalysisOptions(min_text_length=10)
        result = analyze_sentiment(text, options)

        # Check the result
        self.assertEqual(result.text, text)
        self.assertEqual(result.document_sentiment.score, 0.0)
        self.assertEqual(result.document_sentiment.magnitude, 0.0)
        self.assertEqual(result.document_sentiment.polarity, SentimentPolarity.NEUTRAL)
        self.assertEqual(len(result.sentences), 0)

    @patch('science_data_kit.core.file_handling.sentiment_analysis.analyze_text')
    def test_analyze_sentiment_failure(self, mock_analyze_text):
        """Test analyzing sentiment when the analysis fails."""
        # Mock the analyze_text function to return a failed result
        mock_result = MagicMock(spec=TextAnalysisResult)
        mock_result.success = False
        mock_result.service_name = "test_service"
        mock_result.sentiment = None
        mock_analyze_text.return_value = mock_result

        # Call the analyze_sentiment function
        text = "This is a test sentence."
        result = analyze_sentiment(text)

        # Check the result
        self.assertEqual(result.text, text)
        self.assertEqual(result.document_sentiment.score, 0.0)
        self.assertEqual(result.document_sentiment.magnitude, 0.0)
        self.assertEqual(result.document_sentiment.polarity, SentimentPolarity.NEUTRAL)
        self.assertEqual(len(result.sentences), 0)
        self.assertEqual(result.raw_result, mock_result)


class TestAnalyzeTextFileSentiment(unittest.TestCase):
    """Tests for the analyze_text_file_sentiment function."""

    @patch('science_data_kit.core.file_handling.sentiment_analysis.extract_text_from_file')
    @patch('science_data_kit.core.file_handling.sentiment_analysis.analyze_sentiment')
    def test_analyze_text_file_sentiment(self, mock_analyze_sentiment, mock_extract_text):
        """Test analyzing sentiment in a text file."""
        # Mock the extract_text_from_file function
        mock_extraction_result = MagicMock()
        mock_extraction_result.text = "This is a test sentence."
        mock_extraction_result.extraction_method = "test_method"
        mock_extract_text.return_value = mock_extraction_result

        # Mock the analyze_sentiment function
        mock_sentiment_result = MagicMock(spec=SentimentAnalysisResult)
        mock_sentiment_result.metadata = {}
        mock_analyze_sentiment.return_value = mock_sentiment_result

        # Mock os.path.getsize
        with patch('os.path.getsize', return_value=100):
            # Call the analyze_text_file_sentiment function
            file_path = "test.txt"
            result = analyze_text_file_sentiment(file_path)

            # Check that extract_text_from_file and analyze_sentiment were called
            mock_extract_text.assert_called_once()
            mock_analyze_sentiment.assert_called_once_with("This is a test sentence.", None)

            # Check that file metadata was added
            self.assertEqual(result.metadata['file_path'], file_path)
            self.assertEqual(result.metadata['file_size'], 100)
            self.assertEqual(result.metadata['extraction_method'], "test_method")

    @patch('science_data_kit.core.file_handling.sentiment_analysis.extract_text_from_file')
    def test_analyze_text_file_sentiment_extraction_failure(self, mock_extract_text):
        """Test analyzing sentiment when text extraction fails."""
        # Mock the extract_text_from_file function to return None
        mock_extract_text.return_value = None

        # Call the analyze_text_file_sentiment function
        file_path = "test.txt"
        result = analyze_text_file_sentiment(file_path)

        # Check the result
        self.assertEqual(result.text, "")
        self.assertEqual(result.document_sentiment.score, 0.0)
        self.assertEqual(result.document_sentiment.magnitude, 0.0)
        self.assertEqual(result.document_sentiment.polarity, SentimentPolarity.NEUTRAL)
        self.assertEqual(result.metadata['file_path'], file_path)
        self.assertEqual(result.metadata['error'], 'Failed to extract text')


class TestVisualizeSentiment(unittest.TestCase):
    """Tests for the visualize_sentiment function."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_sentiment = SentimentScore(
            score=0.3,
            magnitude=1.5,
            polarity=SentimentPolarity.POSITIVE
        )

        self.sentences = [
            SentenceSentiment(
                text="This is a positive sentence.",
                score=0.8,
                magnitude=1.2,
                polarity=SentimentPolarity.VERY_POSITIVE,
                start_offset=0
            ),
            SentenceSentiment(
                text="This is a neutral sentence.",
                score=0.1,
                magnitude=0.5,
                polarity=SentimentPolarity.NEUTRAL,
                start_offset=28
            ),
            SentenceSentiment(
                text="This is a negative sentence.",
                score=-0.6,
                magnitude=1.0,
                polarity=SentimentPolarity.NEGATIVE,
                start_offset=56
            )
        ]

        self.result = SentimentAnalysisResult(
            text="This is a positive sentence. This is a neutral sentence. This is a negative sentence.",
            document_sentiment=self.document_sentiment,
            sentences=self.sentences,
            language="en",
            metadata={"text_length": 84, "sentence_count": 3}
        )

    @patch('science_data_kit.core.file_handling.sentiment_analysis.plt')
    def test_visualize_sentiment(self, mock_plt):
        """Test visualizing sentiment analysis results."""
        # Call the visualize_sentiment function
        output_file = "test_visualization.png"
        visualization_data = visualize_sentiment(self.result, output_file)

        # Check that matplotlib was called
        mock_plt.subplots.assert_called_once()
        mock_plt.savefig.assert_called_once_with(output_file, dpi=300, bbox_inches='tight')
        mock_plt.close.assert_called_once()

        # Check the visualization data
        self.assertEqual(visualization_data['document_sentiment']['score'], 0.3)
        self.assertEqual(visualization_data['document_sentiment']['magnitude'], 1.5)
        self.assertEqual(visualization_data['document_sentiment']['polarity'], 'positive')
        self.assertEqual(visualization_data['sentence_distribution']['very_positive'], 1)
        self.assertEqual(visualization_data['sentence_distribution']['neutral'], 1)
        self.assertEqual(visualization_data['sentence_distribution']['negative'], 1)

    @patch('science_data_kit.core.file_handling.sentiment_analysis.plt')
    def test_visualize_sentiment_no_sentences(self, mock_plt):
        """Test visualizing sentiment analysis results without sentences."""
        # Create a result without sentences
        result = SentimentAnalysisResult(
            text="This is a test.",
            document_sentiment=self.document_sentiment,
            language="en",
            metadata={"text_length": 14}
        )

        # Call the visualize_sentiment function
        visualization_data = visualize_sentiment(result)

        # Check that matplotlib was called
        mock_plt.subplots.assert_called_once()
        mock_plt.close.assert_called_once()

        # Check the visualization data
        self.assertEqual(visualization_data['document_sentiment']['score'], 0.3)
        self.assertEqual(visualization_data['document_sentiment']['magnitude'], 1.5)
        self.assertEqual(visualization_data['document_sentiment']['polarity'], 'positive')
        self.assertEqual(visualization_data['sentence_distribution'], {})

    @patch('science_data_kit.core.file_handling.sentiment_analysis.plt')
    def test_visualize_sentiment_exception(self, mock_plt):
        """Test visualizing sentiment analysis results when an exception occurs."""
        # Mock plt.subplots to raise an exception
        mock_plt.subplots.side_effect = Exception("Test exception")

        # Call the visualize_sentiment function
        visualization_data = visualize_sentiment(self.result)

        # Check the visualization data
        self.assertEqual(visualization_data, {})


class TestGenerateSentimentReport(unittest.TestCase):
    """Tests for the generate_sentiment_report function."""

    def setUp(self):
        """Set up test fixtures."""
        self.document_sentiment = SentimentScore(
            score=0.3,
            magnitude=1.5,
            polarity=SentimentPolarity.POSITIVE
        )

        self.sentences = [
            SentenceSentiment(
                text="This is a positive sentence.",
                score=0.8,
                magnitude=1.2,
                polarity=SentimentPolarity.VERY_POSITIVE,
                start_offset=0
            ),
            SentenceSentiment(
                text="This is a neutral sentence.",
                score=0.1,
                magnitude=0.5,
                polarity=SentimentPolarity.NEUTRAL,
                start_offset=28
            ),
            SentenceSentiment(
                text="This is a negative sentence.",
                score=-0.6,
                magnitude=1.0,
                polarity=SentimentPolarity.NEGATIVE,
                start_offset=56
            )
        ]

        self.result = SentimentAnalysisResult(
            text="This is a positive sentence. This is a neutral sentence. This is a negative sentence.",
            document_sentiment=self.document_sentiment,
            sentences=self.sentences,
            language="en",
            metadata={"text_length": 84, "sentence_count": 3}
        )

    def test_generate_text_sentiment_report(self):
        """Test generating a text sentiment report."""
        # Call the generate_sentiment_report function
        report = generate_sentiment_report(self.result, 'text')

        # Check the report
        self.assertIn("Sentiment Analysis Report", report)
        self.assertIn("Document Sentiment: Positive", report)
        self.assertIn("Score: 0.30", report)
        self.assertIn("Magnitude: 1.50", report)
        self.assertIn("Language: en", report)
        self.assertIn("Sentence Analysis (3 sentences)", report)
        self.assertIn("Sentiment Distribution:", report)
        self.assertIn("Very Positive: 1", report)
        self.assertIn("Neutral: 1", report)
        self.assertIn("Negative: 1", report)
        self.assertIn("Most Positive Sentences:", report)
        self.assertIn("This is a positive sentence.", report)
        self.assertIn("Most Negative Sentences:", report)
        self.assertIn("This is a negative sentence.", report)
        self.assertIn("Most Emotional Sentences:", report)
        self.assertIn("Metadata:", report)
        self.assertIn("text_length: 84", report)
        self.assertIn("sentence_count: 3", report)

    def test_generate_json_sentiment_report(self):
        """Test generating a JSON sentiment report."""
        # Call the generate_sentiment_report function
        report = generate_sentiment_report(self.result, 'json')

        # Parse the JSON report
        report_dict = json.loads(report)

        # Check the report
        self.assertEqual(report_dict["document_sentiment"]["score"], 0.3)
        self.assertEqual(report_dict["document_sentiment"]["magnitude"], 1.5)
        self.assertEqual(report_dict["document_sentiment"]["polarity"], "positive")
        self.assertEqual(report_dict["language"], "en")
        self.assertEqual(len(report_dict["sentences"]), 3)
        self.assertEqual(report_dict["sentences"][0]["text"], "This is a positive sentence.")
        self.assertEqual(report_dict["sentences"][0]["score"], 0.8)
        self.assertEqual(report_dict["sentences"][0]["polarity"], "very_positive")
        self.assertEqual(report_dict["sentiment_distribution"]["very_positive"], 1)
        self.assertEqual(report_dict["sentiment_distribution"]["neutral"], 1)
        self.assertEqual(report_dict["sentiment_distribution"]["negative"], 1)
        self.assertEqual(report_dict["metadata"]["text_length"], 84)
        self.assertEqual(report_dict["metadata"]["sentence_count"], 3)

    def test_generate_html_sentiment_report(self):
        """Test generating an HTML sentiment report."""
        # Call the generate_sentiment_report function
        report = generate_sentiment_report(self.result, 'html')

        # Check the report
        self.assertIn("<!DOCTYPE html>", report)
        self.assertIn("<title>Sentiment Analysis Report</title>", report)
        self.assertIn("<h1>Sentiment Analysis Report</h1>", report)
        self.assertIn("<span class='positive'>Positive</span>", report)
        self.assertIn("Score: 0.30", report)
        self.assertIn("Magnitude: 1.50", report)
        self.assertIn("Language: en", report)
        self.assertIn("<h2>Sentence Analysis (3 sentences)</h2>", report)
        self.assertIn("<h3>Sentiment Distribution</h3>", report)
        self.assertIn("<h3>Most Positive Sentences</h3>", report)
        self.assertIn("<span class='very_positive'>This is a positive sentence.</span>", report)
        self.assertIn("<h3>Most Negative Sentences</h3>", report)
        self.assertIn("<span class='negative'>This is a negative sentence.</span>", report)
        self.assertIn("<h3>Most Emotional Sentences</h3>", report)
        self.assertIn("<h2>Metadata</h2>", report)
        self.assertIn("<strong>text_length:</strong> 84", report)
        self.assertIn("<strong>sentence_count:</strong> 3", report)

    def test_generate_sentiment_report_invalid_format(self):
        """Test generating a report with an invalid format."""
        # Call the generate_sentiment_report function with an invalid format
        with self.assertRaises(ValueError):
            generate_sentiment_report(self.result, 'invalid')


if __name__ == '__main__':
    unittest.main()

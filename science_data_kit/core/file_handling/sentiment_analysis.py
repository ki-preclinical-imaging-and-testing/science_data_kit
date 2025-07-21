"""
Sentiment Analysis module for analyzing sentiment in text content.

This module provides functionality for analyzing sentiment in text content,
integrating with the AI service framework to leverage external sentiment
analysis services. It includes classes for representing sentiment analysis
results, functions for analyzing sentiment in text and text files, and
utilities for visualizing and interpreting sentiment data.

The module builds on the existing AI service integration framework and
text extraction capabilities to provide a comprehensive sentiment analysis
solution for the Science Data Kit.
"""

import logging
import os
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from science_data_kit.core.file_handling.ai_service_integration import (
    analyze_text, TextAnalysisResult
)
from science_data_kit.core.file_handling.text_extraction import (
    extract_text_from_file, TextExtractionOptions
)

# Set up logging
logger = logging.getLogger(__name__)


class SentimentPolarity(Enum):
    """Enumeration of sentiment polarity levels."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class SentimentScore:
    """Represents a sentiment score with magnitude and polarity."""
    score: float
    magnitude: float
    polarity: SentimentPolarity = SentimentPolarity.NEUTRAL
    
    def __post_init__(self):
        """Calculate polarity based on score if not provided."""
        if self.score <= -0.7:
            self.polarity = SentimentPolarity.VERY_NEGATIVE
        elif self.score < 0:
            self.polarity = SentimentPolarity.NEGATIVE
        elif self.score == 0:
            self.polarity = SentimentPolarity.NEUTRAL
        elif self.score < 0.7:
            self.polarity = SentimentPolarity.POSITIVE
        else:
            self.polarity = SentimentPolarity.VERY_POSITIVE


@dataclass
class SentenceSentiment:
    """Represents sentiment analysis for a single sentence."""
    text: str
    score: float
    magnitude: float
    polarity: Optional[SentimentPolarity] = None
    start_offset: int = 0
    
    def __post_init__(self):
        """Calculate polarity based on score if not provided."""
        if self.polarity is None:
            if self.score <= -0.7:
                self.polarity = SentimentPolarity.VERY_NEGATIVE
            elif self.score < 0:
                self.polarity = SentimentPolarity.NEGATIVE
            elif self.score == 0:
                self.polarity = SentimentPolarity.NEUTRAL
            elif self.score < 0.7:
                self.polarity = SentimentPolarity.POSITIVE
            else:
                self.polarity = SentimentPolarity.VERY_POSITIVE


@dataclass
class SentimentAnalysisResult:
    """Result of sentiment analysis on text content."""
    text: str
    document_sentiment: SentimentScore
    sentences: List[SentenceSentiment] = field(default_factory=list)
    language: Optional[str] = None
    raw_result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def average_sentence_score(self) -> float:
        """Calculate the average sentiment score across all sentences."""
        if not self.sentences:
            return 0.0
        return sum(s.score for s in self.sentences) / len(self.sentences)
    
    @property
    def average_sentence_magnitude(self) -> float:
        """Calculate the average sentiment magnitude across all sentences."""
        if not self.sentences:
            return 0.0
        return sum(s.magnitude for s in self.sentences) / len(self.sentences)
    
    @property
    def sentiment_distribution(self) -> Dict[SentimentPolarity, int]:
        """Get the distribution of sentiment polarities across sentences."""
        distribution = {
            SentimentPolarity.VERY_NEGATIVE: 0,
            SentimentPolarity.NEGATIVE: 0,
            SentimentPolarity.NEUTRAL: 0,
            SentimentPolarity.POSITIVE: 0,
            SentimentPolarity.VERY_POSITIVE: 0
        }
        
        for sentence in self.sentences:
            distribution[sentence.polarity] += 1
        
        return distribution
    
    @property
    def most_positive_sentences(self) -> List[SentenceSentiment]:
        """Get sentences sorted by sentiment score (most positive first)."""
        return sorted(self.sentences, key=lambda s: s.score, reverse=True)
    
    @property
    def most_negative_sentences(self) -> List[SentenceSentiment]:
        """Get sentences sorted by sentiment score (most negative first)."""
        return sorted(self.sentences, key=lambda s: s.score)
    
    @property
    def most_emotional_sentences(self) -> List[SentenceSentiment]:
        """Get sentences sorted by sentiment magnitude (most emotional first)."""
        return sorted(self.sentences, key=lambda s: s.magnitude, reverse=True)


@dataclass
class SentimentAnalysisOptions:
    """Options for sentiment analysis."""
    language: Optional[str] = None
    extract_sentences: bool = True
    min_text_length: int = 10
    text_extraction_options: Optional[TextExtractionOptions] = None


def analyze_sentiment(text: str, options: Optional[SentimentAnalysisOptions] = None) -> SentimentAnalysisResult:
    """
    Analyze sentiment in text using the best available AI service.
    
    Args:
        text: The text to analyze.
        options: Sentiment analysis options.
        
    Returns:
        SentimentAnalysisResult containing the analysis results.
    """
    if options is None:
        options = SentimentAnalysisOptions()
    
    # Check if text is too short
    if len(text) < options.min_text_length:
        logger.warning(f"Text is too short for sentiment analysis (length: {len(text)}, min: {options.min_text_length})")
        return SentimentAnalysisResult(
            text=text,
            document_sentiment=SentimentScore(score=0.0, magnitude=0.0),
            metadata={"error": "Text too short for analysis"}
        )
    
    # Analyze text using AI service
    features = ['sentiment']
    if options.extract_sentences:
        features.append('sentences')
    
    # Call the AI service
    kwargs = {}
    if options.language:
        kwargs['language'] = options.language
    
    result = analyze_text(text, features, **kwargs)
    
    # Process the result
    if not result.success or not result.sentiment:
        logger.warning("Sentiment analysis failed or returned no results")
        return SentimentAnalysisResult(
            text=text,
            document_sentiment=SentimentScore(score=0.0, magnitude=0.0),
            raw_result=result,
            metadata={"error": "Sentiment analysis failed"}
        )
    
    # Extract document sentiment
    doc_sentiment = SentimentScore(
        score=result.sentiment.get('score', 0.0),
        magnitude=result.sentiment.get('magnitude', 0.0)
    )
    
    # Extract sentences if available
    sentences = []
    if options.extract_sentences and 'sentences' in result.sentiment:
        for sent in result.sentiment['sentences']:
            sentences.append(SentenceSentiment(
                text=sent.get('text', ''),
                score=sent.get('score', 0.0),
                magnitude=sent.get('magnitude', 0.0),
                start_offset=sent.get('start', 0)
            ))
    
    # Extract language if available
    language = None
    if result.language and isinstance(result.language, dict):
        language = result.language.get('language_code')
    
    # Create metadata
    metadata = {
        "service": result.service_name,
        "text_length": len(text),
        "sentence_count": len(sentences)
    }
    
    # Create and return the result
    return SentimentAnalysisResult(
        text=text,
        document_sentiment=doc_sentiment,
        sentences=sentences,
        language=language,
        raw_result=result,
        metadata=metadata
    )


def analyze_text_file_sentiment(file_path: str, options: Optional[SentimentAnalysisOptions] = None) -> SentimentAnalysisResult:
    """
    Analyze sentiment in a text file using the best available AI service.
    
    Args:
        file_path: Path to the text file to analyze.
        options: Sentiment analysis options.
        
    Returns:
        SentimentAnalysisResult containing the analysis results.
    """
    # Extract text from file
    extraction_result = extract_text_from_file(
        file_path, 
        options.text_extraction_options if options else None
    )
    
    if not extraction_result or not extraction_result.text:
        logger.warning(f"Failed to extract text from file: {file_path}")
        return SentimentAnalysisResult(
            text="",
            document_sentiment=SentimentScore(score=0.0, magnitude=0.0),
            metadata={
                "file_path": file_path,
                "error": "Failed to extract text"
            }
        )
    
    # Analyze the extracted text
    result = analyze_sentiment(extraction_result.text, options)
    
    # Add file metadata
    try:
        file_size = os.path.getsize(file_path)
    except Exception as e:
        logger.warning(f"Failed to get file size: {e}")
        file_size = 0
    
    result.metadata["file_path"] = file_path
    result.metadata["file_size"] = file_size
    result.metadata["extraction_method"] = extraction_result.extraction_method
    
    return result


def visualize_sentiment(result: SentimentAnalysisResult, output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Visualize sentiment analysis results.
    
    Args:
        result: Sentiment analysis result to visualize.
        output_file: Path to save the visualization (if None, no file is saved).
        
    Returns:
        Dictionary with visualization data.
    """
    try:
        # Try to import visualization libraries
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Plot document sentiment
        sentiment_score = result.document_sentiment.score
        sentiment_magnitude = result.document_sentiment.magnitude
        
        # Create a color map for sentiment scores
        cmap = plt.cm.RdYlGn  # Red-Yellow-Green colormap
        norm = plt.Normalize(-1, 1)
        
        # Plot sentiment score gauge
        ax1.set_title('Document Sentiment')
        ax1.set_xlim(-1, 1)
        ax1.set_ylim(0, 1)
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.yaxis.set_visible(False)
        
        # Add colored bar for sentiment range
        for i in np.linspace(-1, 1, 100):
            ax1.axvline(i, color=cmap(norm(i)), alpha=0.7, linewidth=5)
        
        # Add marker for current sentiment
        ax1.scatter(sentiment_score, 0.5, s=300, color='black', zorder=10)
        ax1.text(sentiment_score, 0.5, f'{sentiment_score:.2f}', 
                 ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Add magnitude indicator
        ax1.text(0, 0.2, f'Magnitude: {sentiment_magnitude:.2f}', 
                 ha='center', va='center', fontsize=12)
        
        # Add polarity labels
        ax1.text(-0.85, 0.8, 'Very Negative', ha='center', va='center', fontsize=10)
        ax1.text(-0.5, 0.8, 'Negative', ha='center', va='center', fontsize=10)
        ax1.text(0, 0.8, 'Neutral', ha='center', va='center', fontsize=10)
        ax1.text(0.5, 0.8, 'Positive', ha='center', va='center', fontsize=10)
        ax1.text(0.85, 0.8, 'Very Positive', ha='center', va='center', fontsize=10)
        
        # Plot sentence distribution if sentences are available
        if result.sentences:
            # Get sentiment distribution
            distribution = result.sentiment_distribution
            
            # Convert to lists for plotting
            labels = [p.value for p in SentimentPolarity]
            values = [distribution[p] for p in SentimentPolarity]
            
            # Define colors for each polarity
            colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']
            
            # Plot bar chart
            bars = ax2.bar(labels, values, color=colors)
            ax2.set_title('Sentence Sentiment Distribution')
            ax2.set_xlabel('Sentiment Polarity')
            ax2.set_ylabel('Number of Sentences')
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                             f'{height:.0f}', ha='center', va='bottom')
            
            # Rotate x-axis labels for better readability
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        else:
            ax2.set_title('No Sentence Data Available')
            ax2.axis('off')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to file if requested
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved to {output_file}")
        
        # Close the plot to free memory
        plt.close()
        
        # Return visualization data
        visualization_data = {
            "document_sentiment": {
                "score": result.document_sentiment.score,
                "magnitude": result.document_sentiment.magnitude,
                "polarity": result.document_sentiment.polarity.value
            }
        }
        
        if result.sentences:
            visualization_data["sentence_distribution"] = {
                p.value: distribution[p] for p in SentimentPolarity if distribution[p] > 0
            }
        else:
            visualization_data["sentence_distribution"] = {}
        
        return visualization_data
    
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        return {}


def generate_sentiment_report(result: SentimentAnalysisResult, format: str = 'text') -> str:
    """
    Generate a report of sentiment analysis results.
    
    Args:
        result: Sentiment analysis result to report.
        format: Report format ('text', 'json', or 'html').
        
    Returns:
        Report string in the specified format.
    """
    if format == 'text':
        return _generate_text_report(result)
    elif format == 'json':
        return _generate_json_report(result)
    elif format == 'html':
        return _generate_html_report(result)
    else:
        raise ValueError(f"Unknown report format: {format}")


def _generate_text_report(result: SentimentAnalysisResult) -> str:
    """Generate a text report of sentiment analysis results."""
    lines = []
    lines.append("Sentiment Analysis Report")
    lines.append("========================")
    lines.append("")
    
    # Document sentiment
    lines.append(f"Document Sentiment: {result.document_sentiment.polarity.name.replace('_', ' ').title()}")
    lines.append(f"Score: {result.document_sentiment.score:.2f}")
    lines.append(f"Magnitude: {result.document_sentiment.magnitude:.2f}")
    
    # Language
    if result.language:
        lines.append(f"Language: {result.language}")
    
    lines.append("")
    
    # Sentence analysis
    if result.sentences:
        lines.append(f"Sentence Analysis ({len(result.sentences)} sentences)")
        lines.append("----------------" + "-" * len(str(len(result.sentences))))
        lines.append("")
        
        # Sentiment distribution
        lines.append("Sentiment Distribution:")
        distribution = result.sentiment_distribution
        for polarity in SentimentPolarity:
            if distribution[polarity] > 0:
                lines.append(f"  {polarity.name.replace('_', ' ').title()}: {distribution[polarity]}")
        
        lines.append("")
        
        # Most positive sentences
        lines.append("Most Positive Sentences:")
        for i, sentence in enumerate(result.most_positive_sentences[:3]):
            lines.append(f"  {i+1}. \"{sentence.text}\" (Score: {sentence.score:.2f})")
        
        lines.append("")
        
        # Most negative sentences
        lines.append("Most Negative Sentences:")
        for i, sentence in enumerate(result.most_negative_sentences[:3]):
            lines.append(f"  {i+1}. \"{sentence.text}\" (Score: {sentence.score:.2f})")
        
        lines.append("")
        
        # Most emotional sentences
        lines.append("Most Emotional Sentences:")
        for i, sentence in enumerate(result.most_emotional_sentences[:3]):
            lines.append(f"  {i+1}. \"{sentence.text}\" (Magnitude: {sentence.magnitude:.2f})")
        
        lines.append("")
    
    # Metadata
    if result.metadata:
        lines.append("Metadata:")
        for key, value in result.metadata.items():
            if key != 'error':  # Skip error messages in metadata
                lines.append(f"  {key}: {value}")
    
    return "\n".join(lines)


def _generate_json_report(result: SentimentAnalysisResult) -> str:
    """Generate a JSON report of sentiment analysis results."""
    report = {
        "document_sentiment": {
            "score": result.document_sentiment.score,
            "magnitude": result.document_sentiment.magnitude,
            "polarity": result.document_sentiment.polarity.value
        },
        "language": result.language,
        "sentences": [
            {
                "text": s.text,
                "score": s.score,
                "magnitude": s.magnitude,
                "polarity": s.polarity.value,
                "start_offset": s.start_offset
            }
            for s in result.sentences
        ],
        "sentiment_distribution": {
            p.value: result.sentiment_distribution[p]
            for p in SentimentPolarity
            if result.sentiment_distribution[p] > 0
        },
        "metadata": result.metadata
    }
    
    return json.dumps(report, indent=2)


def _generate_html_report(result: SentimentAnalysisResult) -> str:
    """Generate an HTML report of sentiment analysis results."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("  <title>Sentiment Analysis Report</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
    html.append("    h1 { color: #333; }")
    html.append("    h2 { color: #666; margin-top: 20px; }")
    html.append("    h3 { color: #999; }")
    html.append("    .summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
    html.append("    .very_negative { color: #d7191c; }")
    html.append("    .negative { color: #fdae61; }")
    html.append("    .neutral { color: #ffffbf; background-color: #f0f0f0; }")
    html.append("    .positive { color: #a6d96a; }")
    html.append("    .very_positive { color: #1a9641; }")
    html.append("    table { border-collapse: collapse; width: 100%; }")
    html.append("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
    html.append("    th { background-color: #f2f2f2; }")
    html.append("    tr:nth-child(even) { background-color: #f9f9f9; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    
    # Title
    html.append("  <h1>Sentiment Analysis Report</h1>")
    
    # Document sentiment
    html.append("  <div class='summary'>")
    html.append("    <h2>Document Sentiment</h2>")
    html.append(f"    <p>Sentiment: <span class='{result.document_sentiment.polarity.value}'>{result.document_sentiment.polarity.name.replace('_', ' ').title()}</span></p>")
    html.append(f"    <p>Score: {result.document_sentiment.score:.2f}</p>")
    html.append(f"    <p>Magnitude: {result.document_sentiment.magnitude:.2f}</p>")
    
    # Language
    if result.language:
        html.append(f"    <p>Language: {result.language}</p>")
    
    html.append("  </div>")
    
    # Sentence analysis
    if result.sentences:
        html.append(f"  <h2>Sentence Analysis ({len(result.sentences)} sentences)</h2>")
        
        # Sentiment distribution
        html.append("  <h3>Sentiment Distribution</h3>")
        html.append("  <table>")
        html.append("    <tr><th>Sentiment</th><th>Count</th></tr>")
        
        distribution = result.sentiment_distribution
        for polarity in SentimentPolarity:
            if distribution[polarity] > 0:
                html.append(f"    <tr><td class='{polarity.value}'>{polarity.name.replace('_', ' ').title()}</td><td>{distribution[polarity]}</td></tr>")
        
        html.append("  </table>")
        
        # Most positive sentences
        html.append("  <h3>Most Positive Sentences</h3>")
        html.append("  <ol>")
        for sentence in result.most_positive_sentences[:3]:
            html.append(f"    <li><span class='{sentence.polarity.value}'>{sentence.text}</span> (Score: {sentence.score:.2f})</li>")
        html.append("  </ol>")
        
        # Most negative sentences
        html.append("  <h3>Most Negative Sentences</h3>")
        html.append("  <ol>")
        for sentence in result.most_negative_sentences[:3]:
            html.append(f"    <li><span class='{sentence.polarity.value}'>{sentence.text}</span> (Score: {sentence.score:.2f})</li>")
        html.append("  </ol>")
        
        # Most emotional sentences
        html.append("  <h3>Most Emotional Sentences</h3>")
        html.append("  <ol>")
        for sentence in result.most_emotional_sentences[:3]:
            html.append(f"    <li><span class='{sentence.polarity.value}'>{sentence.text}</span> (Magnitude: {sentence.magnitude:.2f})</li>")
        html.append("  </ol>")
    
    # Metadata
    if result.metadata:
        html.append("  <h2>Metadata</h2>")
        html.append("  <table>")
        html.append("    <tr><th>Key</th><th>Value</th></tr>")
        
        for key, value in result.metadata.items():
            if key != 'error':  # Skip error messages in metadata
                html.append(f"    <tr><td><strong>{key}:</strong></td><td>{value}</td></tr>")
        
        html.append("  </table>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)
"""
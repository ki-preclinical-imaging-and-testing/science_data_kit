"""
Duplicate File Detection for Science Data Kit

This module provides functionality for detecting duplicate or near-duplicate files
based on content and metadata analysis. It leverages the existing file similarity
metrics and content-based similarity analysis to identify duplicates with configurable
thresholds and detection strategies.

The module includes:
1. Functions for detecting exact duplicates (identical content)
2. Functions for detecting near-duplicates (similar content)
3. Functions for detecting metadata-based duplicates
4. Configurable thresholds and detection strategies
5. Result classes for representing duplicate detection results
"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from science_data_kit.core.file_handling.similarity_analysis import (
    calculate_content_similarity, calculate_metadata_similarity,
    get_file_similarity_metrics
)

# Set up logging
logger = logging.getLogger(__name__)


class DuplicateDetectionStrategy(Enum):
    """Strategies for detecting duplicate files."""
    EXACT_MATCH = "exact_match"  # Only detect files with identical content
    CONTENT_SIMILARITY = "content_similarity"  # Detect files with similar content
    METADATA_SIMILARITY = "metadata_similarity"  # Detect files with similar metadata
    COMBINED = "combined"  # Use both content and metadata similarity


@dataclass
class DuplicateGroup:
    """A group of duplicate or near-duplicate files."""
    files: List[str] = field(default_factory=list)
    similarity_score: float = 1.0
    detection_method: str = "exact_match"
    reference_file: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DuplicateDetectionResult:
    """Result of a duplicate detection operation."""
    duplicate_groups: List[DuplicateGroup] = field(default_factory=list)
    total_files_analyzed: int = 0
    total_duplicates_found: int = 0
    detection_strategy: str = "exact_match"
    threshold: float = 1.0
    execution_time: float = 0.0
    error_message: Optional[str] = None


def detect_exact_duplicates(file_paths: List[str]) -> DuplicateDetectionResult:
    """
    Detect exact duplicate files based on content hash.

    Args:
        file_paths: List of file paths to analyze.

    Returns:
        DuplicateDetectionResult containing groups of duplicate files.
    """
    import time
    start_time = time.time()
    
    try:
        # Dictionary to store file hashes and their corresponding paths
        hash_map: Dict[str, List[str]] = {}
        
        # Calculate hash for each file
        for file_path in file_paths:
            try:
                file_hash = _calculate_file_hash(file_path)
                if file_hash in hash_map:
                    hash_map[file_hash].append(file_path)
                else:
                    hash_map[file_hash] = [file_path]
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {str(e)}")
        
        # Create duplicate groups
        duplicate_groups = []
        total_duplicates = 0
        
        for file_hash, paths in hash_map.items():
            if len(paths) > 1:  # Only include groups with more than one file
                group = DuplicateGroup(
                    files=paths,
                    similarity_score=1.0,
                    detection_method="exact_match",
                    reference_file=paths[0],
                    metadata={
                        "hash": file_hash,
                        "file_size": os.path.getsize(paths[0])
                    }
                )
                duplicate_groups.append(group)
                total_duplicates += len(paths) - 1  # Count all files except the reference
        
        # Create result
        result = DuplicateDetectionResult(
            duplicate_groups=duplicate_groups,
            total_files_analyzed=len(file_paths),
            total_duplicates_found=total_duplicates,
            detection_strategy="exact_match",
            threshold=1.0,
            execution_time=time.time() - start_time
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error detecting exact duplicates: {str(e)}")
        return DuplicateDetectionResult(
            error_message=f"Error detecting exact duplicates: {str(e)}",
            execution_time=time.time() - start_time
        )


def detect_similar_files(file_paths: List[str], threshold: float = 0.9, 
                         strategy: DuplicateDetectionStrategy = DuplicateDetectionStrategy.CONTENT_SIMILARITY,
                         max_comparisons: Optional[int] = None) -> DuplicateDetectionResult:
    """
    Detect similar files based on content and/or metadata similarity.

    Args:
        file_paths: List of file paths to analyze.
        threshold: Similarity threshold (0.0 to 1.0) for considering files as duplicates.
        strategy: Detection strategy to use.
        max_comparisons: Maximum number of file comparisons to perform (None for no limit).

    Returns:
        DuplicateDetectionResult containing groups of similar files.
    """
    import time
    start_time = time.time()
    
    try:
        # First, group files by size to reduce comparison space
        size_groups: Dict[int, List[str]] = {}
        for file_path in file_paths:
            try:
                size = os.path.getsize(file_path)
                if size in size_groups:
                    size_groups[size].append(file_path)
                else:
                    size_groups[size] = [file_path]
            except Exception as e:
                logger.warning(f"Error getting size of file {file_path}: {str(e)}")
        
        # Only compare files within the same size group
        duplicate_groups = []
        total_duplicates = 0
        comparisons_performed = 0
        
        # Track which files have already been assigned to a group
        assigned_files = set()
        
        # Process each size group
        for size, group_files in size_groups.items():
            if len(group_files) <= 1:
                continue  # Skip groups with only one file
            
            # Compare each file with every other file in the group
            for i in range(len(group_files)):
                if group_files[i] in assigned_files:
                    continue  # Skip files already in a group
                
                # Start a new potential duplicate group
                current_group = [group_files[i]]
                reference_file = group_files[i]
                
                for j in range(len(group_files)):
                    if i == j or group_files[j] in assigned_files:
                        continue  # Skip self-comparison and files already in a group
                    
                    # Check if we've reached the maximum number of comparisons
                    if max_comparisons is not None and comparisons_performed >= max_comparisons:
                        logger.warning(f"Maximum number of comparisons ({max_comparisons}) reached")
                        break
                    
                    # Calculate similarity based on strategy
                    similarity = _calculate_similarity(group_files[i], group_files[j], strategy)
                    comparisons_performed += 1
                    
                    # If similarity is above threshold, add to current group
                    if similarity >= threshold:
                        current_group.append(group_files[j])
                        assigned_files.add(group_files[j])
                
                # If we found duplicates, add the group
                if len(current_group) > 1:
                    group = DuplicateGroup(
                        files=current_group,
                        similarity_score=threshold,  # Use threshold as minimum similarity
                        detection_method=strategy.value,
                        reference_file=reference_file,
                        metadata={
                            "file_size": size,
                            "strategy": strategy.value
                        }
                    )
                    duplicate_groups.append(group)
                    total_duplicates += len(current_group) - 1  # Count all files except the reference
                    assigned_files.add(reference_file)  # Mark reference file as assigned
            
            # Check if we've reached the maximum number of comparisons
            if max_comparisons is not None and comparisons_performed >= max_comparisons:
                break
        
        # Create result
        result = DuplicateDetectionResult(
            duplicate_groups=duplicate_groups,
            total_files_analyzed=len(file_paths),
            total_duplicates_found=total_duplicates,
            detection_strategy=strategy.value,
            threshold=threshold,
            execution_time=time.time() - start_time
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error detecting similar files: {str(e)}")
        return DuplicateDetectionResult(
            error_message=f"Error detecting similar files: {str(e)}",
            execution_time=time.time() - start_time
        )


def detect_duplicates(file_paths: List[str], threshold: float = 0.9,
                      strategy: DuplicateDetectionStrategy = DuplicateDetectionStrategy.COMBINED,
                      max_comparisons: Optional[int] = None) -> DuplicateDetectionResult:
    """
    Detect duplicate files using a two-phase approach:
    1. First detect exact duplicates
    2. Then detect similar files among the remaining files

    Args:
        file_paths: List of file paths to analyze.
        threshold: Similarity threshold (0.0 to 1.0) for considering files as duplicates.
        strategy: Detection strategy to use for similar files.
        max_comparisons: Maximum number of file comparisons to perform (None for no limit).

    Returns:
        DuplicateDetectionResult containing groups of duplicate and similar files.
    """
    import time
    start_time = time.time()
    
    try:
        # First, detect exact duplicates
        exact_result = detect_exact_duplicates(file_paths)
        
        # Get files that are not exact duplicates
        exact_duplicate_files = set()
        for group in exact_result.duplicate_groups:
            for file_path in group.files:
                exact_duplicate_files.add(file_path)
        
        remaining_files = [f for f in file_paths if f not in exact_duplicate_files]
        
        # Then, detect similar files among the remaining files
        similar_result = detect_similar_files(
            remaining_files, 
            threshold=threshold,
            strategy=strategy,
            max_comparisons=max_comparisons
        )
        
        # Combine results
        combined_groups = exact_result.duplicate_groups + similar_result.duplicate_groups
        total_duplicates = exact_result.total_duplicates_found + similar_result.total_duplicates_found
        
        # Create combined result
        result = DuplicateDetectionResult(
            duplicate_groups=combined_groups,
            total_files_analyzed=len(file_paths),
            total_duplicates_found=total_duplicates,
            detection_strategy=f"exact_match+{strategy.value}",
            threshold=threshold,
            execution_time=time.time() - start_time
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error detecting duplicates: {str(e)}")
        return DuplicateDetectionResult(
            error_message=f"Error detecting duplicates: {str(e)}",
            execution_time=time.time() - start_time
        )


def _calculate_file_hash(file_path: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
    """
    Calculate a hash for a file.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', etc.).
        chunk_size: Size of chunks to read from the file.

    Returns:
        Hexadecimal hash string.
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def _calculate_similarity(file1: str, file2: str, 
                          strategy: DuplicateDetectionStrategy) -> float:
    """
    Calculate similarity between two files based on the specified strategy.

    Args:
        file1: Path to the first file.
        file2: Path to the second file.
        strategy: Detection strategy to use.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    if strategy == DuplicateDetectionStrategy.EXACT_MATCH:
        # For exact match, compare hashes
        hash1 = _calculate_file_hash(file1)
        hash2 = _calculate_file_hash(file2)
        return 1.0 if hash1 == hash2 else 0.0
    
    elif strategy == DuplicateDetectionStrategy.CONTENT_SIMILARITY:
        # Use content-based similarity
        return calculate_content_similarity(file1, file2)
    
    elif strategy == DuplicateDetectionStrategy.METADATA_SIMILARITY:
        # Use metadata-based similarity
        return calculate_metadata_similarity(file1, file2)
    
    elif strategy == DuplicateDetectionStrategy.COMBINED:
        # Use a weighted combination of content and metadata similarity
        content_sim = calculate_content_similarity(file1, file2)
        metadata_sim = calculate_metadata_similarity(file1, file2)
        # Weight content similarity more heavily (70% content, 30% metadata)
        return (0.7 * content_sim) + (0.3 * metadata_sim)
    
    else:
        raise ValueError(f"Unknown detection strategy: {strategy}")


def group_duplicates_by_directory(duplicate_groups: List[DuplicateGroup]) -> Dict[str, List[DuplicateGroup]]:
    """
    Group duplicate files by their parent directory.

    Args:
        duplicate_groups: List of duplicate groups.

    Returns:
        Dictionary mapping directory paths to lists of duplicate groups.
    """
    directory_groups: Dict[str, List[DuplicateGroup]] = {}
    
    for group in duplicate_groups:
        # Get the parent directory of the reference file
        if group.reference_file:
            parent_dir = os.path.dirname(group.reference_file)
            if parent_dir in directory_groups:
                directory_groups[parent_dir].append(group)
            else:
                directory_groups[parent_dir] = [group]
    
    return directory_groups


def generate_duplicate_report(result: DuplicateDetectionResult, 
                              format: str = 'text') -> str:
    """
    Generate a report of duplicate files.

    Args:
        result: Duplicate detection result.
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


def _generate_text_report(result: DuplicateDetectionResult) -> str:
    """Generate a text report of duplicate files."""
    import textwrap
    
    lines = []
    lines.append("Duplicate File Detection Report")
    lines.append("==============================")
    lines.append(f"Total files analyzed: {result.total_files_analyzed}")
    lines.append(f"Total duplicates found: {result.total_duplicates_found}")
    lines.append(f"Detection strategy: {result.detection_strategy}")
    lines.append(f"Similarity threshold: {result.threshold}")
    lines.append(f"Execution time: {result.execution_time:.2f} seconds")
    lines.append("")
    
    if result.error_message:
        lines.append(f"ERROR: {result.error_message}")
        lines.append("")
    
    if not result.duplicate_groups:
        lines.append("No duplicate files found.")
        return "\n".join(lines)
    
    # Group by directory for better organization
    dir_groups = group_duplicates_by_directory(result.duplicate_groups)
    
    for dir_path, groups in dir_groups.items():
        lines.append(f"Directory: {dir_path}")
        lines.append("-" * len(f"Directory: {dir_path}"))
        
        for i, group in enumerate(groups, 1):
            lines.append(f"Group {i}: {len(group.files)} files, "
                         f"similarity: {group.similarity_score:.2f}, "
                         f"method: {group.detection_method}")
            
            if group.reference_file:
                lines.append(f"  Reference: {os.path.basename(group.reference_file)}")
            
            for file_path in group.files:
                if file_path != group.reference_file:
                    lines.append(f"  - {os.path.basename(file_path)}")
            
            lines.append("")
    
    return "\n".join(lines)


def _generate_json_report(result: DuplicateDetectionResult) -> str:
    """Generate a JSON report of duplicate files."""
    import json
    
    # Convert result to dictionary
    result_dict = {
        "total_files_analyzed": result.total_files_analyzed,
        "total_duplicates_found": result.total_duplicates_found,
        "detection_strategy": result.detection_strategy,
        "threshold": result.threshold,
        "execution_time": result.execution_time,
        "error_message": result.error_message,
        "duplicate_groups": []
    }
    
    # Add duplicate groups
    for group in result.duplicate_groups:
        group_dict = {
            "files": group.files,
            "similarity_score": group.similarity_score,
            "detection_method": group.detection_method,
            "reference_file": group.reference_file,
            "metadata": group.metadata
        }
        result_dict["duplicate_groups"].append(group_dict)
    
    return json.dumps(result_dict, indent=2)


def _generate_html_report(result: DuplicateDetectionResult) -> str:
    """Generate an HTML report of duplicate files."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("  <title>Duplicate File Detection Report</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
    html.append("    h1 { color: #333; }")
    html.append("    h2 { color: #666; margin-top: 20px; }")
    html.append("    .summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }")
    html.append("    .group { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }")
    html.append("    .reference { font-weight: bold; color: #007bff; }")
    html.append("    .duplicate { margin-left: 20px; }")
    html.append("    .error { color: red; font-weight: bold; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("  <h1>Duplicate File Detection Report</h1>")
    html.append("  <div class='summary'>")
    html.append(f"    <p>Total files analyzed: {result.total_files_analyzed}</p>")
    html.append(f"    <p>Total duplicates found: {result.total_duplicates_found}</p>")
    html.append(f"    <p>Detection strategy: {result.detection_strategy}</p>")
    html.append(f"    <p>Similarity threshold: {result.threshold}</p>")
    html.append(f"    <p>Execution time: {result.execution_time:.2f} seconds</p>")
    html.append("  </div>")
    
    if result.error_message:
        html.append(f"  <p class='error'>ERROR: {result.error_message}</p>")
    
    if not result.duplicate_groups:
        html.append("  <p>No duplicate files found.</p>")
    else:
        # Group by directory for better organization
        dir_groups = group_duplicates_by_directory(result.duplicate_groups)
        
        for dir_path, groups in dir_groups.items():
            html.append(f"  <h2>Directory: {dir_path}</h2>")
            
            for i, group in enumerate(groups, 1):
                html.append(f"  <div class='group'>")
                html.append(f"    <h3>Group {i}: {len(group.files)} files, "
                           f"similarity: {group.similarity_score:.2f}, "
                           f"method: {group.detection_method}</h3>")
                
                if group.reference_file:
                    html.append(f"    <p class='reference'>Reference: {os.path.basename(group.reference_file)}</p>")
                
                html.append("    <ul>")
                for file_path in group.files:
                    if file_path != group.reference_file:
                        html.append(f"      <li class='duplicate'>{os.path.basename(file_path)}</li>")
                html.append("    </ul>")
                html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)
"""
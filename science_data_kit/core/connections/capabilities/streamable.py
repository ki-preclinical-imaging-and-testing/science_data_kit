"""
Streamable capability mixin for Science Data Kit connections.

This module provides a mixin that defines the streamable capability for connections,
allowing them to stream data rather than loading it all at once.
"""

from abc import abstractmethod
from typing import Any, BinaryIO, Dict, Generator, Iterator, Optional


class Streamable:
    """Mixin for connections that support streaming data."""
    
    @abstractmethod
    def stream_download(self, path: str) -> Iterator[bytes]:
        """
        Stream download data in chunks.
        
        Args:
            path: Path to the resource to download
            
        Returns:
            Iterator yielding data chunks as bytes
        """
        pass
    
    @abstractmethod
    def stream_upload(self, path: str, data_iterator: Iterator[bytes]) -> Dict[str, Any]:
        """
        Stream upload data in chunks.
        
        Args:
            path: Path to upload to
            data_iterator: Iterator providing data chunks
            
        Returns:
            Dictionary containing metadata about the uploaded resource
        """
        pass
    
    def download_to_file(self, path: str, local_file: BinaryIO) -> int:
        """
        Download a resource and write it to a local file.
        
        Args:
            path: Path to the resource to download
            local_file: File-like object to write to
            
        Returns:
            Number of bytes downloaded
        """
        total_bytes = 0
        for chunk in self.stream_download(path):
            local_file.write(chunk)
            total_bytes += len(chunk)
        return total_bytes
    
    def upload_from_file(self, path: str, local_file: BinaryIO, 
                        chunk_size: int = 1024 * 1024) -> Dict[str, Any]:
        """
        Upload a local file using streaming.
        
        Args:
            path: Path to upload to
            local_file: File-like object to read from
            chunk_size: Size of chunks to read
            
        Returns:
            Dictionary containing metadata about the uploaded resource
        """
        def chunk_generator() -> Generator[bytes, None, None]:
            while True:
                chunk = local_file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
        return self.stream_upload(path, chunk_generator())
    
    def copy_stream(self, source_path: str, target_path: str) -> Dict[str, Any]:
        """
        Copy a resource from one path to another using streaming.
        
        Args:
            source_path: Path to the source resource
            target_path: Path to the target location
            
        Returns:
            Dictionary containing metadata about the copied resource
        """
        return self.stream_upload(target_path, self.stream_download(source_path))
"""
Unit tests for the API cache functionality.

This module tests the caching functionality for the Science Data Kit API client.
"""

import unittest
import time
from unittest.mock import patch, MagicMock
import json
import requests
from typing import Dict, Any, Optional

from science_data_kit.core.api.cache import APICache, CacheEntry
from science_data_kit.core.api.client import APIClient, SDKClient


class TestCacheEntry(unittest.TestCase):
    """Tests for the CacheEntry class."""
    
    def test_init(self):
        """Test initialization of a cache entry."""
        data = {"key": "value"}
        entry = CacheEntry(data)
        self.assertEqual(entry.data, data)
        self.assertIsNone(entry.expires_at)
        
        # Test with expiration
        expires_at = time.time() + 60
        entry = CacheEntry(data, expires_at)
        self.assertEqual(entry.data, data)
        self.assertEqual(entry.expires_at, expires_at)
    
    def test_is_expired(self):
        """Test checking if a cache entry is expired."""
        data = {"key": "value"}
        
        # Test with no expiration
        entry = CacheEntry(data)
        self.assertFalse(entry.is_expired())
        
        # Test with future expiration
        entry = CacheEntry(data, time.time() + 60)
        self.assertFalse(entry.is_expired())
        
        # Test with past expiration
        entry = CacheEntry(data, time.time() - 60)
        self.assertTrue(entry.is_expired())


class TestAPICache(unittest.TestCase):
    """Tests for the APICache class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = APICache(max_size=10, default_ttl=60)
    
    def test_generate_key(self):
        """Test generating a cache key."""
        method = "GET"
        path = "/api/test"
        params = {"param1": "value1"}
        data = {"data1": "value1"}
        
        key1 = self.cache._generate_key(method, path, params, data)
        self.assertIsInstance(key1, str)
        
        # Test that the same parameters generate the same key
        key2 = self.cache._generate_key(method, path, params, data)
        self.assertEqual(key1, key2)
        
        # Test that different parameters generate different keys
        key3 = self.cache._generate_key(method, path, {"param2": "value2"}, data)
        self.assertNotEqual(key1, key3)
    
    def test_get_set(self):
        """Test getting and setting cache entries."""
        method = "GET"
        path = "/api/test"
        params = {"param1": "value1"}
        data = {"data1": "value1"}
        value = {"result": "test"}
        
        # Test getting a non-existent entry
        hit, result = self.cache.get(method, path, params, data)
        self.assertFalse(hit)
        self.assertIsNone(result)
        
        # Test setting and getting an entry
        self.cache.set(method, path, value, params=params, data=data)
        hit, result = self.cache.get(method, path, params, data)
        self.assertTrue(hit)
        self.assertEqual(result, value)
        
        # Test getting an expired entry
        method = "GET"
        path = "/api/expired"
        self.cache.set(method, path, value, ttl=-1)  # Expired immediately
        hit, result = self.cache.get(method, path)
        self.assertFalse(hit)
        self.assertIsNone(result)
    
    def test_invalidate(self):
        """Test invalidating cache entries."""
        # Add some entries
        self.cache.set("GET", "/api/test1", {"result": "test1"})
        self.cache.set("GET", "/api/test2", {"result": "test2"})
        self.cache.set("POST", "/api/test1", {"result": "test3"})
        
        # Invalidate by method
        count = self.cache.invalidate(method="POST")
        self.assertEqual(count, 1)
        hit, _ = self.cache.get("POST", "/api/test1")
        self.assertFalse(hit)
        hit, _ = self.cache.get("GET", "/api/test1")
        self.assertTrue(hit)
        
        # Invalidate by path
        count = self.cache.invalidate(path="/api/test2")
        self.assertEqual(count, 1)
        hit, _ = self.cache.get("GET", "/api/test2")
        self.assertFalse(hit)
        hit, _ = self.cache.get("GET", "/api/test1")
        self.assertTrue(hit)
        
        # Invalidate all
        count = self.cache.invalidate()
        self.assertEqual(count, 1)
        hit, _ = self.cache.get("GET", "/api/test1")
        self.assertFalse(hit)
    
    def test_clear(self):
        """Test clearing the cache."""
        # Add some entries
        self.cache.set("GET", "/api/test1", {"result": "test1"})
        self.cache.set("GET", "/api/test2", {"result": "test2"})
        
        # Clear the cache
        count = self.cache.clear()
        self.assertEqual(count, 2)
        hit, _ = self.cache.get("GET", "/api/test1")
        self.assertFalse(hit)
        hit, _ = self.cache.get("GET", "/api/test2")
        self.assertFalse(hit)
    
    def test_cleanup(self):
        """Test cleaning up expired entries."""
        # Add some entries
        self.cache.set("GET", "/api/test1", {"result": "test1"})
        self.cache.set("GET", "/api/test2", {"result": "test2"}, ttl=-1)  # Expired immediately
        
        # Clean up expired entries
        count = self.cache.cleanup()
        self.assertEqual(count, 1)
        hit, _ = self.cache.get("GET", "/api/test1")
        self.assertTrue(hit)
        hit, _ = self.cache.get("GET", "/api/test2")
        self.assertFalse(hit)
    
    def test_max_size(self):
        """Test that the cache respects the maximum size."""
        # Add more entries than the maximum size
        for i in range(15):
            self.cache.set("GET", f"/api/test{i}", {"result": f"test{i}"})
        
        # Check that the cache size is limited
        self.assertLessEqual(len(self.cache.cache), 10)


class TestAPIClientCache(unittest.TestCase):
    """Tests for the APIClient caching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient("http://example.com", enable_cache=True)
        
        # Mock the session.request method
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"result": "test"}
        self.mock_response.ok = True
        self.client.session.request = MagicMock(return_value=self.mock_response)
    
    def test_is_cacheable(self):
        """Test checking if a request is cacheable."""
        # Test with caching enabled
        cacheable, ttl = self.client._is_cacheable("GET", "/api/test")
        self.assertTrue(cacheable)
        self.assertIsNone(ttl)
        
        # Test with caching disabled
        self.client.enable_cache = False
        cacheable, ttl = self.client._is_cacheable("GET", "/api/test")
        self.assertFalse(cacheable)
        self.assertIsNone(ttl)
        
        # Test with non-GET method
        self.client.enable_cache = True
        cacheable, ttl = self.client._is_cacheable("POST", "/api/test")
        self.assertFalse(cacheable)
        self.assertIsNone(ttl)
        
        # Test with cacheable endpoint
        cacheable, ttl = self.client._is_cacheable("GET", "/api/session")
        self.assertTrue(cacheable)
        self.assertEqual(ttl, 60)
    
    def test_request_cache(self):
        """Test that requests are cached."""
        # Make a request
        result1 = self.client._request("GET", "/api/test")
        self.assertEqual(result1, {"result": "test"})
        self.assertEqual(self.client.session.request.call_count, 1)
        
        # Make the same request again
        result2 = self.client._request("GET", "/api/test")
        self.assertEqual(result2, {"result": "test"})
        # The request should be served from the cache
        self.assertEqual(self.client.session.request.call_count, 1)
        
        # Make a request with skip_cache=True
        result3 = self.client._request("GET", "/api/test", skip_cache=True)
        self.assertEqual(result3, {"result": "test"})
        # A new request should be made
        self.assertEqual(self.client.session.request.call_count, 2)
    
    def test_enable_caching(self):
        """Test enabling and disabling caching."""
        # Make a request with caching enabled
        result1 = self.client._request("GET", "/api/test")
        self.assertEqual(result1, {"result": "test"})
        self.assertEqual(self.client.session.request.call_count, 1)
        
        # Make the same request again
        result2 = self.client._request("GET", "/api/test")
        self.assertEqual(result2, {"result": "test"})
        # The request should be served from the cache
        self.assertEqual(self.client.session.request.call_count, 1)
        
        # Disable caching
        self.client.enable_caching(False)
        
        # Make the same request again
        result3 = self.client._request("GET", "/api/test")
        self.assertEqual(result3, {"result": "test"})
        # A new request should be made
        self.assertEqual(self.client.session.request.call_count, 2)
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        # Make a request
        result1 = self.client._request("GET", "/api/test")
        self.assertEqual(result1, {"result": "test"})
        self.assertEqual(self.client.session.request.call_count, 1)
        
        # Clear the cache
        self.client.clear_cache()
        
        # Make the same request again
        result2 = self.client._request("GET", "/api/test")
        self.assertEqual(result2, {"result": "test"})
        # A new request should be made
        self.assertEqual(self.client.session.request.call_count, 2)
    
    def test_invalidate_cache(self):
        """Test invalidating the cache."""
        # Make some requests
        self.client._request("GET", "/api/test1")
        self.client._request("GET", "/api/test2")
        self.assertEqual(self.client.session.request.call_count, 2)
        
        # Invalidate the cache for a specific path
        self.client.invalidate_cache(path="/api/test1")
        
        # Make the same requests again
        self.client._request("GET", "/api/test1")
        self.client._request("GET", "/api/test2")
        # Only one new request should be made
        self.assertEqual(self.client.session.request.call_count, 3)


class TestSDKClientCache(unittest.TestCase):
    """Tests for the SDKClient caching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the APIClient
        self.mock_api_client = MagicMock()
        
        # Create an SDKClient with the mock APIClient
        self.client = SDKClient("http://example.com")
        self.client.api_client = self.mock_api_client
    
    def test_enable_caching(self):
        """Test enabling and disabling caching."""
        self.client.enable_caching(True)
        self.mock_api_client.enable_caching.assert_called_with(True)
        
        self.client.enable_caching(False)
        self.mock_api_client.enable_caching.assert_called_with(False)
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        self.mock_api_client.clear_cache.return_value = 5
        result = self.client.clear_cache()
        self.assertEqual(result, 5)
        self.mock_api_client.clear_cache.assert_called_once()
    
    def test_invalidate_cache(self):
        """Test invalidating the cache."""
        self.mock_api_client.invalidate_cache.return_value = 3
        result = self.client.invalidate_cache("GET", "/api/test")
        self.assertEqual(result, 3)
        self.mock_api_client.invalidate_cache.assert_called_with("GET", "/api/test")
    
    def test_query_with_cache(self):
        """Test querying with cache control."""
        self.mock_api_client._request.return_value = {"results": [{"id": 1}]}
        result = self.client.query_with_cache("MATCH (n) RETURN n", {"param": "value"}, skip_cache=True)
        self.assertEqual(result, [{"id": 1}])
        self.mock_api_client._request.assert_called_with(
            method="POST",
            path="/api/database/query",
            data={"query": "MATCH (n) RETURN n", "params": {"param": "value"}},
            skip_cache=True
        )


if __name__ == "__main__":
    unittest.main()
"""
Rate Limiter for Science Data Kit API

This module provides rate limiting functionality for the Science Data Kit API,
allowing for configurable limits on API requests to prevent abuse and ensure fair usage.
"""

from typing import Dict, Any, Optional, Tuple, List, Set
import time
import threading
import logging
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Strategies for rate limiting."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitRule:
    """
    Rule for rate limiting.
    
    Attributes:
        requests: Maximum number of requests allowed.
        period: Time period in seconds.
        strategy: Rate limiting strategy.
        scope: Scope of the rate limit (e.g., "global", "user", "ip").
        endpoints: Set of endpoints to apply the rule to. If empty, applies to all endpoints.
        methods: Set of HTTP methods to apply the rule to. If empty, applies to all methods.
    """
    requests: int
    period: int
    strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW
    scope: str = "user"
    endpoints: Set[str] = None
    methods: Set[str] = None
    
    def __post_init__(self):
        """Initialize default values for endpoints and methods."""
        if self.endpoints is None:
            self.endpoints = set()
        if self.methods is None:
            self.methods = set()
    
    def applies_to(self, endpoint: str, method: str) -> bool:
        """
        Check if the rule applies to the given endpoint and method.
        
        Args:
            endpoint: The endpoint to check.
            method: The HTTP method to check.
            
        Returns:
            True if the rule applies, False otherwise.
        """
        endpoint_match = not self.endpoints or endpoint in self.endpoints
        method_match = not self.methods or method in self.methods
        return endpoint_match and method_match


class RateLimiter:
    """
    Rate limiter for API requests.
    
    This class provides rate limiting functionality for API requests,
    allowing for configurable limits based on various criteria.
    """
    
    def __init__(self, rules: Optional[List[RateLimitRule]] = None):
        """
        Initialize the rate limiter.
        
        Args:
            rules: List of rate limit rules.
        """
        self.rules = rules or []
        self.request_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.last_reset = defaultdict(lambda: defaultdict(float))
        self.lock = threading.RLock()
    
    def add_rule(self, rule: RateLimitRule) -> None:
        """
        Add a rate limit rule.
        
        Args:
            rule: The rule to add.
        """
        self.rules.append(rule)
    
    def check_rate_limit(self, identifier: str, endpoint: str, method: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed based on rate limit rules.
        
        Args:
            identifier: The identifier for the request (e.g., user ID, IP address).
            endpoint: The endpoint being requested.
            method: The HTTP method being used.
            
        Returns:
            A tuple containing:
                - A boolean indicating whether the request is allowed.
                - A dictionary with rate limit information.
        """
        with self.lock:
            now = time.time()
            allowed = True
            rate_limit_info = {}
            
            for rule in self.rules:
                if not rule.applies_to(endpoint, method):
                    continue
                
                rule_key = f"{rule.strategy.value}:{rule.requests}:{rule.period}"
                scope_key = f"{rule.scope}:{identifier}"
                
                # Reset counters if the period has elapsed
                if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                    last_reset = self.last_reset[rule_key][scope_key]
                    if now - last_reset >= rule.period:
                        self.request_counts[rule_key][scope_key][f"{endpoint}:{method}"] = 0
                        self.last_reset[rule_key][scope_key] = now
                
                # Increment the request count
                self.request_counts[rule_key][scope_key][f"{endpoint}:{method}"] += 1
                
                # Check if the limit has been exceeded
                count = self.request_counts[rule_key][scope_key][f"{endpoint}:{method}"]
                if count > rule.requests:
                    allowed = False
                
                # Calculate remaining requests and reset time
                remaining = max(0, rule.requests - count)
                reset_time = self.last_reset[rule_key][scope_key] + rule.period
                
                # Update rate limit information
                rate_limit_info[rule_key] = {
                    "limit": rule.requests,
                    "remaining": remaining,
                    "reset": reset_time,
                    "scope": rule.scope
                }
            
            return allowed, rate_limit_info
    
    def get_rate_limit_headers(self, rate_limit_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Get HTTP headers for rate limiting.
        
        Args:
            rate_limit_info: Rate limit information from check_rate_limit.
            
        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        
        if not rate_limit_info:
            return headers
        
        # Use the most restrictive limit for the standard headers
        most_restrictive = min(
            rate_limit_info.values(),
            key=lambda x: x["remaining"] / x["limit"] if x["limit"] > 0 else float('inf')
        )
        
        headers["X-RateLimit-Limit"] = str(most_restrictive["limit"])
        headers["X-RateLimit-Remaining"] = str(most_restrictive["remaining"])
        headers["X-RateLimit-Reset"] = str(int(most_restrictive["reset"]))
        
        # Add detailed headers for each rule
        for rule_key, info in rate_limit_info.items():
            headers[f"X-RateLimit-{rule_key}-Limit"] = str(info["limit"])
            headers[f"X-RateLimit-{rule_key}-Remaining"] = str(info["remaining"])
            headers[f"X-RateLimit-{rule_key}-Reset"] = str(int(info["reset"]))
        
        return headers
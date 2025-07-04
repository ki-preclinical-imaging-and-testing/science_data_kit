"""
Neo4j Configuration Optimization for Science Data Kit

This module provides functionality for optimizing Neo4j database configuration
to improve performance for various workloads.
"""

import logging
import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union

from .db_manager import Neo4jManager, QueryError, ConnectionError


class Neo4jConfigManager:
    """
    Manages Neo4j configuration settings to optimize database performance.
    
    This class provides methods for:
    - Analyzing database workload patterns
    - Recommending optimal configuration settings
    - Applying configuration changes to Neo4j instances
    - Monitoring performance impact of configuration changes
    """
    
    def __init__(self, db_manager: Optional[Neo4jManager] = None):
        """
        Initialize the Neo4j configuration manager.
        
        Args:
            db_manager: Optional Neo4jManager instance. If None, uses the singleton instance.
        """
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Use provided db_manager or get the singleton instance
        if db_manager is None:
            from .db_manager import db_manager as default_manager
            self.db_manager = default_manager
        else:
            self.db_manager = db_manager
            
        # Default configuration templates for different workloads
        self.config_templates = {
            "default": {
                "dbms.memory.heap.initial_size": "512m",
                "dbms.memory.heap.max_size": "1g",
                "dbms.memory.pagecache.size": "512m",
                "dbms.transaction.timeout": "60s",
                "dbms.security.procedures.unrestricted": "apoc.*",
                "dbms.security.procedures.allowlist": "apoc.*",
                "dbms.directories.import": "/import",
                "dbms.default_listen_address": "0.0.0.0",
                "dbms.logs.query.enabled": "true",
                "dbms.logs.query.threshold": "1000ms"
            },
            "read_optimized": {
                "dbms.memory.heap.initial_size": "1g",
                "dbms.memory.heap.max_size": "2g",
                "dbms.memory.pagecache.size": "2g",
                "dbms.transaction.timeout": "300s",
                "dbms.security.procedures.unrestricted": "apoc.*",
                "dbms.security.procedures.allowlist": "apoc.*",
                "dbms.directories.import": "/import",
                "dbms.default_listen_address": "0.0.0.0",
                "dbms.logs.query.enabled": "true",
                "dbms.logs.query.threshold": "500ms",
                "dbms.tx_state.memory_allocation": "ON_HEAP",
                "dbms.query_cache_size": "100",
                "dbms.jvm.additional": "-XX:+UseG1GC -XX:+DisableExplicitGC"
            },
            "write_optimized": {
                "dbms.memory.heap.initial_size": "1g",
                "dbms.memory.heap.max_size": "2g",
                "dbms.memory.pagecache.size": "1g",
                "dbms.transaction.timeout": "120s",
                "dbms.security.procedures.unrestricted": "apoc.*",
                "dbms.security.procedures.allowlist": "apoc.*",
                "dbms.directories.import": "/import",
                "dbms.default_listen_address": "0.0.0.0",
                "dbms.logs.query.enabled": "true",
                "dbms.logs.query.threshold": "500ms",
                "dbms.tx_state.memory_allocation": "ON_HEAP",
                "dbms.jvm.additional": "-XX:+UseG1GC -XX:+DisableExplicitGC -XX:MaxDirectMemorySize=2g"
            },
            "balanced": {
                "dbms.memory.heap.initial_size": "1g",
                "dbms.memory.heap.max_size": "2g",
                "dbms.memory.pagecache.size": "1g",
                "dbms.transaction.timeout": "180s",
                "dbms.security.procedures.unrestricted": "apoc.*",
                "dbms.security.procedures.allowlist": "apoc.*",
                "dbms.directories.import": "/import",
                "dbms.default_listen_address": "0.0.0.0",
                "dbms.logs.query.enabled": "true",
                "dbms.logs.query.threshold": "500ms",
                "dbms.tx_state.memory_allocation": "ON_HEAP",
                "dbms.query_cache_size": "50",
                "dbms.jvm.additional": "-XX:+UseG1GC -XX:+DisableExplicitGC"
            },
            "high_memory": {
                "dbms.memory.heap.initial_size": "4g",
                "dbms.memory.heap.max_size": "8g",
                "dbms.memory.pagecache.size": "4g",
                "dbms.transaction.timeout": "300s",
                "dbms.security.procedures.unrestricted": "apoc.*",
                "dbms.security.procedures.allowlist": "apoc.*",
                "dbms.directories.import": "/import",
                "dbms.default_listen_address": "0.0.0.0",
                "dbms.logs.query.enabled": "true",
                "dbms.logs.query.threshold": "500ms",
                "dbms.tx_state.memory_allocation": "ON_HEAP",
                "dbms.query_cache_size": "200",
                "dbms.jvm.additional": "-XX:+UseG1GC -XX:+DisableExplicitGC -XX:MaxDirectMemorySize=8g"
            }
        }
    
    def get_current_configuration(self) -> Dict[str, str]:
        """
        Get the current Neo4j configuration settings.
        
        Returns:
            Dictionary containing current configuration settings
            
        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        try:
            # For Neo4j 4.x+
            result = self.db_manager.execute_query("CALL dbms.listConfig()")
            
            config = {}
            for record in result:
                name = record.get("name", "")
                value = record.get("value", "")
                if name and value:
                    config[name] = value
            
            return config
        except QueryError as e:
            self.logger.error(f"Failed to get current configuration: {e}")
            return {}
    
    def analyze_workload(self) -> str:
        """
        Analyze the database workload to determine the optimal configuration template.
        
        Returns:
            String indicating the recommended configuration template
            ("read_optimized", "write_optimized", "balanced", "high_memory", or "default")
        """
        try:
            # Get query metrics
            from .metrics import query_metrics
            metrics = query_metrics.get_metrics()
            
            # Get database statistics
            node_count = self.db_manager.query_to_value("MATCH (n) RETURN count(n) as count")
            relationship_count = self.db_manager.query_to_value("MATCH ()-[r]->() RETURN count(r) as count")
            
            # Calculate read/write ratio from metrics
            read_queries = 0
            write_queries = 0
            
            for query_info in metrics.get("queries", []):
                query = query_info.get("query", "").upper()
                if any(keyword in query for keyword in ["CREATE", "DELETE", "SET", "MERGE", "REMOVE"]):
                    write_queries += 1
                else:
                    read_queries += 1
            
            # Determine available memory
            try:
                # Try to get container memory limit
                with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                    memory_limit = int(f.read().strip()) / (1024 * 1024 * 1024)  # Convert to GB
            except:
                # Default to assuming 8GB if we can't determine
                memory_limit = 8
            
            # Determine workload type based on analysis
            if memory_limit >= 16:
                return "high_memory"
            elif read_queries > write_queries * 3:  # Read-heavy workload (3:1 ratio)
                return "read_optimized"
            elif write_queries > read_queries:  # Write-heavy workload
                return "write_optimized"
            else:  # Balanced workload
                return "balanced"
                
        except Exception as e:
            self.logger.error(f"Error analyzing workload: {e}")
            return "default"
    
    def get_recommended_configuration(self, workload_type: Optional[str] = None) -> Dict[str, str]:
        """
        Get recommended configuration settings based on workload type.
        
        Args:
            workload_type: Optional workload type. If None, analyzes the current workload.
            
        Returns:
            Dictionary containing recommended configuration settings
        """
        if workload_type is None:
            workload_type = self.analyze_workload()
        
        if workload_type not in self.config_templates:
            self.logger.warning(f"Unknown workload type: {workload_type}. Using default configuration.")
            workload_type = "default"
        
        return self.config_templates[workload_type]
    
    def apply_configuration_to_container(self, config: Dict[str, str], container_name: Optional[str] = None) -> bool:
        """
        Apply configuration settings to a Neo4j container.
        
        Args:
            config: Dictionary containing configuration settings
            container_name: Optional container name. If None, uses the container_name from db_manager.
            
        Returns:
            True if configuration was applied successfully, False otherwise
        """
        if container_name is None:
            container_name = self.db_manager.container_name
        
        try:
            import docker
            client = docker.from_env()
            
            # Find the container
            containers = client.containers.list(all=True, filters={"name": container_name})
            if not containers:
                self.logger.error(f"Container {container_name} not found")
                return False
            
            container = containers[0]
            
            # Check if container is running
            if container.status != "running":
                self.logger.error(f"Container {container_name} is not running")
                return False
            
            # Create neo4j.conf with the new settings
            conf_content = "\n".join([f"{key}={value}" for key, value in config.items()])
            
            # Write the configuration to a temporary file
            temp_conf_path = "/tmp/neo4j.conf"
            with open(temp_conf_path, "w") as f:
                f.write(conf_content)
            
            # Copy the configuration file to the container
            with open(temp_conf_path, "rb") as f:
                container.put_archive("/var/lib/neo4j/conf", f.read())
            
            # Restart the container to apply changes
            container.restart()
            
            self.logger.info(f"Applied configuration to container {container_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply configuration to container: {e}")
            return False
    
    def optimize_configuration(self, workload_type: Optional[str] = None, 
                              auto_apply: bool = False) -> Dict[str, Any]:
        """
        Optimize Neo4j configuration based on workload analysis.
        
        Args:
            workload_type: Optional workload type. If None, analyzes the current workload.
            auto_apply: If True, automatically applies the recommended configuration.
            
        Returns:
            Dictionary containing optimization results
        """
        # Get current configuration
        current_config = self.get_current_configuration()
        
        # Get recommended configuration
        if workload_type is None:
            workload_type = self.analyze_workload()
        
        recommended_config = self.get_recommended_configuration(workload_type)
        
        # Identify differences
        differences = {}
        for key, value in recommended_config.items():
            if key not in current_config or current_config[key] != value:
                differences[key] = {
                    "current": current_config.get(key, "not set"),
                    "recommended": value
                }
        
        # Apply configuration if requested
        applied = False
        if auto_apply and differences:
            applied = self.apply_configuration_to_container(recommended_config)
        
        return {
            "workload_type": workload_type,
            "current_config": current_config,
            "recommended_config": recommended_config,
            "differences": differences,
            "applied": applied
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the Neo4j database.
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # Get query metrics
            from .metrics import query_metrics
            metrics = query_metrics.get_metrics()
            
            # Get database statistics
            node_count = self.db_manager.query_to_value("MATCH (n) RETURN count(n) as count")
            relationship_count = self.db_manager.query_to_value("MATCH ()-[r]->() RETURN count(r) as count")
            
            # Get memory usage
            memory_query = "CALL dbms.queryJmx('java.lang:type=Memory') YIELD attributes RETURN attributes.HeapMemoryUsage.value as heap"
            try:
                memory_result = self.db_manager.execute_query(memory_query)
                if memory_result and "heap" in memory_result[0]:
                    heap_memory = memory_result[0]["heap"]
                    used_memory = heap_memory.get("used", 0) / (1024 * 1024)  # Convert to MB
                    max_memory = heap_memory.get("max", 0) / (1024 * 1024)  # Convert to MB
                else:
                    used_memory = "unknown"
                    max_memory = "unknown"
            except:
                used_memory = "unknown"
                max_memory = "unknown"
            
            # Get page cache statistics
            pagecache_query = "CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Page cache') YIELD attributes RETURN attributes"
            try:
                pagecache_result = self.db_manager.execute_query(pagecache_query)
                if pagecache_result:
                    pagecache_stats = pagecache_result[0]["attributes"]
                    hits = pagecache_stats.get("Hits", {}).get("value", 0)
                    misses = pagecache_stats.get("Misses", {}).get("value", 0)
                    if hits and misses:
                        hit_ratio = hits / (hits + misses) * 100
                    else:
                        hit_ratio = 0
                else:
                    hit_ratio = "unknown"
            except:
                hit_ratio = "unknown"
            
            return {
                "database_stats": {
                    "node_count": node_count,
                    "relationship_count": relationship_count
                },
                "memory_usage": {
                    "used_memory_mb": used_memory,
                    "max_memory_mb": max_memory
                },
                "page_cache": {
                    "hit_ratio_percent": hit_ratio
                },
                "query_metrics": metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}


# Create a singleton instance
config_manager = Neo4jConfigManager()
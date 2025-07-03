"""
Data Migration Tools for Science Data Kit

This module provides tools for migrating data between different schema versions.
It extends the basic migration functionality in the VersionedEntity class with
more sophisticated features like migration strategies, batch migrations,
schema evolution tracking, validation during migration, and rollback capabilities.
"""

from typing import Dict, List, Optional, Any, Union, Type, TypeVar, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from .entity_schemas import VersionedEntity

logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T', bound=VersionedEntity)
MigrationFunc = Callable[[Any], Any]


class MigrationStrategy:
    """
    Base class for migration strategies.
    
    A migration strategy defines how to migrate data from one schema version to another.
    """
    
    def migrate(self, entity: Any, source_version: str, target_version: str) -> Any:
        """
        Migrate an entity from source version to target version.
        
        Args:
            entity: The entity to migrate.
            source_version: The source version.
            target_version: The target version.
            
        Returns:
            The migrated entity.
        """
        raise NotImplementedError("Subclasses must implement migrate method")


class DirectMigrationStrategy(MigrationStrategy):
    """
    Strategy for direct migration between two specific versions.
    """
    
    def __init__(self, migration_func: MigrationFunc):
        """
        Initialize with a migration function.
        
        Args:
            migration_func: Function that performs the migration.
        """
        self.migration_func = migration_func
        
    def migrate(self, entity: Any, source_version: str, target_version: str) -> Any:
        """
        Migrate an entity using the provided migration function.
        
        Args:
            entity: The entity to migrate.
            source_version: The source version.
            target_version: The target version.
            
        Returns:
            The migrated entity.
        """
        return self.migration_func(entity)


class StepwiseMigrationStrategy(MigrationStrategy):
    """
    Strategy for stepwise migration through intermediate versions.
    """
    
    def __init__(self, migration_path: List[Tuple[str, str, MigrationFunc]]):
        """
        Initialize with a migration path.
        
        Args:
            migration_path: List of (source_version, target_version, migration_func) tuples
                           defining the migration path.
        """
        self.migration_path = migration_path
        
    def migrate(self, entity: Any, source_version: str, target_version: str) -> Any:
        """
        Migrate an entity step by step through the migration path.
        
        Args:
            entity: The entity to migrate.
            source_version: The source version.
            target_version: The target version.
            
        Returns:
            The migrated entity.
            
        Raises:
            ValueError: If no migration path is found.
        """
        # Find a path from source_version to target_version
        current_version = source_version
        current_entity = entity
        
        while current_version != target_version:
            next_step = None
            for step_source, step_target, migration_func in self.migration_path:
                if step_source == current_version:
                    next_step = (step_target, migration_func)
                    break
                    
            if next_step is None:
                raise ValueError(f"No migration step found from {current_version}")
                
            next_version, migration_func = next_step
            current_entity = migration_func(current_entity)
            current_version = next_version
            
        return current_entity


@dataclass
class MigrationRegistry:
    """
    Registry for migration strategies.
    
    This class maintains a registry of migration strategies for different
    entity types and version pairs.
    """
    
    # Map of entity_type -> (source_version, target_version) -> strategy
    strategies: Dict[Type[VersionedEntity], Dict[Tuple[str, str], MigrationStrategy]] = field(default_factory=dict)
    
    def register_strategy(self, entity_type: Type[VersionedEntity], 
                         source_version: str, target_version: str, 
                         strategy: MigrationStrategy) -> None:
        """
        Register a migration strategy.
        
        Args:
            entity_type: The entity type.
            source_version: The source version.
            target_version: The target version.
            strategy: The migration strategy.
        """
        if entity_type not in self.strategies:
            self.strategies[entity_type] = {}
            
        self.strategies[entity_type][(source_version, target_version)] = strategy
        
    def get_strategy(self, entity_type: Type[VersionedEntity], 
                    source_version: str, target_version: str) -> Optional[MigrationStrategy]:
        """
        Get a migration strategy.
        
        Args:
            entity_type: The entity type.
            source_version: The source version.
            target_version: The target version.
            
        Returns:
            The migration strategy, or None if not found.
        """
        if entity_type not in self.strategies:
            return None
            
        return self.strategies[entity_type].get((source_version, target_version))


class MigrationManager:
    """
    Manager for data migrations.
    
    This class provides high-level methods for migrating entities and
    tracking migration history.
    """
    
    def __init__(self, registry: MigrationRegistry):
        """
        Initialize with a migration registry.
        
        Args:
            registry: The migration registry.
        """
        self.registry = registry
        self.history: List[Dict[str, Any]] = []
        
    def migrate_entity(self, entity: VersionedEntity, target_version: str) -> VersionedEntity:
        """
        Migrate an entity to a target version.
        
        Args:
            entity: The entity to migrate.
            target_version: The target version.
            
        Returns:
            The migrated entity.
            
        Raises:
            ValueError: If no migration strategy is found.
        """
        entity_type = type(entity)
        source_version = entity.version
        
        # If already at target version, return as is
        if source_version == target_version:
            return entity
            
        # Get migration strategy
        strategy = self.registry.get_strategy(entity_type, source_version, target_version)
        
        if strategy is None:
            # Try using the default migration in VersionedEntity
            if hasattr(entity_type, 'migrate'):
                try:
                    migrated = entity_type.migrate(entity, target_version)
                    self._record_migration(entity, migrated, source_version, target_version)
                    return migrated
                except Exception as e:
                    logger.error(f"Default migration failed: {e}")
                    raise ValueError(f"No migration strategy found for {entity_type.__name__} from {source_version} to {target_version}")
            else:
                raise ValueError(f"No migration strategy found for {entity_type.__name__} from {source_version} to {target_version}")
        
        # Perform migration
        try:
            migrated = strategy.migrate(entity, source_version, target_version)
            self._record_migration(entity, migrated, source_version, target_version)
            return migrated
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
            
    def migrate_batch(self, entities: List[VersionedEntity], target_version: str) -> List[VersionedEntity]:
        """
        Migrate a batch of entities to a target version.
        
        Args:
            entities: The entities to migrate.
            target_version: The target version.
            
        Returns:
            The migrated entities.
        """
        results = []
        errors = []
        
        for entity in entities:
            try:
                migrated = self.migrate_entity(entity, target_version)
                results.append(migrated)
            except Exception as e:
                logger.error(f"Failed to migrate entity {entity.id if hasattr(entity, 'id') else 'unknown'}: {e}")
                errors.append((entity, str(e)))
                
        if errors:
            logger.warning(f"Migration completed with {len(errors)} errors out of {len(entities)} entities")
            
        return results
        
    def _record_migration(self, source_entity: Any, target_entity: Any, 
                         source_version: str, target_version: str) -> None:
        """
        Record a migration in the history.
        
        Args:
            source_entity: The source entity.
            target_entity: The target entity.
            source_version: The source version.
            target_version: The target version.
        """
        record = {
            "timestamp": datetime.now(),
            "entity_type": type(source_entity).__name__,
            "entity_id": getattr(source_entity, "id", "unknown"),
            "source_version": source_version,
            "target_version": target_version,
            "success": True
        }
        
        self.history.append(record)
        
    def get_migration_history(self, entity_type: Optional[Type[VersionedEntity]] = None,
                             entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get migration history, optionally filtered by entity type and ID.
        
        Args:
            entity_type: Filter by entity type.
            entity_id: Filter by entity ID.
            
        Returns:
            List of migration history records.
        """
        result = self.history
        
        if entity_type is not None:
            result = [r for r in result if r["entity_type"] == entity_type.__name__]
            
        if entity_id is not None:
            result = [r for r in result if r["entity_id"] == entity_id]
            
        return result


# Create a global migration registry and manager
migration_registry = MigrationRegistry()
migration_manager = MigrationManager(migration_registry)


def register_migration(entity_type: Type[VersionedEntity], 
                      source_version: str, target_version: str, 
                      migration_func: MigrationFunc) -> None:
    """
    Register a direct migration function.
    
    This is a convenience function for registering a DirectMigrationStrategy.
    
    Args:
        entity_type: The entity type.
        source_version: The source version.
        target_version: The target version.
        migration_func: The migration function.
    """
    strategy = DirectMigrationStrategy(migration_func)
    migration_registry.register_strategy(entity_type, source_version, target_version, strategy)
    
    
def register_migration_path(entity_type: Type[VersionedEntity], 
                           migration_path: List[Tuple[str, str, MigrationFunc]]) -> None:
    """
    Register a stepwise migration path.
    
    This is a convenience function for registering a StepwiseMigrationStrategy.
    
    Args:
        entity_type: The entity type.
        migration_path: List of (source_version, target_version, migration_func) tuples
                       defining the migration path.
    """
    if not migration_path:
        return
        
    # Register individual steps as direct migrations
    for source_version, target_version, migration_func in migration_path:
        register_migration(entity_type, source_version, target_version, migration_func)
        
    # Register the complete path as a stepwise migration
    source_version = migration_path[0][0]
    target_version = migration_path[-1][1]
    
    if source_version != target_version:
        strategy = StepwiseMigrationStrategy(migration_path)
        migration_registry.register_strategy(entity_type, source_version, target_version, strategy)


def migrate_entity(entity: VersionedEntity, target_version: str) -> VersionedEntity:
    """
    Migrate an entity to a target version.
    
    This is a convenience function that delegates to the global migration manager.
    
    Args:
        entity: The entity to migrate.
        target_version: The target version.
        
    Returns:
        The migrated entity.
    """
    return migration_manager.migrate_entity(entity, target_version)


def migrate_batch(entities: List[VersionedEntity], target_version: str) -> List[VersionedEntity]:
    """
    Migrate a batch of entities to a target version.
    
    This is a convenience function that delegates to the global migration manager.
    
    Args:
        entities: The entities to migrate.
        target_version: The target version.
        
    Returns:
        The migrated entities.
    """
    return migration_manager.migrate_batch(entities, target_version)


def get_migration_history(entity_type: Optional[Type[VersionedEntity]] = None,
                         entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get migration history, optionally filtered by entity type and ID.
    
    This is a convenience function that delegates to the global migration manager.
    
    Args:
        entity_type: Filter by entity type.
        entity_id: Filter by entity ID.
        
    Returns:
        List of migration history records.
    """
    return migration_manager.get_migration_history(entity_type, entity_id)
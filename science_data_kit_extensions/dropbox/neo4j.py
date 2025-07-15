"""
Science Data Kit - Dropbox Extension
Neo4j Integration Module

This module provides functionality for integrating Dropbox entities with
the Neo4j knowledge graph.
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from science_data_kit.core.db.db_manager import Neo4jManager as DatabaseManager
from science_data_kit.core.models.entity_schemas import BaseEntity, Relationship

from .entities import DropboxFile, DropboxFolder
from .files import DropboxFileManager

logger = logging.getLogger(__name__)

class DropboxNeo4jIntegration:
    """
    Class for integrating Dropbox entities with Neo4j knowledge graph.

    This class provides methods for importing Dropbox files and folders into
    Neo4j and creating relationships between them.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the Neo4j integration.

        Args:
            db_manager: DatabaseManager instance for Neo4j access
        """
        self.db_manager = db_manager

        # Ensure database manager is connected
        if not db_manager.is_connected():
            raise ConnectionError("Database manager is not connected to Neo4j")

    def import_dropbox_entity(self, entity: Union[DropboxFile, DropboxFolder]) -> str:
        """
        Import a Dropbox entity into Neo4j.

        Args:
            entity: DropboxFile or DropboxFolder entity

        Returns:
            Neo4j node ID
        """
        try:
            # Convert entity to dictionary
            entity_dict = entity.to_dict()

            # Create Cypher parameters
            params = {
                "id": entity.id,
                "name": entity.name,
                "description": entity.description,
                "entity_type": entity.entity_type,
                "properties": entity_dict
            }

            # Create Cypher query based on entity type
            if isinstance(entity, DropboxFile):
                query = """
                MERGE (f:File:DropboxFile {id: $id})
                SET f.name = $name,
                    f.description = $description,
                    f.entity_type = $entity_type,
                    f.file_path = $properties.file_path,
                    f.file_type = $properties.file_type,
                    f.size_bytes = $properties.size_bytes,
                    f.created_at = datetime($properties.created_at),
                    f.modified_at = datetime($properties.modified_at),
                    f.dropbox_id = $properties.complex_properties.dropbox_metadata.value.id,
                    f.dropbox_path = $properties.complex_properties.dropbox_metadata.value.path,
                    f.properties = $properties
                RETURN id(f) as node_id
                """
                # Convert datetime strings to Neo4j datetime format
                params["properties"]["created_at"] = entity_dict["created_at"].replace("T", " ")
                params["properties"]["modified_at"] = entity_dict["modified_at"].replace("T", " ")

            elif isinstance(entity, DropboxFolder):
                query = """
                MERGE (f:Folder:DropboxFolder {id: $id})
                SET f.name = $name,
                    f.description = $description,
                    f.entity_type = $entity_type,
                    f.dropbox_id = $properties.complex_properties.dropbox_metadata.value.id,
                    f.dropbox_path = $properties.complex_properties.dropbox_metadata.value.path,
                    f.properties = $properties
                RETURN id(f) as node_id
                """
            else:
                raise ValueError(f"Unsupported entity type: {type(entity)}")

            # Execute query
            result = self.db_manager.execute_query(query, params)

            # Return Neo4j node ID
            return result[0]["node_id"]

        except Neo4jError as e:
            logger.error(f"Neo4j error importing entity {entity.id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error importing entity {entity.id}: {e}")
            raise

    def create_folder_hierarchy_relationships(
        self, 
        folder_entities: List[DropboxFolder],
        file_entities: Optional[List[DropboxFile]] = None
    ) -> List[str]:
        """
        Create CONTAINS relationships between folders in a hierarchy.

        Args:
            folder_entities: List of DropboxFolder entities
            file_entities: Optional list of DropboxFile entities to include

        Returns:
            List of created relationship IDs
        """
        try:
            # Create a dictionary of folders by path for quick lookup
            folders_by_path = {
                folder.complex_properties["dropbox_metadata"].value["path"]: folder
                for folder in folder_entities
            }

            relationship_ids = []

            # Create folder-to-folder relationships
            for folder in folder_entities:
                folder_path = folder.complex_properties["dropbox_metadata"].value["path"]

                # Skip root folder
                if folder_path == "/" or not folder_path:
                    continue

                # Find parent folder
                parent_path = "/".join(folder_path.split("/")[:-1])
                if not parent_path:
                    parent_path = "/"

                parent_folder = folders_by_path.get(parent_path)

                if parent_folder:
                    # Create relationship
                    relationship = Relationship(
                        source_id=parent_folder.id,
                        target_id=folder.id,
                        relationship_type="CONTAINS",
                        properties={
                            "source_type": "dropbox_folder",
                            "target_type": "dropbox_folder"
                        }
                    )

                    # Import relationship to Neo4j
                    rel_id = self._import_relationship(relationship)
                    relationship_ids.append(rel_id)

            # Create folder-to-file relationships if files are provided
            if file_entities:
                for file in file_entities:
                    file_path = file.complex_properties["dropbox_metadata"].value["path"]

                    # Find parent folder
                    parent_path = "/".join(file_path.split("/")[:-1])
                    if not parent_path:
                        parent_path = "/"

                    parent_folder = folders_by_path.get(parent_path)

                    if parent_folder:
                        # Create relationship
                        relationship = Relationship(
                            source_id=parent_folder.id,
                            target_id=file.id,
                            relationship_type="CONTAINS",
                            properties={
                                "source_type": "dropbox_folder",
                                "target_type": "dropbox_file"
                            }
                        )

                        # Import relationship to Neo4j
                        rel_id = self._import_relationship(relationship)
                        relationship_ids.append(rel_id)

            return relationship_ids

        except Exception as e:
            logger.error(f"Error creating folder hierarchy relationships: {e}")
            raise

    def _import_relationship(self, relationship: Relationship) -> str:
        """
        Import a relationship into Neo4j.

        Args:
            relationship: Relationship entity

        Returns:
            Neo4j relationship ID
        """
        try:
            # Convert relationship to dictionary
            rel_dict = relationship.to_dict()

            # Create Cypher parameters
            params = {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "type": relationship.relationship_type,
                "properties": rel_dict
            }

            # Create Cypher query
            query = """
            MATCH (source {id: $source_id})
            MATCH (target {id: $target_id})
            MERGE (source)-[r:CONTAINS]->(target)
            SET r.relationship_type = $type,
                r.properties = $properties
            RETURN id(r) as relationship_id
            """

            # Execute query
            result = self.db_manager.execute_query(query, params)

            # Return Neo4j relationship ID
            return result[0]["relationship_id"]

        except Neo4jError as e:
            logger.error(f"Neo4j error importing relationship: {e}")
            raise
        except Exception as e:
            logger.error(f"Error importing relationship: {e}")
            raise

    def import_dropbox_folder_contents(
        self, 
        file_manager: DropboxFileManager, 
        folder_path: str,
        recursive: bool = False
    ) -> Tuple[List[DropboxFolder], List[DropboxFile]]:
        """
        Import the contents of a Dropbox folder into Neo4j.

        Args:
            file_manager: DropboxFileManager instance
            folder_path: Path to the folder to import
            recursive: Whether to import recursively

        Returns:
            Tuple of (folder_entities, file_entities)
        """
        try:
            # List folder contents
            items = file_manager.list_folder(folder_path, recursive=recursive)

            # Create entities
            from .entities import create_entities_from_dropbox_items
            entities = create_entities_from_dropbox_items(items)

            # Separate folders and files
            folder_entities = [e for e in entities if isinstance(e, DropboxFolder)]
            file_entities = [e for e in entities if isinstance(e, DropboxFile)]

            # Import entities to Neo4j
            for entity in entities:
                self.import_dropbox_entity(entity)

            # Create folder hierarchy relationships
            self.create_folder_hierarchy_relationships(folder_entities, file_entities)

            return folder_entities, file_entities

        except Exception as e:
            logger.error(f"Error importing folder contents for {folder_path}: {e}")
            raise

    def get_cypher_templates(self) -> Dict[str, str]:
        """
        Get a dictionary of Cypher query templates for common operations.

        Returns:
            Dictionary of named Cypher query templates
        """
        return {
            "get_dropbox_file": """
            MATCH (f:DropboxFile {id: $id})
            RETURN f
            """,

            "get_dropbox_folder": """
            MATCH (f:DropboxFolder {id: $id})
            RETURN f
            """,

            "get_folder_contents": """
            MATCH (folder:DropboxFolder {dropbox_path: $path})-[:CONTAINS]->(item)
            RETURN item
            """,

            "get_folder_hierarchy": """
            MATCH path = (root:DropboxFolder {dropbox_path: $root_path})-[:CONTAINS*]->(folder:DropboxFolder)
            RETURN path
            """,

            "get_file_ancestors": """
            MATCH path = (folder:DropboxFolder)-[:CONTAINS*]->(file:DropboxFile {id: $file_id})
            RETURN path
            """,

            "search_dropbox_files": """
            MATCH (f:DropboxFile)
            WHERE f.name CONTAINS $search_term OR f.description CONTAINS $search_term
            RETURN f
            """,

            "get_shared_files": """
            MATCH (f:DropboxFile)
            WHERE exists(f.properties.complex_properties.dropbox_sharing)
            RETURN f
            """
        }

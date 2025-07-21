"""
Microsoft Graph Neo4j Integration for Science Data Kit

This module provides functionality for integrating Microsoft Graph entities with the Neo4j knowledge graph.
It includes functions for creating nodes and relationships for SharePoint sites, lists, drives, files, and folders.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.models.sharepoint_schemas import (
    SharePointSite, SharePointList, SharePointListItem, 
    SharePointDrive, SharePointFile, SharePointFolder
)

logger = logging.getLogger(__name__)


class MSGraphNeo4jIntegration:
    """
    Class for integrating Microsoft Graph entities with Neo4j.
    
    This class provides methods for creating nodes and relationships for SharePoint sites,
    lists, drives, files, and folders in the Neo4j knowledge graph.
    """
    
    def __init__(self, db_manager: Optional[Neo4jManager] = None):
        """
        Initialize the MSGraphNeo4jIntegration instance.
        
        Args:
            db_manager: Neo4j database manager instance. If None, a new instance will be created.
        """
        self.db_manager = db_manager or Neo4jManager()
    
    def create_site_node(self, site: SharePointSite) -> str:
        """
        Create a node for a SharePoint site in Neo4j.
        
        Args:
            site: The SharePoint site entity.
            
        Returns:
            The ID of the created node.
        """
        cypher = """
        MERGE (site:SharePointSite {graph_id: $graph_id})
        ON CREATE SET
            site.id = $id,
            site.name = $name,
            site.display_name = $display_name,
            site.description = $description,
            site.web_url = $web_url,
            site.site_collection_id = $site_collection_id,
            site.root_web = $root_web,
            site.created_by = $created_by,
            site.last_modified_by = $last_modified_by,
            site.created_at = $created_at,
            site.updated_at = $updated_at
        ON MATCH SET
            site.name = $name,
            site.display_name = $display_name,
            site.description = $description,
            site.web_url = $web_url,
            site.site_collection_id = $site_collection_id,
            site.root_web = $root_web,
            site.created_by = $created_by,
            site.last_modified_by = $last_modified_by,
            site.updated_at = $updated_at
        RETURN site.id as id
        """
        
        params = {
            'id': site.id,
            'graph_id': site.graph_id,
            'name': site.name,
            'display_name': site.display_name,
            'description': site.description,
            'web_url': site.web_url,
            'site_collection_id': site.site_collection_id,
            'root_web': site.root_web,
            'created_by': site.created_by,
            'last_modified_by': site.last_modified_by,
            'created_at': site.created_at.isoformat(),
            'updated_at': site.updated_at.isoformat()
        }
        
        result = self.db_manager.run_query(cypher, params)
        return result[0]['id'] if result else None
    
    def create_list_node(self, list_entity: SharePointList) -> str:
        """
        Create a node for a SharePoint list in Neo4j.
        
        Args:
            list_entity: The SharePoint list entity.
            
        Returns:
            The ID of the created node.
        """
        cypher = """
        MERGE (list:SharePointList {graph_id: $graph_id})
        ON CREATE SET
            list.id = $id,
            list.name = $name,
            list.display_name = $display_name,
            list.description = $description,
            list.web_url = $web_url,
            list.site_id = $site_id,
            list.list_template = $list_template,
            list.created_by = $created_by,
            list.last_modified_by = $last_modified_by,
            list.created_at = $created_at,
            list.updated_at = $updated_at
        ON MATCH SET
            list.name = $name,
            list.display_name = $display_name,
            list.description = $description,
            list.web_url = $web_url,
            list.site_id = $site_id,
            list.list_template = $list_template,
            list.created_by = $created_by,
            list.last_modified_by = $last_modified_by,
            list.updated_at = $updated_at
        
        WITH list
        
        MATCH (site:SharePointSite {graph_id: $site_id})
        MERGE (site)-[:HAS_LIST]->(list)
        
        RETURN list.id as id
        """
        
        params = {
            'id': list_entity.id,
            'graph_id': list_entity.graph_id,
            'name': list_entity.name,
            'display_name': list_entity.display_name,
            'description': list_entity.description,
            'web_url': list_entity.web_url,
            'site_id': list_entity.site_id,
            'list_template': list_entity.list_template,
            'created_by': list_entity.created_by,
            'last_modified_by': list_entity.last_modified_by,
            'created_at': list_entity.created_at.isoformat(),
            'updated_at': list_entity.updated_at.isoformat()
        }
        
        result = self.db_manager.run_query(cypher, params)
        return result[0]['id'] if result else None
    
    def create_list_item_node(self, item: SharePointListItem) -> str:
        """
        Create a node for a SharePoint list item in Neo4j.
        
        Args:
            item: The SharePoint list item entity.
            
        Returns:
            The ID of the created node.
        """
        # Convert fields to a format that can be stored in Neo4j
        fields_json = {k: str(v) for k, v in item.fields.items()}
        
        cypher = """
        MERGE (item:SharePointListItem {graph_id: $graph_id})
        ON CREATE SET
            item.id = $id,
            item.name = $name,
            item.list_id = $list_id,
            item.site_id = $site_id,
            item.web_url = $web_url,
            item.created_by = $created_by,
            item.last_modified_by = $last_modified_by,
            item.fields = $fields,
            item.created_at = $created_at,
            item.updated_at = $updated_at
        ON MATCH SET
            item.name = $name,
            item.list_id = $list_id,
            item.site_id = $site_id,
            item.web_url = $web_url,
            item.created_by = $created_by,
            item.last_modified_by = $last_modified_by,
            item.fields = $fields,
            item.updated_at = $updated_at
        
        WITH item
        
        MATCH (list:SharePointList {graph_id: $list_id})
        MERGE (list)-[:HAS_ITEM]->(item)
        
        RETURN item.id as id
        """
        
        params = {
            'id': item.id,
            'graph_id': item.graph_id,
            'name': item.name,
            'list_id': item.list_id,
            'site_id': item.site_id,
            'web_url': item.web_url,
            'created_by': item.created_by,
            'last_modified_by': item.last_modified_by,
            'fields': fields_json,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        }
        
        result = self.db_manager.run_query(cypher, params)
        return result[0]['id'] if result else None
    
    def create_drive_node(self, drive: SharePointDrive) -> str:
        """
        Create a node for a SharePoint drive in Neo4j.
        
        Args:
            drive: The SharePoint drive entity.
            
        Returns:
            The ID of the created node.
        """
        cypher = """
        MERGE (drive:SharePointDrive {graph_id: $graph_id})
        ON CREATE SET
            drive.id = $id,
            drive.name = $name,
            drive.display_name = $display_name,
            drive.description = $description,
            drive.web_url = $web_url,
            drive.site_id = $site_id,
            drive.drive_type = $drive_type,
            drive.created_by = $created_by,
            drive.last_modified_by = $last_modified_by,
            drive.root_folder_id = $root_folder_id,
            drive.created_at = $created_at,
            drive.updated_at = $updated_at
        ON MATCH SET
            drive.name = $name,
            drive.display_name = $display_name,
            drive.description = $description,
            drive.web_url = $web_url,
            drive.site_id = $site_id,
            drive.drive_type = $drive_type,
            drive.created_by = $created_by,
            drive.last_modified_by = $last_modified_by,
            drive.root_folder_id = $root_folder_id,
            drive.updated_at = $updated_at
        
        WITH drive
        
        MATCH (site:SharePointSite {graph_id: $site_id})
        MERGE (site)-[:HAS_DRIVE]->(drive)
        
        RETURN drive.id as id
        """
        
        params = {
            'id': drive.id,
            'graph_id': drive.graph_id,
            'name': drive.name,
            'display_name': drive.display_name,
            'description': drive.description,
            'web_url': drive.web_url,
            'site_id': drive.site_id,
            'drive_type': drive.drive_type,
            'created_by': drive.created_by,
            'last_modified_by': drive.last_modified_by,
            'root_folder_id': drive.root_folder_id,
            'created_at': drive.created_at.isoformat(),
            'updated_at': drive.updated_at.isoformat()
        }
        
        result = self.db_manager.run_query(cypher, params)
        return result[0]['id'] if result else None
    
    def create_file_node(self, file: SharePointFile) -> str:
        """
        Create a node for a SharePoint file in Neo4j.
        
        Args:
            file: The SharePoint file entity.
            
        Returns:
            The ID of the created node.
        """
        cypher = """
        MERGE (file:SharePointFile {graph_id: $graph_id})
        ON CREATE SET
            file.id = $id,
            file.name = $name,
            file.site_id = $site_id,
            file.drive_id = $drive_id,
            file.web_url = $web_url,
            file.size = $size,
            file.file_type = $file_type,
            file.content_type = $content_type,
            file.etag = $etag,
            file.shared = $shared,
            file.virus_status = $virus_status,
            file.created_by = $created_by,
            file.last_modified_by = $last_modified_by,
            file.parent_reference = $parent_reference,
            file.created_at = $created_at,
            file.updated_at = $updated_at
        ON MATCH SET
            file.name = $name,
            file.site_id = $site_id,
            file.drive_id = $drive_id,
            file.web_url = $web_url,
            file.size = $size,
            file.file_type = $file_type,
            file.content_type = $content_type,
            file.etag = $etag,
            file.shared = $shared,
            file.virus_status = $virus_status,
            file.created_by = $created_by,
            file.last_modified_by = $last_modified_by,
            file.parent_reference = $parent_reference,
            file.updated_at = $updated_at
        
        WITH file
        
        MATCH (drive:SharePointDrive {graph_id: $drive_id})
        MERGE (drive)-[:CONTAINS]->(file)
        
        WITH file
        
        MATCH (folder:SharePointFolder {graph_id: $parent_reference})
        MERGE (folder)-[:CONTAINS]->(file)
        
        RETURN file.id as id
        """
        
        params = {
            'id': file.id,
            'graph_id': file.graph_id,
            'name': file.name,
            'site_id': file.site_id,
            'drive_id': file.drive_id,
            'web_url': file.web_url,
            'size': file.size,
            'file_type': file.file_type,
            'content_type': file.content_type,
            'etag': file.etag,
            'shared': file.shared,
            'virus_status': file.virus_status,
            'created_by': file.created_by,
            'last_modified_by': file.last_modified_by,
            'parent_reference': file.parent_reference,
            'created_at': file.created_at.isoformat(),
            'updated_at': file.updated_at.isoformat()
        }
        
        result = self.db_manager.run_query(cypher, params)
        return result[0]['id'] if result else None
    
    def create_folder_node(self, folder: SharePointFolder) -> str:
        """
        Create a node for a SharePoint folder in Neo4j.
        
        Args:
            folder: The SharePoint folder entity.
            
        Returns:
            The ID of the created node.
        """
        cypher = """
        MERGE (folder:SharePointFolder {graph_id: $graph_id})
        ON CREATE SET
            folder.id = $id,
            folder.name = $name,
            folder.site_id = $site_id,
            folder.drive_id = $drive_id,
            folder.web_url = $web_url,
            folder.child_count = $child_count,
            folder.shared = $shared,
            folder.created_by = $created_by,
            folder.last_modified_by = $last_modified_by,
            folder.parent_reference = $parent_reference,
            folder.created_at = $created_at,
            folder.updated_at = $updated_at
        ON MATCH SET
            folder.name = $name,
            folder.site_id = $site_id,
            folder.drive_id = $drive_id,
            folder.web_url = $web_url,
            folder.child_count = $child_count,
            folder.shared = $shared,
            folder.created_by = $created_by,
            folder.last_modified_by = $last_modified_by,
            folder.parent_reference = $parent_reference,
            folder.updated_at = $updated_at
        
        WITH folder
        
        MATCH (drive:SharePointDrive {graph_id: $drive_id})
        MERGE (drive)-[:CONTAINS]->(folder)
        
        WITH folder
        
        MATCH (parent:SharePointFolder {graph_id: $parent_reference})
        WHERE $parent_reference <> $graph_id
        MERGE (parent)-[:CONTAINS]->(folder)
        
        RETURN folder.id as id
        """
        
        params = {
            'id': folder.id,
            'graph_id': folder.graph_id,
            'name': folder.name,
            'site_id': folder.site_id,
            'drive_id': folder.drive_id,
            'web_url': folder.web_url,
            'child_count': folder.child_count,
            'shared': folder.shared,
            'created_by': folder.created_by,
            'last_modified_by': folder.last_modified_by,
            'parent_reference': folder.parent_reference,
            'created_at': folder.created_at.isoformat(),
            'updated_at': folder.updated_at.isoformat()
        }
        
        result = self.db_manager.run_query(cypher, params)
        return result[0]['id'] if result else None
    
    def import_sharepoint_site(self, site: SharePointSite, include_drives: bool = True, include_lists: bool = True) -> Dict[str, Any]:
        """
        Import a SharePoint site and its related entities into Neo4j.
        
        Args:
            site: The SharePoint site entity.
            include_drives: Whether to import drives associated with the site.
            include_lists: Whether to import lists associated with the site.
            
        Returns:
            A dictionary with the results of the import operation.
        """
        results = {
            'site': self.create_site_node(site),
            'drives': [],
            'lists': []
        }
        
        if include_drives:
            for drive_id in site.drives:
                results['drives'].append(drive_id)
        
        if include_lists:
            for list_id in site.lists:
                results['lists'].append(list_id)
        
        return results
    
    def import_sharepoint_drive(self, drive: SharePointDrive, include_items: bool = False, items: List[Union[SharePointFile, SharePointFolder]] = None) -> Dict[str, Any]:
        """
        Import a SharePoint drive and its items into Neo4j.
        
        Args:
            drive: The SharePoint drive entity.
            include_items: Whether to import items associated with the drive.
            items: List of items to import (if include_items is True).
            
        Returns:
            A dictionary with the results of the import operation.
        """
        results = {
            'drive': self.create_drive_node(drive),
            'items': []
        }
        
        if include_items and items:
            for item in items:
                if isinstance(item, SharePointFile):
                    item_id = self.create_file_node(item)
                elif isinstance(item, SharePointFolder):
                    item_id = self.create_folder_node(item)
                else:
                    continue
                
                results['items'].append(item_id)
        
        return results
    
    def import_sharepoint_list(self, list_entity: SharePointList, include_items: bool = False, items: List[SharePointListItem] = None) -> Dict[str, Any]:
        """
        Import a SharePoint list and its items into Neo4j.
        
        Args:
            list_entity: The SharePoint list entity.
            include_items: Whether to import items associated with the list.
            items: List of items to import (if include_items is True).
            
        Returns:
            A dictionary with the results of the import operation.
        """
        results = {
            'list': self.create_list_node(list_entity),
            'items': []
        }
        
        if include_items and items:
            for item in items:
                item_id = self.create_list_item_node(item)
                results['items'].append(item_id)
        
        return results
    
    def get_cypher_templates(self) -> Dict[str, str]:
        """
        Get a dictionary of Cypher query templates for common operations.
        
        Returns:
            A dictionary mapping template names to Cypher queries.
        """
        return {
            'get_site_by_id': """
                MATCH (site:SharePointSite {graph_id: $graph_id})
                RETURN site
            """,
            'get_drive_by_id': """
                MATCH (drive:SharePointDrive {graph_id: $graph_id})
                RETURN drive
            """,
            'get_list_by_id': """
                MATCH (list:SharePointList {graph_id: $graph_id})
                RETURN list
            """,
            'get_file_by_id': """
                MATCH (file:SharePointFile {graph_id: $graph_id})
                RETURN file
            """,
            'get_folder_by_id': """
                MATCH (folder:SharePointFolder {graph_id: $graph_id})
                RETURN folder
            """,
            'get_site_drives': """
                MATCH (site:SharePointSite {graph_id: $site_id})-[:HAS_DRIVE]->(drive:SharePointDrive)
                RETURN drive
            """,
            'get_site_lists': """
                MATCH (site:SharePointSite {graph_id: $site_id})-[:HAS_LIST]->(list:SharePointList)
                RETURN list
            """,
            'get_drive_files': """
                MATCH (drive:SharePointDrive {graph_id: $drive_id})-[:CONTAINS]->(file:SharePointFile)
                RETURN file
            """,
            'get_drive_folders': """
                MATCH (drive:SharePointDrive {graph_id: $drive_id})-[:CONTAINS]->(folder:SharePointFolder)
                RETURN folder
            """,
            'get_folder_contents': """
                MATCH (folder:SharePointFolder {graph_id: $folder_id})-[:CONTAINS]->(item)
                RETURN item
            """,
            'get_list_items': """
                MATCH (list:SharePointList {graph_id: $list_id})-[:HAS_ITEM]->(item:SharePointListItem)
                RETURN item
            """,
            'search_files_by_name': """
                MATCH (file:SharePointFile)
                WHERE file.name CONTAINS $search_term
                RETURN file
            """,
            'search_files_by_content_type': """
                MATCH (file:SharePointFile)
                WHERE file.content_type CONTAINS $search_term
                RETURN file
            """,
            'get_file_path': """
                MATCH path = (drive:SharePointDrive)-[:CONTAINS*]->(file:SharePointFile {graph_id: $file_id})
                RETURN path
            """,
            'get_folder_path': """
                MATCH path = (drive:SharePointDrive)-[:CONTAINS*]->(folder:SharePointFolder {graph_id: $folder_id})
                RETURN path
            """,
            'get_related_files': """
                MATCH (file:SharePointFile {graph_id: $file_id})
                MATCH (related:SharePointFile)
                WHERE related.file_type = file.file_type AND related.graph_id <> $file_id
                RETURN related
            """
        }
"""
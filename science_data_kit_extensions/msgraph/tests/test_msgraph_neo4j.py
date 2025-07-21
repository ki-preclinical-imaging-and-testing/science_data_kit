"""
Tests for Microsoft Graph Neo4j Integration for Science Data Kit
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from science_data_kit.core.db.msgraph_neo4j import MSGraphNeo4jIntegration
from science_data_kit.core.models.sharepoint_schemas import (
    SharePointSite, SharePointList, SharePointListItem, 
    SharePointDrive, SharePointFile, SharePointFolder
)


class TestMSGraphNeo4jIntegration(unittest.TestCase):
    """
    Test cases for Microsoft Graph Neo4j Integration
    """
    
    def setUp(self):
        """
        Set up test environment
        """
        # Create a mock Neo4jManager
        self.mock_db_manager = MagicMock()
        
        # Create an instance of MSGraphNeo4jIntegration with the mock db_manager
        self.integration = MSGraphNeo4jIntegration(db_manager=self.mock_db_manager)
        
        # Set up mock return values
        self.mock_db_manager.run_query.return_value = [{"id": "test-id"}]
        
        # Create test entities
        self.site = SharePointSite(
            id="site1",
            name="Test Site",
            graph_id="graph-site1",
            resource_type="site",
            display_name="Test Site",
            description="A test site",
            web_url="https://example.com/sites/test",
            site_collection_id="collection1",
            root_web=True,
            created_by="User 1",
            last_modified_by="User 2",
            drives=["drive1", "drive2"],
            lists=["list1", "list2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.list_entity = SharePointList(
            id="list1",
            name="Test List",
            graph_id="graph-list1",
            resource_type="list",
            display_name="Test List",
            description="A test list",
            web_url="https://example.com/sites/test/lists/testlist",
            site_id="site1",
            list_template="genericList",
            created_by="User 1",
            last_modified_by="User 2",
            columns={"Title": {"type": "text"}},
            items=["item1", "item2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.list_item = SharePointListItem(
            id="item1",
            name="Test Item",
            graph_id="graph-item1",
            resource_type="listItem",
            list_id="list1",
            site_id="site1",
            web_url="https://example.com/sites/test/lists/testlist/items/1",
            created_by="User 1",
            last_modified_by="User 2",
            fields={"Title": "Test Item", "Description": "A test item"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.drive = SharePointDrive(
            id="drive1",
            name="Test Drive",
            graph_id="graph-drive1",
            resource_type="drive",
            display_name="Test Drive",
            description="A test drive",
            web_url="https://example.com/sites/test/documents",
            site_id="site1",
            drive_type="documentLibrary",
            created_by="User 1",
            last_modified_by="User 2",
            quota={},
            root_folder_id="root",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.file = SharePointFile(
            id="file1",
            name="test.docx",
            graph_id="graph-file1",
            resource_type="file",
            site_id="site1",
            drive_id="drive1",
            web_url="https://example.com/sites/test/documents/test.docx",
            size=12345,
            file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content_type="Document",
            etag="etag123",
            shared=True,
            sharing_info={"scope": "users"},
            virus_status="clean",
            checkout_info={},
            version_info={"version": "1.0"},
            created_by="User 1",
            last_modified_by="User 2",
            parent_reference="folder1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.folder = SharePointFolder(
            id="folder1",
            name="Test Folder",
            graph_id="graph-folder1",
            resource_type="folder",
            site_id="site1",
            drive_id="drive1",
            web_url="https://example.com/sites/test/documents/testfolder",
            size=0,
            child_count=5,
            special_folder={},
            shared=True,
            sharing_info={"scope": "users"},
            created_by="User 1",
            last_modified_by="User 2",
            parent_reference="root",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_create_site_node(self):
        """
        Test creating a SharePoint site node in Neo4j
        """
        # Call the method
        result = self.integration.create_site_node(self.site)
        
        # Check that run_query was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check that the Cypher query contains the expected MERGE statement
        cypher_query = self.mock_db_manager.run_query.call_args[0][0]
        self.assertIn("MERGE (site:SharePointSite {graph_id: $graph_id})", cypher_query)
        
        # Check that the parameters contain the correct values
        params = self.mock_db_manager.run_query.call_args[0][1]
        self.assertEqual(params["id"], "site1")
        self.assertEqual(params["graph_id"], "graph-site1")
        self.assertEqual(params["name"], "Test Site")
        self.assertEqual(params["display_name"], "Test Site")
        self.assertEqual(params["description"], "A test site")
        self.assertEqual(params["web_url"], "https://example.com/sites/test")
        self.assertEqual(params["site_collection_id"], "collection1")
        self.assertTrue(params["root_web"])
        self.assertEqual(params["created_by"], "User 1")
        self.assertEqual(params["last_modified_by"], "User 2")
        
        # Check the result
        self.assertEqual(result, "test-id")
    
    def test_create_list_node(self):
        """
        Test creating a SharePoint list node in Neo4j
        """
        # Call the method
        result = self.integration.create_list_node(self.list_entity)
        
        # Check that run_query was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check that the Cypher query contains the expected MERGE statements
        cypher_query = self.mock_db_manager.run_query.call_args[0][0]
        self.assertIn("MERGE (list:SharePointList {graph_id: $graph_id})", cypher_query)
        self.assertIn("MATCH (site:SharePointSite {graph_id: $site_id})", cypher_query)
        self.assertIn("MERGE (site)-[:HAS_LIST]->(list)", cypher_query)
        
        # Check that the parameters contain the correct values
        params = self.mock_db_manager.run_query.call_args[0][1]
        self.assertEqual(params["id"], "list1")
        self.assertEqual(params["graph_id"], "graph-list1")
        self.assertEqual(params["name"], "Test List")
        self.assertEqual(params["display_name"], "Test List")
        self.assertEqual(params["description"], "A test list")
        self.assertEqual(params["web_url"], "https://example.com/sites/test/lists/testlist")
        self.assertEqual(params["site_id"], "site1")
        self.assertEqual(params["list_template"], "genericList")
        self.assertEqual(params["created_by"], "User 1")
        self.assertEqual(params["last_modified_by"], "User 2")
        
        # Check the result
        self.assertEqual(result, "test-id")
    
    def test_create_list_item_node(self):
        """
        Test creating a SharePoint list item node in Neo4j
        """
        # Call the method
        result = self.integration.create_list_item_node(self.list_item)
        
        # Check that run_query was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check that the Cypher query contains the expected MERGE statements
        cypher_query = self.mock_db_manager.run_query.call_args[0][0]
        self.assertIn("MERGE (item:SharePointListItem {graph_id: $graph_id})", cypher_query)
        self.assertIn("MATCH (list:SharePointList {graph_id: $list_id})", cypher_query)
        self.assertIn("MERGE (list)-[:HAS_ITEM]->(item)", cypher_query)
        
        # Check that the parameters contain the correct values
        params = self.mock_db_manager.run_query.call_args[0][1]
        self.assertEqual(params["id"], "item1")
        self.assertEqual(params["graph_id"], "graph-item1")
        self.assertEqual(params["name"], "Test Item")
        self.assertEqual(params["list_id"], "list1")
        self.assertEqual(params["site_id"], "site1")
        self.assertEqual(params["web_url"], "https://example.com/sites/test/lists/testlist/items/1")
        self.assertEqual(params["created_by"], "User 1")
        self.assertEqual(params["last_modified_by"], "User 2")
        self.assertEqual(params["fields"], {"Title": "Test Item", "Description": "A test item"})
        
        # Check the result
        self.assertEqual(result, "test-id")
    
    def test_create_drive_node(self):
        """
        Test creating a SharePoint drive node in Neo4j
        """
        # Call the method
        result = self.integration.create_drive_node(self.drive)
        
        # Check that run_query was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check that the Cypher query contains the expected MERGE statements
        cypher_query = self.mock_db_manager.run_query.call_args[0][0]
        self.assertIn("MERGE (drive:SharePointDrive {graph_id: $graph_id})", cypher_query)
        self.assertIn("MATCH (site:SharePointSite {graph_id: $site_id})", cypher_query)
        self.assertIn("MERGE (site)-[:HAS_DRIVE]->(drive)", cypher_query)
        
        # Check that the parameters contain the correct values
        params = self.mock_db_manager.run_query.call_args[0][1]
        self.assertEqual(params["id"], "drive1")
        self.assertEqual(params["graph_id"], "graph-drive1")
        self.assertEqual(params["name"], "Test Drive")
        self.assertEqual(params["display_name"], "Test Drive")
        self.assertEqual(params["description"], "A test drive")
        self.assertEqual(params["web_url"], "https://example.com/sites/test/documents")
        self.assertEqual(params["site_id"], "site1")
        self.assertEqual(params["drive_type"], "documentLibrary")
        self.assertEqual(params["created_by"], "User 1")
        self.assertEqual(params["last_modified_by"], "User 2")
        self.assertEqual(params["root_folder_id"], "root")
        
        # Check the result
        self.assertEqual(result, "test-id")
    
    def test_create_file_node(self):
        """
        Test creating a SharePoint file node in Neo4j
        """
        # Call the method
        result = self.integration.create_file_node(self.file)
        
        # Check that run_query was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check that the Cypher query contains the expected MERGE statements
        cypher_query = self.mock_db_manager.run_query.call_args[0][0]
        self.assertIn("MERGE (file:SharePointFile {graph_id: $graph_id})", cypher_query)
        self.assertIn("MATCH (drive:SharePointDrive {graph_id: $drive_id})", cypher_query)
        self.assertIn("MERGE (drive)-[:CONTAINS]->(file)", cypher_query)
        self.assertIn("MATCH (folder:SharePointFolder {graph_id: $parent_reference})", cypher_query)
        self.assertIn("MERGE (folder)-[:CONTAINS]->(file)", cypher_query)
        
        # Check that the parameters contain the correct values
        params = self.mock_db_manager.run_query.call_args[0][1]
        self.assertEqual(params["id"], "file1")
        self.assertEqual(params["graph_id"], "graph-file1")
        self.assertEqual(params["name"], "test.docx")
        self.assertEqual(params["site_id"], "site1")
        self.assertEqual(params["drive_id"], "drive1")
        self.assertEqual(params["web_url"], "https://example.com/sites/test/documents/test.docx")
        self.assertEqual(params["size"], 12345)
        self.assertEqual(params["file_type"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(params["content_type"], "Document")
        self.assertEqual(params["etag"], "etag123")
        self.assertTrue(params["shared"])
        self.assertEqual(params["virus_status"], "clean")
        self.assertEqual(params["created_by"], "User 1")
        self.assertEqual(params["last_modified_by"], "User 2")
        self.assertEqual(params["parent_reference"], "folder1")
        
        # Check the result
        self.assertEqual(result, "test-id")
    
    def test_create_folder_node(self):
        """
        Test creating a SharePoint folder node in Neo4j
        """
        # Call the method
        result = self.integration.create_folder_node(self.folder)
        
        # Check that run_query was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check that the Cypher query contains the expected MERGE statements
        cypher_query = self.mock_db_manager.run_query.call_args[0][0]
        self.assertIn("MERGE (folder:SharePointFolder {graph_id: $graph_id})", cypher_query)
        self.assertIn("MATCH (drive:SharePointDrive {graph_id: $drive_id})", cypher_query)
        self.assertIn("MERGE (drive)-[:CONTAINS]->(folder)", cypher_query)
        self.assertIn("MATCH (parent:SharePointFolder {graph_id: $parent_reference})", cypher_query)
        self.assertIn("MERGE (parent)-[:CONTAINS]->(folder)", cypher_query)
        
        # Check that the parameters contain the correct values
        params = self.mock_db_manager.run_query.call_args[0][1]
        self.assertEqual(params["id"], "folder1")
        self.assertEqual(params["graph_id"], "graph-folder1")
        self.assertEqual(params["name"], "Test Folder")
        self.assertEqual(params["site_id"], "site1")
        self.assertEqual(params["drive_id"], "drive1")
        self.assertEqual(params["web_url"], "https://example.com/sites/test/documents/testfolder")
        self.assertEqual(params["child_count"], 5)
        self.assertTrue(params["shared"])
        self.assertEqual(params["created_by"], "User 1")
        self.assertEqual(params["last_modified_by"], "User 2")
        self.assertEqual(params["parent_reference"], "root")
        
        # Check the result
        self.assertEqual(result, "test-id")
    
    def test_import_sharepoint_site(self):
        """
        Test importing a SharePoint site and its related entities into Neo4j
        """
        # Call the method
        result = self.integration.import_sharepoint_site(self.site)
        
        # Check that create_site_node was called with the correct arguments
        self.mock_db_manager.run_query.assert_called_once()
        
        # Check the result
        self.assertEqual(result["site"], "test-id")
        self.assertEqual(result["drives"], ["drive1", "drive2"])
        self.assertEqual(result["lists"], ["list1", "list2"])
    
    def test_get_cypher_templates(self):
        """
        Test getting Cypher query templates for common operations
        """
        # Call the method
        templates = self.integration.get_cypher_templates()
        
        # Check that the templates dictionary contains the expected keys
        self.assertIn("get_site_by_id", templates)
        self.assertIn("get_drive_by_id", templates)
        self.assertIn("get_list_by_id", templates)
        self.assertIn("get_file_by_id", templates)
        self.assertIn("get_folder_by_id", templates)
        self.assertIn("get_site_drives", templates)
        self.assertIn("get_site_lists", templates)
        self.assertIn("get_drive_files", templates)
        self.assertIn("get_drive_folders", templates)
        self.assertIn("get_folder_contents", templates)
        self.assertIn("get_list_items", templates)
        self.assertIn("search_files_by_name", templates)
        self.assertIn("search_files_by_content_type", templates)
        self.assertIn("get_file_path", templates)
        self.assertIn("get_folder_path", templates)
        self.assertIn("get_related_files", templates)
        
        # Check that the templates contain valid Cypher queries
        for template_name, template in templates.items():
            self.assertIsInstance(template, str)
            self.assertIn("MATCH", template)
            self.assertIn("RETURN", template)


if __name__ == "__main__":
    unittest.main()
"""
"""
Tests for SharePoint entity schemas in the Microsoft Graph Extension for Science Data Kit
"""

import unittest
from datetime import datetime

from science_data_kit.core.models.sharepoint_schemas import (
    SharePointSite, SharePointList, SharePointListItem, 
    SharePointDrive, SharePointFile, SharePointFolder,
    convert_msgraph_site, convert_msgraph_list, convert_msgraph_list_item,
    convert_msgraph_drive, convert_msgraph_drive_item, validate_sharepoint_entity
)


class TestSharePointSchemas(unittest.TestCase):
    """
    Test cases for SharePoint entity schemas
    """
    
    def test_sharepoint_site(self):
        """
        Test SharePointSite entity schema
        """
        # Create a SharePointSite instance
        site = SharePointSite(
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
        
        # Validate the entity
        errors = validate_sharepoint_entity(site, SharePointSite)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")
        
        # Check attributes
        self.assertEqual(site.id, "site1")
        self.assertEqual(site.name, "Test Site")
        self.assertEqual(site.graph_id, "graph-site1")
        self.assertEqual(site.resource_type, "site")
        self.assertEqual(site.display_name, "Test Site")
        self.assertEqual(site.description, "A test site")
        self.assertEqual(site.web_url, "https://example.com/sites/test")
        self.assertEqual(site.site_collection_id, "collection1")
        self.assertTrue(site.root_web)
        self.assertEqual(site.created_by, "User 1")
        self.assertEqual(site.last_modified_by, "User 2")
        self.assertEqual(site.drives, ["drive1", "drive2"])
        self.assertEqual(site.lists, ["list1", "list2"])
    
    def test_sharepoint_list(self):
        """
        Test SharePointList entity schema
        """
        # Create a SharePointList instance
        list_entity = SharePointList(
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
        
        # Validate the entity
        errors = validate_sharepoint_entity(list_entity, SharePointList)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")
        
        # Check attributes
        self.assertEqual(list_entity.id, "list1")
        self.assertEqual(list_entity.name, "Test List")
        self.assertEqual(list_entity.graph_id, "graph-list1")
        self.assertEqual(list_entity.resource_type, "list")
        self.assertEqual(list_entity.display_name, "Test List")
        self.assertEqual(list_entity.description, "A test list")
        self.assertEqual(list_entity.web_url, "https://example.com/sites/test/lists/testlist")
        self.assertEqual(list_entity.site_id, "site1")
        self.assertEqual(list_entity.list_template, "genericList")
        self.assertEqual(list_entity.created_by, "User 1")
        self.assertEqual(list_entity.last_modified_by, "User 2")
        self.assertEqual(list_entity.columns, {"Title": {"type": "text"}})
        self.assertEqual(list_entity.items, ["item1", "item2"])
    
    def test_sharepoint_file(self):
        """
        Test SharePointFile entity schema
        """
        # Create a SharePointFile instance
        file = SharePointFile(
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
        
        # Validate the entity
        errors = validate_sharepoint_entity(file, SharePointFile)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")
        
        # Check attributes
        self.assertEqual(file.id, "file1")
        self.assertEqual(file.name, "test.docx")
        self.assertEqual(file.graph_id, "graph-file1")
        self.assertEqual(file.resource_type, "file")
        self.assertEqual(file.site_id, "site1")
        self.assertEqual(file.drive_id, "drive1")
        self.assertEqual(file.web_url, "https://example.com/sites/test/documents/test.docx")
        self.assertEqual(file.size, 12345)
        self.assertEqual(file.file_type, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(file.content_type, "Document")
        self.assertEqual(file.etag, "etag123")
        self.assertTrue(file.shared)
        self.assertEqual(file.sharing_info, {"scope": "users"})
        self.assertEqual(file.virus_status, "clean")
        self.assertEqual(file.checkout_info, {})
        self.assertEqual(file.version_info, {"version": "1.0"})
        self.assertEqual(file.created_by, "User 1")
        self.assertEqual(file.last_modified_by, "User 2")
        self.assertEqual(file.parent_reference, "folder1")
    
    def test_convert_msgraph_site(self):
        """
        Test convert_msgraph_site function
        """
        # Create a sample Microsoft Graph site response
        site_data = {
            "id": "site1",
            "displayName": "Test Site",
            "description": "A test site",
            "webUrl": "https://example.com/sites/test",
            "siteCollection": {"id": "collection1"},
            "root": {"web": {"id": "root1"}},
            "createdBy": {"user": {"displayName": "User 1"}},
            "lastModifiedBy": {"user": {"displayName": "User 2"}}
        }
        
        # Convert to SharePointSite
        site = convert_msgraph_site(site_data)
        
        # Check conversion
        self.assertEqual(site.id, "site1")
        self.assertEqual(site.name, "Test Site")
        self.assertEqual(site.graph_id, "site1")
        self.assertEqual(site.resource_type, "site")
        self.assertEqual(site.display_name, "Test Site")
        self.assertEqual(site.description, "A test site")
        self.assertEqual(site.web_url, "https://example.com/sites/test")
        self.assertEqual(site.site_collection_id, "collection1")
        self.assertTrue(site.root_web)
        self.assertEqual(site.created_by, "User 1")
        self.assertEqual(site.last_modified_by, "User 2")
        self.assertEqual(site.drives, [])
        self.assertEqual(site.lists, [])
    
    def test_convert_msgraph_drive_item(self):
        """
        Test convert_msgraph_drive_item function
        """
        # Create a sample Microsoft Graph file response
        file_data = {
            "id": "file1",
            "name": "test.docx",
            "webUrl": "https://example.com/sites/test/documents/test.docx",
            "size": 12345,
            "file": {
                "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "virusStatus": "clean"
            },
            "contentType": {"name": "Document"},
            "eTag": "etag123",
            "@microsoft.graph.downloadUrl": "https://example.com/download",
            "sharingInfo": {"scope": "users"},
            "createdBy": {"user": {"displayName": "User 1"}},
            "lastModifiedBy": {"user": {"displayName": "User 2"}},
            "parentReference": {"id": "folder1"}
        }
        
        # Convert to SharePointFile
        file = convert_msgraph_drive_item(file_data, "site1", "drive1")
        
        # Check conversion
        self.assertIsInstance(file, SharePointFile)
        self.assertEqual(file.id, "file1")
        self.assertEqual(file.name, "test.docx")
        self.assertEqual(file.graph_id, "file1")
        self.assertEqual(file.resource_type, "file")
        self.assertEqual(file.site_id, "site1")
        self.assertEqual(file.drive_id, "drive1")
        self.assertEqual(file.web_url, "https://example.com/sites/test/documents/test.docx")
        self.assertEqual(file.size, 12345)
        self.assertEqual(file.file_type, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(file.content_type, "Document")
        self.assertEqual(file.etag, "etag123")
        self.assertTrue(file.shared)
        self.assertEqual(file.sharing_info, {"scope": "users"})
        self.assertEqual(file.virus_status, "clean")
        self.assertEqual(file.created_by, "User 1")
        self.assertEqual(file.last_modified_by, "User 2")
        self.assertEqual(file.parent_reference, "folder1")
        
        # Create a sample Microsoft Graph folder response
        folder_data = {
            "id": "folder1",
            "name": "Test Folder",
            "webUrl": "https://example.com/sites/test/documents/testfolder",
            "size": 0,
            "folder": {"childCount": 5},
            "specialFolder": {"name": "documents"},
            "sharingInfo": {"scope": "users"},
            "createdBy": {"user": {"displayName": "User 1"}},
            "lastModifiedBy": {"user": {"displayName": "User 2"}},
            "parentReference": {"id": "root"}
        }
        
        # Convert to SharePointFolder
        folder = convert_msgraph_drive_item(folder_data, "site1", "drive1")
        
        # Check conversion
        self.assertIsInstance(folder, SharePointFolder)
        self.assertEqual(folder.id, "folder1")
        self.assertEqual(folder.name, "Test Folder")
        self.assertEqual(folder.graph_id, "folder1")
        self.assertEqual(folder.resource_type, "folder")
        self.assertEqual(folder.site_id, "site1")
        self.assertEqual(folder.drive_id, "drive1")
        self.assertEqual(folder.web_url, "https://example.com/sites/test/documents/testfolder")
        self.assertEqual(folder.child_count, 5)
        self.assertEqual(folder.special_folder, {"name": "documents"})
        self.assertTrue(folder.shared)
        self.assertEqual(folder.sharing_info, {"scope": "users"})
        self.assertEqual(folder.created_by, "User 1")
        self.assertEqual(folder.last_modified_by, "User 2")
        self.assertEqual(folder.parent_reference, "root")


if __name__ == "__main__":
    unittest.main()
"""
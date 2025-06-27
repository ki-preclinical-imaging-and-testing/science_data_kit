"""
Unit tests for Microsoft Graph API Entity Schemas

This module contains unit tests for the Microsoft Graph API entity schemas.
"""

import unittest
from datetime import datetime
from typing import Dict, Any

from science_data_kit.core.models.msgraph_schemas import (
    User, Group, Message, Event, DriveItem,
    validate_msgraph_entity,
    convert_msgraph_user,
    convert_msgraph_group,
    convert_msgraph_message
)


class TestMSGraphSchemas(unittest.TestCase):
    """
    Test cases for the Microsoft Graph API entity schemas.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        # Sample user data
        self.user_data = {
            "id": "user-1",
            "displayName": "User 1",
            "mail": "user1@example.com",
            "userPrincipalName": "user1@example.com",
            "department": "Engineering",
            "jobTitle": "Software Engineer",
            "officeLocation": "Building A",
            "businessPhones": ["+1 123-456-7890"],
            "mobilePhone": "+1 234-567-8901"
        }
        
        # Sample group data
        self.group_data = {
            "id": "group-1",
            "displayName": "Group 1",
            "description": "Test Group 1",
            "mail": "group1@example.com",
            "groupTypes": ["Unified"],
            "securityEnabled": True,
            "mailEnabled": True
        }
        
        # Sample message data
        self.message_data = {
            "id": "message-1",
            "subject": "Test Subject",
            "body": {
                "content": "Test Body",
                "contentType": "text"
            },
            "from": {
                "emailAddress": {
                    "address": "sender@example.com",
                    "name": "Sender"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "recipient1@example.com",
                        "name": "Recipient 1"
                    }
                },
                {
                    "emailAddress": {
                        "address": "recipient2@example.com",
                        "name": "Recipient 2"
                    }
                }
            ],
            "ccRecipients": [
                {
                    "emailAddress": {
                        "address": "cc1@example.com",
                        "name": "CC 1"
                    }
                }
            ],
            "bccRecipients": [
                {
                    "emailAddress": {
                        "address": "bcc1@example.com",
                        "name": "BCC 1"
                    }
                }
            ],
            "receivedDateTime": "2023-01-01T12:00:00Z",
            "hasAttachments": True
        }
        
        # Sample event data
        self.event_data = {
            "id": "event-1",
            "subject": "Test Event",
            "body": {
                "content": "Test Event Body",
                "contentType": "text"
            },
            "start": {
                "dateTime": "2023-01-01T10:00:00Z",
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": "2023-01-01T11:00:00Z",
                "timeZone": "UTC"
            },
            "location": {
                "displayName": "Conference Room A"
            },
            "organizer": {
                "emailAddress": {
                    "address": "organizer@example.com",
                    "name": "Organizer"
                }
            },
            "attendees": [
                {
                    "emailAddress": {
                        "address": "attendee1@example.com",
                        "name": "Attendee 1"
                    }
                }
            ],
            "isAllDay": False
        }
        
        # Sample drive item data
        self.drive_item_data = {
            "id": "item-1",
            "name": "Test File.docx",
            "size": 12345,
            "webUrl": "https://example.com/test-file",
            "createdBy": {
                "user": {
                    "displayName": "Creator"
                }
            },
            "lastModifiedBy": {
                "user": {
                    "displayName": "Modifier"
                }
            },
            "file": {
                "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            },
            "parentReference": {
                "id": "folder-1"
            }
        }
    
    def test_user_schema(self):
        """
        Test User schema.
        """
        # Create a User instance
        user = User(
            id="user-1",
            graph_id="user-1",
            resource_type="user",
            display_name="User 1",
            email="user1@example.com",
            user_principal_name="user1@example.com",
            department="Engineering",
            job_title="Software Engineer",
            office_location="Building A",
            business_phones=["+1 123-456-7890"],
            mobile_phone="+1 234-567-8901",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            properties={}
        )
        
        # Verify the instance
        self.assertEqual(user.id, "user-1")
        self.assertEqual(user.graph_id, "user-1")
        self.assertEqual(user.resource_type, "user")
        self.assertEqual(user.display_name, "User 1")
        self.assertEqual(user.email, "user1@example.com")
        self.assertEqual(user.user_principal_name, "user1@example.com")
        self.assertEqual(user.department, "Engineering")
        self.assertEqual(user.job_title, "Software Engineer")
        self.assertEqual(user.office_location, "Building A")
        self.assertEqual(user.business_phones, ["+1 123-456-7890"])
        self.assertEqual(user.mobile_phone, "+1 234-567-8901")
    
    def test_group_schema(self):
        """
        Test Group schema.
        """
        # Create a Group instance
        group = Group(
            id="group-1",
            graph_id="group-1",
            resource_type="group",
            display_name="Group 1",
            description="Test Group 1",
            mail="group1@example.com",
            group_types=["Unified"],
            security_enabled=True,
            mail_enabled=True,
            members=["user-1", "user-2"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            properties={}
        )
        
        # Verify the instance
        self.assertEqual(group.id, "group-1")
        self.assertEqual(group.graph_id, "group-1")
        self.assertEqual(group.resource_type, "group")
        self.assertEqual(group.display_name, "Group 1")
        self.assertEqual(group.description, "Test Group 1")
        self.assertEqual(group.mail, "group1@example.com")
        self.assertEqual(group.group_types, ["Unified"])
        self.assertEqual(group.security_enabled, True)
        self.assertEqual(group.mail_enabled, True)
        self.assertEqual(group.members, ["user-1", "user-2"])
    
    def test_message_schema(self):
        """
        Test Message schema.
        """
        # Create a Message instance
        message = Message(
            id="message-1",
            graph_id="message-1",
            resource_type="message",
            subject="Test Subject",
            body="Test Body",
            from_email="sender@example.com",
            to_recipients=["recipient1@example.com", "recipient2@example.com"],
            cc_recipients=["cc1@example.com"],
            bcc_recipients=["bcc1@example.com"],
            received_datetime=datetime(2023, 1, 1, 12, 0, 0),
            has_attachments=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            properties={}
        )
        
        # Verify the instance
        self.assertEqual(message.id, "message-1")
        self.assertEqual(message.graph_id, "message-1")
        self.assertEqual(message.resource_type, "message")
        self.assertEqual(message.subject, "Test Subject")
        self.assertEqual(message.body, "Test Body")
        self.assertEqual(message.from_email, "sender@example.com")
        self.assertEqual(message.to_recipients, ["recipient1@example.com", "recipient2@example.com"])
        self.assertEqual(message.cc_recipients, ["cc1@example.com"])
        self.assertEqual(message.bcc_recipients, ["bcc1@example.com"])
        self.assertEqual(message.received_datetime, datetime(2023, 1, 1, 12, 0, 0))
        self.assertEqual(message.has_attachments, True)
    
    def test_event_schema(self):
        """
        Test Event schema.
        """
        # Create an Event instance
        event = Event(
            id="event-1",
            graph_id="event-1",
            resource_type="event",
            subject="Test Event",
            body="Test Event Body",
            start_datetime=datetime(2023, 1, 1, 10, 0, 0),
            end_datetime=datetime(2023, 1, 1, 11, 0, 0),
            location="Conference Room A",
            organizer="organizer@example.com",
            attendees=["attendee1@example.com"],
            is_all_day=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            properties={}
        )
        
        # Verify the instance
        self.assertEqual(event.id, "event-1")
        self.assertEqual(event.graph_id, "event-1")
        self.assertEqual(event.resource_type, "event")
        self.assertEqual(event.subject, "Test Event")
        self.assertEqual(event.body, "Test Event Body")
        self.assertEqual(event.start_datetime, datetime(2023, 1, 1, 10, 0, 0))
        self.assertEqual(event.end_datetime, datetime(2023, 1, 1, 11, 0, 0))
        self.assertEqual(event.location, "Conference Room A")
        self.assertEqual(event.organizer, "organizer@example.com")
        self.assertEqual(event.attendees, ["attendee1@example.com"])
        self.assertEqual(event.is_all_day, False)
    
    def test_drive_item_schema(self):
        """
        Test DriveItem schema.
        """
        # Create a DriveItem instance
        drive_item = DriveItem(
            id="item-1",
            graph_id="item-1",
            resource_type="driveItem",
            name="Test File.docx",
            size=12345,
            web_url="https://example.com/test-file",
            created_by="Creator",
            last_modified_by="Modifier",
            file_type="docx",
            folder_child_count=0,
            parent_reference="folder-1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            properties={}
        )
        
        # Verify the instance
        self.assertEqual(drive_item.id, "item-1")
        self.assertEqual(drive_item.graph_id, "item-1")
        self.assertEqual(drive_item.resource_type, "driveItem")
        self.assertEqual(drive_item.name, "Test File.docx")
        self.assertEqual(drive_item.size, 12345)
        self.assertEqual(drive_item.web_url, "https://example.com/test-file")
        self.assertEqual(drive_item.created_by, "Creator")
        self.assertEqual(drive_item.last_modified_by, "Modifier")
        self.assertEqual(drive_item.file_type, "docx")
        self.assertEqual(drive_item.folder_child_count, 0)
        self.assertEqual(drive_item.parent_reference, "folder-1")
    
    def test_validate_msgraph_entity(self):
        """
        Test validate_msgraph_entity function.
        """
        # Create a valid User instance
        user = User(
            id="user-1",
            graph_id="user-1",
            resource_type="user",
            display_name="User 1",
            email="user1@example.com",
            user_principal_name="user1@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            properties={}
        )
        
        # Validate the instance
        errors = validate_msgraph_entity(user, User)
        self.assertEqual(len(errors), 0)
        
        # Create an invalid entity (missing required fields)
        invalid_entity = {"id": "user-1"}
        
        # Validate the invalid entity
        errors = validate_msgraph_entity(invalid_entity, User)
        self.assertGreater(len(errors), 0)
    
    def test_convert_msgraph_user(self):
        """
        Test convert_msgraph_user function.
        """
        # Convert user data
        user = convert_msgraph_user(self.user_data)
        
        # Verify the result
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, "user-1")
        self.assertEqual(user.graph_id, "user-1")
        self.assertEqual(user.resource_type, "user")
        self.assertEqual(user.display_name, "User 1")
        self.assertEqual(user.email, "user1@example.com")
        self.assertEqual(user.user_principal_name, "user1@example.com")
        self.assertEqual(user.department, "Engineering")
        self.assertEqual(user.job_title, "Software Engineer")
        self.assertEqual(user.office_location, "Building A")
        self.assertEqual(user.business_phones, ["+1 123-456-7890"])
        self.assertEqual(user.mobile_phone, "+1 234-567-8901")
    
    def test_convert_msgraph_group(self):
        """
        Test convert_msgraph_group function.
        """
        # Convert group data
        group = convert_msgraph_group(self.group_data)
        
        # Verify the result
        self.assertIsInstance(group, Group)
        self.assertEqual(group.id, "group-1")
        self.assertEqual(group.graph_id, "group-1")
        self.assertEqual(group.resource_type, "group")
        self.assertEqual(group.display_name, "Group 1")
        self.assertEqual(group.description, "Test Group 1")
        self.assertEqual(group.mail, "group1@example.com")
        self.assertEqual(group.group_types, ["Unified"])
        self.assertEqual(group.security_enabled, True)
        self.assertEqual(group.mail_enabled, True)
        self.assertEqual(group.members, [])  # Members are fetched separately
    
    def test_convert_msgraph_message(self):
        """
        Test convert_msgraph_message function.
        """
        # Convert message data
        message = convert_msgraph_message(self.message_data)
        
        # Verify the result
        self.assertIsInstance(message, Message)
        self.assertEqual(message.id, "message-1")
        self.assertEqual(message.graph_id, "message-1")
        self.assertEqual(message.resource_type, "message")
        self.assertEqual(message.subject, "Test Subject")
        self.assertEqual(message.body, "Test Body")
        self.assertEqual(message.from_email, "sender@example.com")
        self.assertEqual(message.to_recipients, ["recipient1@example.com", "recipient2@example.com"])
        self.assertEqual(message.cc_recipients, ["cc1@example.com"])
        self.assertEqual(message.bcc_recipients, ["bcc1@example.com"])
        self.assertTrue(isinstance(message.received_datetime, datetime))
        self.assertEqual(message.has_attachments, True)
        
        # Test with missing fields
        minimal_message = {
            "id": "message-2",
            "subject": "Minimal Subject"
        }
        message = convert_msgraph_message(minimal_message)
        self.assertEqual(message.id, "message-2")
        self.assertEqual(message.subject, "Minimal Subject")
        self.assertEqual(message.body, "")
        self.assertEqual(message.from_email, "")
        self.assertEqual(message.to_recipients, [])
        self.assertEqual(message.cc_recipients, [])
        self.assertEqual(message.bcc_recipients, [])
        self.assertTrue(isinstance(message.received_datetime, datetime))
        self.assertEqual(message.has_attachments, False)


if __name__ == '__main__':
    unittest.main()
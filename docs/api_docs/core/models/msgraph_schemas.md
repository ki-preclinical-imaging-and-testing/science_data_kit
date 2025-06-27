# msgraph_schemas.py - Microsoft Graph API Entity Schemas

This module defines entity schemas for Microsoft Graph API entities, providing a consistent structure for data validation and database operations.

## Classes

### MicrosoftGraphEntity

Base class for Microsoft Graph API entities.

```python
@dataclass
class MicrosoftGraphEntity(BaseEntity):
```

**Attributes:**
- `graph_id` (str): The unique identifier for the entity in Microsoft Graph.
- `resource_type` (str): The type of resource in Microsoft Graph.

### User

Schema for a Microsoft Graph user.

```python
@dataclass
class User(MicrosoftGraphEntity):
```

**Attributes:**
- `display_name` (str): The display name of the user.
- `email` (str): The email address of the user.
- `user_principal_name` (str): The user principal name (UPN) of the user.
- `department` (str, optional): The department the user works in. Defaults to "".
- `job_title` (str, optional): The job title of the user. Defaults to "".
- `office_location` (str, optional): The office location of the user. Defaults to "".
- `business_phones` (List[str], optional): The business phone numbers of the user. Defaults to an empty list.
- `mobile_phone` (str, optional): The mobile phone number of the user. Defaults to "".

### Group

Schema for a Microsoft Graph group.

```python
@dataclass
class Group(MicrosoftGraphEntity):
```

**Attributes:**
- `display_name` (str): The display name of the group.
- `description` (str, optional): The description of the group. Defaults to "".
- `mail` (str, optional): The email address of the group. Defaults to "".
- `group_types` (List[str], optional): The types of the group. Defaults to an empty list.
- `security_enabled` (bool, optional): Whether the group is security-enabled. Defaults to False.
- `mail_enabled` (bool, optional): Whether the group is mail-enabled. Defaults to False.
- `members` (List[str], optional): The members of the group. Defaults to an empty list.

### Message

Schema for a Microsoft Graph message.

```python
@dataclass
class Message(MicrosoftGraphEntity):
```

**Attributes:**
- `subject` (str): The subject of the message.
- `body` (str): The body of the message.
- `from_email` (str): The email address of the sender.
- `to_recipients` (List[str]): The email addresses of the recipients.
- `cc_recipients` (List[str], optional): The email addresses of the CC recipients. Defaults to an empty list.
- `bcc_recipients` (List[str], optional): The email addresses of the BCC recipients. Defaults to an empty list.
- `received_datetime` (datetime, optional): The date and time the message was received. Defaults to current datetime.
- `has_attachments` (bool, optional): Whether the message has attachments. Defaults to False.

### Event

Schema for a Microsoft Graph calendar event.

```python
@dataclass
class Event(MicrosoftGraphEntity):
```

**Attributes:**
- `subject` (str): The subject of the event.
- `body` (str): The body of the event.
- `start_datetime` (datetime): The start date and time of the event.
- `end_datetime` (datetime): The end date and time of the event.
- `location` (str, optional): The location of the event. Defaults to "".
- `organizer` (str, optional): The organizer of the event. Defaults to "".
- `attendees` (List[str], optional): The attendees of the event. Defaults to an empty list.
- `is_all_day` (bool, optional): Whether the event is an all-day event. Defaults to False.

### DriveItem

Schema for a Microsoft Graph drive item (file or folder).

```python
@dataclass
class DriveItem(MicrosoftGraphEntity):
```

**Attributes:**
- `name` (str): The name of the drive item.
- `size` (int): The size of the drive item in bytes.
- `web_url` (str): The URL to the drive item in the web browser.
- `created_by` (str): The user who created the drive item.
- `last_modified_by` (str): The user who last modified the drive item.
- `file_type` (str, optional): The file type of the drive item. Defaults to "".
- `folder_child_count` (int, optional): The number of children in the folder. Defaults to 0.
- `parent_reference` (str, optional): The parent folder of the drive item. Defaults to "".

## Functions

### validate_msgraph_entity

```python
def validate_msgraph_entity(entity: Any, schema_class: type) -> List[str]
```

Validates a Microsoft Graph entity against a schema class.

**Parameters:**
- `entity` (Any): The entity to validate.
- `schema_class` (type): The schema class to validate against.

**Returns:**
- A list of validation errors, or an empty list if validation passes.

### convert_msgraph_user

```python
def convert_msgraph_user(user_data: Dict[str, Any]) -> User
```

Convert Microsoft Graph user data to a User entity.

**Parameters:**
- `user_data` (Dict[str, Any]): The user data from Microsoft Graph API.

**Returns:**
- A User entity.

### convert_msgraph_group

```python
def convert_msgraph_group(group_data: Dict[str, Any]) -> Group
```

Convert Microsoft Graph group data to a Group entity.

**Parameters:**
- `group_data` (Dict[str, Any]): The group data from Microsoft Graph API.

**Returns:**
- A Group entity.

### convert_msgraph_message

```python
def convert_msgraph_message(message_data: Dict[str, Any]) -> Message
```

Convert Microsoft Graph message data to a Message entity.

**Parameters:**
- `message_data` (Dict[str, Any]): The message data from Microsoft Graph API.

**Returns:**
- A Message entity.
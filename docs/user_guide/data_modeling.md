# Data Modeling Guide

## Overview

The Science Data Kit provides powerful data modeling capabilities that allow you to define, validate, and work with complex data models in a knowledge graph. This guide explains how to use the SDK's data modeling features, including versioning for data models, relationship management utilities, data migration tools, complex property types, and data validation rules engine.

## Table of Contents

1. [Introduction](#introduction)
2. [Entity Schemas](#entity-schemas)
3. [Versioning Data Models](#versioning-data-models)
4. [Relationship Management](#relationship-management)
5. [Data Migration](#data-migration)
6. [Complex Property Types](#complex-property-types)
7. [Data Validation Rules](#data-validation-rules)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

Data modeling is a critical aspect of working with knowledge graphs. The Science Data Kit provides a comprehensive set of tools for defining, validating, and working with data models:

- **Entity Schemas**: Define the structure of nodes and relationships in your knowledge graph
- **Versioning**: Create versioned entities with support for schema versioning, migration, and backward compatibility
- **Relationship Management**: Define and work with complex relationship patterns, such as paths, trees, and graphs
- **Data Migration**: Migrate data between different schema versions
- **Complex Property Types**: Define and validate complex property types, including nested objects, arrays, and specialized types
- **Data Validation**: Define and apply validation rules to data

These features help you create robust, flexible, and maintainable data models for your knowledge graph applications.

## Entity Schemas

Entity schemas define the structure of nodes and relationships in your knowledge graph, including labels, properties, and validation rules.

### Defining Node Schemas

Here's an example of defining a node schema:

```python
from science_data_kit.core.models import EntitySchema, PropertyDefinition

# Define a schema for Person nodes
person_schema = EntitySchema(
    name="Person",
    label="Person",
    description="A person entity",
    properties=[
        PropertyDefinition(
            name="name",
            type="string",
            description="The person's name",
            required=True
        ),
        PropertyDefinition(
            name="age",
            type="integer",
            description="The person's age",
            required=True,
            validation={"min": 0, "max": 120}
        ),
        PropertyDefinition(
            name="email",
            type="string",
            description="The person's email address",
            required=False,
            validation={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
        )
    ],
    primary_key="email"
)
```

### Defining Relationship Schemas

You can also define schemas for relationships:

```python
# Define a schema for WORKS_FOR relationships
works_for_schema = EntitySchema(
    name="WorksFor",
    type="WORKS_FOR",
    description="A relationship indicating that a person works for a company",
    properties=[
        PropertyDefinition(
            name="start_date",
            type="date",
            description="The date when the person started working for the company",
            required=True
        ),
        PropertyDefinition(
            name="position",
            type="string",
            description="The person's position in the company",
            required=True
        ),
        PropertyDefinition(
            name="salary",
            type="float",
            description="The person's salary",
            required=False,
            validation={"min": 0}
        )
    ],
    source_label="Person",
    target_label="Company"
)
```

### Registering Schemas

You can register schemas with the schema registry:

```python
from science_data_kit.core.models import SchemaRegistry

# Create a schema registry
registry = SchemaRegistry()

# Register schemas
registry.register_schema(person_schema)
registry.register_schema(works_for_schema)

# Get a schema by name
retrieved_schema = registry.get_schema("Person")
print(f"Retrieved schema: {retrieved_schema.name}")
```

### Validating Data Against Schemas

You can validate data against schemas:

```python
# Create a person entity
person_data = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

# Validate the data against the schema
is_valid, errors = person_schema.validate(person_data)
if is_valid:
    print("Person data is valid")
else:
    print(f"Validation errors: {errors}")
```

## Versioning Data Models

The Science Data Kit supports versioning for data models, allowing you to evolve your schemas over time while maintaining backward compatibility.

### Creating Versioned Schemas

Here's an example of creating a versioned schema:

```python
from science_data_kit.core.models import VersionedEntitySchema

# Define a versioned schema for Person nodes
person_schema_v1 = VersionedEntitySchema(
    name="Person",
    label="Person",
    version="1.0",
    description="A person entity (version 1.0)",
    properties=[
        PropertyDefinition(
            name="name",
            type="string",
            description="The person's name",
            required=True
        ),
        PropertyDefinition(
            name="age",
            type="integer",
            description="The person's age",
            required=True,
            validation={"min": 0, "max": 120}
        ),
        PropertyDefinition(
            name="email",
            type="string",
            description="The person's email address",
            required=False,
            validation={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
        )
    ],
    primary_key="email"
)

# Create a new version of the schema
person_schema_v2 = VersionedEntitySchema(
    name="Person",
    label="Person",
    version="2.0",
    description="A person entity (version 2.0)",
    properties=[
        PropertyDefinition(
            name="name",
            type="string",
            description="The person's name",
            required=True
        ),
        PropertyDefinition(
            name="age",
            type="integer",
            description="The person's age",
            required=True,
            validation={"min": 0, "max": 120}
        ),
        PropertyDefinition(
            name="email",
            type="string",
            description="The person's email address",
            required=False,
            validation={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
        ),
        PropertyDefinition(
            name="phone",
            type="string",
            description="The person's phone number",
            required=False,
            validation={"pattern": r"^\+?[0-9]{10,15}$"}
        )
    ],
    primary_key="email"
)
```

### Registering Versioned Schemas

You can register versioned schemas with the schema registry:

```python
from science_data_kit.core.models import VersionedSchemaRegistry

# Create a versioned schema registry
registry = VersionedSchemaRegistry()

# Register schemas
registry.register_schema(person_schema_v1)
registry.register_schema(person_schema_v2)

# Get the latest version of a schema
latest_schema = registry.get_latest_schema("Person")
print(f"Latest schema version: {latest_schema.version}")

# Get a specific version of a schema
v1_schema = registry.get_schema("Person", "1.0")
print(f"Schema version 1.0: {v1_schema.version}")
```

### Schema Compatibility

You can check if schemas are compatible:

```python
# Check if schemas are compatible
is_compatible, issues = registry.check_compatibility("Person", "1.0", "2.0")
if is_compatible:
    print("Schemas are compatible")
else:
    print(f"Compatibility issues: {issues}")
```

## Relationship Management

The Science Data Kit provides utilities for managing complex relationship patterns, such as paths, trees, and graphs.

### Path Management

You can work with paths in the knowledge graph:

```python
from science_data_kit.core.models import PathManager

# Create a path manager
path_manager = PathManager(db_manager)

# Find paths between nodes
paths = path_manager.find_paths(
    start_node_id=123,
    end_node_id=456,
    relationship_types=["WORKS_FOR", "PART_OF"],
    max_depth=3
)

# Print the paths
for path in paths:
    print(f"Path: {path}")
```

### Tree Management

You can work with tree structures:

```python
from science_data_kit.core.models import TreeManager

# Create a tree manager
tree_manager = TreeManager(db_manager)

# Get a tree rooted at a node
tree = tree_manager.get_tree(
    root_node_id=123,
    relationship_type="CONTAINS",
    direction="outgoing",
    max_depth=5
)

# Print the tree
tree_manager.print_tree(tree)
```

### Graph Management

You can work with subgraphs:

```python
from science_data_kit.core.models import GraphManager

# Create a graph manager
graph_manager = GraphManager(db_manager)

# Get a subgraph
subgraph = graph_manager.get_subgraph(
    node_ids=[123, 456, 789],
    include_relationships=True
)

# Export the subgraph to a file
graph_manager.export_subgraph(subgraph, "subgraph.graphml")
```

## Data Migration

The Science Data Kit provides tools for migrating data between different schema versions.

### Creating Migration Plans

Here's an example of creating a migration plan:

```python
from science_data_kit.core.models import MigrationPlan, MigrationStep

# Create a migration plan
migration_plan = MigrationPlan(
    source_schema=person_schema_v1,
    target_schema=person_schema_v2,
    description="Migrate Person entities from version 1.0 to 2.0"
)

# Add migration steps
migration_plan.add_step(
    MigrationStep(
        description="Add phone property",
        property_name="phone",
        default_value=None
    )
)
```

### Executing Migration Plans

You can execute migration plans:

```python
from science_data_kit.core.models import DataMigrator

# Create a data migrator
migrator = DataMigrator(db_manager)

# Execute the migration plan
result = migrator.execute_plan(
    migration_plan,
    batch_size=100,
    dry_run=False
)

# Print the migration result
print(f"Migration result: {result.success}")
print(f"Entities migrated: {result.entities_migrated}")
print(f"Errors: {result.errors}")
```

### Rollback Migrations

You can rollback migrations if needed:

```python
# Rollback the migration
rollback_result = migrator.rollback(
    migration_plan,
    batch_size=100
)

# Print the rollback result
print(f"Rollback result: {rollback_result.success}")
print(f"Entities rolled back: {rollback_result.entities_migrated}")
print(f"Errors: {rollback_result.errors}")
```

## Complex Property Types

The Science Data Kit supports complex property types, including nested objects, arrays, and specialized types.

### Nested Objects

You can define nested object properties:

```python
from science_data_kit.core.models import PropertyDefinition, NestedObjectType

# Define an address type
address_type = NestedObjectType(
    properties=[
        PropertyDefinition(
            name="street",
            type="string",
            description="Street address",
            required=True
        ),
        PropertyDefinition(
            name="city",
            type="string",
            description="City",
            required=True
        ),
        PropertyDefinition(
            name="state",
            type="string",
            description="State or province",
            required=True
        ),
        PropertyDefinition(
            name="postal_code",
            type="string",
            description="Postal code",
            required=True
        ),
        PropertyDefinition(
            name="country",
            type="string",
            description="Country",
            required=True
        )
    ]
)

# Define a schema with a nested object property
person_with_address_schema = EntitySchema(
    name="PersonWithAddress",
    label="Person",
    description="A person entity with an address",
    properties=[
        PropertyDefinition(
            name="name",
            type="string",
            description="The person's name",
            required=True
        ),
        PropertyDefinition(
            name="address",
            type=address_type,
            description="The person's address",
            required=False
        )
    ],
    primary_key="name"
)
```

### Array Properties

You can define array properties:

```python
from science_data_kit.core.models import ArrayType

# Define an array of strings
string_array_type = ArrayType(
    item_type="string",
    min_items=0,
    max_items=10
)

# Define a schema with an array property
person_with_skills_schema = EntitySchema(
    name="PersonWithSkills",
    label="Person",
    description="A person entity with skills",
    properties=[
        PropertyDefinition(
            name="name",
            type="string",
            description="The person's name",
            required=True
        ),
        PropertyDefinition(
            name="skills",
            type=string_array_type,
            description="The person's skills",
            required=False
        )
    ],
    primary_key="name"
)
```

### Specialized Types

You can define specialized property types:

```python
from science_data_kit.core.models import EnumType, GeoPointType

# Define an enum type
status_type = EnumType(
    values=["active", "inactive", "pending"],
    default="active"
)

# Define a geo-point type
location_type = GeoPointType()

# Define a schema with specialized property types
person_with_specialized_types_schema = EntitySchema(
    name="PersonWithSpecializedTypes",
    label="Person",
    description="A person entity with specialized property types",
    properties=[
        PropertyDefinition(
            name="name",
            type="string",
            description="The person's name",
            required=True
        ),
        PropertyDefinition(
            name="status",
            type=status_type,
            description="The person's status",
            required=True
        ),
        PropertyDefinition(
            name="location",
            type=location_type,
            description="The person's location",
            required=False
        )
    ],
    primary_key="name"
)
```

## Data Validation Rules

The Science Data Kit provides a powerful rules engine for validating data against complex business rules.

### Defining Validation Rules

Here's an example of defining validation rules:

```python
from science_data_kit.core.models import ValidationRule, RuleSet

# Define validation rules
min_age_rule = ValidationRule(
    name="MinAgeRule",
    description="Ensures that a person's age is at least 18",
    entity_type="Person",
    condition="entity.age < 18",
    message="Person must be at least 18 years old"
)

valid_email_rule = ValidationRule(
    name="ValidEmailRule",
    description="Ensures that a person's email is valid",
    entity_type="Person",
    condition="not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', entity.email)",
    message="Invalid email format",
    imports=["import re"]
)

# Create a rule set
person_rule_set = RuleSet(
    name="PersonRules",
    description="Validation rules for Person entities",
    rules=[min_age_rule, valid_email_rule]
)
```

### Registering Rule Sets

You can register rule sets with the rules engine:

```python
from science_data_kit.core.models import RulesEngine

# Create a rules engine
rules_engine = RulesEngine()

# Register rule sets
rules_engine.register_rule_set(person_rule_set)

# Get a rule set by name
retrieved_rule_set = rules_engine.get_rule_set("PersonRules")
print(f"Retrieved rule set: {retrieved_rule_set.name}")
```

### Validating Data Against Rules

You can validate data against rules:

```python
# Create a person entity
person_data = {
    "name": "Alice",
    "age": 16,
    "email": "alice@example.com"
}

# Validate the data against the rules
validation_result = rules_engine.validate(
    entity_type="Person",
    data=person_data
)

# Print the validation result
print(f"Validation result: {validation_result.is_valid}")
if not validation_result.is_valid:
    for violation in validation_result.violations:
        print(f"Rule: {violation.rule_name}, Message: {violation.message}")
```

### Custom Validation Functions

You can define custom validation functions:

```python
from science_data_kit.core.models import CustomValidationFunction

# Define a custom validation function
def validate_age_range(entity, min_age, max_age):
    if entity.get("age") is None:
        return True, None
    age = entity["age"]
    if age < min_age or age > max_age:
        return False, f"Age must be between {min_age} and {max_age}"
    return True, None

# Create a custom validation function
age_range_validator = CustomValidationFunction(
    name="AgeRangeValidator",
    function=validate_age_range,
    parameters={"min_age": 18, "max_age": 65}
)

# Register the custom validation function
rules_engine.register_custom_function(age_range_validator)

# Use the custom validation function in a rule
custom_age_rule = ValidationRule(
    name="CustomAgeRule",
    description="Ensures that a person's age is within a specified range",
    entity_type="Person",
    condition="not custom.AgeRangeValidator(entity, 18, 65)",
    message="Person's age must be between 18 and 65"
)
```

## Best Practices

Here are some best practices for using the data modeling capabilities of the Science Data Kit:

1. **Define Clear Schemas**: Create clear, well-documented schemas for all entity types in your knowledge graph.
2. **Use Versioning**: Use versioned schemas to manage changes to your data model over time.
3. **Plan Migrations Carefully**: Plan data migrations carefully, considering the impact on existing data and applications.
4. **Validate Early**: Validate data against schemas and rules as early as possible in your data pipeline.
5. **Use Complex Types Appropriately**: Use complex property types (nested objects, arrays, specialized types) when they make your data model clearer and more maintainable.
6. **Document Relationships**: Document the relationships between entities, including their directionality, cardinality, and properties.
7. **Test Thoroughly**: Test your data model with various data scenarios to ensure it works correctly.
8. **Monitor Performance**: Monitor the performance of your data model, especially when working with large datasets.

## Troubleshooting

Here are some common issues and their solutions:

### Schema Validation Issues

- **Issue**: Schema validation fails unexpectedly.
  - **Solution**: Check that your data matches the schema definition, including property types, required properties, and validation rules. Use the validation error messages to identify specific issues.

### Migration Issues

- **Issue**: Data migration fails or produces unexpected results.
  - **Solution**: Test your migration plan with a small subset of data before applying it to your entire dataset. Use the dry run option to preview the changes without actually applying them.

### Performance Issues

- **Issue**: Operations on complex data models are slow.
  - **Solution**: Optimize your data model by simplifying complex structures, using appropriate indexes, and batching operations when possible.

### Relationship Management Issues

- **Issue**: Relationship queries return unexpected results.
  - **Solution**: Check the directionality of your relationships and ensure that your queries specify the correct relationship types and directions.

### Versioning Issues

- **Issue**: Incompatible schema versions cause errors.
  - **Solution**: Use the compatibility checking features to identify and resolve compatibility issues between schema versions.

If you encounter other issues, please refer to the SDK documentation or contact support.
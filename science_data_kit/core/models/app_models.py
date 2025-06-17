"""
Application Models for Science Data Kit

This module provides utilities for working with Neo4j models using neomodel.
It includes functions for mapping Neo4j types to neomodel property types,
initializing neomodel classes dynamically, and merging nodes with existing nodes.
"""

from typing import Dict, List, Any, Optional, Type, Tuple, Union, Callable
import pandas as pd
from neomodel import (
    StructuredNode, StringProperty, IntegerProperty, 
    RelationshipTo, DateProperty
)

def type_mapping(neo_type: str) -> Optional[Type]:
    """
    Maps Neo4j types to neomodel property types.
    
    Args:
        neo_type: The Neo4j type to map.
        
    Returns:
        The corresponding neomodel property type, or None if not found.
    """
    mapping = {
        'String': StringProperty,
        'Integer': IntegerProperty,
        'Date': DateProperty,
        # Add other Neomodel property types as needed
    }
    return mapping.get(neo_type, None)

def initialize_neomodel_classes(
    neomodel_map: Dict[str, Dict[str, str]], 
    rel_pair: Tuple[str, str] = ('has_parent', 'HAS_PARENT')
) -> Dict[str, Type[StructuredNode]]:
    """
    Dynamically creates neomodel classes based on a mapping.
    
    Args:
        neomodel_map: A dictionary mapping label names to property dictionaries.
            Each property dictionary maps property names to Neo4j types.
        rel_pair: A tuple containing (relationship_name, relationship_type).
            
    Returns:
        A dictionary mapping label names to neomodel classes.
    """
    neomodel_classes = {}
    
    # Iterate over the Neomodel map
    for label, property_dict in neomodel_map.items():
        props = {}
        for prop, neo_type in property_dict.items():
            mapped_type = type_mapping(neo_type)
            if mapped_type:
                props[prop] = mapped_type()
        
        # Define the relationship for each class
        props[rel_pair[0]] = RelationshipTo('StructuredNode', rel_pair[1])
        
        # Dynamically create Neomodel class inheriting from StructuredNode
        NewClass = type(label, (StructuredNode,), props)
        
        # Add the class to globals() so you can use it later
        globals()[label] = NewClass
        
        # Collect class information in the neomodel_classes dictionary
        neomodel_classes[label] = NewClass
    
    return neomodel_classes

def print_neomodel_map(neomodel_map: Dict[str, Dict[str, str]]) -> None:
    """
    Prints a neomodel map for debugging.
    
    Args:
        neomodel_map: A dictionary mapping label names to property dictionaries.
    """
    for label, property_types in neomodel_map.items():
        print(label)
        for prop, neo_type in property_types.items():
            print(neo_type, prop)
        print()

def generate_neomodel_map(property_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    """
    Generates a neomodel map from a property map.
    
    Args:
        property_map: A dictionary mapping label names to property dictionaries.
            
    Returns:
        A dictionary mapping label names to property type dictionaries.
    """
    neomodel_map = {}
    
    for label, property_dict in property_map.items():
        property_types = {prop: 'String' for prop in property_dict.keys()}
        neomodel_map[label] = property_types
    
    return neomodel_map

def test_labels_for_neomodel_class_availability(samples_df: pd.DataFrame) -> Dict[str, bool]:
    """
    Tests if neomodel classes are available for given labels.
    
    Args:
        samples_df: A DataFrame containing a 'label' column.
            
    Returns:
        A dictionary mapping label names to availability status.
    """
    label_class_mapping = {}
    
    label_names = list(samples_df['label'].value_counts(dropna=False).index)
    
    # Iterate through the list of label names
    for label_name in label_names:
        # Check if the class exists in the global namespace
        if label_name in globals():
            label_class_mapping[label_name] = True
        else:
            label_class_mapping[label_name] = False
            print(f"No class found for label '{label_name}'.")
    
    return label_class_mapping

def merge_nodes_with_existing(
    db_connection: Any,
    entities_df: pd.DataFrame,
    label_column: str,
    property_columns: List[str],
    target_label: str,
    match_columns: List[str],
    relationship_type: str,
    source_to_target_map: Optional[Dict[str, str]] = None
) -> None:
    """
    Merge new nodes with existing nodes in Neo4j.
    
    Args:
        db_connection: Neo4j database connection.
        entities_df: DataFrame containing entities to be merged.
        label_column: Column specifying the node label for each entity.
        property_columns: Columns to be included as properties in the node.
        target_label: Label of the target nodes to match against.
        match_columns: Columns used to match existing nodes.
        relationship_type: Type of relationship to create between nodes.
        source_to_target_map: Optional dictionary mapping source property names to target property names.
    """
    with db_connection.session() as session:
        for _, row in entities_df.iterrows():
            node_label = row[label_column]
            node_properties = {col: row[col] for col in property_columns if pd.notna(row[col])}
            m_match_conditions = ", ".join([f"{col}: ${col}" for col in node_properties.keys()])
            
            # Use target property names in the Cypher query if a mapping is provided
            if source_to_target_map:
                # Create match conditions using target property names
                n_match_conditions = ", ".join([f"{source_to_target_map.get(col, col)}: ${col}" for col in match_columns])
                
                # Create SET statements using target property names
                n_set_statements = ", ".join([f"n.{source_to_target_map.get(key, key)} = ${key}" for key in match_columns]) if match_columns else ""
            else:
                # Use source property names if no mapping is provided
                n_match_conditions = ", ".join([f"{col}: ${col}" for col in match_columns])
                n_set_statements = ", ".join([f"n.{key} = ${key}" for key in match_columns]) if match_columns else ""
            
            # Create parameters using source property names
            match_params = {col: row[col] for col in match_columns}
            
            # Create SET statements for the source entity
            m_set_statements = ", ".join([f"m.{key} = ${key}" for key in node_properties.keys()])
            
            cypher_query = f"""
            MERGE (n:{target_label} {{{n_match_conditions}}})
            ON CREATE SET {n_set_statements}
            ON MATCH SET {n_set_statements}
            MERGE (m:{node_label} {{{m_match_conditions}}})
            ON CREATE SET {m_set_statements}
            ON MATCH SET {m_set_statements}
            MERGE (m)-[:{relationship_type}]->(n)
            """
            
            params = {**match_params, **node_properties}
            session.run(cypher_query, params)

# Example model definitions using the functions above
# These are equivalent to the models defined in the original models.py file

def create_default_models() -> Dict[str, Type[StructuredNode]]:
    """
    Creates default models for the application.
    
    Returns:
        A dictionary mapping label names to neomodel classes.
    """
    # Define the property map for the default models
    property_map = {
        "Folder": {
            "filepath": "String"
        },
        "File": {
            "filepath": "String"
        }
    }
    
    # Generate the neomodel map
    neomodel_map = generate_neomodel_map(property_map)
    
    # Initialize the neomodel classes
    return initialize_neomodel_classes(neomodel_map)

# Create the default models
default_models = create_default_models()

# Extract the models for easier access
Folder = default_models.get("Folder")
File = default_models.get("File")
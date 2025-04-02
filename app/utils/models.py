from neomodel import (StructuredNode, StringProperty, IntegerProperty, RelationshipTo, DateProperty)
from neo4j import GraphDatabase
import pandas as pd

def type_mapping(neo_type):
    mapping = {
        'String': StringProperty,
        'Integer': IntegerProperty,
        # Add other Neomodel property types as needed
    }
    return mapping.get(neo_type, None)

def initialize_neomodel_classes(
        neomodel_map, rel_pair=('has_parent','HAS_PARENT')):
    neomodel_classes = {}
    # Iterate over the Neomodel map
    for label, property_dict in neomodel_map.items():
        props = {}
        for prop, neo_type in property_dict.items():
            mapped_type = type_mapping(neo_type)
            if mapped_type:
                props[prop] = mapped_type()

        # Define the 'has_parent' relationship for each class
        props[rel_pair[0]] = RelationshipTo('StructuredNode', rel_pair[1])
        # Dynamically create Neomodel class inheriting from StructuredNode
        NewClass = type(label, (StructuredNode,), props)
        # Optionally, add the class to globals() so you can use it later
        globals()[label] = NewClass
        # Collect class information in the neomodel_classes dictionary
        neomodel_classes[label] = NewClass

    return neomodel_classes


def print_neomodel_map(neomodel_map):
    for label, property_types in neomodel_map.items():
        print(label)
        for prop, neo_type in property_types.items():
            print(neo_type, prop)
        print()

def generate_neomodel_map(property_map):
    neomodel_map = {}

    for label, property_dict in property_map.items():
        property_types = {prop: 'String' for prop in property_dict.keys()}
        neomodel_map[label] = property_types

    return neomodel_map

def test_labels_for_neomodel_class_availability(samples_df):
    label_class_mapping = {}

    label_names = list(samples_df['label'].value_counts(dropna=False).index)

    # Iterate through the list of label names
    for label_name in label_names:
        # Check if the class exists in the global namespace
        if label_name in globals():
            label_class_mapping[label_name] = True
        else:
            label_class_mapping[label_name] = False

    # Print the mapping
    for label_name, exists in label_class_mapping.items():
        if not exists:
            print(f"No class found for label '{label_name}'.")

    return label_class_mapping

def merge_nodes_with_existing(
        db_connection,
        entities_df,
        label_column,
        property_columns,
        target_label,
        match_columns,
        relationship_type
):
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

    Returns:
        None (Executes Neo4j queries)
    """

    with db_connection.session() as session:
        for _, row in entities_df.iterrows():
            node_label = row[label_column]
            node_properties = {col: row[col] for col in property_columns if pd.notna(row[col])}
            m_match_conditions = ", ".join([f"{col}: ${col}" for col in node_properties.keys()])
            n_match_conditions = ", ".join([f"{col}: ${col}" for col in match_columns])
            match_params = {col: row[col] for col in match_columns}

            # Separate `SET` statements for `n` (target node) and `m` (new entity)
            n_set_statements = ", ".join([f"n.{key} = ${key}" for key in match_columns]) if match_columns else ""
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

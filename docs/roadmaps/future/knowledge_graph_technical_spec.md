# Knowledge Graph Documentation System - Technical Specification

## Documentation Markup Standards

### Structured Comment Markup
The knowledge graph system uses HTML-style comments for structured markup in markdown files and docstrings:

```markdown
<!-- concept: data_integration, api_integration -->
<!-- pattern: connector_implementation, oauth2_pattern -->
```

These structured comments can be placed in:
- Markdown files (.md)
- Python docstrings (using triple quotes)
- README files
- Other documentation files

### Concept Tags
Concept tags identify scientific or technical concepts related to a component or documentation section:

```markdown
<!-- concept: data_integration, api_integration, authentication -->
```

Concepts should follow these conventions:
- Use snake_case for concept names
- Use hierarchical naming for subconcepts (e.g., `data_integration.file_integration`)
- Separate multiple concepts with commas
- Order from most general to most specific

### Pattern Tags
Pattern tags identify implementation patterns used in a component or described in documentation:

```markdown
<!-- pattern: connector_implementation, oauth2_pattern -->
```

Patterns should follow these conventions:
- Use snake_case for pattern names
- Use descriptive names that indicate the pattern's purpose
- Separate multiple patterns with commas
- Order from most general to most specific

### Cross-Reference Markup
Cross-references between components use the following syntax:

```markdown
- {class}`science_data_kit.core.data.DataPipeline` - Uses this manager for data storage
- {method}`science_data_kit.core.query.QueryBuilder.build_query` - Builds queries executed by this manager
```

Cross-references can link to:
- Classes
- Methods
- Functions
- Modules
- Documentation sections

### Extension Pattern Documentation
Extension patterns are documented using structured sections:

```markdown
## Extension Patterns
### Custom Query Methods
<!-- pattern: domain_specific_extension, query_customization -->
Add domain-specific query methods by inheriting and adding methods:
```python
class GenomicsNeo4jManager(Neo4jManager):
    def find_gene_pathways(self, gene_id: str) -> List[Pathway]:
        # Custom genomics query logic
```
```

## Knowledge Graph Schema Design

### Base Node Classes

#### BaseDocumentationNode
Abstract base class for all knowledge graph nodes:

```python
class BaseDocumentationNode:
    def __init__(self, name: str, node_type: str, **kwargs):
        self.name = name
        self.node_type = node_type
        self.properties = kwargs
    
    @classmethod
    def create_domain_subtype(cls, domain: str, **domain_properties):
        """Create domain-specific node subtypes at runtime"""
        return cls(node_type=f"{cls.__name__}_{domain}", **domain_properties)
```

#### ComponentNode
Represents software components (classes, functions, modules):

```python
class ComponentNode(BaseDocumentationNode):
    def __init__(self, name: str, component_type: str, file_path: str, 
                 line_range: tuple = None, **kwargs):
        super().__init__(name, "ComponentNode", **kwargs)
        self.component_type = component_type  # class, function, module, etc.
        self.file_path = file_path
        self.line_range = line_range
```

#### ConceptNode
Represents scientific/technical concepts:

```python
class ConceptNode(BaseDocumentationNode):
    def __init__(self, name: str, parent: str = None, domain: str = None, **kwargs):
        super().__init__(name, "ConceptNode", **kwargs)
        self.parent = parent
        self.domain = domain
```

#### PatternNode
Represents implementation patterns:

```python
class PatternNode(BaseDocumentationNode):
    def __init__(self, name: str, pattern_category: str = None, **kwargs):
        super().__init__(name, "PatternNode", **kwargs)
        self.pattern_category = pattern_category
```

#### DocumentNode
Represents documentation files and sections:

```python
class DocumentNode(BaseDocumentationNode):
    def __init__(self, name: str, file_path: str, section_id: str = None, 
                 content: str = None, **kwargs):
        super().__init__(name, "DocumentNode", **kwargs)
        self.file_path = file_path
        self.section_id = section_id
        self.content = content
```

### Relationship Types

The knowledge graph uses the following relationship types:

1. `CONTAINS`: Hierarchical relationship (module contains class, class contains method)
2. `IMPLEMENTS`: Component implements a pattern
3. `ADDRESSES`: Component addresses a concept
4. `RELATED_TO`: General relationship between nodes
5. `EXTENDS`: Inheritance relationship between components
6. `USES`: Usage relationship between components
7. `DOCUMENTED_IN`: Component is documented in a document
8. `CHILD_OF`: Hierarchical relationship in concept taxonomy
9. `INSTANCE_OF`: Type relationship (node is instance of node type)
10. `SIMILAR_TO`: Similarity relationship between concepts or patterns

### Neo4j Schema

The Neo4j schema uses labels to represent node types and properties to store node attributes:

```cypher
// Base node structure
CREATE CONSTRAINT ON (n:BaseDocumentationNode) ASSERT n.name IS UNIQUE;

// Component nodes
CREATE CONSTRAINT ON (n:ComponentNode) ASSERT (n.name, n.component_type) IS UNIQUE;
CREATE INDEX ON :ComponentNode(component_type);
CREATE INDEX ON :ComponentNode(file_path);

// Concept nodes
CREATE CONSTRAINT ON (n:ConceptNode) ASSERT n.name IS UNIQUE;
CREATE INDEX ON :ConceptNode(domain);
CREATE INDEX ON :ConceptNode(parent);

// Pattern nodes
CREATE CONSTRAINT ON (n:PatternNode) ASSERT n.name IS UNIQUE;
CREATE INDEX ON :PatternNode(pattern_category);

// Document nodes
CREATE CONSTRAINT ON (n:DocumentNode) ASSERT (n.file_path, n.section_id) IS UNIQUE;
CREATE INDEX ON :DocumentNode(file_path);
```

## Parser Architecture

### Parser Components

#### DocumentationParser
Main parser class that orchestrates the parsing process:

```python
class DocumentationParser:
    def __init__(self):
        self.parsers = {}
        self.register_default_parsers()
    
    def register_parser(self, file_extension, parser):
        self.parsers[file_extension] = parser
    
    def register_default_parsers(self):
        self.register_parser('.py', PythonFileParser())
        self.register_parser('.md', MarkdownFileParser())
        self.register_parser('.rst', ReStructuredTextParser())
    
    def parse_file(self, file_path):
        ext = os.path.splitext(file_path)[1]
        if ext in self.parsers:
            return self.parsers[ext].parse(file_path)
        return None
    
    def parse_directory(self, directory_path, recursive=True):
        results = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                result = self.parse_file(file_path)
                if result:
                    results.append(result)
            if not recursive:
                break
        return results
```

#### FileParser
Base class for file-specific parsers:

```python
class FileParser:
    def parse(self, file_path):
        """Parse a file and return extracted nodes and relationships"""
        raise NotImplementedError()
    
    def extract_concepts(self, content):
        """Extract concept tags from content"""
        import re
        concept_matches = re.findall(r'<!-- concept: ([^>]+) -->', content)
        concepts = []
        for match in concept_matches:
            concepts.extend([tag.strip() for tag in match.split(',')])
        return concepts
    
    def extract_patterns(self, content):
        """Extract pattern tags from content"""
        import re
        pattern_matches = re.findall(r'<!-- pattern: ([^>]+) -->', content)
        patterns = []
        for match in pattern_matches:
            patterns.extend([tag.strip() for tag in match.split(',')])
        return patterns
    
    def extract_cross_references(self, content):
        """Extract cross-references from content"""
        import re
        ref_matches = re.findall(r'\{([^}]+)\}`([^`]+)`', content)
        references = []
        for ref_type, ref_target in ref_matches:
            references.append((ref_type, ref_target))
        return references
```

#### PythonFileParser
Parser for Python files:

```python
class PythonFileParser(FileParser):
    def parse(self, file_path):
        import ast
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        nodes = []
        relationships = []
        
        # Parse module
        module_node = ComponentNode(
            name=os.path.basename(file_path),
            component_type='module',
            file_path=file_path
        )
        nodes.append(module_node)
        
        # Parse classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_node = self.parse_class(node, file_path)
                nodes.append(class_node)
                relationships.append(('CONTAINS', module_node, class_node))
            elif isinstance(node, ast.FunctionDef) and node.parent_field == tree:
                func_node = self.parse_function(node, file_path)
                nodes.append(func_node)
                relationships.append(('CONTAINS', module_node, func_node))
        
        return {'nodes': nodes, 'relationships': relationships}
    
    def parse_class(self, class_def, file_path):
        # Implementation details
        pass
    
    def parse_function(self, func_def, file_path):
        # Implementation details
        pass
```

#### MarkdownFileParser
Parser for Markdown files:

```python
class MarkdownFileParser(FileParser):
    def parse(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        nodes = []
        relationships = []
        
        # Create document node
        doc_node = DocumentNode(
            name=os.path.basename(file_path),
            file_path=file_path,
            content=content
        )
        nodes.append(doc_node)
        
        # Extract concepts
        concepts = self.extract_concepts(content)
        for concept in concepts:
            concept_node = ConceptNode(name=concept)
            nodes.append(concept_node)
            relationships.append(('ADDRESSES', doc_node, concept_node))
        
        # Extract patterns
        patterns = self.extract_patterns(content)
        for pattern in patterns:
            pattern_node = PatternNode(name=pattern)
            nodes.append(pattern_node)
            relationships.append(('IMPLEMENTS', doc_node, pattern_node))
        
        # Extract sections
        sections = self.extract_sections(content)
        for section in sections:
            section_node = DocumentNode(
                name=section['title'],
                file_path=file_path,
                section_id=section['id'],
                content=section['content']
            )
            nodes.append(section_node)
            relationships.append(('CONTAINS', doc_node, section_node))
        
        return {'nodes': nodes, 'relationships': relationships}
    
    def extract_sections(self, content):
        # Implementation details
        pass
```

### Graph Builder

#### KnowledgeGraphBuilder
Builds the knowledge graph from parsed documentation:

```python
class KnowledgeGraphBuilder:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.graph = Neo4jGraph(neo4j_uri, neo4j_user, neo4j_password)
        self.parser = DocumentationParser()
    
    def build_graph(self, directory_path, recursive=True):
        """Build the knowledge graph from a directory of files"""
        parse_results = self.parser.parse_directory(directory_path, recursive)
        self.create_nodes(parse_results)
        self.create_relationships(parse_results)
        self.infer_additional_relationships()
    
    def create_nodes(self, parse_results):
        """Create nodes in the graph database"""
        for result in parse_results:
            for node in result['nodes']:
                self.graph.create_node(node)
    
    def create_relationships(self, parse_results):
        """Create relationships in the graph database"""
        for result in parse_results:
            for rel_type, source, target in result['relationships']:
                self.graph.create_relationship(source, target, rel_type)
    
    def infer_additional_relationships(self):
        """Infer additional relationships based on existing data"""
        # Infer concept hierarchy relationships
        self.graph.execute_query("""
        MATCH (c1:ConceptNode), (c2:ConceptNode)
        WHERE c1.name CONTAINS '.' AND c2.name = split(c1.name, '.')[0]
        MERGE (c1)-[:CHILD_OF]->(c2)
        """)
        
        # Infer related concepts from co-occurrence
        self.graph.execute_query("""
        MATCH (n)-[:ADDRESSES]->(c1:ConceptNode)
        MATCH (n)-[:ADDRESSES]->(c2:ConceptNode)
        WHERE c1 <> c2
        MERGE (c1)-[:RELATED_TO]->(c2)
        """)
```

## AI Query Interface Specifications

### Query Interface

#### KnowledgeGraphQuery
Interface for querying the knowledge graph:

```python
class KnowledgeGraphQuery:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.graph = Neo4jGraph(neo4j_uri, neo4j_user, neo4j_password)
    
    def find_component(self, name, component_type=None):
        """Find a component by name and type"""
        query = "MATCH (c:ComponentNode {name: $name})"
        if component_type:
            query += " WHERE c.component_type = $component_type"
        query += " RETURN c"
        return self.graph.execute_query(query, {"name": name, "component_type": component_type})
    
    def find_concept(self, name):
        """Find a concept by name"""
        query = "MATCH (c:ConceptNode {name: $name}) RETURN c"
        return self.graph.execute_query(query, {"name": name})
    
    def find_pattern(self, name):
        """Find a pattern by name"""
        query = "MATCH (p:PatternNode {name: $name}) RETURN p"
        return self.graph.execute_query(query, {"name": name})
    
    def find_components_by_concept(self, concept_name):
        """Find components that address a concept"""
        query = """
        MATCH (c:ComponentNode)-[:ADDRESSES]->(concept:ConceptNode {name: $concept_name})
        RETURN c
        """
        return self.graph.execute_query(query, {"concept_name": concept_name})
    
    def find_components_by_pattern(self, pattern_name):
        """Find components that implement a pattern"""
        query = """
        MATCH (c:ComponentNode)-[:IMPLEMENTS]->(pattern:PatternNode {name: $pattern_name})
        RETURN c
        """
        return self.graph.execute_query(query, {"pattern_name": pattern_name})
    
    def find_related_components(self, component_name):
        """Find components related to a given component"""
        query = """
        MATCH (c:ComponentNode {name: $component_name})-[r]->(related)
        RETURN type(r) as relationship_type, related
        """
        return self.graph.execute_query(query, {"component_name": component_name})
    
    def find_extension_point(self, query_string):
        """Find extension points based on a query string"""
        # Parse query string for concepts and patterns
        concepts = []
        patterns = []
        for term in query_string.split('+'):
            term = term.strip()
            if term.startswith('concept:'):
                concepts.append(term[8:].strip())
            elif term.startswith('pattern:'):
                patterns.append(term[8:].strip())
            else:
                # Try to match as concept or pattern
                concept_result = self.find_concept(term)
                if concept_result:
                    concepts.append(term)
                else:
                    pattern_result = self.find_pattern(term)
                    if pattern_result:
                        patterns.append(term)
        
        # Build query based on concepts and patterns
        query_parts = []
        if concepts:
            concept_query = """
            MATCH (c:ComponentNode)-[:ADDRESSES]->(concept:ConceptNode)
            WHERE concept.name IN $concepts
            """
            query_parts.append(concept_query)
        
        if patterns:
            pattern_query = """
            MATCH (c:ComponentNode)-[:IMPLEMENTS]->(pattern:PatternNode)
            WHERE pattern.name IN $patterns
            """
            query_parts.append(pattern_query)
        
        if not query_parts:
            return []
        
        query = " WITH c ".join(query_parts) + " RETURN c"
        return self.graph.execute_query(query, {"concepts": concepts, "patterns": patterns})
```

### Natural Language Query Parser

#### NLQueryParser
Parses natural language queries into structured queries:

```python
class NLQueryParser:
    def __init__(self):
        self.concept_patterns = [
            r'related to (\w+)',
            r'about (\w+)',
            r'(\w+) concept',
            r'concept of (\w+)'
        ]
        self.pattern_patterns = [
            r'using (\w+) pattern',
            r'implements (\w+)',
            r'following (\w+) pattern',
            r'(\w+) implementation'
        ]
        self.component_patterns = [
            r'class (\w+)',
            r'function (\w+)',
            r'module (\w+)',
            r'component (\w+)'
        ]
    
    def parse(self, query_string):
        """Parse a natural language query into a structured query"""
        concepts = self.extract_concepts(query_string)
        patterns = self.extract_patterns(query_string)
        components = self.extract_components(query_string)
        
        structured_query = {
            'concepts': concepts,
            'patterns': patterns,
            'components': components,
            'original_query': query_string
        }
        
        return structured_query
    
    def extract_concepts(self, query_string):
        """Extract concepts from a query string"""
        concepts = []
        for pattern in self.concept_patterns:
            import re
            matches = re.findall(pattern, query_string)
            concepts.extend(matches)
        return concepts
    
    def extract_patterns(self, query_string):
        """Extract patterns from a query string"""
        patterns = []
        for pattern in self.pattern_patterns:
            import re
            matches = re.findall(pattern, query_string)
            patterns.extend(matches)
        return patterns
    
    def extract_components(self, query_string):
        """Extract components from a query string"""
        components = []
        for pattern in self.component_patterns:
            import re
            matches = re.findall(pattern, query_string)
            components.extend(matches)
        return components
```

## Integration Requirements

### Sphinx Integration

The knowledge graph system integrates with Sphinx documentation through a custom extension:

```python
def setup(app):
    app.add_config_value('knowledge_graph_enabled', True, 'html')
    app.add_directive('concept', ConceptDirective)
    app.add_directive('pattern', PatternDirective)
    app.add_role('concept', concept_role)
    app.add_role('pattern', pattern_role)
    app.connect('builder-inited', initialize_knowledge_graph)
    app.connect('build-finished', build_knowledge_graph)
    
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

The extension provides:
- Directives for defining concepts and patterns
- Roles for referencing concepts and patterns
- Automatic knowledge graph building during documentation build
- Visualization of concept and pattern relationships

### CI/CD Integration

The knowledge graph system integrates with CI/CD through GitHub Actions:

```yaml
name: Knowledge Graph Build

on:
  push:
    branches: [ main ]
    paths:
      - '**.py'
      - '**.md'
      - '**.rst'
  pull_request:
    branches: [ main ]
    paths:
      - '**.py'
      - '**.md'
      - '**.rst'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Build knowledge graph
      run: |
        python -m science_data_kit.knowledge_graph.build
    - name: Validate documentation
      run: |
        python -m science_data_kit.knowledge_graph.validate
    - name: Generate documentation report
      run: |
        python -m science_data_kit.knowledge_graph.report
    - name: Upload documentation report
      uses: actions/upload-artifact@v2
      with:
        name: documentation-report
        path: documentation-report.html
```

### IDE Integration

The knowledge graph system integrates with VS Code through a custom extension:

```json
{
  "name": "scidk-knowledge-graph",
  "displayName": "SciDK Knowledge Graph",
  "description": "Knowledge graph integration for Science Data Kit",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.60.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [
    "onLanguage:python",
    "onLanguage:markdown"
  ],
  "main": "./extension.js",
  "contributes": {
    "commands": [
      {
        "command": "scidk-knowledge-graph.showGraph",
        "title": "SciDK: Show Knowledge Graph"
      },
      {
        "command": "scidk-knowledge-graph.addConcept",
        "title": "SciDK: Add Concept Tag"
      },
      {
        "command": "scidk-knowledge-graph.addPattern",
        "title": "SciDK: Add Pattern Tag"
      }
    ]
  }
}
```

The extension provides:
- Commands for adding concept and pattern tags
- Visualization of the knowledge graph
- Code completion for concepts and patterns
- Hover information for concepts and patterns
- Navigation to related components
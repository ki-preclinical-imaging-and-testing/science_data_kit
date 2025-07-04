# Science Data Kit Architecture Diagrams

This directory contains architecture diagrams for the Science Data Kit project. These diagrams provide a visual representation of the system's components, their relationships, and interactions.

## Diagram Types

The diagrams are created using [PlantUML](https://plantuml.com/), a text-based diagramming tool that allows for version control of diagrams and easy modification.

## Available Diagrams

### Caching System Architecture

- **File**: [caching_architecture.puml](caching_architecture.puml)
- **Description**: This diagram illustrates the architecture of the caching system implemented in `science_data_kit/core/utils/common_utils.py`. It shows the relationships between the `Cache` base class, the `LRUCache` implementation, the `memoize` decorator, and the `create_key_from_args` utility function.

## Viewing the Diagrams

To view the PlantUML diagrams, you can:

1. Use the [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. Install a PlantUML plugin for your IDE (available for VS Code, PyCharm, etc.)
3. Use the PlantUML command-line tool to generate images:

```bash
plantuml caching_architecture.puml
```

## Creating New Diagrams

When creating new architecture diagrams:

1. Use PlantUML format (.puml extension)
2. Follow the naming convention: `<component>_architecture.puml`
3. Include a brief description of the diagram in this README
4. Keep diagrams focused on a specific component or subsystem
5. Include notes to explain complex parts of the architecture

## Best Practices

- Keep diagrams simple and focused on one aspect of the system
- Use consistent styling across diagrams
- Update diagrams when the architecture changes
- Include meaningful notes to explain design decisions
- Use appropriate diagram types for different aspects (class diagrams for structure, sequence diagrams for interactions, etc.)
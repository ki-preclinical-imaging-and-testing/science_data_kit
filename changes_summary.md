# Changes Summary

## CLI Improvements

- Created a new CLI module (science_data_kit/cli.py) that provides a unified command-line interface
- Added 'science_data_kit' and 'sdk' commands that point to the same functionality
- CLI now automatically activates the environment if needed
- CLI automatically runs the Streamlit app with the correct path

## Environment Standardization

- Changed virtual environment name from '.venv' to 'science-data-kit-env' in install.sh
- Updated all scripts to use the standardized environment name
- Ensured consistent environment activation across all entry points

## Neo4j Container Handling

- Improved Neo4j container management in install.sh
- Added logic to handle existing but stopped Neo4j containers
- Added proper error handling and recovery for Neo4j container operations

## UI Module Updates

- Simplified page imports in app.py by using the pages package
- Updated __init__.py in the pages package to export all page render functions
- Applied the same import simplification to workshop_app.py
- Removed whitespace and improved code formatting

## Dependency Updates

- Moved matplotlib from optional to required dependencies
- Removed references to non-existent 'app' package in pyproject.toml and setup.py
- Updated entry points in pyproject.toml and setup.py to use the new CLI module

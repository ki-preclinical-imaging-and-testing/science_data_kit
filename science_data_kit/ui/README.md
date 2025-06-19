# Science Data Kit - Current Application

## Overview

This is the current version of the Science Data Kit application. It uses a modern, class-based architecture with a more modular and maintainable design compared to the legacy version.

## Key Features

- Class-based architecture with `BasePage` and specific page implementations
- Driver connectors displayed in the sidebar for better user experience
- Improved state management
- More consistent UI across pages
- Better separation of concerns between UI components and business logic

## Application Structure

- `app.py` - Main entry point for the application
- `state.py` - Session state management
- `config.py` - Application configuration
- `pages/` - Page implementations
  - `base_page.py` - Base class for all pages
  - `connect.py` - Connect page showing driver connectors in the sidebar
  - Other page implementations
- `components/` - Reusable UI components
- `adapters/` - Adapters for external services

## Running the Application

To run the current version of the application:

```bash
python run_app.py
```

## Legacy Version

The legacy version of the application is maintained for reference purposes only in the `app/` directory at the project root. It should not be used for new development.

If you need to run the legacy version for any reason, you can do so using:

```bash
python run_legacy_app.py
```

Or by using the `--legacy` flag with the main application:

```bash
python run_app.py --legacy
```

## Development Guidelines

- All new features should be implemented in this version of the application
- Follow the existing class-based architecture
- Use the `BasePage` class for new pages
- Place reusable components in the `components/` directory
- Maintain separation between UI and business logic
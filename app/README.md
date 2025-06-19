# Science Data Kit - Legacy Application

## IMPORTANT NOTICE

**This is the legacy version of the Science Data Kit application.**

This code is maintained for reference purposes only and is not actively developed. The current version of the application is located in the `science_data_kit/ui/` directory.

## Running the Legacy App

If you need to run this legacy version for any reason, you can do so using:

```bash
python run_legacy_app.py
```

Or by using the `--legacy` flag with the main application:

```bash
python run_app.py --legacy
```

## Legacy App Structure

The legacy app uses a more direct approach with functions rendered directly in the main content area:

- `app/app.py` - Main entry point for the legacy application
- `app/menu.py` - Navigation menu for the legacy app
- `app/connect.py` - Connect page showing driver connectors in the main panel
- `app/utils/` - Utility functions for the legacy app

## Transition to New App

The new application (in `science_data_kit/ui/`) uses a class-based approach with `BasePage` and specific page classes like `ConnectPage`. The new app shows driver connectors in the sidebar and has a more modular, maintainable architecture.

For new development, please use the new application structure.
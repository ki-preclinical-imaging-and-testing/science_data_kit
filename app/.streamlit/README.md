# Streamlit Configuration

This directory contains configuration files for the Streamlit application.

## config.toml

The `config.toml` file contains configuration settings for the Streamlit application. Here's what each section does:

### [server]
- `maxMessageSize`: Sets the maximum message size limit in MB. Default is 200 MB, but we've increased it to 500 MB to handle larger dataframes and charts.

### [theme]
- Contains settings for the visual appearance of the application.
- `primaryColor`: The main color used for interactive elements (currently set to a green color: #4CAF50).
- `backgroundColor`: The background color of the main content area (currently set to a dark green: #1E3B2C).
- `secondaryBackgroundColor`: The background color of sidebar and other secondary areas (currently set to a dark teal: #004D40).
- `textColor`: The color of the text (currently set to white: #FFFFFF for better readability against the dark background).

## Adjusting Configuration

If you encounter "MessageSizeError" or "exceeds the message size limit" errors:

1. Increase the `maxMessageSize` value in the `config.toml` file.
2. Restart the Streamlit application for changes to take effect.

Note that increasing the limit may lead to longer loading times and higher memory consumption.

## Additional Configuration Options

The `config.toml` file includes commented examples of other configuration options that can be uncommented and adjusted as needed.

For more information on Streamlit configuration options, see the [Streamlit documentation](https://docs.streamlit.io/library/advanced-features/configuration).

# Ollama Integration Guide

## Overview

Science Data Kit (SDK) supports integration with Ollama, allowing you to use local Large Language Models (LLMs) for chat and data analysis. This guide explains how to set up and use Ollama with SDK.

## What is Ollama?

[Ollama](https://ollama.ai/) is an open-source tool that lets you run large language models locally on your computer. It provides a simple API for running models like Llama 2, Mistral, Mixtral, and others without requiring a cloud service or API key.

## Prerequisites

Before using Ollama with SDK, you need to:

1. Install Ollama on your system by following the instructions at [ollama.ai](https://ollama.ai/)
2. Download at least one model using the Ollama CLI (e.g., `ollama pull llama2`)
3. Ensure the Ollama service is running (it typically runs on port 11434)

## Connecting to Ollama in SDK

### Basic Connection

1. Navigate to the Chat feature in SDK
2. In the LLM Connection settings, select "Ollama" as the LLM Provider
3. The default base URL is `http://localhost:11434` (change this if your Ollama instance is running elsewhere)
4. Click "Refresh Models" to fetch the list of available models from your Ollama installation
5. Select your preferred model from the dropdown list
6. Adjust Temperature and Max Tokens settings as needed
7. Click "Save Settings" to apply your configuration

### Authentication (Optional)

If your Ollama instance requires authentication:

1. Check the "Enable Authentication" box
2. Enter your username and password
3. Click "Save Settings" to apply your configuration

### Remote Ollama Instances

To connect to a remote Ollama instance:

1. Change the "Ollama Base URL" to point to your remote instance (e.g., `http://your-server-ip:11434`)
2. Enable authentication if required
3. Click "Save Settings" to apply your configuration

## Troubleshooting

### Common Issues

1. **"Failed to get Ollama models" error**:
   - Ensure the Ollama service is running
   - Check that the base URL is correct
   - Verify network connectivity to the Ollama server

2. **Authentication failures**:
   - Double-check your username and password
   - Ensure the Ollama server is configured to use authentication

3. **Model not available**:
   - Use the Ollama CLI to download the model: `ollama pull model-name`
   - Click "Refresh Models" to update the list of available models

### Logs and Debugging

If you encounter issues with the Ollama integration:

1. Check the Ollama server logs for errors
2. Verify that the model you're trying to use is properly installed
3. Try restarting the Ollama service

## Advanced Configuration

### Model Parameters

You can adjust the following parameters for Ollama models:

- **Temperature**: Controls the randomness of the model's output (0.0 to 1.0)
- **Max Tokens**: Limits the length of the generated response

### Performance Considerations

- Larger models require more system resources (RAM and GPU)
- Consider using smaller models on systems with limited resources
- For optimal performance, a system with a GPU is recommended

## Further Resources

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/README.md)
- [Available Ollama Models](https://ollama.ai/library)
- [Ollama GitHub Repository](https://github.com/ollama/ollama)
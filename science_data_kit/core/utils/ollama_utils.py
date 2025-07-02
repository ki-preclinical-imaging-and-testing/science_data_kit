import os
import docker
import requests
from typing import Tuple, List, Dict, Any, Optional

def get_ollama_container_status(container_name: str = "dsk-ollama-instance") -> Tuple[bool, str]:
    """
    Check if the Ollama container exists and get its status.

    Args:
        container_name: Name of the Ollama container.

    Returns:
        A tuple containing (container_exists, container_status).
    """
    try:
        print(f"Checking status of Ollama container: {container_name}")
        client = docker.from_env()
        containers = client.containers.list(all=True, filters={"name": container_name})

        if containers:
            status = containers[0].status
            print(f"Ollama container '{container_name}' exists with status: {status}")

            # Get more detailed information about the container
            container = containers[0]
            container_info = container.attrs

            # Check if the container has any logs that might indicate issues
            logs = container.logs(tail=20).decode('utf-8', errors='replace')
            print(f"Recent logs from Ollama container:\n{logs}")

            # Check container health if available
            health_status = "Not available"
            if 'Health' in container_info['State']:
                health_status = container_info['State']['Health']['Status']
                print(f"Container health status: {health_status}")

            return True, status

        print(f"Ollama container '{container_name}' not found")
        return False, "not found"
    except Exception as e:
        error_message = f"Error checking Ollama container status: {str(e)}"
        print(error_message)
        return False, "error"

def is_ollama_accessible(url: str = "http://localhost:11434") -> bool:
    """
    Check if the Ollama API is accessible.

    Args:
        url: The base URL for the Ollama API.

    Returns:
        True if the API is accessible, False otherwise.
    """
    try:
        # Handle empty or None URL
        if not url:
            print("URL is empty, using default http://localhost:11434")
            url = "http://localhost:11434"

        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            print(f"URL '{url}' is missing scheme, adding http://")
            url = f"http://{url}"

        # Check if URL is just a scheme without host
        if url in ["http://", "https://"]:
            print("URL contains only scheme, using default http://localhost:11434")
            url = "http://localhost:11434"

        # Check if URL is a path without host (like /api/tags)
        if url.startswith(('http://', 'https://')) and url.count('/') == 2 and not url.replace('http://', '').replace('https://', ''):
            print("URL contains only scheme without host, using default http://localhost:11434")
            url = "http://localhost:11434"

        # Ensure URL doesn't end with a slash before adding /api/tags
        if url.endswith('/'):
            url = url[:-1]

        api_url = f"{url}/api/tags"
        print(f"Checking if Ollama API is accessible at {api_url}")
        response = requests.get(api_url, timeout=5)  # Increased timeout
        success = response.status_code == 200
        print(f"Ollama API accessibility check: {'Success' if success else 'Failed'} with status code {response.status_code}")
        return success
    except Exception as e:
        print(f"Error checking Ollama API accessibility: {str(e)}")
        return False

def get_ollama_models(url: str = "http://localhost:11434") -> List[str]:
    """
    Get a list of available models from Ollama API.

    Args:
        url: The base URL for the Ollama API.

    Returns:
        A list of model names.
    """
    try:
        # Handle empty or None URL
        if not url:
            print("URL is empty, using default http://localhost:11434")
            url = "http://localhost:11434"

        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            print(f"URL '{url}' is missing scheme, adding http://")
            url = f"http://{url}"

        # Check if URL is just a scheme without host
        if url in ["http://", "https://"]:
            print("URL contains only scheme, using default http://localhost:11434")
            url = "http://localhost:11434"

        # Check if URL is a path without host (like /api/tags)
        if url.startswith(('http://', 'https://')) and url.count('/') == 2 and not url.replace('http://', '').replace('https://', ''):
            print("URL contains only scheme without host, using default http://localhost:11434")
            url = "http://localhost:11434"

        # Ensure URL doesn't end with a slash before adding /api/tags
        if url.endswith('/'):
            url = url[:-1]

        api_url = f"{url}/api/tags"
        print(f"Getting Ollama models from {api_url}")

        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            model_names = [model.get("name") for model in models_data]
            print(f"Found {len(model_names)} models: {', '.join(model_names)}")
            return model_names

        print(f"Failed to get models, status code: {response.status_code}. Using default models.")
        return ["llama2", "mistral", "mixtral", "phi"]  # Default models if API call fails
    except Exception as e:
        print(f"Error getting Ollama models: {str(e)}. Using default models.")
        return ["llama2", "mistral", "mixtral", "phi"]  # Default models if API call fails

def start_ollama_container(
    container_name: str = "dsk-ollama-instance",
    port: int = 11434,
    version: str = "latest"
) -> Tuple[bool, str]:
    """
    Start the Ollama container.

    Args:
        container_name: Name to give the container.
        port: Port to expose the Ollama API on.
        version: Ollama version to use.

    Returns:
        A tuple containing (success, message).
    """
    try:
        # First, check if Ollama API is already accessible
        api_url = f"http://localhost:{port}"
        if is_ollama_accessible(api_url):
            print(f"Ollama API is already accessible at {api_url}")
            print("No need to start a new container")
            return True, f"Ollama API is already accessible at {api_url}"

        print(f"Starting Ollama container '{container_name}' on port {port} with version '{version}'")
        client = docker.from_env()

        # Check if container already exists
        print(f"Checking if container '{container_name}' already exists")
        existing_containers = client.containers.list(all=True, filters={"name": container_name})
        if existing_containers:
            container = existing_containers[0]
            print(f"Container '{container_name}' exists with status: {container.status}")

            if container.status == "running":
                print(f"Container '{container_name}' is already running")
                return True, f"Ollama container '{container_name}' is already running"

            # Container exists but is not running, try to start it
            print(f"Starting existing container '{container_name}'")
            try:
                container.start()
                print(f"Successfully started existing container '{container_name}'")
                return True, f"Ollama container '{container_name}' started successfully"
            except Exception as e:
                error_message = f"Failed to start existing container '{container_name}': {str(e)}"
                print(error_message)

                # If starting fails, try to remove the container and create a new one
                print(f"Removing failed container '{container_name}' and creating a new one")
                try:
                    container.remove(force=True)
                    print(f"Removed container '{container_name}'")
                except Exception as remove_error:
                    print(f"Error removing container: {str(remove_error)}")
                    # Continue anyway, as the container might not exist anymore

        # Try different image names based on what might be available
        image_names = [
            "ollama/ollama",  # Official image without version
            f"ollama/ollama:{version}",  # Official image with version
            "ollama",  # Simple name
            f"ollama:{version}"  # Simple name with version
        ]

        # Check if any of the images exist locally
        print("Checking for local Ollama images")
        available_images = []
        for image_name in image_names:
            try:
                client.images.get(image_name)
                available_images.append(image_name)
                print(f"Found local image: {image_name}")
            except Exception:
                print(f"Image not found locally: {image_name}")

        # If we have local images, try those first
        if available_images:
            print(f"Using available local images: {available_images}")
            image_names = available_images + [img for img in image_names if img not in available_images]

        error_messages = []
        for image_name in image_names:
            try:
                print(f"Attempting to start Ollama container with image: {image_name}")
                # Create and start container
                container = client.containers.run(
                    image_name,
                    name=container_name,
                    detach=True,
                    ports={f'11434/tcp': port},
                    volumes={
                        f"{container_name}-data": {"bind": "/root/.ollama", "mode": "rw"}
                    }
                )

                print(f"Successfully started Ollama container with image: {image_name}")

                # Check container logs for any startup issues
                logs = container.logs(tail=20).decode('utf-8', errors='replace')
                print(f"Container startup logs:\n{logs}")

                # Check if there are any error messages in the logs
                if "error" in logs.lower() or "failed" in logs.lower():
                    print("Warning: Potential issues found in container logs")

                return True, f"Ollama container '{container_name}' started successfully with image {image_name}"
            except Exception as e:
                error_message = f"Failed to start with image {image_name}: {str(e)}"
                print(error_message)
                error_messages.append(error_message)

        # If we get here, all attempts failed
        detailed_errors = "\n".join(error_messages)
        print(f"All attempts to start Ollama container failed")
        return False, f"Error starting Ollama container. Tried multiple images but all failed:\n{detailed_errors}"
    except Exception as e:
        error_message = f"Error starting Ollama container: {str(e)}"
        print(error_message)
        return False, error_message

def stop_ollama_container(container_name: str = "dsk-ollama-instance") -> Tuple[bool, str]:
    """
    Stop the Ollama container.

    Args:
        container_name: Name of the Ollama container.

    Returns:
        A tuple containing (success, message).
    """
    try:
        client = docker.from_env()
        containers = client.containers.list(filters={"name": container_name})

        if containers:
            container = containers[0]
            container.stop()
            return True, f"Ollama container '{container_name}' stopped successfully"

        return False, f"Ollama container '{container_name}' not found"
    except Exception as e:
        return False, f"Error stopping Ollama container: {e}"

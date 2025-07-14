#!/bin/bash
set -e

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for flags
CLEAN_INSTALL=false
INSTALL_EXTENSIONS=false
EXTENSIONS_TO_INSTALL="all"
SHOW_HELP=false

for arg in "$@"; do
    if [ "$arg" == "--clean" ]; then
        CLEAN_INSTALL=true
    elif [ "$arg" == "-e" ] || [ "$arg" == "--extensions" ]; then
        INSTALL_EXTENSIONS=true
    elif [[ "$arg" == --extensions=* ]]; then
        INSTALL_EXTENSIONS=true
        EXTENSIONS_TO_INSTALL="${arg#*=}"
    elif [ "$arg" == "-h" ] || [ "$arg" == "--help" ]; then
        SHOW_HELP=true
    fi
done

# Show help and exit if requested
if [ "$SHOW_HELP" = true ]; then
    show_help
    exit 0
fi

# Print a colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Display help information
show_help() {
    echo "Science Data Kit Installation Script"
    echo ""
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean             Perform a clean installation (removes existing virtual environment)"
    echo "  -e, --extensions    Install all extensions (dropbox, msgraph, google, etc.)"
    echo "  --extensions=LIST   Install specific extensions (comma-separated list)"
    echo "                      Available extensions: dropbox, msgraph, google, jupyter, viz, dev, all"
    echo "  -h, --help          Display this help message"
    echo ""
    echo "Examples:"
    echo "  ./install.sh                     # Install core package only"
    echo "  ./install.sh --clean             # Clean installation of core package"
    echo "  ./install.sh -e                  # Install core package with all extensions"
    echo "  ./install.sh --extensions=dropbox,msgraph  # Install with specific extensions"
    echo ""
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Fix apt_pkg module error - only if needed for specific operations
fix_apt_pkg() {
    # Check if we've already set the workaround flag
    if [ "${APT_PKG_UNAVAILABLE:-0}" = "1" ]; then
        return 0
    fi

    # Check if apt_pkg is already available
    if python3 -c "import apt_pkg" &>/dev/null; then
        return 0
    fi

    # Only try to fix apt_pkg if we're not in direct installation mode
    if [ "${DIRECT_INSTALL:-0}" = "1" ]; then
        export APT_PKG_UNAVAILABLE=1
        return 0
    fi

    print_message $YELLOW "apt_pkg module not found. This is only needed for some apt operations."
    print_message $YELLOW "Setting up workarounds for apt commands..."
    export APT_PKG_UNAVAILABLE=1

    # We'll try a direct installation approach instead of fixing apt_pkg
    export DIRECT_INSTALL=1
}


# Check system dependencies
check_dependencies() {
    print_message $BLUE "Checking system dependencies..."

    # Python check and installation is now handled by setup_python_env
    # We'll just check for Docker and Docker Compose here

    # Check for Docker
    if ! command_exists docker; then
        print_message $YELLOW "Warning: Docker not found"
        print_message $YELLOW "Docker is required for Neo4j and other services."
        print_message $YELLOW "Would you like to install Docker? (y/n)"
        read -r install_docker
        if [[ "$install_docker" =~ ^[Yy]$ ]]; then
            install_docker
        else
            print_message $YELLOW "Skipping Docker installation. You will need to install it manually."
        fi
    else
        print_message $GREEN "Found Docker"
        # Check if Docker daemon is running
        if ! docker info >/dev/null 2>&1; then
            print_message $YELLOW "Warning: Docker daemon is not running"
            print_message $YELLOW "Please start the Docker daemon before using Science Data Kit."
        fi
    fi

    # Check for Docker Compose
    if ! command_exists docker-compose; then
        print_message $YELLOW "Warning: Docker Compose not found"
        print_message $YELLOW "Docker Compose is recommended for managing multiple containers."
        print_message $YELLOW "Would you like to install Docker Compose? (y/n)"
        read -r install_compose
        if [[ "$install_compose" =~ ^[Yy]$ ]]; then
            install_docker_compose
        else
            print_message $YELLOW "Skipping Docker Compose installation. You will need to install it manually if needed."
        fi
    else
        print_message $GREEN "Found Docker Compose"
    fi

    # Check for GitHub CLI
    if ! command_exists gh; then
        print_message $YELLOW "Warning: GitHub CLI (gh) not found"
        print_message $YELLOW "GitHub CLI is required for GitHub Actions and other GitHub integrations."
        print_message $YELLOW "Would you like to install GitHub CLI? (y/n)"
        read -r install_gh
        if [[ "$install_gh" =~ ^[Yy]$ ]]; then
            install_github_cli
        else
            print_message $YELLOW "Skipping GitHub CLI installation. You will need to install it manually if needed."
        fi
    else
        print_message $GREEN "Found GitHub CLI"
    fi
}

# Install Docker (platform-specific)
install_docker() {
    print_message $BLUE "Installing Docker..."

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu
            print_message $BLUE "Detected Debian/Ubuntu system"

            # Fix apt_pkg module error
            fix_apt_pkg

            sudo apt-get update || true
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

            # Get Ubuntu codename, with fallback if lsb_release fails
            UBUNTU_CODENAME=$(lsb_release -cs 2>/dev/null || grep -oP 'VERSION_CODENAME=\K\w+' /etc/os-release 2>/dev/null || echo "jammy")
            print_message $YELLOW "Detected Ubuntu codename for Docker: $UBUNTU_CODENAME"

            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            # Fix apt_pkg module error again before next apt-get
            fix_apt_pkg

            sudo apt-get update || true
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        elif command_exists yum; then
            # RHEL/CentOS/Fedora
            print_message $BLUE "Detected RHEL/CentOS/Fedora system"
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
        else
            print_message $RED "Unsupported Linux distribution"
            print_message $YELLOW "Please install Docker manually: https://docs.docker.com/engine/install/"
            return 1
        fi

        # Start and enable Docker service
        sudo systemctl start docker
        sudo systemctl enable docker

        # Add current user to docker group
        sudo usermod -aG docker $USER
        print_message $YELLOW "You may need to log out and log back in for Docker group changes to take effect."

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_message $BLUE "Detected macOS system"
        print_message $YELLOW "Please install Docker Desktop for Mac manually:"
        print_message $YELLOW "https://docs.docker.com/desktop/mac/install/"
        return 1

    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        print_message $BLUE "Detected Windows system"
        print_message $YELLOW "Please install Docker Desktop for Windows manually:"
        print_message $YELLOW "https://docs.docker.com/desktop/windows/install/"
        return 1

    else
        print_message $RED "Unsupported operating system: $OSTYPE"
        print_message $YELLOW "Please install Docker manually: https://docs.docker.com/engine/install/"
        return 1
    fi

    print_message $GREEN "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    print_message $BLUE "Installing Docker Compose..."

    # Get the latest version
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_message $YELLOW "Docker Compose is included with Docker Desktop for Mac."
        print_message $YELLOW "Please install Docker Desktop for Mac if you haven't already."
        return 0

    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        print_message $YELLOW "Docker Compose is included with Docker Desktop for Windows."
        print_message $YELLOW "Please install Docker Desktop for Windows if you haven't already."
        return 0

    else
        print_message $RED "Unsupported operating system: $OSTYPE"
        print_message $YELLOW "Please install Docker Compose manually: https://docs.docker.com/compose/install/"
        return 1
    fi

    print_message $GREEN "Docker Compose installed successfully"
}

# Install GitHub CLI
install_github_cli() {
    print_message $BLUE "Installing GitHub CLI..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu
            print_message $BLUE "Detected Debian/Ubuntu system"

            # Fix apt_pkg module error
            fix_apt_pkg

            # Add GitHub CLI repository
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

            # Fix apt_pkg module error again before next apt-get
            fix_apt_pkg

            sudo apt-get update || true
            sudo apt-get install -y gh

        elif command_exists yum; then
            # RHEL/CentOS/Fedora
            print_message $BLUE "Detected RHEL/CentOS/Fedora system"

            # Add GitHub CLI repository
            sudo dnf install -y 'dnf-command(config-manager)'
            sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
            sudo dnf install -y gh

        elif command_exists dnf; then
            # Newer Fedora
            print_message $BLUE "Detected Fedora system"

            # Add GitHub CLI repository
            sudo dnf install -y 'dnf-command(config-manager)'
            sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
            sudo dnf install -y gh

        elif command_exists pacman; then
            # Arch Linux
            print_message $BLUE "Detected Arch Linux system"
            sudo pacman -S --noconfirm github-cli

        else
            print_message $RED "Unsupported Linux distribution"
            print_message $YELLOW "Please install GitHub CLI manually: https://github.com/cli/cli#installation"
            return 1
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_message $BLUE "Detected macOS system"

        if command_exists brew; then
            brew install gh
        else
            print_message $RED "Homebrew not found. Please install Homebrew first:"
            print_message $YELLOW "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            print_message $YELLOW "Then install GitHub CLI with: brew install gh"
            return 1
        fi

    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        print_message $BLUE "Detected Windows system"
        print_message $YELLOW "Please install GitHub CLI for Windows manually:"
        print_message $YELLOW "https://github.com/cli/cli#windows"
        print_message $YELLOW "Or use: winget install --id GitHub.cli"
        return 1

    else
        print_message $RED "Unsupported operating system: $OSTYPE"
        print_message $YELLOW "Please install GitHub CLI manually: https://github.com/cli/cli#installation"
        return 1
    fi

    print_message $GREEN "GitHub CLI installed successfully"
}

# Check if Ollama container is running
check_ollama() {
    print_message $BLUE "Checking for Ollama container..."

    # First, check if Ollama API is accessible regardless of container
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_message $GREEN "Ollama API is accessible at http://localhost:11434"

        # Check if it's running in a Docker container
        if docker ps | grep -q "ollama"; then
            print_message $GREEN "Ollama is running in a Docker container"
        else
            print_message $YELLOW "Ollama is running, but not in a Docker container managed by this script."
            print_message $YELLOW "This could be a native Ollama installation or a container with a different name."
        fi

        return 0
    fi

    # Check if docker-compose is available
    if command_exists docker-compose && [ -f "docker-compose.yml" ]; then
        print_message $BLUE "Using Docker Compose to check Ollama status"

        # Check if Ollama container is running via docker-compose
        if docker-compose ps | grep -q "ollama.*Up"; then
            print_message $GREEN "Ollama container is running (via docker-compose)"
            # Check if Ollama API is accessible
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is accessible"
                return 0
            else
                print_message $YELLOW "Ollama container is running but the API is not accessible"
                return 1
            fi
        else
            print_message $YELLOW "Ollama container is not running (via docker-compose)"
            return 1
        fi
    else
        # Fallback to direct Docker commands
        print_message $BLUE "Using direct Docker commands to check Ollama status"

        # Check if Ollama container is running (check both old and new names)
        if docker ps | grep -q "dsk-ollama-instance"; then
            print_message $GREEN "Ollama container (dsk-ollama-instance) is running"
            # Check if Ollama API is accessible
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is accessible"
                return 0
            else
                print_message $YELLOW "Ollama container is running but the API is not accessible"
                return 1
            fi
        elif docker ps | grep -q "ollama-instance"; then
            print_message $GREEN "Ollama container (ollama-instance) is running"
            # Check if Ollama API is accessible
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is accessible"
                return 0
            else
                print_message $YELLOW "Ollama container is running but the API is not accessible"
                return 1
            fi
        else
            print_message $YELLOW "Ollama container is not running"
            return 1
        fi
    fi
}

# Install Ollama using Docker
install_ollama() {
    print_message $BLUE "Installing Ollama using Docker..."

    # First, check if Ollama API is already accessible
    print_message $BLUE "Checking if Ollama API is already accessible..."
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_message $GREEN "Ollama API is already accessible at http://localhost:11434"
        print_message $YELLOW "An Ollama service is already running. No need to start a new container."

        # Check if it's running in a Docker container
        if docker ps | grep -q "ollama"; then
            print_message $GREEN "Ollama is running in a Docker container"
        else
            print_message $YELLOW "Ollama is running, but not in a Docker container managed by this script."
            print_message $YELLOW "This could be a native Ollama installation or a container with a different name."
        fi

        # Pull a default model if needed
        print_message $BLUE "Checking for default model (llama2)..."
        if ! curl -s http://localhost:11434/api/tags | grep -q "llama2"; then
            print_message $BLUE "Downloading default model (llama2)..."
            curl -X POST http://localhost:11434/api/pull -d '{"name": "llama2"}'
            print_message $GREEN "Default model downloaded"
        else
            print_message $GREEN "Default model (llama2) is already available"
        fi

        # Still create the docker-compose.yml file if needed
        if command_exists docker-compose && [ ! -f "docker-compose.yml" ]; then
            print_message $BLUE "Creating docker-compose.yml file for future use..."
            cat > docker-compose.yml << EOL
services:
  neo4j:
    image: neo4j:latest
    container_name: neo4j-instance
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data:/data
    environment:
      - NEO4J_AUTH=neo4j/password

  ollama:
    image: ollama/ollama:latest
    container_name: dsk-ollama-instance
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

volumes:
  neo4j-data:
  ollama-data:
EOL
            print_message $GREEN "Created docker-compose.yml file"
        fi

        return 0
    fi

    # Check if Docker is installed
    if ! command_exists docker; then
        print_message $RED "Docker is required to run Ollama container"
        print_message $YELLOW "Please install Docker first"
        return 1
    fi

    # Check if docker-compose is available
    if command_exists docker-compose; then
        print_message $BLUE "Docker Compose is available, using it to install Ollama"

        # Check if docker-compose.yml exists
        if [ -f "docker-compose.yml" ]; then
            print_message $BLUE "Using existing docker-compose.yml file"
        else
            # Create docker-compose.yml file
            print_message $BLUE "Creating docker-compose.yml file..."
            cat > docker-compose.yml << EOL
services:
  neo4j:
    image: neo4j:latest
    container_name: neo4j-instance
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data:/data
    environment:
      - NEO4J_AUTH=neo4j/password

  ollama:
    image: ollama/ollama:latest
    container_name: dsk-ollama-instance
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

volumes:
  neo4j-data:
  ollama-data:
EOL
            print_message $GREEN "Created docker-compose.yml file"
        fi

        # Check if there's a conflicting container using the same port
        if docker ps | grep -q "0.0.0.0:11434"; then
            print_message $RED "Port 11434 is already in use by another container"
            print_message $YELLOW "Checking which container is using port 11434..."

            # Find the container using port 11434
            container_id=$(docker ps | grep "0.0.0.0:11434" | awk '{print $1}')
            if [ -n "$container_id" ]; then
                container_name=$(docker inspect --format='{{.Name}}' "$container_id" | sed 's/\///')
                print_message $YELLOW "Container '$container_name' ($container_id) is using port 11434"

                # Ask if the user wants to stop the conflicting container
                print_message $YELLOW "Do you want to stop the conflicting container? (y/n)"
                read -r stop_container
                if [[ "$stop_container" =~ ^[Yy]$ ]]; then
                    print_message $BLUE "Stopping container '$container_name'..."
                    docker stop "$container_id"
                    print_message $GREEN "Container stopped"
                else
                    print_message $YELLOW "Keeping the existing container. Ollama will not be started."
                    return 1
                fi
            fi
        fi

        # Check if there's a conflicting container with the same name but not running
        if docker ps -a | grep -q "dsk-ollama-instance"; then
            print_message $YELLOW "A container named 'dsk-ollama-instance' exists but is not running"
            print_message $YELLOW "Attempting to remove the conflicting container..."
            docker rm -f dsk-ollama-instance >/dev/null 2>&1
            print_message $GREEN "Conflicting container removed"
        fi

        # Start Ollama container using docker-compose
        print_message $BLUE "Starting Ollama container using docker-compose..."
        if ! docker-compose up -d ollama; then
            print_message $RED "Failed to start Ollama container with docker-compose"
            print_message $YELLOW "This could be due to port conflicts or other issues"
            print_message $YELLOW "Checking if Ollama API is accessible despite the error..."

            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is accessible at http://localhost:11434 despite docker-compose error"
                print_message $YELLOW "An Ollama service is already running. No need to start a new container."
                return 0
            else
                print_message $RED "Ollama API is not accessible. Installation failed."
                return 1
            fi
        fi

        # Wait for Ollama to start
        print_message $BLUE "Waiting for Ollama API to become available..."
        max_attempts=30
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is now accessible"
                break
            fi
            attempt=$((attempt+1))
            print_message $YELLOW "Waiting for Ollama API to start (attempt $attempt/$max_attempts)..."
            sleep 2
        done

        if [ $attempt -eq $max_attempts ]; then
            print_message $RED "Timed out waiting for Ollama API to become accessible"
            print_message $YELLOW "Checking container status..."
            docker ps | grep ollama
            print_message $YELLOW "Recent logs from Ollama container:"
            docker logs --tail 20 dsk-ollama-instance
            return 1
        fi
    else
        # Fallback to direct Docker commands
        print_message $BLUE "Docker Compose not found, using direct Docker commands"

        # Check if there's a conflicting container using the same port
        if docker ps | grep -q "0.0.0.0:11434"; then
            print_message $RED "Port 11434 is already in use by another container"
            print_message $YELLOW "Checking which container is using port 11434..."

            # Find the container using port 11434
            container_id=$(docker ps | grep "0.0.0.0:11434" | awk '{print $1}')
            if [ -n "$container_id" ]; then
                container_name=$(docker inspect --format='{{.Name}}' "$container_id" | sed 's/\///')
                print_message $YELLOW "Container '$container_name' ($container_id) is using port 11434"

                # Ask if the user wants to stop the conflicting container
                print_message $YELLOW "Do you want to stop the conflicting container? (y/n)"
                read -r stop_container
                if [[ "$stop_container" =~ ^[Yy]$ ]]; then
                    print_message $BLUE "Stopping container '$container_name'..."
                    docker stop "$container_id"
                    print_message $GREEN "Container stopped"
                else
                    print_message $YELLOW "Keeping the existing container. Ollama will not be started."
                    return 1
                fi
            fi
        fi

        # Check if there's a conflicting container with the same name but not running
        if docker ps -a | grep -q "dsk-ollama-instance"; then
            print_message $YELLOW "A container named 'dsk-ollama-instance' exists but is not running"
            print_message $YELLOW "Attempting to remove the conflicting container..."
            docker rm -f dsk-ollama-instance >/dev/null 2>&1
            print_message $GREEN "Conflicting container removed"
        fi

        # Create a Docker volume for Ollama data
        print_message $BLUE "Creating Docker volume for Ollama data..."
        docker volume create ollama-data

        # Run Ollama container
        print_message $BLUE "Starting Ollama container..."
        if ! docker run -d \
            --name dsk-ollama-instance \
            -p 11434:11434 \
            -v ollama-data:/root/.ollama \
            ollama/ollama:latest; then

            print_message $RED "Failed to start Ollama container"
            print_message $YELLOW "This could be due to port conflicts or other issues"
            print_message $YELLOW "Checking if Ollama API is accessible despite the error..."

            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is accessible at http://localhost:11434 despite container error"
                print_message $YELLOW "An Ollama service is already running. No need to start a new container."
                return 0
            else
                print_message $RED "Ollama API is not accessible. Installation failed."
                return 1
            fi
        fi

        # Wait for Ollama to start
        print_message $BLUE "Waiting for Ollama API to become available..."
        max_attempts=30
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_message $GREEN "Ollama API is now accessible"
                break
            fi
            attempt=$((attempt+1))
            print_message $YELLOW "Waiting for Ollama API to start (attempt $attempt/$max_attempts)..."
            sleep 2
        done

        if [ $attempt -eq $max_attempts ]; then
            print_message $RED "Timed out waiting for Ollama API to become accessible"
            print_message $YELLOW "Checking container status..."
            docker ps | grep ollama
            print_message $YELLOW "Recent logs from Ollama container:"
            docker logs --tail 20 dsk-ollama-instance
            return 1
        fi
    fi

    # Pull a default model
    print_message $BLUE "Downloading a default model (llama2)..."
    curl -X POST http://localhost:11434/api/pull -d '{"name": "llama2"}'
    print_message $GREEN "Default model downloaded"

    print_message $GREEN "Ollama container installed successfully"
    return 0
}

# Set up Python virtual environment
setup_python_env() {
    print_message $BLUE "Setting up Python virtual environment..."

    # Define Python version requirements
    PYTHON_MIN_VERSION="3.12"
    PYTHON_MAX_VERSION="3.13"
    VENV_DIR="science-data-kit-env"

    # Find suitable Python command
    PYTHON_CMD=""
    for cmd in python3.13 python3.12 python3 python; do
        if command_exists "$cmd"; then
            version=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
            major_minor=$(echo $version | cut -d. -f1-2)

            # Check if version is 3.12 or 3.13
            if [ "$major_minor" = "3.12" ] || [ "$major_minor" = "3.13" ]; then
                PYTHON_CMD="$cmd"
                break
            fi
        fi
    done

    # If no suitable Python found, try to install it
    if [ -z "$PYTHON_CMD" ]; then
        print_message $YELLOW "No suitable Python version found (need $PYTHON_MIN_VERSION or $PYTHON_MAX_VERSION). Attempting to install..."

        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command_exists apt-get; then
                # Debian/Ubuntu - try to install both versions, system will pick what's available
                print_message $BLUE "Detected Debian/Ubuntu system"

                # Handle apt_pkg issues gracefully
                print_message $BLUE "Updating package lists..."
                if ! sudo apt-get update 2>/dev/null; then
                    print_message $YELLOW "Warning: apt update had some issues, but continuing..."
                    # Try to fix common apt_pkg issues
                    sudo apt-get install --reinstall python3-apt 2>/dev/null || true
                fi

                # Try deadsnakes PPA for newer Python versions
                if ! apt-cache show python3.13 >/dev/null 2>&1 && ! apt-cache show python3.12 >/dev/null 2>&1; then
                    print_message $BLUE "Adding deadsnakes PPA for Python 3.12/3.13..."
                    sudo apt-get install -y software-properties-common || {
                        print_message $RED "Failed to install software-properties-common"
                        exit 1
                    }

                    # Add PPA with error handling
                    if sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null; then
                        print_message $GREEN "Successfully added deadsnakes PPA"
                        sudo apt-get update 2>/dev/null || print_message $YELLOW "Update had warnings but continuing..."
                    else
                        print_message $YELLOW "Failed to add deadsnakes PPA, trying manual method..."
                        # Manual PPA addition as fallback
                        echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list
                        sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 2>/dev/null || true
                        sudo apt-get update 2>/dev/null || print_message $YELLOW "Update had warnings but continuing..."
                    fi
                fi

                # Try to install 3.13 first, fall back to 3.12
                PYTHON_INSTALLED=false
                if apt-cache show python3.13 >/dev/null 2>&1; then
                    print_message $BLUE "Installing Python 3.13..."
                    if sudo apt-get install -y python3.13 python3.13-venv python3.13-dev 2>/dev/null; then
                        PYTHON_INSTALLED=true
                        PYTHON_CMD="python3.13"
                        # Try to install pip for 3.13
                        sudo apt-get install -y python3.13-pip 2>/dev/null || {
                            print_message $YELLOW "pip not available via apt, will install via get-pip.py later"
                        }
                    fi
                fi

                if [ "$PYTHON_INSTALLED" = false ] && apt-cache show python3.12 >/dev/null 2>&1; then
                    print_message $BLUE "Installing Python 3.12..."
                    if sudo apt-get install -y python3.12 python3.12-venv python3.12-dev 2>/dev/null; then
                        PYTHON_INSTALLED=true
                        PYTHON_CMD="python3.12"
                        # Try to install pip for 3.12
                        sudo apt-get install -y python3.12-pip 2>/dev/null || {
                            print_message $YELLOW "pip not available via apt, will install via get-pip.py later"
                        }
                    fi
                fi

                if [ "$PYTHON_INSTALLED" = false ]; then
                    print_message $RED "Failed to install Python 3.12 or 3.13 from repositories."
                    print_message $YELLOW "You may need to:"
                    print_message $YELLOW "1. Fix the apt_pkg issue: sudo apt-get install --reinstall python3-apt"
                    print_message $YELLOW "2. Or install Python manually from https://python.org/downloads/"
                    print_message $YELLOW "3. Or use pyenv: curl https://pyenv.run | bash"
                    exit 1
                fi
            elif command_exists yum; then
                # RHEL/CentOS
                print_message $BLUE "Detected RHEL/CentOS system"
                print_message $YELLOW "Note: You may need to enable EPEL repository for newer Python versions"
                if yum list available | grep -q python313; then
                    sudo yum install -y python313 python313-pip python313-devel
                    PYTHON_CMD="python3.13"
                elif yum list available | grep -q python312; then
                    sudo yum install -y python312 python312-pip python312-devel
                    PYTHON_CMD="python3.12"
                else
                    print_message $RED "Python 3.12/3.13 not available in repositories. Consider using pyenv."
                    exit 1
                fi
            elif command_exists dnf; then
                # Fedora
                print_message $BLUE "Detected Fedora system"
                if dnf list available | grep -q python3.13; then
                    sudo dnf install -y python3.13 python3.13-pip python3.13-devel
                    PYTHON_CMD="python3.13"
                elif dnf list available | grep -q python3.12; then
                    sudo dnf install -y python3.12 python3.12-pip python3.12-devel
                    PYTHON_CMD="python3.12"
                else
                    print_message $RED "Python 3.12/3.13 not available. Try: sudo dnf install python3 python3-pip"
                    exit 1
                fi
            elif command_exists pacman; then
                # Arch Linux (usually has latest Python)
                print_message $BLUE "Detected Arch Linux system"
                sudo pacman -S --noconfirm python python-pip python-virtualenv
                PYTHON_CMD="python"
            else
                print_message $RED "Unsupported Linux distribution."
                print_message $YELLOW "Please install Python 3.12 or 3.13 manually, or consider using pyenv:"
                print_message $YELLOW "curl https://pyenv.run | bash"
                exit 1
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            print_message $BLUE "Detected macOS system"
            if command_exists brew; then
                # Try to install Python 3.13, fall back to 3.12
                if brew list --formula | grep -q python@3.13; then
                    brew install python@3.13
                    PYTHON_CMD="python3.13"
                elif brew list --formula | grep -q python@3.12; then
                    brew install python@3.12
                    PYTHON_CMD="python3.12"
                else
                    print_message $BLUE "Installing latest Python (should be 3.12+)..."
                    brew install python
                    PYTHON_CMD="python3"
                fi
            else
                print_message $RED "Homebrew not found. Please install Homebrew first:"
                print_message $YELLOW "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                print_message $YELLOW "Or install Python 3.12/3.13 from https://python.org/downloads/"
                exit 1
            fi
        else
            print_message $RED "Unsupported operating system: $OSTYPE"
            print_message $YELLOW "Please install Python 3.12 or 3.13 manually from https://python.org/downloads/"
            exit 1
        fi

        # Check again after installation
        if [ -z "$PYTHON_CMD" ]; then
            for cmd in python3.13 python3.12 python3 python; do
                if command_exists "$cmd"; then
                    version=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
                    major_minor=$(echo $version | cut -d. -f1-2)

                    # Check if version is 3.12 or 3.13
                    if [ "$major_minor" = "3.12" ] || [ "$major_minor" = "3.13" ]; then
                        PYTHON_CMD="$cmd"
                        break
                    fi
                fi
            done
        fi

        if [ -z "$PYTHON_CMD" ]; then
            print_message $RED "Failed to install suitable Python version."
            print_message $YELLOW "Please install Python 3.12 or 3.13 manually from https://python.org/downloads/"
            print_message $YELLOW "Or consider using pyenv: curl https://pyenv.run | bash"
            exit 1
        fi
    fi

    print_message $GREEN "Using Python: $PYTHON_CMD"
    $PYTHON_CMD --version

    # Check if venv module is available
    if ! $PYTHON_CMD -m venv --help >/dev/null 2>&1; then
        print_message $YELLOW "Python venv module not available. Installing..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if command_exists apt-get; then
                sudo apt-get install -y python3-venv
            elif command_exists yum; then
                sudo yum install -y python3-venv
            elif command_exists dnf; then
                sudo dnf install -y python3-venv
            fi
        fi
    fi

    # Remove existing virtual environment if it exists
    if [ -d "$VENV_DIR" ]; then
        print_message $YELLOW "Found existing virtual environment in ./$VENV_DIR"
        print_message $YELLOW "Removing it to create a fresh one..."
        rm -rf "$VENV_DIR"
    fi

    # Create a new virtual environment
    print_message $BLUE "Creating virtual environment in ./$VENV_DIR..."
    if ! $PYTHON_CMD -m venv "$VENV_DIR"; then
        print_message $RED "Failed to create virtual environment."
        print_message $YELLOW "If you're using Python 3.12+, make sure python3-venv or equivalent is installed."
        print_message $YELLOW "You can try: sudo apt-get install python3-venv"
        print_message $YELLOW "Or for specific Python version: sudo apt-get install python3.12-venv"
        exit 1
    fi

    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
    print_message $GREEN "Created virtual environment in ./$VENV_DIR using $PYTHON_CMD"

    # Activate virtual environment
    if [ -f "$ACTIVATE_SCRIPT" ]; then
        source "$ACTIVATE_SCRIPT"
        print_message $GREEN "Activated virtual environment from $ACTIVATE_SCRIPT"
    else
        print_message $RED "Virtual environment activate script not found at $ACTIVATE_SCRIPT"
        print_message $RED "Installation cannot continue."
        exit 1
    fi

    # Upgrade pip
    print_message $BLUE "Upgrading pip..."
    pip install --upgrade pip

    print_message $GREEN "Python virtual environment set up successfully"
}

# Install the package and its dependencies
install_package() {
    print_message $BLUE "Installing Science Data Kit and dependencies..."

    # Install the package in development mode
    if [ "$INSTALL_EXTENSIONS" = true ]; then
        if [ "$EXTENSIONS_TO_INSTALL" = "all" ]; then
            print_message $BLUE "Installing Science Data Kit with all extensions..."
            pip install -e ".[all]"
        else
            print_message $BLUE "Installing Science Data Kit with extensions: $EXTENSIONS_TO_INSTALL"
            pip install -e ".[$EXTENSIONS_TO_INSTALL]"
        fi
    else
        print_message $BLUE "Installing Science Data Kit core package..."
        pip install -e .
    fi

    # Explicitly install neo4j-graphrag to ensure it's available
    print_message $BLUE "Ensuring neo4j-graphrag is installed..."
    pip install neo4j-graphrag>=0.6.1

    # Explicitly install psycopg2 for PostgreSQL connections
    print_message $BLUE "Ensuring psycopg2 is installed..."
    pip install psycopg2-binary

    print_message $GREEN "Science Data Kit installed successfully"
}

# Configure Neo4j
configure_neo4j() {
    print_message $BLUE "Configuring Neo4j..."

    # Check if docker-compose is available
    if command_exists docker-compose; then
        print_message $BLUE "Docker Compose is available, using it to manage Neo4j container"

        # Check if the container is already running via docker-compose
        if docker ps | grep -q "neo4j-instance"; then
            print_message $YELLOW "Neo4j container is already running"
        # Check if Neo4j container exists but is not running
        elif docker ps -a | grep -q "neo4j-instance"; then
            print_message $YELLOW "Neo4j container exists but is not running."
            print_message $YELLOW "Attempting to start the existing container..."
            if ! docker start neo4j-instance; then
                print_message $RED "Failed to start existing Neo4j container"
                print_message $YELLOW "Removing the container and trying to create a new one..."
                docker rm -f neo4j-instance >/dev/null 2>&1
                # Start the Neo4j service using docker-compose
                print_message $BLUE "Starting Neo4j container using docker-compose..."
                docker-compose up -d neo4j
                print_message $GREEN "Neo4j container started with docker-compose"
            else
                print_message $GREEN "Existing Neo4j container started"
            fi
        else
            # Start the Neo4j service using docker-compose
            print_message $BLUE "Starting Neo4j container using docker-compose..."
            docker-compose up -d neo4j
            print_message $GREEN "Neo4j container started with docker-compose"
        fi
    else
        # Fallback to direct Docker commands
        print_message $BLUE "Docker Compose not found, using direct Docker commands"

        # Check if Neo4j container is already running
        if docker ps | grep -q "neo4j-instance"; then
            print_message $YELLOW "Neo4j container is already running"
        # Check if Neo4j container exists but is not running
        elif docker ps -a | grep -q "neo4j-instance"; then
            print_message $YELLOW "Neo4j container exists but is not running. Starting it..."
            docker start neo4j-instance
            print_message $GREEN "Neo4j container started"
        else
            # Create a Docker volume for Neo4j data
            docker volume create neo4j-data

            # Run Neo4j container
            docker run -d \
                --name neo4j-instance \
                -p 7474:7474 -p 7687:7687 \
                -v neo4j-data:/data \
                -e NEO4J_AUTH=neo4j/password \
                neo4j:latest

            print_message $GREEN "Neo4j container started"
            print_message $YELLOW "Default credentials: neo4j/password"
            print_message $YELLOW "Neo4j browser available at: http://localhost:7474"
        fi
    fi

    # Create db_config.yaml if it doesn't exist
    if [ ! -f "db_config.yaml" ]; then
        cat > db_config.yaml << EOL
uri: bolt://localhost:7687
user: neo4j
password: password
EOL
        print_message $GREEN "Created db_config.yaml with default Neo4j credentials"
    fi
}

# Configure Ollama
configure_ollama() {
    print_message $BLUE "Configuring Ollama..."

    # First, check if Ollama API is already accessible
    print_message $BLUE "Checking if Ollama API is already accessible..."
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_message $GREEN "Ollama API is already accessible at http://localhost:11434"
        print_message $YELLOW "An Ollama service is already running. No need to start a new container."

        # Check if it's running in a Docker container
        if docker ps | grep -q "ollama"; then
            print_message $GREEN "Ollama is running in a Docker container"
        else
            print_message $YELLOW "Ollama is running, but not in a Docker container managed by this script."
            print_message $YELLOW "This could be a native Ollama installation or a container with a different name."
        fi

        # Pull a default model if needed
        print_message $BLUE "Checking for default model (llama2)..."
        if ! curl -s http://localhost:11434/api/tags | grep -q "llama2"; then
            print_message $BLUE "Downloading default model (llama2)..."
            curl -X POST http://localhost:11434/api/pull -d '{"name": "llama2"}'
            print_message $GREEN "Default model downloaded"
        else
            print_message $GREEN "Default model (llama2) is already available"
        fi

        return 0
    fi

    # Check if docker-compose is available
    if command_exists docker-compose; then
        print_message $BLUE "Docker Compose is available, using it to manage Ollama container"

        # Check if docker-compose.yml exists
        if [ ! -f "docker-compose.yml" ]; then
            print_message $YELLOW "docker-compose.yml file not found. Creating it..."
            # Call install_ollama to create the docker-compose.yml file
            install_ollama
            return $?
        fi

        # Check if the container is already running via docker-compose
        if docker ps | grep -q "dsk-ollama-instance"; then
            print_message $YELLOW "Ollama container is already running"
        else
            # Check if there's a conflicting container using the same port
            if docker ps | grep -q "0.0.0.0:11434"; then
                print_message $RED "Port 11434 is already in use by another container"
                print_message $YELLOW "Checking which container is using port 11434..."

                # Find the container using port 11434
                container_id=$(docker ps | grep "0.0.0.0:11434" | awk '{print $1}')
                if [ -n "$container_id" ]; then
                    container_name=$(docker inspect --format='{{.Name}}' "$container_id" | sed 's/\///')
                    print_message $YELLOW "Container '$container_name' ($container_id) is using port 11434"

                    # Ask if the user wants to stop the conflicting container
                    print_message $YELLOW "Do you want to stop the conflicting container? (y/n)"
                    read -r stop_container
                    if [[ "$stop_container" =~ ^[Yy]$ ]]; then
                        print_message $BLUE "Stopping container '$container_name'..."
                        docker stop "$container_id"
                        print_message $GREEN "Container stopped"
                    else
                        print_message $YELLOW "Keeping the existing container. Ollama will not be started."
                        return 1
                    fi
                fi
            fi

            # Check for both old and new container names
            if docker ps -a | grep -q "dsk-ollama-instance"; then
                print_message $YELLOW "A container named 'dsk-ollama-instance' exists but is not running"
                print_message $YELLOW "Attempting to remove the conflicting container..."
                docker rm -f dsk-ollama-instance >/dev/null 2>&1
                print_message $GREEN "Conflicting container removed"
            elif docker ps -a | grep -q "ollama-instance"; then
                print_message $YELLOW "A container named 'ollama-instance' exists but is not running"
                print_message $YELLOW "Attempting to remove the conflicting container..."
                docker rm -f ollama-instance >/dev/null 2>&1
                print_message $GREEN "Conflicting container removed"
            fi

            # Start the Ollama service using docker-compose
            print_message $BLUE "Starting Ollama container using docker-compose..."
            if ! docker-compose up -d ollama; then
                print_message $RED "Failed to start Ollama container with docker-compose"
                print_message $YELLOW "This could be due to port conflicts or other issues"
                print_message $YELLOW "Checking if Ollama API is accessible despite the error..."

                if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                    print_message $GREEN "Ollama API is accessible at http://localhost:11434 despite docker-compose error"
                    print_message $YELLOW "An Ollama service is already running. No need to start a new container."
                    return 0
                else
                    print_message $RED "Ollama API is not accessible. Installation failed."
                    return 1
                fi
            fi

            print_message $GREEN "Ollama container started with docker-compose"

            # Wait for Ollama to start
            print_message $BLUE "Waiting for Ollama API to become available..."
            max_attempts=30
            attempt=0
            while [ $attempt -lt $max_attempts ]; do
                if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                    print_message $GREEN "Ollama API is now accessible"
                    break
                fi
                attempt=$((attempt+1))
                print_message $YELLOW "Waiting for Ollama API to start (attempt $attempt/$max_attempts)..."
                sleep 2
            done

            if [ $attempt -eq $max_attempts ]; then
                print_message $RED "Timed out waiting for Ollama API to become accessible"
                print_message $YELLOW "Checking container status..."
                docker ps | grep ollama
                print_message $YELLOW "Recent logs from Ollama container:"
                docker logs --tail 20 dsk-ollama-instance
                return 1
            fi

            # Pull a default model
            print_message $BLUE "Downloading a default model (llama2)..."
            curl -X POST http://localhost:11434/api/pull -d '{"name": "llama2"}'
            print_message $GREEN "Default model downloaded"
        fi
    else
        # Fallback to direct Docker commands
        print_message $BLUE "Docker Compose not found, using direct Docker commands"

        # Check if Ollama container is already running
        if docker ps | grep -q "dsk-ollama-instance"; then
            print_message $YELLOW "Ollama container is already running"
        # Check for both old and new container names
        elif docker ps -a | grep -q "dsk-ollama-instance"; then
            print_message $YELLOW "Ollama container exists but is not running. Starting it..."
            if ! docker start dsk-ollama-instance; then
                print_message $RED "Failed to start existing Ollama container"
                print_message $YELLOW "Removing the container and trying to create a new one..."
                docker rm -f dsk-ollama-instance >/dev/null 2>&1
                # Continue to the container creation code below
            else
                print_message $GREEN "Ollama container started"
            fi
        elif docker ps -a | grep -q "ollama-instance"; then
            print_message $YELLOW "Old Ollama container exists but is not running."
            print_message $YELLOW "Removing the old container and creating a new one with updated name..."
            docker rm -f ollama-instance >/dev/null 2>&1
            # Continue to the container creation code below
        else
            # Check if there's a conflicting container using the same port
            if docker ps | grep -q "0.0.0.0:11434"; then
                print_message $RED "Port 11434 is already in use by another container"
                print_message $YELLOW "Checking which container is using port 11434..."

                # Find the container using port 11434
                container_id=$(docker ps | grep "0.0.0.0:11434" | awk '{print $1}')
                if [ -n "$container_id" ]; then
                    container_name=$(docker inspect --format='{{.Name}}' "$container_id" | sed 's/\///')
                    print_message $YELLOW "Container '$container_name' ($container_id) is using port 11434"

                    # Ask if the user wants to stop the conflicting container
                    print_message $YELLOW "Do you want to stop the conflicting container? (y/n)"
                    read -r stop_container
                    if [[ "$stop_container" =~ ^[Yy]$ ]]; then
                        print_message $BLUE "Stopping container '$container_name'..."
                        docker stop "$container_id"
                        print_message $GREEN "Container stopped"
                    else
                        print_message $YELLOW "Keeping the existing container. Ollama will not be started."
                        return 1
                    fi
                fi
            fi

            # Create a Docker volume for Ollama data
            print_message $BLUE "Creating Docker volume for Ollama data..."
            docker volume create ollama-data

            # Run Ollama container
            print_message $BLUE "Starting Ollama container..."
            if ! docker run -d \
                --name dsk-ollama-instance \
                -p 11434:11434 \
                -v ollama-data:/root/.ollama \
                ollama/ollama:latest; then

                print_message $RED "Failed to start Ollama container"
                print_message $YELLOW "This could be due to port conflicts or other issues"
                print_message $YELLOW "Checking if Ollama API is accessible despite the error..."

                if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                    print_message $GREEN "Ollama API is accessible at http://localhost:11434 despite container error"
                    print_message $YELLOW "An Ollama service is already running. No need to start a new container."
                    return 0
                else
                    print_message $RED "Ollama API is not accessible. Installation failed."
                    return 1
                fi
            fi

            print_message $GREEN "Ollama container started"
            print_message $YELLOW "Ollama API available at: http://localhost:11434"

            # Wait for Ollama to start
            print_message $BLUE "Waiting for Ollama API to become available..."
            max_attempts=30
            attempt=0
            while [ $attempt -lt $max_attempts ]; do
                if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                    print_message $GREEN "Ollama API is now accessible"
                    break
                fi
                attempt=$((attempt+1))
                print_message $YELLOW "Waiting for Ollama API to start (attempt $attempt/$max_attempts)..."
                sleep 2
            done

            if [ $attempt -eq $max_attempts ]; then
                print_message $RED "Timed out waiting for Ollama API to become accessible"
                print_message $YELLOW "Checking container status..."
                docker ps | grep ollama
                print_message $YELLOW "Recent logs from Ollama container:"
                docker logs --tail 20 dsk-ollama-instance
                return 1
            fi

            # Pull a default model
            print_message $BLUE "Downloading a default model (llama2)..."
            curl -X POST http://localhost:11434/api/pull -d '{"name": "llama2"}'
            print_message $GREEN "Default model downloaded"
        fi
    fi
}

# Main installation function
main() {
    print_message $BLUE "=== Science Data Kit Installation ==="

    # Check dependencies
    check_dependencies

    # Set up Python environment
    setup_python_env

    # Install the package
    install_package

    # Configure Neo4j
    configure_neo4j

    # Configure Ollama if running with --clean flag or explicitly requested
    if [ "$CLEAN_INSTALL" = true ]; then
        configure_ollama
    else
        print_message $YELLOW "Would you like to set up Ollama for local LLM functionality? (y/n)"
        read -r setup_ollama
        if [[ "$setup_ollama" =~ ^[Yy]$ ]]; then
            configure_ollama
        fi
    fi

    print_message $GREEN "=== Installation Complete ==="

    # Display information about installed extensions
    if [ "$INSTALL_EXTENSIONS" = true ]; then
        if [ "$EXTENSIONS_TO_INSTALL" = "all" ]; then
            print_message $GREEN "All extensions have been installed"
        else
            print_message $GREEN "Installed extensions: $EXTENSIONS_TO_INSTALL"
        fi
    else
        print_message $YELLOW "Note: Only the core package was installed. To install extensions, use:"
        print_message $YELLOW "  ./install.sh -e                  # Install all extensions"
        print_message $YELLOW "  ./install.sh --extensions=dropbox,msgraph  # Install specific extensions"
    fi

    print_message $GREEN "To start Science Data Kit, run:"
    print_message $YELLOW "source $ACTIVATE_SCRIPT"
    print_message $YELLOW "science_data_kit"

    # Note: isatools has been removed from the codebase
    # The Science Data Kit now uses the new ontology module for ontology integration
    print_message $GREEN "The Science Data Kit now uses Neo4j's neosemantics (n10s) plugin for ontology integration"
    print_message $GREEN "No additional installation steps are required for ontology support"
}

# Run the main function
main

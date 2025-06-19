#!/bin/bash
set -e

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running with --clean flag
CLEAN_INSTALL=false
for arg in "$@"; do
    if [ "$arg" == "--clean" ]; then
        CLEAN_INSTALL=true
    fi
done

# Print a colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python (platform-specific)
install_python() {
    print_message $BLUE "Installing Python 3.10+ (preferably 3.11 or 3.12)..."

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu
            print_message $BLUE "Detected Debian/Ubuntu system"
            print_message $BLUE "Adding deadsnakes PPA for Python installation..."
            sudo apt-get update
            sudo apt-get install -y software-properties-common
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt-get update

            # Try to install Python 3.12 first, then fall back to 3.11, then 3.10
            if apt-cache show python3.12 &>/dev/null; then
                print_message $BLUE "Installing Python 3.12..."
                sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
                PYTHON_VERSION="3.12"
            elif apt-cache show python3.11 &>/dev/null; then
                print_message $BLUE "Installing Python 3.11..."
                sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
                PYTHON_VERSION="3.11"
            else
                print_message $BLUE "Installing Python 3.10..."
                sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
                PYTHON_VERSION="3.10"
            fi

            # Set installed Python as the default python3
            if command_exists update-alternatives; then
                sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.${PYTHON_VERSION#*.} 1
            fi

            # Install pip for the installed Python version
            print_message $BLUE "Installing pip for Python ${PYTHON_VERSION}..."
            curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.${PYTHON_VERSION#*.}

        elif command_exists yum; then
            # RHEL/CentOS/Fedora
            print_message $BLUE "Detected RHEL/CentOS/Fedora system"

            # For RHEL/CentOS 8+
            if grep -q "release 8" /etc/redhat-release 2>/dev/null || grep -q "release 9" /etc/redhat-release 2>/dev/null; then
                # Try to install Python 3.12 first, then fall back to 3.11, then 3.10
                if dnf list python3.12 &>/dev/null; then
                    sudo dnf install -y python3.12 python3.12-devel
                    PYTHON_VERSION="3.12"
                elif dnf list python3.11 &>/dev/null; then
                    sudo dnf install -y python3.11 python3.11-devel
                    PYTHON_VERSION="3.11"
                else
                    sudo dnf install -y python3.10 python3.10-devel
                    PYTHON_VERSION="3.10"
                fi
            else
                # For older versions or Fedora
                print_message $YELLOW "Installing Python 3.10+ on this system requires additional repositories."
                print_message $YELLOW "Would you like to install Python using the EPEL repository? (y/n)"
                read -r install_epel
                if [[ "$install_epel" =~ ^[Yy]$ ]]; then
                    sudo yum install -y epel-release

                    # Try to install Python 3.12 first, then fall back to 3.11, then 3.10
                    if yum list python3.12 &>/dev/null; then
                        sudo yum install -y python3.12 python3.12-devel
                        PYTHON_VERSION="3.12"
                    elif yum list python3.11 &>/dev/null; then
                        sudo yum install -y python3.11 python3.11-devel
                        PYTHON_VERSION="3.11"
                    else
                        sudo yum install -y python3.10 python3.10-devel
                        PYTHON_VERSION="3.10"
                    fi
                else
                    print_message $YELLOW "Please install Python 3.10+ manually."
                    print_message $YELLOW "Visit https://www.python.org/downloads/ for more information."
                    return 1
                fi
            fi

            # Install pip for the installed Python version
            curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.${PYTHON_VERSION#*.}

        else
            print_message $YELLOW "Automatic Python installation is not supported for this Linux distribution."
            print_message $YELLOW "Please install Python 3.10+ manually:"
            print_message $YELLOW "1. Visit https://www.python.org/downloads/"
            print_message $YELLOW "2. Download Python 3.10 or higher (preferably 3.11 or 3.12)"
            print_message $YELLOW "3. Follow the installation instructions for your distribution"
            return 1
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_message $BLUE "Detected macOS system"

        if command_exists brew; then
            # Try to install Python 3.12 first, then fall back to 3.11, then 3.10
            if brew info python@3.12 &>/dev/null; then
                print_message $BLUE "Installing Python 3.12 using Homebrew..."
                brew install python@3.12
                PYTHON_VERSION="3.12"
            elif brew info python@3.11 &>/dev/null; then
                print_message $BLUE "Installing Python 3.11 using Homebrew..."
                brew install python@3.11
                PYTHON_VERSION="3.11"
            else
                print_message $BLUE "Installing Python 3.10 using Homebrew..."
                brew install python@3.10
                PYTHON_VERSION="3.10"
            fi

            # Add to PATH if needed
            if ! command_exists python3.${PYTHON_VERSION#*.}; then
                print_message $YELLOW "Python ${PYTHON_VERSION} installed but not in PATH."
                print_message $YELLOW "Add it to your PATH with:"
                print_message $YELLOW "echo 'export PATH=\"/usr/local/opt/python@${PYTHON_VERSION}/bin:\$PATH\"' >> ~/.zshrc"
                print_message $YELLOW "or"
                print_message $YELLOW "echo 'export PATH=\"/usr/local/opt/python@${PYTHON_VERSION}/bin:\$PATH\"' >> ~/.bash_profile"
            fi
        else
            print_message $YELLOW "Homebrew not found. Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

            if command_exists brew; then
                # Try to install Python 3.12 first, then fall back to 3.11, then 3.10
                if brew info python@3.12 &>/dev/null; then
                    print_message $BLUE "Installing Python 3.12 using Homebrew..."
                    brew install python@3.12
                    PYTHON_VERSION="3.12"
                elif brew info python@3.11 &>/dev/null; then
                    print_message $BLUE "Installing Python 3.11 using Homebrew..."
                    brew install python@3.11
                    PYTHON_VERSION="3.11"
                else
                    print_message $BLUE "Installing Python 3.10 using Homebrew..."
                    brew install python@3.10
                    PYTHON_VERSION="3.10"
                fi
            else
                print_message $RED "Failed to install Homebrew."
                print_message $YELLOW "Please install Python 3.10+ manually:"
                print_message $YELLOW "1. Visit https://www.python.org/downloads/"
                print_message $YELLOW "2. Download Python 3.10 or higher for macOS (preferably 3.11 or 3.12)"
                print_message $YELLOW "3. Follow the installation instructions"
                return 1
            fi
        fi

    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        print_message $BLUE "Detected Windows system"
        print_message $YELLOW "Please install Python 3.10+ manually:"
        print_message $YELLOW "1. Visit https://www.python.org/downloads/"
        print_message $YELLOW "2. Download Python 3.10 or higher for Windows (preferably 3.11 or 3.12)"
        print_message $YELLOW "3. During installation, check 'Add Python to PATH'"
        print_message $YELLOW "4. Restart your terminal after installation"
        return 1

    else
        print_message $RED "Unsupported operating system: $OSTYPE"
        print_message $YELLOW "Please install Python 3.10+ manually:"
        print_message $YELLOW "Visit https://www.python.org/downloads/ for more information."
        return 1
    fi

    # Verify Python installation
    PYTHON_CMD="python3.${PYTHON_VERSION#*.}"
    if command_exists $PYTHON_CMD; then
        print_message $GREEN "Python ${PYTHON_VERSION} installed successfully"
        # Create a symlink to python3 if needed
        if ! command_exists python3 || [[ $(python3 --version 2>&1) != *"${PYTHON_VERSION}"* ]]; then
            print_message $YELLOW "Creating symlink for python3 -> ${PYTHON_CMD}"
            sudo ln -sf $(which $PYTHON_CMD) /usr/local/bin/python3
        fi
    else
        print_message $RED "Python ${PYTHON_VERSION} installation may have failed."
        print_message $YELLOW "Please try installing manually:"
        print_message $YELLOW "Visit https://www.python.org/downloads/ for more information."
        return 1
    fi

    # Install/upgrade pip
    print_message $BLUE "Ensuring pip is installed and up to date..."
    python3 -m ensurepip --upgrade || curl -sS https://bootstrap.pypa.io/get-pip.py | python3

    return 0
}

# Check system dependencies
check_dependencies() {
    print_message $BLUE "Checking system dependencies..."

    # Check for Python 3.10+ (preferably 3.11 or 3.12)
    if command_exists python3; then
        python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        python_major=$(echo $python_version | cut -d. -f1)
        python_minor=$(echo $python_version | cut -d. -f2)

        if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]); then
            print_message $RED "Error: Python 3.10 or higher is required (found $python_version)"
            print_message $YELLOW "Would you like to install Python 3.10+ (preferably 3.11 or 3.12)? (y/n)"
            read -r install_python_choice
            if [[ "$install_python_choice" =~ ^[Yy]$ ]]; then
                install_python
                # Re-check Python version after installation
                if command_exists python3; then
                    python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
                    python_major=$(echo $python_version | cut -d. -f1)
                    python_minor=$(echo $python_version | cut -d. -f2)

                    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]); then
                        print_message $RED "Python 3.10+ installation failed or not set as default."
                        print_message $YELLOW "Please install Python 3.10 or higher (preferably 3.11 or 3.12) manually before continuing."
                        exit 1
                    else
                        print_message $GREEN "Found Python $python_version"
                    fi
                else
                    print_message $RED "Python 3 not found after installation attempt."
                    print_message $YELLOW "Please install Python 3.10 or higher (preferably 3.11 or 3.12) manually before continuing."
                    exit 1
                fi
            else
                print_message $YELLOW "Please install Python 3.10 or higher (preferably 3.11 or 3.12) before continuing."
                exit 1
            fi
        else
            print_message $GREEN "Found Python $python_version"
        fi
    else
        print_message $RED "Error: Python 3 not found"
        print_message $YELLOW "Would you like to install Python 3.10+ (preferably 3.11 or 3.12)? (y/n)"
        read -r install_python_choice
        if [[ "$install_python_choice" =~ ^[Yy]$ ]]; then
            install_python
            # Check if Python is now available
            if ! command_exists python3; then
                print_message $RED "Python 3 not found after installation attempt."
                print_message $YELLOW "Please install Python 3.10 or higher (preferably 3.11 or 3.12) manually before continuing."
                exit 1
            else
                python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
                print_message $GREEN "Found Python $python_version"
            fi
        else
            print_message $YELLOW "Please install Python 3.10 or higher (preferably 3.11 or 3.12) before continuing."
            exit 1
        fi
    fi

    # Check for pip
    if ! command_exists pip3; then
        print_message $RED "Error: pip3 not found"
        print_message $YELLOW "Please install pip3 before continuing."
        exit 1
    else
        print_message $GREEN "Found pip3"
    fi

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
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
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

# Check if Ollama container is running
check_ollama() {
    print_message $BLUE "Checking for Ollama container..."

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

        # Check if Ollama container is running
        if docker ps | grep -q "ollama-instance"; then
            print_message $GREEN "Ollama container is running"
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
version: '3'
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
    container_name: ollama-instance
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

        # Start Ollama container using docker-compose
        print_message $BLUE "Starting Ollama container using docker-compose..."
        docker-compose up -d ollama

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
            print_message $YELLOW "You may need to check the container logs: docker-compose logs ollama"
            return 1
        fi
    else
        # Fallback to direct Docker commands
        print_message $BLUE "Docker Compose not found, using direct Docker commands"

        # Create a Docker volume for Ollama data
        print_message $BLUE "Creating Docker volume for Ollama data..."
        docker volume create ollama-data

        # Run Ollama container
        print_message $BLUE "Starting Ollama container..."
        docker run -d \
            --name ollama-instance \
            -p 11434:11434 \
            -v ollama-data:/root/.ollama \
            ollama/ollama:latest

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
            print_message $YELLOW "You may need to check the container logs: docker logs ollama-instance"
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

    # Check if venv module is available
    if ! python3 -c "import venv" &>/dev/null; then
        print_message $YELLOW "Python venv module not found. Installing venv module..."

        # Get Python version for specific package installation
        python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

        if command_exists apt-get; then
            print_message $BLUE "Attempting to install python${python_version}-venv package..."
            sudo apt-get update
            if ! sudo apt-get install -y python${python_version}-venv; then
                print_message $YELLOW "Failed to install python${python_version}-venv. Trying python3-venv instead..."
                if ! sudo apt-get install -y python3-venv; then
                    print_message $RED "Failed to install venv module. Please install it manually."
                    print_message $YELLOW "For Ubuntu/Debian: sudo apt-get install python3-venv"
                    print_message $YELLOW "For other systems: pip3 install virtualenv"
                    exit 1
                fi
            fi
        elif command_exists yum; then
            sudo yum install -y python3-venv
        else
            pip3 install virtualenv
        fi
    fi

    # Define possible virtual environment directories
    VENV_DIRS=("venv" ".venv")
    VENV_DIR=""
    ACTIVATE_SCRIPT=""

    # Check if any existing virtual environment is valid
    for dir in "${VENV_DIRS[@]}"; do
        if [ -d "$dir" ] && [ -f "$dir/bin/activate" ]; then
            VENV_DIR="$dir"
            ACTIVATE_SCRIPT="$dir/bin/activate"
            print_message $GREEN "Found valid virtual environment in ./$dir"
            break
        elif [ -d "$dir" ] && [ ! -f "$dir/bin/activate" ]; then
            print_message $YELLOW "Found $dir directory but it doesn't contain an activate script."
            print_message $YELLOW "This suggests the virtual environment is corrupted or incomplete."
            print_message $YELLOW "Would you like to remove it and create a new one? (y/n)"
            read -r recreate_venv
            if [[ "$recreate_venv" =~ ^[Yy]$ ]]; then
                rm -rf "$dir"
                print_message $BLUE "Removed corrupted $dir directory."
            fi
        fi
    done

    # Create a new virtual environment if none exists
    if [ -z "$VENV_DIR" ]; then
        VENV_DIR="venv"  # Default to venv
        print_message $BLUE "Creating virtual environment in ./$VENV_DIR..."
        if ! python3 -m venv "$VENV_DIR"; then
            print_message $RED "Failed to create virtual environment."
            print_message $YELLOW "If you're using Python 3.12+, make sure python3-venv or equivalent is installed."
            print_message $YELLOW "You can try: sudo apt-get install python3-venv"
            print_message $YELLOW "Or for specific Python version: sudo apt-get install python3.X-venv"
            exit 1
        fi
        ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
        print_message $GREEN "Created virtual environment in ./$VENV_DIR"
    fi

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
    pip install --upgrade pip

    print_message $GREEN "Python virtual environment set up successfully"
}

# Install the package and its dependencies
install_package() {
    print_message $BLUE "Installing Science Data Kit and dependencies..."

    # Install the package in development mode
    pip install -e .

    # Explicitly install neo4j-graphrag to ensure it's available
    print_message $BLUE "Ensuring neo4j-graphrag is installed..."
    pip install neo4j-graphrag>=0.6.1

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

    # Check if docker-compose is available
    if command_exists docker-compose; then
        print_message $BLUE "Docker Compose is available, using it to manage Ollama container"

        # Check if the container is already running via docker-compose
        if docker ps | grep -q "ollama-instance"; then
            print_message $YELLOW "Ollama container is already running"
        else
            # Start the Ollama service using docker-compose
            print_message $BLUE "Starting Ollama container using docker-compose..."
            docker-compose up -d ollama
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

            # Pull a default model
            print_message $BLUE "Downloading a default model (llama2)..."
            curl -X POST http://localhost:11434/api/pull -d '{"name": "llama2"}'
            print_message $GREEN "Default model downloaded"
        fi
    else
        # Fallback to direct Docker commands
        print_message $BLUE "Docker Compose not found, using direct Docker commands"

        # Check if Ollama container is already running
        if docker ps | grep -q "ollama-instance"; then
            print_message $YELLOW "Ollama container is already running"
        # Check if Ollama container exists but is not running
        elif docker ps -a | grep -q "ollama-instance"; then
            print_message $YELLOW "Ollama container exists but is not running. Starting it..."
            docker start ollama-instance
            print_message $GREEN "Ollama container started"
        else
            # Create a Docker volume for Ollama data
            docker volume create ollama-data

            # Run Ollama container
            docker run -d \
                --name ollama-instance \
                -p 11434:11434 \
                -v ollama-data:/root/.ollama \
                ollama/ollama:latest

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
    print_message $GREEN "To start Science Data Kit, run:"
    print_message $YELLOW "source $ACTIVATE_SCRIPT"
    print_message $YELLOW "science_data_kit"

    # Optional: Install isatools
    print_message $BLUE "Would you like to install isatools? (y/n)"
    read -r install_isatools
    if [[ "$install_isatools" =~ ^[Yy]$ ]]; then
        print_message $BLUE "Which version of isatools would you like to install?"
        print_message $YELLOW "1) Basic isatools (Python 3.10+, limited functionality)"
        print_message $YELLOW "   - Compatible with Python 3.11 and 3.12"
        print_message $YELLOW "   - Recommended for newer Python versions"
        print_message $YELLOW "2) Full isatools (Python 3.9, complete functionality)"
        print_message $YELLOW "   - Includes mzML file processing capabilities"
        print_message $YELLOW "   - Requires Python 3.9 (will create a separate environment)"
        read -r isatools_version

        if [ "$isatools_version" -eq 1 ]; then
            # Get current Python version
            python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

            if [[ $(echo "$python_version" | cut -d. -f1) -eq 3 && $(echo "$python_version" | cut -d. -f2) -ge 12 ]]; then
                print_message $BLUE "Installing basic isatools for Python $python_version..."
                pip install -e .[isatools]
                print_message $GREEN "Basic isatools installed successfully"
            else
                print_message $BLUE "Installing basic isatools for Python $python_version..."
                pip install -e .[isatools]
                print_message $GREEN "Basic isatools installed successfully"
                print_message $YELLOW "Note: For Python 3.12+, some additional compatibility fixes are available."
                print_message $YELLOW "Would you like to run the Python 3.12+ compatibility script? (y/n)"
                read -r run_compat_script
                if [[ "$run_compat_script" =~ ^[Yy]$ ]]; then
                    python install_isatools_py312.py
                fi
            fi
        elif [ "$isatools_version" -eq 2 ]; then
            print_message $BLUE "Installing full isatools for Python 3.9..."
            print_message $YELLOW "This will create a separate Python 3.9 environment."
            if command_exists conda; then
                bash install_isatools.sh
            else
                python install_isatools.py
            fi
            print_message $GREEN "Full isatools installed successfully"
        else
            print_message $RED "Invalid option. Skipping isatools installation."
        fi
    fi
}

# Run the main function
main

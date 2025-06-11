#!/bin/bash
set -e

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check system dependencies
check_dependencies() {
    print_message $BLUE "Checking system dependencies..."
    
    # Check for Python 3.10+
    if command_exists python3; then
        python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        python_major=$(echo $python_version | cut -d. -f1)
        python_minor=$(echo $python_version | cut -d. -f2)
        
        if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 10 ]); then
            print_message $RED "Error: Python 3.10 or higher is required (found $python_version)"
            print_message $YELLOW "Please install Python 3.10 or higher before continuing."
            exit 1
        else
            print_message $GREEN "Found Python $python_version"
        fi
    else
        print_message $RED "Error: Python 3 not found"
        print_message $YELLOW "Please install Python 3.10 or higher before continuing."
        exit 1
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

# Set up Python virtual environment
setup_python_env() {
    print_message $BLUE "Setting up Python virtual environment..."
    
    # Check if virtualenv is installed
    if ! command_exists python3 -m venv; then
        print_message $YELLOW "Installing venv module..."
        if command_exists apt-get; then
            sudo apt-get install -y python3-venv
        elif command_exists yum; then
            sudo yum install -y python3-venv
        else
            pip3 install virtualenv
        fi
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_message $GREEN "Created virtual environment in ./venv"
    else
        print_message $YELLOW "Virtual environment already exists in ./venv"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_message $GREEN "Python virtual environment set up successfully"
}

# Install the package and its dependencies
install_package() {
    print_message $BLUE "Installing Science Data Kit and dependencies..."
    
    # Install the package in development mode
    pip install -e .
    
    print_message $GREEN "Science Data Kit installed successfully"
}

# Configure Neo4j
configure_neo4j() {
    print_message $BLUE "Configuring Neo4j..."
    
    # Check if Neo4j container is already running
    if docker ps | grep -q "neo4j-instance"; then
        print_message $YELLOW "Neo4j container is already running"
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
        
        # Create db_config.yaml if it doesn't exist
        if [ ! -f "db_config.yaml" ]; then
            cat > db_config.yaml << EOL
uri: bolt://localhost:7687
user: neo4j
password: password
EOL
            print_message $GREEN "Created db_config.yaml with default Neo4j credentials"
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
    
    print_message $GREEN "=== Installation Complete ==="
    print_message $GREEN "To start Science Data Kit, run:"
    print_message $YELLOW "source venv/bin/activate"
    print_message $YELLOW "science_data_kit"
    
    # Optional: Install isatools
    print_message $BLUE "Would you like to install isatools? (y/n)"
    read -r install_isatools
    if [[ "$install_isatools" =~ ^[Yy]$ ]]; then
        print_message $BLUE "Which version of isatools would you like to install?"
        print_message $YELLOW "1) Basic isatools (Python 3.12+, limited functionality)"
        print_message $YELLOW "2) Full isatools (Python 3.9, complete functionality)"
        read -r isatools_version
        
        if [ "$isatools_version" -eq 1 ]; then
            print_message $BLUE "Installing basic isatools for Python 3.12+..."
            pip install -e .[isatools]
            print_message $GREEN "Basic isatools installed successfully"
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
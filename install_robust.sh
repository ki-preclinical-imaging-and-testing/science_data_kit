#!/bin/bash
set -e

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PACKAGE_NAME="science-data-kit"
MAIN_VENV_NAME="science-data-kit-env"

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

# Install virtualenv if not available
ensure_virtualenv() {
    print_message $BLUE "Ensuring virtualenv is available..."

    if command_exists virtualenv; then
        print_message $GREEN "virtualenv is already installed"
        return 0
    fi

    # Try to install virtualenv using pip
    if command_exists pip3; then
        print_message $BLUE "Installing virtualenv using pip3..."
        pip3 install --user virtualenv
    elif command_exists pip; then
        print_message $BLUE "Installing virtualenv using pip..."
        pip install --user virtualenv
    else
        # Install using package manager
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if command_exists apt-get; then
                print_message $BLUE "Installing virtualenv using apt..."
                sudo apt-get update
                sudo apt-get install -y python3-virtualenv
            elif command_exists yum; then
                sudo yum install -y python3-virtualenv
            elif command_exists dnf; then
                sudo dnf install -y python3-virtualenv
            elif command_exists pacman; then
                sudo pacman -S --noconfirm python-virtualenv
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            if command_exists brew; then
                brew install virtualenv
            else
                print_message $RED "Please install Homebrew first or install virtualenv manually"
                exit 1
            fi
        fi
    fi

    # Verify installation
    if command_exists virtualenv; then
        print_message $GREEN "virtualenv installed successfully"
    else
        print_message $RED "Failed to install virtualenv"
        print_message $YELLOW "Please install virtualenv manually: pip install virtualenv"
        exit 1
    fi
}

# Find and install Python versions
setup_python_versions() {
    print_message $BLUE "Setting up Python versions..."

    # Install Python versions we need
    install_python_versions

    # Find available Python versions
    PYTHON_312_CMD=""
    PYTHON_313_CMD=""

    # Check for Python 3.12/3.13 (for main environment)
    for cmd in python3.13 python3.12 python3 python; do
        if command_exists "$cmd"; then
            version=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
            case "$version" in
                "3.13") PYTHON_313_CMD="$cmd"; break ;;
                "3.12") PYTHON_312_CMD="$cmd"; break ;;
            esac
        fi
    done

    # Select main Python (prefer 3.13, fall back to 3.12)
    if [ -n "$PYTHON_313_CMD" ]; then
        MAIN_PYTHON_CMD="$PYTHON_313_CMD"
        print_message $GREEN "Found Python 3.13: $PYTHON_313_CMD"
    elif [ -n "$PYTHON_312_CMD" ]; then
        MAIN_PYTHON_CMD="$PYTHON_312_CMD"
        print_message $GREEN "Found Python 3.12: $PYTHON_312_CMD"
    else
        print_message $RED "No suitable Python 3.12+ found"
        print_message $YELLOW "Attempting to install Python 3.12/3.13..."
        install_modern_python

        # Try again after installation
        for cmd in python3.13 python3.12 python3 python; do
            if command_exists "$cmd"; then
                version=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
                case "$version" in
                    "3.13") MAIN_PYTHON_CMD="$cmd"; break ;;
                    "3.12") MAIN_PYTHON_CMD="$cmd"; break ;;
                esac
            fi
        done

        if [ -z "$MAIN_PYTHON_CMD" ]; then
            print_message $RED "Failed to install Python 3.12+. Please install manually."
            exit 1
        fi
    fi

    # No need to check for Python 3.9 anymore as we've removed isatools dependencies
}

# Install Python versions
install_python_versions() {
    print_message $BLUE "Installing required Python versions..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            # Ubuntu/Debian
            print_message $BLUE "Adding deadsnakes PPA for multiple Python versions..."
            sudo apt-get update || true
            sudo apt-get install -y software-properties-common

            # Add deadsnakes PPA
            if sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null; then
                sudo apt-get update || true
            else
                # Manual fallback
                echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list
                sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 2>/dev/null || true
                sudo apt-get update || true
            fi

            # Install multiple Python versions
            PYTHON_PACKAGES="python3-pip python3-dev build-essential"

            # Try to install Python 3.13
            if apt-cache show python3.13 >/dev/null 2>&1; then
                PYTHON_PACKAGES="$PYTHON_PACKAGES python3.13 python3.13-venv python3.13-dev"
                print_message $BLUE "Will install Python 3.13"
            fi

            # Try to install Python 3.12
            if apt-cache show python3.12 >/dev/null 2>&1; then
                PYTHON_PACKAGES="$PYTHON_PACKAGES python3.12 python3.12-venv python3.12-dev"
                print_message $BLUE "Will install Python 3.12"
            fi

            # We no longer need Python 3.9 as we've removed isatools dependencies

            sudo apt-get install -y $PYTHON_PACKAGES

        elif command_exists yum || command_exists dnf; then
            # RHEL/CentOS/Fedora
            PKG_MGR="yum"
            if command_exists dnf; then
                PKG_MGR="dnf"
            fi

            sudo $PKG_MGR install -y python3 python3-pip python3-devel gcc

        elif command_exists pacman; then
            # Arch Linux
            sudo pacman -S --noconfirm python python-pip python-virtualenv base-devel
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            # Install Python versions with Homebrew
            brew install python@3.13 python@3.12 || true
        else
            print_message $RED "Homebrew required for macOS. Install from https://brew.sh/"
            exit 1
        fi
    fi
}

# Install modern Python (3.12+) specifically
install_modern_python() {
    print_message $BLUE "Installing modern Python (3.12+)..."
    # This function is called if we don't find 3.12/3.13 after the general installation
    # Most of the work is done in install_python_versions, so this is a fallback
}

# Create virtual environment with specific Python version
create_virtualenv() {
    local env_name="$1"
    local python_cmd="$2"
    local description="$3"

    print_message $BLUE "Creating $description environment: $env_name"
    print_message $BLUE "Using Python: $python_cmd ($($python_cmd --version 2>&1))"

    # Remove existing environment
    if [ -d "$env_name" ]; then
        print_message $YELLOW "Removing existing environment: $env_name"
        rm -rf "$env_name"
    fi

    # Create new environment with specific Python version
    if ! virtualenv -p "$python_cmd" "$env_name"; then
        print_message $RED "Failed to create virtual environment with $python_cmd"
        return 1
    fi

    print_message $GREEN "Created $description environment: $env_name"
    return 0
}

# Setup main environment (Python 3.12+)
setup_main_environment() {
    print_message $BLUE "Setting up main Science Data Kit environment..."

    if ! create_virtualenv "$MAIN_VENV_NAME" "$MAIN_PYTHON_CMD" "main"; then
        exit 1
    fi

    # Activate and install packages
    source "$MAIN_VENV_NAME/bin/activate"

    # Verify we're in the right environment
    current_python=$(python --version 2>&1)
    current_path=$(which python)
    print_message $BLUE "Activated environment - Python: $current_python"
    print_message $BLUE "Python location: $current_path"

    print_message $BLUE "Upgrading pip..."
    pip install --upgrade pip

    print_message $BLUE "Installing Science Data Kit..."
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        pip install -e .
    else
        print_message $YELLOW "No setup.py/pyproject.toml found. Environment ready for development."
    fi

    # Test the environment
    print_message $BLUE "Testing main environment..."
    python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} in {sys.executable}')"

    print_message $GREEN "Main environment setup complete"
    deactivate
}

# Note: isatools environment setup has been removed as we no longer use isatools

# Create wrapper scripts for easy environment switching
create_wrapper_scripts() {
    print_message $BLUE "Creating environment wrapper scripts..."

    # Main environment activation script
    cat > activate_main.sh << 'EOF'
#!/bin/bash
echo "Activating Science Data Kit main environment..."

# Deactivate any existing conda/virtual environments
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "Deactivating conda environment: $CONDA_DEFAULT_ENV"
    conda deactivate 2>/dev/null || true
fi

if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment: $VIRTUAL_ENV"
    deactivate 2>/dev/null || true
fi

# Activate our environment
if [ -f "science-data-kit-env/bin/activate" ]; then
    source science-data-kit-env/bin/activate
    echo "Main environment active ($(python --version))"
    echo "Available commands: science_data_kit, python, pip"
    echo "Type 'deactivate' to exit this environment"
else
    echo "Error: Main environment not found. Please run the installer."
    exit 1
fi
EOF
    chmod +x activate_main.sh

    # Note: isatools environment activation script has been removed as we no longer use isatools

    # Combined launcher script with better environment handling
    cat > science_data_kit.sh << 'EOF'
#!/bin/bash
# Science Data Kit Launcher
echo "Science Data Kit Environment Launcher"
echo "======================================"
echo "Launching main environment (Python 3.12+)"
echo ""

# Function to properly deactivate environments
deactivate_all() {
    # Deactivate conda if active
    if [ -n "$CONDA_DEFAULT_ENV" ]; then
        echo "Deactivating conda environment: $CONDA_DEFAULT_ENV"
        conda deactivate 2>/dev/null || true
    fi

    # Deactivate virtualenv if active
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Deactivating virtual environment: $VIRTUAL_ENV"
        deactivate 2>/dev/null || true
    fi
}

if [ -d "science-data-kit-env" ]; then
    echo "Starting main environment..."
    deactivate_all
    source science-data-kit-env/bin/activate
    echo "Main environment active ($(python --version))"
    exec bash --rcfile <(echo "PS1='(science-data-kit) \u@\h:\w\$ '")
else
    echo "No environments found. Please run the installer first."
    exit 1
fi
EOF
    chmod +x science_data_kit.sh

    # Create a test script to verify environments
    cat > test_environments.sh << 'EOF'
#!/bin/bash
echo "Testing Science Data Kit Environments"
echo "===================================="

echo ""
echo "Testing main environment..."
if [ -d "science-data-kit-env" ]; then
    source science-data-kit-env/bin/activate
    echo "Main environment Python: $(python --version)"
    echo "Main environment location: $(which python)"
    deactivate
else
    echo "Main environment not found!"
fi

echo ""
echo "Current system Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "Current system location: $(which python3 2>/dev/null || echo 'Not found')"
EOF
    chmod +x test_environments.sh

    print_message $GREEN "Wrapper scripts created"
    print_message $YELLOW "Run './test_environments.sh' to verify your environments"
}

# Main installation function
main() {
    print_message $BLUE "=== Science Data Kit Multi-Environment Setup ==="

    # Ensure virtualenv is available
    ensure_virtualenv

    # Setup Python versions
    setup_python_versions

    # Create main environment
    setup_main_environment

    # Note: isatools has been removed from the codebase
    print_message $GREEN "The Science Data Kit now uses Neo4j's neosemantics (n10s) plugin for ontology integration"
    print_message $GREEN "No additional installation steps are required for ontology support"

    # Create wrapper scripts
    create_wrapper_scripts

    print_message $GREEN "=== Installation Complete ==="
    print_message $GREEN "Environment has been created:"
    print_message $YELLOW "  Main: ./activate_main.sh (Python $($MAIN_PYTHON_CMD --version 2>&1))"
    print_message $YELLOW "    - Contains Science Data Kit and all dependencies"
    print_message $YELLOW "    - Use this for all Science Data Kit workflows"
    print_message $YELLOW "  Launcher: ./science_data_kit.sh"

    print_message $BLUE "Quick start:"
    print_message $YELLOW "  ./science_data_kit.sh          # Launch Science Data Kit environment"

    print_message $BLUE "Features:"
    print_message $YELLOW "  • Science Data Kit requires Python 3.12+ for modern features"
    print_message $YELLOW "  • Ontology integration using Neo4j's neosemantics (n10s) plugin"
    print_message $YELLOW "  • Support for various RDF formats (OWL, Turtle, RDF/XML, JSON-LD)"
}

# Run main function
main "$@"

#!/bin/bash

# install.sh - Robust installer for science-data-kit
# Handles Python installation across different platforms

set -e  # Exit on any error

PACKAGE_NAME="science-data-kit"
PYTHON_MIN_VERSION="3.12"
PYTHON_MAX_VERSION="3.13"
VENV_NAME="${PACKAGE_NAME}-env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing ${PACKAGE_NAME}...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    if command_exists "$python_cmd"; then
        local version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local major_minor=$(echo $version | cut -d. -f1-2)
        
        # Check if version is 3.12 or 3.13
        if [ "$major_minor" = "3.12" ] || [ "$major_minor" = "3.13" ]; then
            echo "$python_cmd"
            return 0
        fi
    fi
    return 1
}

# Function to install Python on different platforms
install_python() {
    echo -e "${YELLOW}Installing Python ${PYTHON_MIN_VERSION} or ${PYTHON_MAX_VERSION}...${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu - try to install both versions, system will pick what's available
            echo "Detected Debian/Ubuntu system"
            
            # Handle apt_pkg issues gracefully
            echo "Updating package lists..."
            if ! sudo apt-get update 2>/dev/null; then
                echo -e "${YELLOW}Warning: apt update had some issues, but continuing...${NC}"
                # Try to fix common apt_pkg issues
                sudo apt-get install --reinstall python3-apt 2>/dev/null || true
            fi
            
            # Try deadsnakes PPA for newer Python versions
            if ! apt-cache show python3.13 >/dev/null 2>&1 && ! apt-cache show python3.12 >/dev/null 2>&1; then
                echo "Adding deadsnakes PPA for Python 3.12/3.13..."
                sudo apt-get install -y software-properties-common || {
                    echo -e "${RED}Failed to install software-properties-common${NC}"
                    exit 1
                }
                
                # Add PPA with error handling
                if sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null; then
                    echo "Successfully added deadsnakes PPA"
                    sudo apt-get update 2>/dev/null || echo -e "${YELLOW}Update had warnings but continuing...${NC}"
                else
                    echo -e "${YELLOW}Failed to add deadsnakes PPA, trying manual method...${NC}"
                    # Manual PPA addition as fallback
                    echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list
                    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 2>/dev/null || true
                    sudo apt-get update 2>/dev/null || echo -e "${YELLOW}Update had warnings but continuing...${NC}"
                fi
            fi
            # Try to install 3.13 first, fall back to 3.12
            PYTHON_INSTALLED=false
            if apt-cache show python3.13 >/dev/null 2>&1; then
                echo "Installing Python 3.13..."
                if sudo apt-get install -y python3.13 python3.13-venv python3.13-dev 2>/dev/null; then
                    PYTHON_INSTALLED=true
                    # Try to install pip for 3.13
                    sudo apt-get install -y python3.13-pip 2>/dev/null || {
                        echo "pip not available via apt, will install via get-pip.py later"
                    }
                fi
            fi
            
            if [ "$PYTHON_INSTALLED" = false ] && apt-cache show python3.12 >/dev/null 2>&1; then
                echo "Installing Python 3.12..."
                if sudo apt-get install -y python3.12 python3.12-venv python3.12-dev 2>/dev/null; then
                    PYTHON_INSTALLED=true
                    # Try to install pip for 3.12
                    sudo apt-get install -y python3.12-pip 2>/dev/null || {
                        echo "pip not available via apt, will install via get-pip.py later"
                    }
                fi
            fi
            
            if [ "$PYTHON_INSTALLED" = false ]; then
                echo -e "${RED}Failed to install Python 3.12 or 3.13 from repositories.${NC}"
                echo "You may need to:"
                echo "1. Fix the apt_pkg issue: sudo apt-get install --reinstall python3-apt"
                echo "2. Or install Python manually from https://python.org/downloads/"
                echo "3. Or use pyenv: curl https://pyenv.run | bash"
                exit 1
            fi
        elif command_exists yum; then
            # RHEL/CentOS
            echo "Detected RHEL/CentOS system"
            echo -e "${YELLOW}Note: You may need to enable EPEL repository for newer Python versions${NC}"
            if yum list available | grep -q python313; then
                sudo yum install -y python313 python313-pip python313-devel
            elif yum list available | grep -q python312; then
                sudo yum install -y python312 python312-pip python312-devel
            else
                echo -e "${RED}Python 3.12/3.13 not available in repositories. Consider using pyenv.${NC}"
                exit 1
            fi
        elif command_exists dnf; then
            # Fedora
            echo "Detected Fedora system"
            if dnf list available | grep -q python3.13; then
                sudo dnf install -y python3.13 python3.13-pip python3.13-devel
            elif dnf list available | grep -q python3.12; then
                sudo dnf install -y python3.12 python3.12-pip python3.12-devel
            else
                echo -e "${RED}Python 3.12/3.13 not available. Try: sudo dnf install python3 python3-pip${NC}"
                exit 1
            fi
        elif command_exists pacman; then
            # Arch Linux (usually has latest Python)
            echo "Detected Arch Linux system"
            sudo pacman -S --noconfirm python python-pip python-virtualenv
        else
            echo -e "${RED}Unsupported Linux distribution.${NC}"
            echo "Please install Python 3.12 or 3.13 manually, or consider using pyenv:"
            echo "curl https://pyenv.run | bash"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Detected macOS system"
        if command_exists brew; then
            # Try to install Python 3.13, fall back to 3.12
            if brew list --formula | grep -q python@3.13; then
                brew install python@3.13
            elif brew list --formula | grep -q python@3.12; then
                brew install python@3.12
            else
                echo "Installing latest Python (should be 3.12+)..."
                brew install python
            fi
        else
            echo -e "${RED}Homebrew not found. Please install Homebrew first:${NC}"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "Or install Python 3.12/3.13 from https://python.org/downloads/"
            exit 1
        fi
    else
        echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
        echo "Please install Python 3.12 or 3.13 manually from https://python.org/downloads/"
        exit 1
    fi
}

# Find suitable Python command
PYTHON_CMD=""
for cmd in python3.13 python3.12 python3 python; do
    if PYTHON_CMD=$(check_python_version "$cmd"); then
        break
    fi
done

# If no suitable Python found, try to install it
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}No suitable Python version found (need 3.12 or 3.13). Attempting to install...${NC}"
    install_python
    
    # Check again after installation
    for cmd in python3.13 python3.12 python3 python; do
        if PYTHON_CMD=$(check_python_version "$cmd"); then
            break
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        echo -e "${RED}Failed to install suitable Python version.${NC}"
        echo "Please install Python 3.12 or 3.13 manually from https://python.org/downloads/"
        echo "Or consider using pyenv: curl https://pyenv.run | bash"
        exit 1
    fi
fi

echo -e "${GREEN}Using Python: $PYTHON_CMD${NC}"
$PYTHON_CMD --version

# Check if venv module is available
if ! $PYTHON_CMD -m venv --help >/dev/null 2>&1; then
    echo -e "${RED}Python venv module not available. Installing...${NC}"
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
if [ -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf "$VENV_NAME"
fi

# Create virtual environment
echo -e "${GREEN}Creating virtual environment: $VENV_NAME${NC}"
$PYTHON_CMD -m venv "$VENV_NAME"

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source "$VENV_NAME/Scripts/activate"
else
    source "$VENV_NAME/bin/activate"
fi

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install the package
echo -e "${GREEN}Installing ${PACKAGE_NAME}...${NC}"

# Check if we're in development mode (package doesn't exist on PyPI yet)
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    echo "Found local package files, installing in development mode..."
    pip install -e .
elif [ "$1" = "--test" ]; then
    echo "Test mode: Installing a real package (numpy) to verify setup..."
    pip install numpy
    echo "Test installation successful! Your environment is ready."
else
    # Try to install from PyPI
    if ! pip install "$PACKAGE_NAME"; then
        echo -e "${YELLOW}Package '${PACKAGE_NAME}' not found on PyPI.${NC}"
        echo "This is normal if you're still developing the package."
        echo ""
        echo "Options:"
        echo "1. If you have setup.py/pyproject.toml in this directory:"
        echo "   pip install -e ."
        echo ""
        echo "2. To test the environment setup:"
        echo "   ./install.sh --test"
        echo ""
        echo "3. Once your package is published to PyPI, this will work automatically."
        echo ""
        echo "The Python environment is ready for development!"
    fi
fi

# Test installation
echo -e "${GREEN}Testing installation...${NC}"
if command_exists "$PACKAGE_NAME"; then
    $PACKAGE_NAME --version
    echo -e "${GREEN}✓ Installation successful!${NC}"
elif [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    echo -e "${GREEN}✓ Development environment ready!${NC}"
elif [ "$1" = "--test" ]; then
    python -c "import numpy; print(f'✓ Test successful! Python {python.__version__} with numpy {numpy.__version__}')" 2>/dev/null && echo -e "${GREEN}✓ Environment setup successful!${NC}" || echo -e "${YELLOW}Environment ready for package development${NC}"
else
    echo -e "${YELLOW}Package not installed but environment is ready for development.${NC}"
fi

# Detect user's shell for activation instructions
USER_SHELL=""
if [ -n "$FISH_VERSION" ]; then
    USER_SHELL="fish"
elif [ -n "$ZSH_VERSION" ]; then
    USER_SHELL="zsh"
elif [ -n "$BASH_VERSION" ]; then
    USER_SHELL="bash"
else
    # Try to detect from SHELL environment variable
    case "$SHELL" in
        */fish) USER_SHELL="fish" ;;
        */zsh) USER_SHELL="zsh" ;;
        */bash) USER_SHELL="bash" ;;
        *) USER_SHELL="bash" ;;  # Default fallback
    esac
fi

# Provide usage instructions
echo ""
echo -e "${GREEN}=== Usage Instructions ===${NC}"
echo "To use ${PACKAGE_NAME}, first activate the virtual environment:"
echo ""

case "$USER_SHELL" in
    fish)
        echo "  source ${VENV_NAME}/bin/activate.fish"
        ;;
    *)
        echo "  source ${VENV_NAME}/bin/activate"
        ;;
esac

echo ""
echo "Then run your commands:"
echo "  ${PACKAGE_NAME} --help"
echo ""
echo "To deactivate the environment when done:"
echo "  deactivate"
echo ""

# Show instructions for other shells if not detected correctly
if [ "$USER_SHELL" != "fish" ]; then
    echo -e "${YELLOW}Note: If you're using fish shell, use:${NC}"
    echo "  source ${VENV_NAME}/bin/activate.fish"
    echo ""
fi

echo -e "${GREEN}Happy analyzing!${NC}"
#!/bin/bash

# install.sh - Robust installer for science-data-kit
# Handles Python installation across different platforms

set -e  # Exit on any error

PACKAGE_NAME="science-data-kit"
PYTHON_MIN_VERSION="3.12"
PYTHON_MAX_VERSION="3.13"
VENV_NAME="${PACKAGE_NAME}-env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing ${PACKAGE_NAME}...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    if command_exists "$python_cmd"; then
        local version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        local major_minor=$(echo $version | cut -d. -f1-2)
        
        # Check if version is 3.12 or 3.13
        if [ "$major_minor" = "3.12" ] || [ "$major_minor" = "3.13" ]; then
            echo "$python_cmd"
            return 0
        fi
    fi
    return 1
}

# Function to install Python on different platforms
install_python() {
    echo -e "${YELLOW}Installing Python ${PYTHON_MIN_VERSION} or ${PYTHON_MAX_VERSION}...${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu - try to install both versions, system will pick what's available
            echo "Detected Debian/Ubuntu system"
            
            # Handle apt_pkg issues gracefully
            echo "Updating package lists..."
            if ! sudo apt-get update 2>/dev/null; then
                echo -e "${YELLOW}Warning: apt update had some issues, but continuing...${NC}"
                # Try to fix common apt_pkg issues
                sudo apt-get install --reinstall python3-apt 2>/dev/null || true
            fi
            
            # Try deadsnakes PPA for newer Python versions
            if ! apt-cache show python3.13 >/dev/null 2>&1 && ! apt-cache show python3.12 >/dev/null 2>&1; then
                echo "Adding deadsnakes PPA for Python 3.12/3.13..."
                sudo apt-get install -y software-properties-common || {
                    echo -e "${RED}Failed to install software-properties-common${NC}"
                    exit 1
                }
                
                # Add PPA with error handling
                if sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null; then
                    echo "Successfully added deadsnakes PPA"
                    sudo apt-get update 2>/dev/null || echo -e "${YELLOW}Update had warnings but continuing...${NC}"
                else
                    echo -e "${YELLOW}Failed to add deadsnakes PPA, trying manual method...${NC}"
                    # Manual PPA addition as fallback
                    echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list
                    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 2>/dev/null || true
                    sudo apt-get update 2>/dev/null || echo -e "${YELLOW}Update had warnings but continuing...${NC}"
                fi
            fi
            # Try to install 3.13 first, fall back to 3.12
            PYTHON_INSTALLED=false
            if apt-cache show python3.13 >/dev/null 2>&1; then
                echo "Installing Python 3.13..."
                if sudo apt-get install -y python3.13 python3.13-venv python3.13-dev 2>/dev/null; then
                    PYTHON_INSTALLED=true
                    # Try to install pip for 3.13
                    sudo apt-get install -y python3.13-pip 2>/dev/null || {
                        echo "pip not available via apt, will install via get-pip.py later"
                    }
                fi
            fi
            
            if [ "$PYTHON_INSTALLED" = false ] && apt-cache show python3.12 >/dev/null 2>&1; then
                echo "Installing Python 3.12..."
                if sudo apt-get install -y python3.12 python3.12-venv python3.12-dev 2>/dev/null; then
                    PYTHON_INSTALLED=true
                    # Try to install pip for 3.12
                    sudo apt-get install -y python3.12-pip 2>/dev/null || {
                        echo "pip not available via apt, will install via get-pip.py later"
                    }
                fi
            fi
            
            if [ "$PYTHON_INSTALLED" = false ]; then
                echo -e "${RED}Failed to install Python 3.12 or 3.13 from repositories.${NC}"
                echo "You may need to:"
                echo "1. Fix the apt_pkg issue: sudo apt-get install --reinstall python3-apt"
                echo "2. Or install Python manually from https://python.org/downloads/"
                echo "3. Or use pyenv: curl https://pyenv.run | bash"
                exit 1
            fi
        elif command_exists yum; then
            # RHEL/CentOS
            echo "Detected RHEL/CentOS system"
            echo -e "${YELLOW}Note: You may need to enable EPEL repository for newer Python versions${NC}"
            if yum list available | grep -q python313; then
                sudo yum install -y python313 python313-pip python313-devel
            elif yum list available | grep -q python312; then
                sudo yum install -y python312 python312-pip python312-devel
            else
                echo -e "${RED}Python 3.12/3.13 not available in repositories. Consider using pyenv.${NC}"
                exit 1
            fi
        elif command_exists dnf; then
            # Fedora
            echo "Detected Fedora system"
            if dnf list available | grep -q python3.13; then
                sudo dnf install -y python3.13 python3.13-pip python3.13-devel
            elif dnf list available | grep -q python3.12; then
                sudo dnf install -y python3.12 python3.12-pip python3.12-devel
            else
                echo -e "${RED}Python 3.12/3.13 not available. Try: sudo dnf install python3 python3-pip${NC}"
                exit 1
            fi
        elif command_exists pacman; then
            # Arch Linux (usually has latest Python)
            echo "Detected Arch Linux system"
            sudo pacman -S --noconfirm python python-pip python-virtualenv
        else
            echo -e "${RED}Unsupported Linux distribution.${NC}"
            echo "Please install Python 3.12 or 3.13 manually, or consider using pyenv:"
            echo "curl https://pyenv.run | bash"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Detected macOS system"
        if command_exists brew; then
            # Try to install Python 3.13, fall back to 3.12
            if brew list --formula | grep -q python@3.13; then
                brew install python@3.13
            elif brew list --formula | grep -q python@3.12; then
                brew install python@3.12
            else
                echo "Installing latest Python (should be 3.12+)..."
                brew install python
            fi
        else
            echo -e "${RED}Homebrew not found. Please install Homebrew first:${NC}"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "Or install Python 3.12/3.13 from https://python.org/downloads/"
            exit 1
        fi
    else
        echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
        echo "Please install Python 3.12 or 3.13 manually from https://python.org/downloads/"
        exit 1
    fi
}

# Find suitable Python command
PYTHON_CMD=""
for cmd in python3.13 python3.12 python3 python; do
    if PYTHON_CMD=$(check_python_version "$cmd"); then
        break
    fi
done

# If no suitable Python found, try to install it
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}No suitable Python version found (need 3.12 or 3.13). Attempting to install...${NC}"
    install_python
    
    # Check again after installation
    for cmd in python3.13 python3.12 python3 python; do
        if PYTHON_CMD=$(check_python_version "$cmd"); then
            break
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        echo -e "${RED}Failed to install suitable Python version.${NC}"
        echo "Please install Python 3.12 or 3.13 manually from https://python.org/downloads/"
        echo "Or consider using pyenv: curl https://pyenv.run | bash"
        exit 1
    fi
fi

echo -e "${GREEN}Using Python: $PYTHON_CMD${NC}"
$PYTHON_CMD --version

# Check if venv module is available
if ! $PYTHON_CMD -m venv --help >/dev/null 2>&1; then
    echo -e "${RED}Python venv module not available. Installing...${NC}"
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
if [ -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf "$VENV_NAME"
fi

# Create virtual environment
echo -e "${GREEN}Creating virtual environment: $VENV_NAME${NC}"
$PYTHON_CMD -m venv "$VENV_NAME"

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source "$VENV_NAME/Scripts/activate"
else
    source "$VENV_NAME/bin/activate"
fi

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install the package
echo -e "${GREEN}Installing ${PACKAGE_NAME}...${NC}"
pip install "$PACKAGE_NAME"

# Test installation
echo -e "${GREEN}Testing installation...${NC}"
if command_exists "$PACKAGE_NAME"; then
    $PACKAGE_NAME --version
    echo -e "${GREEN}✓ Installation successful!${NC}"
else
    echo -e "${YELLOW}Package installed but command not found. You may need to activate the environment first.${NC}"
fi

# Detect user's shell for activation instructions
USER_SHELL=""
if [ -n "$FISH_VERSION" ]; then
    USER_SHELL="fish"
elif [ -n "$ZSH_VERSION" ]; then
    USER_SHELL="zsh"
elif [ -n "$BASH_VERSION" ]; then
    USER_SHELL="bash"
else
    # Try to detect from SHELL environment variable
    case "$SHELL" in
        */fish) USER_SHELL="fish" ;;
        */zsh) USER_SHELL="zsh" ;;
        */bash) USER_SHELL="bash" ;;
        *) USER_SHELL="bash" ;;  # Default fallback
    esac
fi

# Provide usage instructions
echo ""
echo -e "${GREEN}=== Usage Instructions ===${NC}"
echo "To use ${PACKAGE_NAME}, first activate the virtual environment:"
echo ""

case "$USER_SHELL" in
    fish)
        echo "  source ${VENV_NAME}/bin/activate.fish"
        ;;
    *)
        echo "  source ${VENV_NAME}/bin/activate"
        ;;
esac

echo ""
echo "Then run your commands:"
echo "  ${PACKAGE_NAME} --help"
echo ""
echo "To deactivate the environment when done:"
echo "  deactivate"
echo ""

# Show instructions for other shells if not detected correctly
if [ "$USER_SHELL" != "fish" ]; then
    echo -e "${YELLOW}Note: If you're using fish shell, use:${NC}"
    echo "  source ${VENV_NAME}/bin/activate.fish"
    echo ""
fi

echo -e "${GREEN}Happy analyzing!${NC}"

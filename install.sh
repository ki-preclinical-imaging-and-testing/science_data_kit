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

# Install Python (platform-specific)
install_python() {
    print_message $BLUE "Installing Python 3.12..."

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu
            print_message $BLUE "Detected Debian/Ubuntu system"

            # Try direct installation first without PPA if Python 3.12 is already available
            if sudo apt-get install -y python3.12 python3.12-venv python3.12-dev; then
                print_message $GREEN "Python 3.12 installed successfully without adding PPA"
                PYTHON_VERSION="3.12"
            else
                print_message $BLUE "Adding deadsnakes PPA for Python installation..."

                # Check for apt_pkg and set up workarounds if needed
                fix_apt_pkg

                # If we're in direct installation mode, skip the PPA setup
                if [ "${DIRECT_INSTALL:-0}" = "1" ]; then
                    print_message $YELLOW "Skipping PPA setup, trying direct installation..."
                else
                    sudo apt-get update || true
                    sudo apt-get install -y software-properties-common

                    # If APT_PKG_UNAVAILABLE is set or add-apt-repository fails, use the manual approach
                    if [ "${APT_PKG_UNAVAILABLE:-0}" = "1" ] || ! sudo add-apt-repository -y ppa:deadsnakes/ppa; then
                        print_message $YELLOW "add-apt-repository failed. Adding PPA manually..."

                        # Get Ubuntu codename, with fallback if lsb_release fails
                        UBUNTU_CODENAME=$(lsb_release -cs 2>/dev/null || grep -oP 'VERSION_CODENAME=\K\w+' /etc/os-release 2>/dev/null || echo "jammy")
                        print_message $YELLOW "Detected Ubuntu codename: $UBUNTU_CODENAME"

                        echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu $UBUNTU_CODENAME main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list

                        # Use multiple methods to add the key, trying each until one works
                        print_message $YELLOW "Adding deadsnakes PPA key..."

                        # Method 1: Direct download from Ubuntu key server
                        if ! curl -fsSL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF23C5A6CF475977595C89F51BA6932366A755776" | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/deadsnakes.gpg 2>/dev/null; then
                            print_message $YELLOW "Method 1 failed. Trying alternative key import method..."

                            # Method 2: Use apt-key (deprecated but might work)
                            if ! sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 2>/dev/null; then
                                print_message $YELLOW "Method 2 failed. Trying alternative key import method..."

                                # Method 3: Use direct key data
                                print_message $YELLOW "Using hardcoded key data as fallback..."
                                # This is the deadsnakes PPA key in base64 format
                                echo "mQINBFTlMNUBEADDLj7FrRzRpYN8cRo5FQeOj7Z5V6Y/6uZL886yKbCgLRkOvGqnRqpXoLzFXBMIrLR/w4INOlCiIjPQX+X1AuLaAH9SQ0HyKFG+cZ3zx/ZOFfRHvzI2IzLjYXLTRnKi6TmYKJQqMj/z3lbllR0GYqXTvUXgFfJJyHzCxaXAOHQHAZCZQTK5FT4UQXjQkLZYQ4Jw9WdYBs6JF98GgwUNxwZnEcnZeiILJ2z8ZtBXlGKsdf4dJUJLVWUUi76UNKLCKqLNEX7imGZRZNW0EYFWsQlYXjOglnVZacsVs6XrQVZU8xWI3iz5WyGMQeBSMZGPkMJFpu+ZuNPk0ftpQnwILF9uxJEPW41O9Dj1AJn9S8GJL0YJIbE7FJJ1ucQTKuFY8QU+AwLOXs8RsXOKUkHMP0g7ARvZZRX8rNBUuGCdF/AUY8cPjVOCVGnLLJl0Cz1qhKkQQOUS/8YEjlZPJMsKvMtGQnSUJK8zXgkxZLiOjbUKXPdEkP9ftJVV8ZU0aUPLFM6UX9kKbPLM3KS2XE7uICzXYXdz3yNYUvTFEXnGHBPsRrLuN5y1vLcPU/bK4CzuCQMnWJ5aZj2uQie8wuHUy1uMZEJLjLzR4sGVlU4HRXbZjGOy2CuQQUYZJLLXI6ULnLJQtj6wJf9ZO/ItD4cUmEqTWz+/vyCUgSZzQzDgj3NIWpuCWpvv+QV/XdRIJZs1aMdmBOJKqpkJE3ts9Mv0uHbdWCUiMz2JsPKEYvQFpi0HxiQ/YpCQOQIDAQABtB9MYXVuY2hwYWQgUFBBIGZvciBkZWFkc25ha2VzIFBQQYkCOAQTAQIAIgUCVOUw1QIbAwYLCQgHAwIGFQgCCQoLBBYCAwECHgECF4AACgkQumkjZmrXV3ZdORAAwRXYrt1IveFAHhNWJbzGkGTUZ2eWTb/JZ/4qKjKYNsLELtYkUTEYQH9oJUVe9JtSGBRCWLZ9UYzGEPjTyPTFQtjYmL6sn6KZEpCxEHyMIHKBCLJVXPqxdSQYgW6y1aMQcJYLHcKd4s1ceFpQIHxijpxWs5JKbVBkv/QCPB8N8CCCRiZKwSBPTJ98G5uO1/IYPDpFkVeFBQTT6XA2UUZXiJwlIRDQWFZCAtEBU6C2xGmqVoGRWKn+LXXn2E4KzfTsOjXYUBCQvhgqmwm18R7apeTjbHFqjBWxHGIv02WCT9xJNUL+8iBKp2y+c6LqbgOy0/YJMXxmVMrfWsL6YxvMTHGQlbjtjieZUqEyMtOUdvwmPeEQE/Ap9JwKWMhQFRKKAXF2PVOdgLEz/nANwIZJwpvuQdMKmgZPvXpWHaKBFxJZhEfBvAYMYZEsAKgCELHEGGVlxzKnFSZYNkYOsYHmrYgLDQHRiXwQXbF8tNDjPgj+Xj5hEXDR4T+UMrUmKnf/qbLUJKClZJl92xAGVCy+JCN/hqVxXxGGZRHUHzUVJdvuJHQjQXLBYEgGnfaA8Vk9ypqLMn0phD3VGVQUgGh6jRJZMcbqMn3YTh7M1r1WdAJlqxTZMFq8mSCnmIaRFrCpIUEwD4ZFOEUCAwEAAQ==" | base64 -d | sudo tee /etc/apt/trusted.gpg.d/deadsnakes.gpg >/dev/null

                                # Check if the key was added successfully
                                if [ ! -s /etc/apt/trusted.gpg.d/deadsnakes.gpg ]; then
                                    print_message $YELLOW "All key import methods failed. Continuing without key verification..."
                                    print_message $YELLOW "You may see warnings about unauthenticated packages."
                                else
                                    print_message $GREEN "PPA key added successfully using fallback method."
                                fi
                            else
                                print_message $GREEN "PPA key added successfully using apt-key."
                            fi
                        else
                            print_message $GREEN "PPA key added successfully using direct download."
                        fi
                    fi
                fi
            fi
            sudo apt-get update || true

            # If we haven't already installed Python 3.12 directly
            if [ -z "$PYTHON_VERSION" ]; then
                # Try to install Python 3.12 first, then fall back to 3.11, then 3.10
                # Use a direct approach if apt-cache might fail due to apt_pkg issues
                if [ "${APT_PKG_UNAVAILABLE:-0}" = "1" ] || [ "${DIRECT_INSTALL:-0}" = "1" ]; then
                    print_message $YELLOW "Using direct Python installation approach..."

                    # Try Python 3.12 first
                    if sudo apt-get install -y python3.12 python3.12-venv python3.12-dev; then
                        print_message $GREEN "Python 3.12 installed successfully"
                        PYTHON_VERSION="3.12"
                    # Then try Python 3.11
                    elif sudo apt-get install -y python3.11 python3.11-venv python3.11-dev; then
                        print_message $GREEN "Python 3.11 installed successfully"
                        PYTHON_VERSION="3.11"
                    # Finally try Python 3.10
                    elif sudo apt-get install -y python3.10 python3.10-venv python3.10-dev; then
                        print_message $GREEN "Python 3.10 installed successfully"
                        PYTHON_VERSION="3.10"
                    else
                        print_message $RED "Failed to install Python. Please install Python 3.12+ manually."
                        return 1
                    fi
                else
                    # Normal approach using apt-cache
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
                fi
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

    # Check for Python 3.12+
    # First, try to find Python 3.12 in common locations
    python312_paths=("python3.12" "/usr/bin/python3.12" "/usr/local/bin/python3.12" "$HOME/.pyenv/shims/python3.12")
    python312_path=""

    for path in "${python312_paths[@]}"; do
        if command -v "$path" &>/dev/null; then
            python312_path="$path"
            python_version=$("$path" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            print_message $GREEN "Found Python $python_version at $python312_path"
            export PYTHON_PATH="$python312_path"
            break
        fi
    done

    # If Python 3.12 wasn't found in common locations, check the default python3
    if [ -z "$python312_path" ] && command_exists python3; then
        python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        python_major=$(echo $python_version | cut -d. -f1)
        python_minor=$(echo $python_version | cut -d. -f2)

        if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 12 ]; then
            python312_path="python3"
            print_message $GREEN "Found Python $python_version"
            export PYTHON_PATH="$python312_path"
        fi
    fi

    # If Python 3.12+ wasn't found, offer to install it
    if [ -z "$python312_path" ]; then
        if command_exists python3; then
            python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            print_message $RED "Error: Python 3.12 or higher is required (found $python_version)"
        else
            print_message $RED "Error: Python 3 not found"
        fi

        print_message $YELLOW "Would you like to install Python 3.12? (y/n)"
        read -r install_python_choice
        if [[ "$install_python_choice" =~ ^[Yy]$ ]]; then
            install_python

            # After installation, try to find Python 3.12 again
            for path in "${python312_paths[@]}"; do
                if command -v "$path" &>/dev/null; then
                    python312_path="$path"
                    python_version=$("$path" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
                    print_message $GREEN "Found Python $python_version at $python312_path"
                    export PYTHON_PATH="$python312_path"
                    break
                fi
            done

            # If still not found, check default python3
            if [ -z "$python312_path" ] && command_exists python3; then
                python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
                python_major=$(echo $python_version | cut -d. -f1)
                python_minor=$(echo $python_version | cut -d. -f2)

                if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 12 ]; then
                    python312_path="python3"
                    print_message $GREEN "Found Python $python_version"
                    export PYTHON_PATH="$python312_path"
                fi
            fi

            # If still not found, exit
            if [ -z "$python312_path" ]; then
                print_message $RED "Python 3.12+ installation failed or not found."
                print_message $YELLOW "Please install Python 3.12 or higher manually before continuing."
                exit 1
            fi
        else
            print_message $YELLOW "Please install Python 3.12 or higher before continuing."
            exit 1
        fi
    fi

    # We'll check for pip after setting up the virtual environment
    # This ensures we're using the pip from the virtual environment

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

    # Use the Python 3.12+ path found in check_dependencies
    if [ -n "${PYTHON_PATH}" ]; then
        python3="${PYTHON_PATH}"
        python_version=$("$python3" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        print_message $GREEN "Using Python $python_version at $python3"
    else
        print_message $RED "Python 3.12+ path not found. This should not happen."
        print_message $YELLOW "Trying to use system python3 as fallback..."
        python3="python3"
    fi

    # Check if venv module is available
    if ! $python3 -c "import venv" &>/dev/null; then
        print_message $YELLOW "Python venv module not found. Installing venv module..."

        # Get Python version for specific package installation
        python_version=$($python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

        if command_exists apt-get; then
            # Fix apt_pkg module error
            fix_apt_pkg

            print_message $BLUE "Attempting to install python${python_version}-venv package..."
            sudo apt-get update || true
            if ! sudo apt-get install -y python${python_version}-venv; then
                print_message $YELLOW "Failed to install python${python_version}-venv. Trying python3-venv instead..."

                # Fix apt_pkg module error again before next apt-get
                fix_apt_pkg

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

    # Always create a fresh virtual environment in the repository
    VENV_DIR=".venv"

    # Remove existing virtual environment if it exists
    if [ -d "$VENV_DIR" ]; then
        print_message $YELLOW "Found existing virtual environment in ./$VENV_DIR"
        print_message $YELLOW "Removing it to create a fresh one..."
        rm -rf "$VENV_DIR"
    fi

    # Create a new virtual environment
    print_message $BLUE "Creating virtual environment in ./$VENV_DIR with Python 3.12+..."
    if ! $python3 -m venv "$VENV_DIR"; then
        print_message $RED "Failed to create virtual environment."
        print_message $YELLOW "If you're using Python 3.12+, make sure python3-venv or equivalent is installed."
        print_message $YELLOW "You can try: sudo apt-get install python3-venv"
        print_message $YELLOW "Or for specific Python version: sudo apt-get install python3.12-venv"
        exit 1
    fi

    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
    print_message $GREEN "Created virtual environment in ./$VENV_DIR using $python3"

    # Activate virtual environment
    if [ -f "$ACTIVATE_SCRIPT" ]; then
        source "$ACTIVATE_SCRIPT"
        print_message $GREEN "Activated virtual environment from $ACTIVATE_SCRIPT"
    else
        print_message $RED "Virtual environment activate script not found at $ACTIVATE_SCRIPT"
        print_message $RED "Installation cannot continue."
        exit 1
    fi

    # Check for pip in the virtual environment
    if ! command -v pip &>/dev/null; then
        print_message $RED "Error: pip not found in virtual environment"
        print_message $YELLOW "Installing pip in the virtual environment..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | python
    else
        print_message $GREEN "Found pip in virtual environment"
        # Upgrade pip
        pip install --upgrade pip
    fi

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
    print_message $GREEN "To start Science Data Kit, run:"
    print_message $YELLOW "source $ACTIVATE_SCRIPT"
    print_message $YELLOW "science_data_kit"

    # Optional: Install isatools
    print_message $BLUE "Would you like to install isatools? (y/n)"
    read -r install_isatools
    if [[ "$install_isatools" =~ ^[Yy]$ ]]; then
        print_message $BLUE "Which version of isatools would you like to install?"
        print_message $YELLOW "1) Basic isatools (Python 3.12+, limited functionality)"
        print_message $YELLOW "   - Compatible with Python 3.12+"
        print_message $YELLOW "   - Recommended for newer Python versions"
        print_message $YELLOW "2) Full isatools (Python 3.9, complete functionality)"
        print_message $YELLOW "   - Includes mzML file processing capabilities"
        print_message $YELLOW "   - Requires Python 3.9 (will create a separate environment)"
        read -r isatools_version

        if [ "$isatools_version" -eq 1 ]; then
            # We're already in a Python 3.12+ virtual environment
            python_version=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            print_message $BLUE "Installing basic isatools in virtual environment (Python $python_version)..."
            pip install -e .[isatools]
            print_message $GREEN "Basic isatools installed successfully"
            print_message $BLUE "Running Python 3.12+ compatibility script..."
            python install_isatools_py312.py
        elif [ "$isatools_version" -eq 2 ]; then
            print_message $BLUE "Installing full isatools for Python 3.9..."
            print_message $YELLOW "This will create a separate Python 3.9 environment."
            if command_exists conda; then
                bash install_isatools.sh
            else
                # Use the system Python for this script since it will create its own environment
                /usr/bin/python3 install_isatools.py
            fi
            print_message $GREEN "Full isatools installed successfully"
        else
            print_message $RED "Invalid option. Skipping isatools installation."
        fi
    fi
}

# Run the main function
main

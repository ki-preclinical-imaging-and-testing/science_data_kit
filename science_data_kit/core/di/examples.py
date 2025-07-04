"""
Examples of using the Dependency Injection system in Science Data Kit

This module provides examples of how to use the dependency injection system,
including registering components, injecting dependencies, and using decorators.
"""

from typing import List, Optional, Protocol
from abc import ABC, abstractmethod

from .container import container
from .decorators import injectable, singleton, provides, singleton_provides, inject


# Example 1: Basic dependency injection with interfaces

class Logger(ABC):
    """Abstract base class for loggers."""
    
    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message."""
        pass


class ConsoleLogger(Logger):
    """Logger implementation that logs to the console."""
    
    def log(self, message: str) -> None:
        """Log a message to the console."""
        print(f"[LOG] {message}")


class FileLogger(Logger):
    """Logger implementation that logs to a file."""
    
    def __init__(self, filename: str = "app.log"):
        """Initialize the file logger."""
        self.filename = filename
    
    def log(self, message: str) -> None:
        """Log a message to a file."""
        print(f"[FILE] Would write to {self.filename}: {message}")


class UserService:
    """Service for user operations."""
    
    def __init__(self, logger: Logger):
        """Initialize the user service with a logger."""
        self.logger = logger
    
    def create_user(self, username: str) -> None:
        """Create a new user."""
        self.logger.log(f"Creating user: {username}")


def example_basic_di():
    """Example of basic dependency injection with interfaces."""
    # Register the logger implementation
    container.register(Logger, ConsoleLogger)
    
    # Resolve the logger
    logger = container.resolve(Logger)
    logger.log("Hello from the resolved logger!")
    
    # Create a service with the injected logger
    user_service = UserService(logger)
    user_service.create_user("john_doe")
    
    # Change the logger implementation
    container.register(Logger, FileLogger)
    
    # Resolve the new logger
    logger = container.resolve(Logger)
    logger.log("Hello from the new logger!")
    
    # Create a service with the new logger
    user_service = UserService(logger)
    user_service.create_user("jane_doe")


# Example 2: Using decorators for dependency injection

@injectable
class ConfigService:
    """Service for configuration management."""
    
    def get_config(self, key: str, default: Optional[str] = None) -> str:
        """Get a configuration value."""
        # In a real implementation, this would read from a config file or database
        configs = {
            "app_name": "Science Data Kit",
            "version": "1.0.0",
        }
        return configs.get(key, default or "")


@singleton
class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        """Initialize the database service."""
        print("DatabaseService initialized (should only happen once)")
        self.connected = False
    
    def connect(self) -> None:
        """Connect to the database."""
        if not self.connected:
            print("Connecting to the database...")
            self.connected = True
        else:
            print("Already connected to the database")
    
    def query(self, sql: str) -> List[dict]:
        """Execute a query on the database."""
        if not self.connected:
            self.connect()
        print(f"Executing query: {sql}")
        return [{"id": 1, "name": "Example"}]


@provides(Logger)
class DebugLogger(Logger):
    """Logger implementation with debug information."""
    
    def log(self, message: str) -> None:
        """Log a message with debug information."""
        print(f"[DEBUG] {message}")


class ApplicationService:
    """Service for application operations."""
    
    @inject
    def __init__(self, config_service: ConfigService, db_service: DatabaseService, logger: Logger):
        """Initialize the application service with injected dependencies."""
        self.config_service = config_service
        self.db_service = db_service
        self.logger = logger
    
    def start(self) -> None:
        """Start the application."""
        app_name = self.config_service.get_config("app_name")
        self.logger.log(f"Starting application: {app_name}")
        self.db_service.connect()
        users = self.db_service.query("SELECT * FROM users")
        self.logger.log(f"Found {len(users)} users")


def example_decorator_di():
    """Example of using decorators for dependency injection."""
    # The decorators have already registered the components with the container
    
    # Create an application service with injected dependencies
    app_service = ApplicationService()
    app_service.start()
    
    # Create another instance to demonstrate singleton behavior
    another_app_service = ApplicationService()
    another_app_service.start()


# Example 3: Method injection

class ReportService:
    """Service for generating reports."""
    
    def __init__(self):
        """Initialize the report service."""
        pass
    
    @inject
    def generate_report(self, report_type: str, logger: Logger, db_service: DatabaseService) -> str:
        """Generate a report with injected dependencies."""
        logger.log(f"Generating {report_type} report")
        data = db_service.query(f"SELECT * FROM {report_type}")
        return f"Report: {report_type} with {len(data)} records"


def example_method_injection():
    """Example of method injection."""
    report_service = ReportService()
    report = report_service.generate_report("sales")
    print(report)


if __name__ == "__main__":
    print("\n=== Example 1: Basic Dependency Injection ===")
    example_basic_di()
    
    print("\n=== Example 2: Decorator-based Dependency Injection ===")
    example_decorator_di()
    
    print("\n=== Example 3: Method Injection ===")
    example_method_injection()
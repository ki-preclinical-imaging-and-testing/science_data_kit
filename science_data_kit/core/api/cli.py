"""
Command-Line Interface for Science Data Kit API

This module provides a command-line interface for interacting with the Science Data Kit API,
making it easy to perform common operations from the command line.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional

from .client import SDKClient, APIClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CLI:
    """Command-line interface for the Science Data Kit API."""

    def __init__(self):
        """Initialize the CLI."""
        self.parser = argparse.ArgumentParser(
            description="Science Data Kit Command-Line Interface",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  sdk login example_user --url http://localhost:8000
  sdk query "MATCH (n) RETURN n.name, n.type LIMIT 5"
  sdk create-session "My Session" --database "My Database"
  sdk info
"""
        )
        self.parser.add_argument('--url', default='http://localhost:8000',
                                help='Base URL of the API (default: http://localhost:8000)')
        self.parser.add_argument('--config', default='~/.sdkconfig',
                                help='Path to config file (default: ~/.sdkconfig)')
        self.parser.add_argument('--verbose', '-v', action='store_true',
                                help='Enable verbose output')
        
        self.subparsers = self.parser.add_subparsers(dest='command', help='Command to execute')
        
        # Login command
        login_parser = self.subparsers.add_parser('login', help='Log in to the API')
        login_parser.add_argument('user_id', help='User ID to log in with')
        
        # Logout command
        self.subparsers.add_parser('logout', help='Log out from the API')
        
        # Info command
        self.subparsers.add_parser('info', help='Get information about the current session')
        
        # Query command
        query_parser = self.subparsers.add_parser('query', help='Execute a database query')
        query_parser.add_argument('query', help='Query to execute')
        query_parser.add_argument('--params', help='Query parameters as JSON string')
        query_parser.add_argument('--output', '-o', help='Output file for query results')
        query_parser.add_argument('--format', choices=['json', 'csv', 'table'], default='table',
                                help='Output format (default: table)')
        
        # Create session command
        create_session_parser = self.subparsers.add_parser('create-session', help='Create a new session')
        create_session_parser.add_argument('name', help='Session name')
        create_session_parser.add_argument('--description', help='Session description')
        
        # Create database command
        create_db_parser = self.subparsers.add_parser('create-database', help='Create a new database')
        create_db_parser.add_argument('name', help='Database name')
        create_db_parser.add_argument('--description', help='Database description')
        
        # Create session with database command
        create_session_db_parser = self.subparsers.add_parser('create-session-with-database', 
                                                            help='Create a new session with a database')
        create_session_db_parser.add_argument('session_name', help='Session name')
        create_session_db_parser.add_argument('database_name', help='Database name')
        
        # Delete session command
        self.subparsers.add_parser('delete-session', help='Delete the current session')
        
        # Cache commands
        cache_parser = self.subparsers.add_parser('cache', help='Cache management commands')
        cache_subparsers = cache_parser.add_subparsers(dest='cache_command', help='Cache command to execute')
        
        cache_subparsers.add_parser('enable', help='Enable caching')
        cache_subparsers.add_parser('disable', help='Disable caching')
        cache_subparsers.add_parser('clear', help='Clear the cache')
        
        invalidate_parser = cache_subparsers.add_parser('invalidate', help='Invalidate cache entries')
        invalidate_parser.add_argument('--method', help='HTTP method to match')
        invalidate_parser.add_argument('--path', help='Request path to match')
        
        self.client = None
        self.config = {}
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the config file.
            
        Returns:
            The loaded configuration.
        """
        config_path = os.path.expanduser(config_path)
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {str(e)}")
        
        return {}
    
    def save_config(self, config_path: str, config: Dict[str, Any]) -> None:
        """
        Save configuration to a file.
        
        Args:
            config_path: Path to the config file.
            config: The configuration to save.
        """
        config_path = os.path.expanduser(config_path)
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save config to {config_path}: {str(e)}")
    
    def initialize_client(self, args: argparse.Namespace) -> SDKClient:
        """
        Initialize the SDK client.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            The initialized SDK client.
        """
        # Load config
        self.config = self.load_config(args.config)
        
        # Get base URL from args or config
        base_url = args.url or self.config.get('base_url', 'http://localhost:8000')
        
        # Initialize client
        client = SDKClient(base_url=base_url)
        
        # Set log level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Auto-login if token is available
        token = self.config.get('token')
        if token:
            client.api_client.token = token
        
        return client
    
    def format_output(self, data: Any, format_type: str, output_file: Optional[str] = None) -> None:
        """
        Format and output data.
        
        Args:
            data: The data to output.
            format_type: The output format (json, csv, table).
            output_file: Optional output file path.
        """
        if format_type == 'json':
            output = json.dumps(data, indent=2)
        elif format_type == 'csv':
            if not isinstance(data, list) or not data:
                print("Data is not a list or is empty, cannot format as CSV")
                return
            
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.DictWriter(output_buffer, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            output = output_buffer.getvalue()
        elif format_type == 'table':
            if not isinstance(data, list) or not data:
                output = str(data)
            else:
                from tabulate import tabulate
                headers = data[0].keys() if data else []
                rows = [list(item.values()) for item in data]
                output = tabulate(rows, headers=headers, tablefmt='grid')
        else:
            output = str(data)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
        else:
            print(output)
    
    def handle_login(self, args: argparse.Namespace) -> int:
        """
        Handle the login command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            response = self.client.login(args.user_id)
            print(f"Logged in as {args.user_id}")
            
            # Save token to config
            self.config['base_url'] = args.url
            self.config['token'] = self.client.api_client.token
            self.save_config(args.config, self.config)
            
            return 0
        except APIClientError as e:
            logger.error(f"Login failed: {e.message}")
            return 1
    
    def handle_logout(self, args: argparse.Namespace) -> int:
        """
        Handle the logout command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            response = self.client.logout()
            print("Logged out successfully")
            
            # Remove token from config
            if 'token' in self.config:
                del self.config['token']
                self.save_config(args.config, self.config)
            
            return 0
        except APIClientError as e:
            logger.error(f"Logout failed: {e.message}")
            return 1
    
    def handle_info(self, args: argparse.Namespace) -> int:
        """
        Handle the info command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            info = self.client.get_user_info()
            self.format_output(info, 'json')
            return 0
        except APIClientError as e:
            logger.error(f"Failed to get info: {e.message}")
            return 1
    
    def handle_query(self, args: argparse.Namespace) -> int:
        """
        Handle the query command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            params = {}
            if args.params:
                try:
                    params = json.loads(args.params)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in params argument")
                    return 1
            
            results = self.client.query(args.query, params)
            self.format_output(results, args.format, args.output)
            return 0
        except APIClientError as e:
            logger.error(f"Query failed: {e.message}")
            return 1
    
    def handle_create_session(self, args: argparse.Namespace) -> int:
        """
        Handle the create-session command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            data = {"name": args.name}
            if args.description:
                data["description"] = args.description
            
            response = self.client.api_client.create_session(data)
            print(f"Session created: {response.get('session_id')}")
            return 0
        except APIClientError as e:
            logger.error(f"Failed to create session: {e.message}")
            return 1
    
    def handle_create_database(self, args: argparse.Namespace) -> int:
        """
        Handle the create-database command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            data = {"name": args.name}
            if args.description:
                data["description"] = args.description
            
            response = self.client.api_client.create_database(data)
            print(f"Database created: {response.get('database_id')}")
            return 0
        except APIClientError as e:
            logger.error(f"Failed to create database: {e.message}")
            return 1
    
    def handle_create_session_with_database(self, args: argparse.Namespace) -> int:
        """
        Handle the create-session-with-database command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            response = self.client.create_session_with_database(
                session_name=args.session_name,
                database_name=args.database_name
            )
            print(f"Session created: {response.get('session_id')}")
            return 0
        except APIClientError as e:
            logger.error(f"Failed to create session with database: {e.message}")
            return 1
    
    def handle_delete_session(self, args: argparse.Namespace) -> int:
        """
        Handle the delete-session command.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            response = self.client.api_client.delete_session()
            print("Session deleted successfully")
            return 0
        except APIClientError as e:
            logger.error(f"Failed to delete session: {e.message}")
            return 1
    
    def handle_cache(self, args: argparse.Namespace) -> int:
        """
        Handle cache commands.
        
        Args:
            args: Command-line arguments.
            
        Returns:
            Exit code.
        """
        try:
            if args.cache_command == 'enable':
                self.client.enable_caching(True)
                print("Caching enabled")
            elif args.cache_command == 'disable':
                self.client.enable_caching(False)
                print("Caching disabled")
            elif args.cache_command == 'clear':
                count = self.client.clear_cache()
                print(f"Cleared {count} cache entries")
            elif args.cache_command == 'invalidate':
                count = self.client.invalidate_cache(args.method, args.path)
                print(f"Invalidated {count} cache entries")
            else:
                print("Unknown cache command")
                return 1
            
            return 0
        except Exception as e:
            logger.error(f"Cache operation failed: {str(e)}")
            return 1
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments. If None, sys.argv[1:] is used.
            
        Returns:
            Exit code.
        """
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            # Initialize client
            self.client = self.initialize_client(parsed_args)
            
            # Handle command
            if parsed_args.command == 'login':
                return self.handle_login(parsed_args)
            elif parsed_args.command == 'logout':
                return self.handle_logout(parsed_args)
            elif parsed_args.command == 'info':
                return self.handle_info(parsed_args)
            elif parsed_args.command == 'query':
                return self.handle_query(parsed_args)
            elif parsed_args.command == 'create-session':
                return self.handle_create_session(parsed_args)
            elif parsed_args.command == 'create-database':
                return self.handle_create_database(parsed_args)
            elif parsed_args.command == 'create-session-with-database':
                return self.handle_create_session_with_database(parsed_args)
            elif parsed_args.command == 'delete-session':
                return self.handle_delete_session(parsed_args)
            elif parsed_args.command == 'cache':
                return self.handle_cache(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return 1


def main():
    """Run the CLI."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
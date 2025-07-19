"""
Test script for Chat API endpoints

This script tests the Flask API endpoints for the chat page.
It verifies that the endpoints return the expected responses.
"""

import unittest
import json
import os
import sys
from flask import Flask, session
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from science_data_kit.web.routes import main_bp
from science_data_kit.core.pages.chat import ChatPage

class ChatAPITest(unittest.TestCase):
    """Test case for Chat API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.register_blueprint(main_bp)
        
        # Create a test client
        self.client = self.app.test_client()
        
        # Create a test context
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        # Set up session for login_required decorator
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'test_user'

    def tearDown(self):
        """Tear down the test environment."""
        self.ctx.pop()

    def test_chat_page_loads(self):
        """Test that the chat page loads successfully."""
        with patch.object(ChatPage, 'get_page_data', return_value=MagicMock()):
            response = self.client.get('/chat')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Chat with your data', response.data)

    def test_connect_to_neo4j(self):
        """Test the connect to Neo4j endpoint."""
        with patch.object(ChatPage, 'connect_to_neo4j', return_value={'success': True, 'message': 'Connected to Neo4j'}):
            response = self.client.post('/api/chat/connect-neo4j', 
                                       json={
                                           'uri': 'bolt://localhost:7687',
                                           'user': 'neo4j',
                                           'password': 'password',
                                           'database': 'neo4j'
                                       })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Connected to Neo4j')

    def test_initialize_graph_rag(self):
        """Test the initialize GraphRAG endpoint."""
        with patch.object(ChatPage, 'initialize_graph_rag', return_value={'success': True, 'message': 'GraphRAG initialized'}):
            response = self.client.post('/api/chat/initialize-graph-rag')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'GraphRAG initialized')

    def test_update_chat_settings(self):
        """Test the update chat settings endpoint."""
        with patch.object(ChatPage, 'update_llm_settings', return_value={'success': True, 'message': 'Settings updated'}):
            response = self.client.post('/api/chat/settings', 
                                       json={
                                           'provider': 'OpenAI',
                                           'api_key': 'test_api_key',
                                           'model': 'gpt-3.5-turbo',
                                           'temperature': 0.7,
                                           'max_tokens': 1000
                                       })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Settings updated')

    def test_refresh_ollama_models(self):
        """Test the refresh Ollama models endpoint."""
        with patch.object(ChatPage, 'refresh_ollama_models', return_value={'success': True, 'message': 'Models refreshed', 'models': ['llama2', 'mistral']}):
            response = self.client.post('/api/chat/refresh-ollama-models', 
                                       json={
                                           'base_url': 'http://localhost:11434'
                                       })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Models refreshed')
            self.assertEqual(data['models'], ['llama2', 'mistral'])

    def test_send_chat_message(self):
        """Test the send chat message endpoint."""
        with patch.object(ChatPage, 'send_message', return_value={'success': True, 'response': 'This is a test response'}):
            response = self.client.post('/api/chat/send-message', 
                                       json={
                                           'message': 'This is a test message'
                                       })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['response'], 'This is a test response')

    def test_clear_chat_history(self):
        """Test the clear chat history endpoint."""
        with patch.object(ChatPage, 'clear_chat_history', return_value={'success': True, 'message': 'Chat history cleared'}):
            response = self.client.post('/api/chat/clear-history')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Chat history cleared')

    def test_error_handling(self):
        """Test error handling in the API endpoints."""
        # Test missing message in send_chat_message
        response = self.client.post('/api/chat/send-message', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Message is required', data['error'])

        # Test missing parameters in connect_to_neo4j
        response = self.client.post('/api/chat/connect-neo4j', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('All connection parameters are required', data['error'])

if __name__ == '__main__':
    unittest.main()
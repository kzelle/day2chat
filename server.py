import os
import json
import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import html
from database.db import Database
from github_api import GitHubAPI
from github_manager import GitHubManager

# Load environment variables
load_dotenv()

class ChatServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.github_api = GitHubAPI(
            token=os.getenv('GITHUB_TOKEN'),
            username=os.getenv('GITHUB_USERNAME')
        )
        self.github_manager = GitHubManager(self.github_api, self.db)
        super().__init__(*args, **kwargs)

    def _send_cors_headers(self):
        """Send CORS headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_json_response(self, data: Any, status: int = 200):
        """Send JSON response with proper headers."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_json_body(self) -> Dict:
        """Read and parse JSON request body."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        return json.loads(body.decode())

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/messages':
            messages = self.db.get_messages()
            self._send_json_response(messages)
            
        elif parsed_path.path == '/repositories':
            repositories = self.github_manager.get_repositories()
            self._send_json_response(repositories)
            
        elif parsed_path.path.startswith('/static/'):
            # Serve static files
            try:
                with open('.' + parsed_path.path, 'rb') as f:
                    self.send_response(200)
                    if parsed_path.path.endswith('.css'):
                        self.send_header('Content-Type', 'text/css')
                    elif parsed_path.path.endswith('.js'):
                        self.send_header('Content-Type', 'application/javascript')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self._send_json_response({'error': 'File not found'}, 404)
        
        else:
            # Serve index.html for the root path
            if parsed_path.path == '/':
                try:
                    with open('./static/index.html', 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(f.read())
                except FileNotFoundError:
                    self._send_json_response({'error': 'File not found'}, 404)
            else:
                self._send_json_response({'error': 'Not found'}, 404)

    def do_POST(self):
        """Handle POST requests."""
        try:
            data = self._read_json_body()
            
            if self.path == '/messages':
                # Sanitize input
                content = html.escape(data.get('content', '').strip())
                if not content:
                    self._send_json_response({'error': 'Content is required'}, 400)
                    return
                
                # Add message to database
                message = self.db.add_message(content)
                
                # Sync with GitHub if repository is set
                if message.get('repository_id'):
                    git_hash = self.github_manager.sync_message(message)
                    if git_hash:
                        self.db.update_message_git_hash(message['id'], git_hash)
                
                self._send_json_response(message)
                
            elif self.path == '/repositories':
                owner = data.get('owner', '').strip()
                name = data.get('name', '').strip()
                
                if not owner or not name:
                    self._send_json_response({'error': 'Owner and name are required'}, 400)
                    return
                
                repository = self.github_manager.add_repository(owner, name)
                self._send_json_response(repository)
                
            elif self.path == '/push':
                success = self.github_manager.sync_all_messages()
                self._send_json_response({
                    'success': success,
                    'message': 'Messages synced successfully' if success else 'Sync failed'
                })
                
            else:
                self._send_json_response({'error': 'Not found'}, 404)
                
        except json.JSONDecodeError:
            self._send_json_response({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)

def run_server(host: str = 'localhost', port: int = 8004):
    """Run the server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, ChatServer)
    print(f"Server running at http://{host}:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8004))
    run_server(host, port)

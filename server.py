import os
import json
import asyncio
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import html
from datetime import datetime
from github_api import GitHubAPI

# Load environment variables
load_dotenv()

# Check required environment variables
required_vars = ['GITHUB_TOKEN', 'GITHUB_USERNAME']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please make sure your .env file contains:")
    print("GITHUB_TOKEN=your_github_token")
    print("GITHUB_USERNAME=your_github_username")
    exit(1)

class ChatServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        try:
            self.github_api = GitHubAPI(
                token=os.getenv('GITHUB_TOKEN'),
                username=os.getenv('GITHUB_USERNAME')
            )
            super().__init__(*args, **kwargs)
        except Exception as e:
            print(f"Error initializing server: {str(e)}")
            print(traceback.format_exc())
            raise

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

    def _store_message(self, content: str) -> Dict:
        """Store a message as a text file in the repository."""
        try:
            timestamp = datetime.now().isoformat()
            message = {
                'content': content,
                'timestamp': timestamp
            }
            
            # Create messages directory if it doesn't exist
            messages_dir = 'messages'
            if not os.path.exists(messages_dir):
                os.makedirs(messages_dir)
            
            # Create a unique filename based on timestamp
            filename = f"{timestamp.replace(':', '-')}.txt"
            filepath = os.path.join(messages_dir, filename)
            
            # Write message to local file
            with open(filepath, 'w') as f:
                f.write(f"Content: {content}\nTimestamp: {timestamp}\n")
            
            # Commit and push to GitHub
            self.github_api.create_or_update_file(
                owner=os.getenv('GITHUB_USERNAME'),
                repo=os.getenv('GITHUB_REPO_NAME', 'day2chat'),
                path=f"messages/{filename}",
                content=f"Content: {content}\nTimestamp: {timestamp}\n",
                message=f"Add message from {timestamp}"
            )
            
            return message
        except Exception as e:
            print(f"Error storing message: {str(e)}")
            print(traceback.format_exc())
            raise

    def _get_messages(self) -> List[Dict]:
        """Get all messages from the messages directory."""
        messages = []
        messages_dir = 'messages'
        
        if os.path.exists(messages_dir):
            for filename in sorted(os.listdir(messages_dir)):
                if filename.endswith('.txt'):
                    filepath = os.path.join(messages_dir, filename)
                    with open(filepath, 'r') as f:
                        content = f.read()
                        # Parse the content
                        lines = content.strip().split('\n')
                        message_content = lines[0].replace('Content: ', '', 1)
                        timestamp = lines[1].replace('Timestamp: ', '', 1)
                        messages.append({
                            'content': message_content,
                            'timestamp': timestamp
                        })
        
        return messages

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/messages':
            try:
                messages = self._get_messages()
                self._send_json_response(messages)
            except Exception as e:
                print(f"Error getting messages: {str(e)}")
                self._send_json_response({'error': str(e)}, 500)
        
        elif parsed_path.path.startswith('/static/'):
            # Serve static files
            try:
                file_path = '.' + parsed_path.path
                with open(file_path, 'rb') as f:
                    self.send_response(200)
                    if file_path.endswith('.css'):
                        self.send_header('Content-Type', 'text/css')
                    elif file_path.endswith('.js'):
                        self.send_header('Content-Type', 'application/javascript')
                    elif file_path.endswith('.html'):
                        self.send_header('Content-Type', 'text/html')
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self._send_json_response({'error': 'File not found'}, 404)
        
        elif parsed_path.path == '/':
            # Serve index.html for root path
            try:
                with open('./static/index.html', 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self._send_json_response({'error': 'index.html not found'}, 404)
        
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
                
                # Store the message
                message = self._store_message(content)
                self._send_json_response(message)
            else:
                self._send_json_response({'error': 'Not found'}, 404)
                
        except json.JSONDecodeError:
            self._send_json_response({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            print(f"Server error: {str(e)}")
            print(traceback.format_exc())
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

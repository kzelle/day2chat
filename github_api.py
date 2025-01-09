import os
import requests
from typing import Dict, Optional, List
import json

class GitHubAPI:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_repository(self, name: str, private: bool = False) -> Dict:
        """Create a new GitHub repository."""
        url = f"{self.base_url}/user/repos"
        data = {
            "name": name,
            "private": private,
            "auto_init": True
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_repository(self, owner: str, name: str) -> Optional[Dict]:
        """Get repository information."""
        url = f"{self.base_url}/repos/{owner}/{name}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def create_file(self, owner: str, repo: str, path: str, content: str, message: str) -> Dict:
        """Create a new file in the repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        import base64
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        data = {
            "message": message,
            "content": content_base64
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def update_file(self, owner: str, repo: str, path: str, content: str, message: str, sha: str) -> Dict:
        """Update an existing file in the repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        import base64
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        data = {
            "message": message,
            "content": content_base64,
            "sha": sha
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_file(self, owner: str, repo: str, path: str) -> Optional[Dict]:
        """Get file content and metadata."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def create_or_update_file(self, owner: str, repo: str, path: str, content: str, message: str) -> Dict:
        """Create or update a file in the repository."""
        existing_file = self.get_file(owner, repo, path)
        
        if existing_file:
            return self.update_file(owner, repo, path, content, message, existing_file['sha'])
        else:
            return self.create_file(owner, repo, path, content, message)

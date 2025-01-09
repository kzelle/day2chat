import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from github_api import GitHubAPI
from database.db import Database

class GitHubManager:
    def __init__(self, github_api: GitHubAPI, database: Database):
        self.github_api = github_api
        self.database = database

    def sync_message(self, message: Dict) -> Optional[str]:
        """Sync a message to GitHub and return the git hash."""
        try:
            # Get repository information from the database
            if message.get('repository_id'):
                repositories = self.database.get_repositories()
                repo = next((r for r in repositories if r['id'] == message['repository_id']), None)
                
                if repo:
                    # Create the message content
                    message_data = {
                        'id': message['id'],
                        'content': message['content'],
                        'timestamp': message['timestamp']
                    }
                    
                    # Create or update the file in GitHub
                    file_path = f"messages/{message['id']}.json"
                    result = self.github_api.create_or_update_file(
                        owner=repo['owner'],
                        repo=repo['name'],
                        path=file_path,
                        content=json.dumps(message_data, indent=2),
                        message=f"Update message {message['id']}"
                    )
                    
                    # Return the git hash
                    return result['content']['sha']
            
            return None
        except Exception as e:
            print(f"Error syncing message to GitHub: {str(e)}")
            return None

    def add_repository(self, owner: str, name: str) -> Dict:
        """Add a new repository for tracking."""
        # Check if the repository exists on GitHub
        repo = self.github_api.get_repository(owner, name)
        if not repo:
            raise ValueError(f"Repository {owner}/{name} not found on GitHub")
        
        # Add the repository to the database
        return self.database.add_repository(owner, name)

    def get_repositories(self) -> List[Dict]:
        """Get all tracked repositories."""
        return self.database.get_repositories()

    def sync_all_messages(self) -> bool:
        """Sync all messages to their respective repositories."""
        try:
            messages = self.database.get_messages()
            for message in messages:
                if not message.get('git_hash'):
                    git_hash = self.sync_message(message)
                    if git_hash:
                        self.database.update_message_git_hash(message['id'], git_hash)
            return True
        except Exception as e:
            print(f"Error syncing all messages: {str(e)}")
            return False

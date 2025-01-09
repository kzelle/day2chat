import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class Database:
    def __init__(self, db_path: str = "messages.db"):
        # Make sure we store the database in the database directory
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    repository_id INTEGER,
                    git_hash TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (repository_id) REFERENCES repositories(id)
                )
            ''')
            
            # Create repositories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(owner, name)
                )
            ''')
            
            conn.commit()

    def add_message(self, content: str, repository_id: Optional[int] = None, git_hash: Optional[str] = None) -> Dict:
        """Add a new message to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (content, repository_id, git_hash)
                VALUES (?, ?, ?)
            ''', (content, repository_id, git_hash))
            
            message_id = cursor.lastrowid
            cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
            row = cursor.fetchone()
            
            return {
                'id': row[0],
                'content': row[1],
                'repository_id': row[2],
                'git_hash': row[3],
                'timestamp': row[4]
            }

    def get_messages(self) -> List[Dict]:
        """Retrieve all messages from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC')
            
            return [{
                'id': row['id'],
                'content': row['content'],
                'repository_id': row['repository_id'],
                'git_hash': row['git_hash'],
                'timestamp': row['timestamp']
            } for row in cursor.fetchall()]

    def add_repository(self, owner: str, name: str) -> Dict:
        """Add a new repository to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO repositories (owner, name)
                    VALUES (?, ?)
                ''', (owner, name))
                
                repo_id = cursor.lastrowid
                cursor.execute('SELECT * FROM repositories WHERE id = ?', (repo_id,))
                row = cursor.fetchone()
                
                return {
                    'id': row[0],
                    'name': row[1],
                    'owner': row[2],
                    'created_at': row[3]
                }
            except sqlite3.IntegrityError:
                cursor.execute('''
                    SELECT * FROM repositories 
                    WHERE owner = ? AND name = ?
                ''', (owner, name))
                row = cursor.fetchone()
                return {
                    'id': row[0],
                    'name': row[1],
                    'owner': row[2],
                    'created_at': row[3]
                }

    def get_repositories(self) -> List[Dict]:
        """Retrieve all repositories from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM repositories ORDER BY created_at DESC')
            
            return [{
                'id': row['id'],
                'name': row['name'],
                'owner': row['owner'],
                'created_at': row['created_at']
            } for row in cursor.fetchall()]

    def update_message_git_hash(self, message_id: int, git_hash: str):
        """Update the git hash for a message."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages 
                SET git_hash = ?
                WHERE id = ?
            ''', (git_hash, message_id))
            conn.commit()

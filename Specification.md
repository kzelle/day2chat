# Project Specification: Git-Backed Messaging System

Create a lightweight web-based messaging application that uses Git as a backend storage system. The application should allow users to send and receive messages while maintaining a complete history of all communications through Git.

## Core Requirements

### Technical Stack
- Backend: Pure Python (no web frameworks)
- Frontend: Vanilla JavaScript, HTML5, CSS3 (with CSS Variables)
- Database: SQLite3 for local storage
- Version Control: Git for message persistence
- API Integration: GitHub REST API for backup/sync
- Required Python Packages:
  - aiohttp==3.9.1
  - python-dotenv==1.0.0
  - requests==2.31.0

### Key Features
1. Message Management
   - Send and receive text messages
   - Store messages in both SQLite and Git
   - Real-time message updates without page refresh
   - Message history preservation

2. GitHub Integration
   - Backup messages to GitHub repositories
   - Support for multiple repository management
   - Automatic sync with remote repositories
   - GitHub authentication via personal access tokens

3. User Interface
   - Clean, modern web interface
   - Message display area with automatic updates
   - Repository management interface
   - Simple message input system

### Technical Components

1. Server (server.py)
   - Custom HTTP server using Python's `http.server`
   - Endpoint handlers for messages and repositories
   - Static file serving
   - Async support using `asyncio` and `aiohttp`
   - CORS and security headers

2. Database Layer (`database/db.py`)
   - SQLite database implementation
   - Tables:
     - messages (id, content, repository_id, git_hash, timestamp)
     - repositories (id, name, owner, created_at)
   - Message storage and retrieval
   - Repository tracking with unique constraints

3. GitHub Integration
   - GitHub API wrapper (github_api.py) using `requests` library
   - Repository management (github_manager.py)
   - Git operations handler (git_handler.py)
   - Automatic error handling and retries

4. Frontend
   - Single page application with embedded CSS
   - Modern CSS with CSS Variables for theming
   - Real-time message updates via polling
   - Error handling and display
   - XSS protection with HTML escaping
   - Responsive design with flexbox

5. Configuration
   - Environment-based configuration
   - Setup utility for environment management
   - GitHub token management

### Required Environment Variables
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `GITHUB_USERNAME`: GitHub username
- `GITHUB_REPO_NAME`: Default repository name (optional)
- `PORT`: Server port (default: 8004)
- `HOST`: Server host (default: localhost)

### Project Structure
```
project_root/
├── .env                 # Environment variables
├── .env.example        # Example environment file
├── README.md           # Documentation
├── requirements.txt    # Python dependencies
├── setup.py           # Environment setup utility
├── server.py          # Main server
├── git_handler.py     # Git operations
├── github_api.py      # GitHub API wrapper
├── github_manager.py  # Repository management
├── database/          # Database module
│   └── db.py         # Database implementation
├── static/            # Static assets
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript files
└── tests/            # Test suite
```

### Implementation Requirements

1. Server Implementation
   - Custom HTTP server using Python's `http.server`
   - Support for GET/POST methods
   - JSON response format
   - Static file serving
   - Async capabilities for real-time updates

2. Database Design
   - Messages table with timestamp and content
   - Repositories table for GitHub integration
   - Efficient querying system

3. Git Integration
   - Automatic commit on new messages
   - Push/pull synchronization
   - Conflict resolution
   - Repository management

4. Security Considerations
   - Secure token storage
   - Input validation
   - Error handling
   - Rate limiting

5. User Interface
   - Clean, minimal design
   - Real-time updates
   - Error feedback
   - Loading states

### API Endpoints

1. Messages
   - GET /messages - Retrieve messages
     - Response: `[{id, content, timestamp, git_hash}]`
   - POST /messages - Create new message
     - Request: `{content: string}`
     - Response: `{id, content, timestamp, git_hash}`

2. Repositories
   - GET /repositories - List repositories
     - Response: `[{id, name, owner, created_at}]`
   - POST /repositories - Add repository
     - Request: `{owner: string, name: string}`
     - Response: `{id, name, owner, created_at}`
   - POST /push - Trigger push to GitHub
     - Response: `{success: boolean, message: string}`

### Development Steps

1. Environment Setup
   - Python environment setup
   - Dependencies installation
   - Environment variable configuration

2. Core Implementation
   - Server setup
   - Database implementation
   - Git integration
   - GitHub API integration

3. Frontend Development
   - HTML structure
   - JavaScript functionality
   - CSS styling
   - Real-time updates

4. Testing
   - Unit tests
   - Integration tests
   - Manual testing

5. Documentation
   - README
   - API documentation
   - Setup instructions

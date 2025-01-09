# Git-Backed Chat Application

A lightweight web-based messaging application that uses Git as a backend storage system. Messages are stored locally in SQLite and synced with GitHub repositories.

## Features

- Send and receive text messages in real-time
- Store messages in both SQLite and Git
- Backup messages to GitHub repositories
- Clean, modern web interface
- Real-time message updates without page refresh

## Prerequisites

- Python 3.7+
- GitHub account and Personal Access Token
- Git installed on your system

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd day2chat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your GitHub credentials:
```
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username
GITHUB_REPO_NAME=your_repo_name
PORT=8004
HOST=localhost
```

## Running the Application

1. Start the server:
```bash
python server.py
```

2. Open your web browser and navigate to:
```
http://localhost:8004
```

## Usage

1. **Sending Messages**
   - Type your message in the input area
   - Press Enter or click Send

2. **Adding a Repository**
   - Click "Add Repository"
   - Enter the repository owner and name
   - Click Add

3. **Syncing with GitHub**
   - Click "Sync to GitHub" to manually sync messages

## Project Structure

```
project_root/
├── .env                 # Environment variables
├── .env.example        # Example environment file
├── README.md           # Documentation
├── requirements.txt    # Python dependencies
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

## Security Notes

- Never commit your `.env` file
- Keep your GitHub token secure
- The application uses CORS headers and input sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

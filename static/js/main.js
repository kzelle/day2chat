document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const addRepoBtn = document.getElementById('addRepoBtn');
    const syncBtn = document.getElementById('syncBtn');
    const repoModal = document.getElementById('repoModal');
    const repoForm = document.getElementById('repoForm');
    const cancelRepoBtn = document.getElementById('cancelRepoBtn');

    // API endpoints
    const API = {
        MESSAGES: '/messages',
        REPOSITORIES: '/repositories',
        PUSH: '/push'
    };

    // Fetch messages every 5 seconds
    let lastMessageId = 0;
    setInterval(fetchMessages, 5000);

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    addRepoBtn.addEventListener('click', () => repoModal.style.display = 'block');
    cancelRepoBtn.addEventListener('click', () => repoModal.style.display = 'none');
    repoForm.addEventListener('submit', addRepository);
    syncBtn.addEventListener('click', syncToGitHub);

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === repoModal) {
            repoModal.style.display = 'none';
        }
    });

    // Functions
    async function fetchMessages() {
        try {
            const response = await fetch(API.MESSAGES);
            const messages = await response.json();
            
            if (messages.length > 0 && messages[0].id !== lastMessageId) {
                lastMessageId = messages[0].id;
                renderMessages(messages);
            }
        } catch (error) {
            showToast('Error fetching messages', false);
        }
    }

    async function sendMessage() {
        const content = messageInput.value.trim();
        if (!content) return;

        try {
            const response = await fetch(API.MESSAGES, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) throw new Error('Failed to send message');

            messageInput.value = '';
            await fetchMessages();
        } catch (error) {
            showToast('Error sending message', false);
        }
    }

    async function addRepository(e) {
        e.preventDefault();
        
        const owner = document.getElementById('ownerInput').value.trim();
        const name = document.getElementById('nameInput').value.trim();

        try {
            const response = await fetch(API.REPOSITORIES, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ owner, name })
            });

            if (!response.ok) throw new Error('Failed to add repository');

            repoModal.style.display = 'none';
            repoForm.reset();
            showToast('Repository added successfully', true);
        } catch (error) {
            showToast('Error adding repository', false);
        }
    }

    async function syncToGitHub() {
        try {
            const response = await fetch(API.PUSH, {
                method: 'POST'
            });

            const result = await response.json();
            showToast(result.message, result.success);
        } catch (error) {
            showToast('Error syncing with GitHub', false);
        }
    }

    function renderMessages(messages) {
        messagesContainer.innerHTML = messages.map(message => `
            <div class="message">
                <div class="message-content">${message.content}</div>
                <div class="message-meta">
                    ${new Date(message.timestamp).toLocaleString()}
                    ${message.git_hash ? `<span title="Synced to GitHub">✓</span>` : ''}
                </div>
            </div>
        `).join('');
        
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showToast(message, success = true) {
        const toast = document.createElement('div');
        toast.className = `toast ${success ? 'success' : 'error'}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Initial fetch
    fetchMessages();
});

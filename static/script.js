// Toggle chatbot open/close
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('active');
}

// Send message
function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (message === '') return;

    // Show user message
    appendMessage(message, 'user-message');
    input.value = '';

    // Send to Flask backend
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.response, 'bot-message');
    });
}

function appendMessage(text, className) {
    const chatbox = document.getElementById('chatbox');
    const div = document.createElement('div');
    div.classList.add('message', className);
    div.innerHTML = `<span>${text}</span>`;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

// Send message on Enter key
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
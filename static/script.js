// Premium InfraChat Script Engine
// Handles Navigation, Cinematic Chatbot, and Ambient Interactivity

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initReveals();
});

// ========== Intelligent Navigation ==========
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('menuToggle');
    const overlay = document.getElementById('sidebarOverlay');

    if (toggle && sidebar) {
        toggle.onclick = () => {
            sidebar.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
        };
    }

    if (overlay) {
        overlay.onclick = () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        };
    }
}

// ========== Advanced AI Chatbot Interface ==========
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    chatWindow.classList.toggle('active');
    
    if (chatWindow.classList.contains('active')) {
        const input = document.getElementById('userInput');
        if (input) input.focus();
    }
}

function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (message === '') return;

    appendMessage(message, 'user-message');
    input.value = '';

    const chatbox = document.getElementById('chatbox');
    const typingId = 'typing-' + Date.now();
    
    // Premium Typing Indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = typingId;
    typingDiv.innerHTML = '<span style="opacity:0.5; font-size:12px; font-weight:800; letter-spacing:1px;"><i class="fas fa-ellipsis fa-fade"></i> SYNTHESIZING COMMAND...</span>';
    chatbox.appendChild(typingDiv);
    scrollChat();

    // Comm Link Engagement
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        const indicator = document.getElementById(typingId);
        if (indicator) indicator.remove();
        appendMessage(data.response, 'bot-message');
    })
    .catch(err => {
        const indicator = document.getElementById(typingId);
        if (indicator) indicator.remove();
        appendMessage('⚠️ CRITICAL LINK FAILURE. Retrying synthesized command required.', 'bot-message');
    });
}

function appendMessage(text, className) {
    const chatbox = document.getElementById('chatbox');
    const div = document.createElement('div');
    div.classList.add('message', className);
    
    // Formatting logic
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<b style="color:var(--accent);">$1</b>');
    formattedText = formattedText.replace(/\n/g, '<br>');
    
    div.innerHTML = `<span>${formattedText}</span>`;
    
    // Inject Dynamic Data Tile for Machine Queries
    if (className === 'bot-message' && (text.includes('RPM') || text.includes('Details'))) {
        const dataTile = extractToDataTile(text);
        if (dataTile) div.innerHTML += dataTile;
    }
    
    chatbox.appendChild(div);
    scrollChat();
}

function extractToDataTile(text) {
    const idMatch = text.match(/Machine\s+([A-Z0-9]+)/);
    const rpmMatch = text.match(/RPM:\s*(\d+)/);
    const torqueMatch = text.match(/Torque:\s*([\d\.]+)/);
    
    if (!idMatch) return '';

    return `
        <div class="chat-data-card" style="margin-top: 15px; background: var(--bg-subtle); border-radius: 16px; padding: 20px; border: 1px solid var(--border);">
            <div class="chat-data-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div>
                    <span style="font-size: 10px; text-transform: uppercase; color: var(--muted); font-weight: 800; letter-spacing: 1px;">Asset UID</span>
                    <div style="font-family: 'JetBrains Mono'; font-weight: 800; color: var(--primary);">${idMatch[1]}</div>
                </div>
                <div>
                    <span style="font-size: 10px; text-transform: uppercase; color: var(--muted); font-weight: 800; letter-spacing: 1px;">Velocity (RPM)</span>
                    <div style="font-family: 'JetBrains Mono'; font-weight: 800; color: var(--accent);">${rpmMatch ? rpmMatch[1] : '—'}</div>
                </div>
            </div>
            <a href="/dashboard" class="chip" style="display: block; text-align: center; margin-top: 15px; background: var(--primary); color: #fff; text-decoration: none; border: none;">
                <i class="fas fa-arrow-up-right-from-square"></i> Full Performance Node
            </a>
        </div>
    `;
}

function scrollChat() {
    const chatbox = document.getElementById('chatbox');
    chatbox.scrollTo({ top: chatbox.scrollHeight, behavior: 'smooth' });
}

function quickQuery(cmd) {
    const input = document.getElementById('userInput');
    if (input) {
        input.value = cmd;
        sendMessage();
    }
}

// Reveal Logic
function initReveals() {
    const reveals = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, { threshold: 0.1 });
    reveals.forEach(r => observer.observe(r));
}

// Event Listeners
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'userInput') {
        sendMessage();
    }
});

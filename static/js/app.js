// LLaMA MindMap JavaScript
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('authToken');
let mindmapData = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    if (authToken) {
        showMindmapSection();
    }
});

function switchTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    
    document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
    document.getElementById(`${tab}Form`).classList.add('active');
}

async function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        alert('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            alert('Login successful!');
            showMindmapSection();
        } else {
            alert(data.message || 'Login failed');
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

async function register() {
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    if (!username || !email || !password) {
        alert('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Registration successful! Please login.');
            switchTab('login');
        } else {
            alert(data.message || 'Registration failed');
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mindmapSection').style.display = 'none';
    clearMindmap();
}

function showMindmapSection() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mindmapSection').style.display = 'block';
}

function createMindmap() {
    const topic = document.getElementById('topicInput').value.trim();
    if (!topic) {
        alert('Please enter a topic');
        return;
    }

    const container = document.getElementById('mindmapContainer');
    container.innerHTML = `
        <div class="mindmap-node">
            <h3>${topic}</h3>
            <div class="node-actions">
                <button class="btn" onclick="alert('Feature coming soon!')">Expand</button>
                <button class="btn" onclick="alert('Feature coming soon!')">Generate Steps</button>
                <button class="btn" onclick="alert('Feature coming soon!')">Analyze</button>
            </div>
        </div>
    `;
}

function clearMindmap() {
    document.getElementById('mindmapContainer').innerHTML = 
        '<p style="text-align: center; color: #666; margin-top: 100px;">Enter a topic above to start creating your mindmap</p>';
    document.getElementById('topicInput').value = '';
}
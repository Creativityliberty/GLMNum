/**
 * GLM v3.0 - Complete Web UI Application
 * =======================================
 * 
 * Full-featured application with Transform, Chat, and Unified Search modes
 */

// Configuration
const API_BASE_URL = 'http://localhost:8081';
const REFRESH_INTERVAL = 5000;

// State
let currentState = {
    mode: 'transform',
    sourceDomain: 'text',
    targetDomain: 'code',
    content: '',
    apiOnline: false,
    chatMessages: []
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 GLM Web UI Initialized');
    console.log(`📍 API Base URL: ${API_BASE_URL}`);
    
    // Setup event listeners
    setupEventListeners();
    
    // Check API status
    checkAPIStatus();
    setInterval(checkAPIStatus, REFRESH_INTERVAL);
    
    // Initialize UI
    updateInputContainer();
});

// ============================================================================
// API STATUS CHECK
// ============================================================================

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            credentials: 'omit'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API Response:', data);
            currentState.apiOnline = true;
            updateAPIStatus(true);
        } else {
            console.warn('⚠️ API returned status:', response.status);
            currentState.apiOnline = false;
            updateAPIStatus(false);
        }
    } catch (error) {
        console.error('❌ API Connection Error:', error.message);
        currentState.apiOnline = false;
        updateAPIStatus(false);
    }
}

function updateAPIStatus(online) {
    const statusEl = document.getElementById('apiStatus');
    if (!statusEl) return;
    
    if (online) {
        statusEl.innerHTML = '✅ API Online';
        statusEl.className = 'api-status online';
    } else {
        statusEl.innerHTML = '❌ API Offline';
        statusEl.className = 'api-status offline';
    }
}

// ============================================================================
// MODE SWITCHING
// ============================================================================

function switchMode(mode) {
    currentState.mode = mode;
    
    // Hide all modes
    document.getElementById('transformMode').classList.remove('active');
    document.getElementById('chatMode').classList.remove('active');
    document.getElementById('unifiedMode').classList.remove('active');
    
    // Show selected mode
    document.getElementById(mode + 'Mode').classList.add('active');
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Transform mode
    const sourceDomain = document.getElementById('sourceDomain');
    const targetDomain = document.getElementById('targetDomain');
    const transformBtn = document.getElementById('transformBtn');
    const similarityBtn = document.getElementById('similarityBtn');
    
    if (sourceDomain) {
        sourceDomain.addEventListener('change', (e) => {
            currentState.sourceDomain = e.target.value;
            updateInputContainer();
        });
    }
    
    if (targetDomain) {
        targetDomain.addEventListener('change', (e) => {
            currentState.targetDomain = e.target.value;
        });
    }
    
    if (transformBtn) {
        transformBtn.addEventListener('click', performTransform);
    }
    
    if (similarityBtn) {
        similarityBtn.addEventListener('click', performSimilarity);
    }
    
    // Chat mode
    const chatBtn = document.getElementById('chatBtn');
    const chatInput = document.getElementById('chatInput');
    
    if (chatBtn) {
        chatBtn.addEventListener('click', sendChatMessage);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    // Unified search
    const searchBtn = document.getElementById('searchBtn');
    const answerBtn = document.getElementById('answerBtn');
    
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    if (answerBtn) {
        answerBtn.addEventListener('click', generateAnswer);
    }
}

// ============================================================================
// TRANSFORM MODE
// ============================================================================

async function performTransform() {
    if (!currentState.apiOnline) {
        showError('❌ API is not online');
        return;
    }
    
    if (!currentState.content.trim()) {
        showError('Please enter content to transform.');
        return;
    }
    
    const btn = document.getElementById('transformBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Transforming...';
    
    try {
        const payload = {
            content: currentState.content,
            source_domain: currentState.sourceDomain,
            target_domain: currentState.targetDomain
        };
        
        const response = await fetch(`${API_BASE_URL}/transform`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            credentials: 'omit',
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            displayTransformResult(data);
            showSuccess('✅ Transformation completed!');
        } else {
            const error = await response.json();
            showError(`❌ Error: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔄 Transform';
    }
}

async function performSimilarity() {
    if (!currentState.apiOnline) {
        showError('❌ API is not online');
        return;
    }
    
    const content1 = document.getElementById('similarityInput1')?.value.trim();
    const content2 = document.getElementById('similarityInput2')?.value.trim();
    
    if (!content1 || !content2) {
        showError('Please enter both contents.');
        return;
    }
    
    const btn = document.getElementById('similarityBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Calculating...';
    
    try {
        const payload = {
            content1: content1,
            content2: content2,
            domain: currentState.sourceDomain
        };
        
        const response = await fetch(`${API_BASE_URL}/similarity`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            credentials: 'omit',
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySimilarityResult(data);
            showSuccess('✅ Similarity calculated!');
        } else {
            const error = await response.json();
            showError(`❌ Error: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📊 Calculate Similarity';
    }
}

function updateInputContainer() {
    const container = document.getElementById('inputContainer');
    if (!container) return;
    
    const domain = currentState.sourceDomain;
    let placeholder = 'Enter content...';
    let defaultValue = '';
    
    switch(domain) {
        case 'code':
            placeholder = 'Enter Python code...';
            defaultValue = 'def hello(name):\n    return f"Hello, {name}!"';
            break;
        case 'text':
            placeholder = 'Enter text...';
            defaultValue = 'Artificial intelligence is revolutionizing technology.';
            break;
        case 'geometry':
            placeholder = 'Enter geometry description...';
            defaultValue = 'triangle';
            break;
        case 'image':
            placeholder = 'Enter image description...';
            defaultValue = 'A red square on a white background';
            break;
    }
    
    container.innerHTML = `<textarea id="textInput" placeholder="${placeholder}" class="input-field">${defaultValue}</textarea>`;
    
    const textInput = document.getElementById('textInput');
    if (textInput) {
        textInput.addEventListener('input', (e) => {
            currentState.content = e.target.value;
        });
    }
}

function displayTransformResult(data) {
    const resultContent = document.getElementById('resultContent');
    if (!resultContent) return;
    
    resultContent.innerHTML = `
        <div class="result-section">
            <pre>${escapeHtml(data.result)}</pre>
        </div>
    `;
    
    const symbolicInfo = document.getElementById('symbolicInfo');
    if (symbolicInfo) {
        symbolicInfo.innerHTML = `
            <div class="triad-display">
                <p><strong>Triad (∆∞Θ):</strong></p>
                <ul>
                    <li>Delta (∆): ${(data.triad.delta * 100).toFixed(1)}%</li>
                    <li>Infinity (∞): ${(data.triad.infinity * 100).toFixed(1)}%</li>
                    <li>Theta (Θ): ${(data.triad.theta * 100).toFixed(1)}%</li>
                </ul>
            </div>
        `;
    }
}

function displaySimilarityResult(data) {
    const resultContent = document.getElementById('similarityResult');
    if (!resultContent) return;
    
    resultContent.innerHTML = `
        <div class="result-section">
            <p><strong>Similarity Score:</strong> ${(data.similarity * 100).toFixed(1)}%</p>
            <div class="score-bar">
                <div class="score-fill" style="width: ${data.similarity * 100}%"></div>
            </div>
        </div>
    `;
}

// ============================================================================
// CHAT MODE
// ============================================================================

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    // Add user message
    addChatMessage('user', message);
    input.value = '';
    
    // Simulate bot response
    setTimeout(() => {
        const responses = [
            'That\'s a great question about GLM transformations!',
            'The ∆∞Θ triad represents different abstraction levels.',
            'You can transform content between text, code, geometry, and image domains.',
            'Try using the Transform Mode to see symbolic representations.',
            'The Unified Search mode helps find relevant documents with triad-aware ranking.'
        ];
        const response = responses[Math.floor(Math.random() * responses.length)];
        addChatMessage('bot', response);
    }, 500);
}

function addChatMessage(sender, text) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;
    
    const messageEl = document.createElement('div');
    messageEl.className = `message ${sender}`;
    messageEl.innerHTML = `<p>${escapeHtml(text)}</p>`;
    messagesDiv.appendChild(messageEl);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ============================================================================
// UNIFIED SEARCH MODE
// ============================================================================

async function performSearch() {
    if (!currentState.apiOnline) {
        showError('❌ API is not online');
        return;
    }
    
    const query = document.getElementById('searchQuery')?.value.trim();
    if (!query) {
        showError('Please enter a search query.');
        return;
    }
    
    const btn = document.getElementById('searchBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Searching...';
    
    try {
        const payload = {
            query: query,
            k: 5,
            triad_target: document.getElementById('triadTarget')?.value || 'auto'
        };
        
        const response = await fetch(`${API_BASE_URL}/unified/search`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            credentials: 'omit',
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySearchResults(data);
            showSuccess('✅ Search completed!');
        } else {
            const error = await response.json();
            showError(`❌ Error: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔍 Search';
    }
}

async function generateAnswer() {
    if (!currentState.apiOnline) {
        showError('❌ API is not online');
        return;
    }
    
    const query = document.getElementById('searchQuery')?.value.trim();
    if (!query) {
        showError('Please enter a query first.');
        return;
    }
    
    const btn = document.getElementById('answerBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Generating...';
    
    try {
        const payload = {
            query: query,
            k: 5,
            triad_target_mode: document.getElementById('triadTarget')?.value || 'auto'
        };
        
        const response = await fetch(`${API_BASE_URL}/unified/answer`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            credentials: 'omit',
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            displayAnswer(data);
            showSuccess('✅ Answer generated!');
        } else {
            const error = await response.json();
            showError(`❌ Error: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📝 Generate Answer';
    }
}

function displaySearchResults(data) {
    const resultsDiv = document.getElementById('searchResults');
    if (!resultsDiv) return;
    
    let html = '<div class="search-results-list">';
    if (data.results && data.results.length > 0) {
        data.results.forEach((result, i) => {
            html += `
                <div class="search-result-item">
                    <h4>Result ${i + 1}</h4>
                    <p>${escapeHtml(result.text)}</p>
                    <p class="score">Score: ${(result.score * 100).toFixed(1)}%</p>
                </div>
            `;
        });
    } else {
        html += '<p class="placeholder">No results found.</p>';
    }
    html += '</div>';
    resultsDiv.innerHTML = html;
}

function displayAnswer(data) {
    const answerDiv = document.getElementById('answerResult');
    if (!answerDiv) return;
    
    answerDiv.innerHTML = `
        <div class="result-section">
            <p>${escapeHtml(data.answer)}</p>
            <p class="metadata">Style: ${data.style} | Documents: ${data.num_documents}</p>
        </div>
    `;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showError(message) {
    console.error('❌', message);
    const alertEl = document.getElementById('alert');
    if (alertEl) {
        alertEl.innerHTML = `<div class="alert alert-error">${message}</div>`;
        setTimeout(() => {
            alertEl.innerHTML = '';
        }, 5000);
    }
}

function showSuccess(message) {
    console.log('✅', message);
    const alertEl = document.getElementById('alert');
    if (alertEl) {
        alertEl.innerHTML = `<div class="alert alert-success">${message}</div>`;
        setTimeout(() => {
            alertEl.innerHTML = '';
        }, 3000);
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

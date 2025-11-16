/**
 * GLM v4.0 Web UI - Application Logic
 * Handles all interactions with the unified backend API
 */

const API_BASE_URL = 'http://localhost:8000';
const API_TIMEOUT = 10000;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showAlert(message, type = 'info') {
    const alertEl = document.getElementById('alert');
    alertEl.textContent = message;
    alertEl.className = `alert show ${type}`;
    setTimeout(() => alertEl.classList.remove('show'), 5000);
}

function setLoading(buttonId, loading = true) {
    const btn = document.getElementById(buttonId);
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Processing...';
    } else {
        btn.disabled = false;
        btn.innerHTML = btn.getAttribute('data-original-text') || btn.textContent;
    }
}

async function fetchAPI(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.mode-content').forEach(el => {
        el.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Mark button as active
    event.target.classList.add('active');
}

function updateStatus(online = false) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    if (online) {
        dot.classList.remove('offline');
        dot.classList.add('online');
        text.textContent = 'API Online';
    } else {
        dot.classList.remove('online');
        dot.classList.add('offline');
        text.textContent = 'API Offline';
    }
}

function displayTriad(triad, containerId) {
    const container = document.getElementById(containerId);
    if (!triad) return;
    
    const html = `
        <div class="triad-item">
            <div class="triad-label">∆ Delta</div>
            <div class="triad-value">${(triad.delta || 0).toFixed(3)}</div>
            <div class="triad-bar">
                <div class="triad-bar-fill" style="width: ${(triad.delta || 0) * 100}%"></div>
            </div>
        </div>
        <div class="triad-item">
            <div class="triad-label">∞ Infinity</div>
            <div class="triad-value">${(triad.infinity || 0).toFixed(3)}</div>
            <div class="triad-bar">
                <div class="triad-bar-fill" style="width: ${(triad.infinity || 0) * 100}%"></div>
            </div>
        </div>
        <div class="triad-item">
            <div class="triad-label">Θ Theta</div>
            <div class="triad-value">${(triad.theta || 0).toFixed(3)}</div>
            <div class="triad-bar">
                <div class="triad-bar-fill" style="width: ${(triad.theta || 0) * 100}%"></div>
            </div>
        </div>
    `;
    container.innerHTML = html;
}

// ============================================================================
// ENCODE FUNCTION
// ============================================================================

async function encodeContent() {
    const content = document.getElementById('encodeInput').value;
    const domain = document.getElementById('encodeDomain').value;
    
    if (!content.trim()) {
        showAlert('Please enter content to encode', 'error');
        return;
    }
    
    try {
        const result = await fetchAPI('/transform', 'POST', {
            content: content,
            domain: domain
        });
        
        const resultBox = document.getElementById('encodeResult');
        document.getElementById('encodeResultText').innerHTML = `
            <strong>Embedding Shape:</strong> ${result.embedding ? result.embedding.length : 'N/A'}<br>
            <strong>Content Type:</strong> ${result.content_type || 'unknown'}<br>
            <strong>Domain:</strong> ${result.domain || 'auto'}
        `;
        
        if (result.triad) {
            displayTriad(result.triad, 'encodeTriad');
        }
        
        resultBox.style.display = 'block';
        showAlert('✅ Encoding successful!', 'success');
    } catch (error) {
        showAlert('❌ Encoding failed: ' + error.message, 'error');
    }
}

// ============================================================================
// SEARCH FUNCTION
// ============================================================================

async function performSearch() {
    const query = document.getElementById('searchQuery').value;
    const mode = document.getElementById('searchMode').value;
    const k = parseInt(document.getElementById('searchK').value);
    
    if (!query.trim()) {
        showAlert('Please enter a search query', 'error');
        return;
    }
    
    try {
        const result = await fetchAPI('/unified/search', 'POST', {
            query: query,
            triad_target: mode,
            k: k
        });
        
        const resultsDiv = document.getElementById('searchResults');
        const resultsList = document.getElementById('searchResultsList');
        
        if (result.results && result.results.length > 0) {
            resultsList.innerHTML = result.results.map(r => `
                <div class="result-item">
                    <h4>${r.doc_id}</h4>
                    <p>${r.content || 'No content'}</p>
                    <span class="score-badge">Score: ${(r.score || 0).toFixed(3)}</span>
                </div>
            `).join('');
        } else {
            resultsList.innerHTML = '<p>No results found</p>';
        }
        
        resultsDiv.style.display = 'block';
        showAlert('✅ Search completed!', 'success');
    } catch (error) {
        showAlert('❌ Search failed: ' + error.message, 'error');
    }
}

// ============================================================================
// Q&A FUNCTION
// ============================================================================

async function generateAnswer() {
    const query = document.getElementById('qaQuery').value;
    const k = parseInt(document.getElementById('qaContext').value);
    
    if (!query.trim()) {
        showAlert('Please enter a question', 'error');
        return;
    }
    
    try {
        const result = await fetchAPI('/unified/answer', 'POST', {
            query: query,
            k: k
        });
        
        const resultBox = document.getElementById('qaResult');
        document.getElementById('qaResultText').textContent = result.answer || 'No answer generated';
        resultBox.style.display = 'block';
        showAlert('✅ Answer generated!', 'success');
    } catch (error) {
        showAlert('❌ Answer generation failed: ' + error.message, 'error');
    }
}

// ============================================================================
// TRANSFORM FUNCTION
// ============================================================================

async function transformContent() {
    const content = document.getElementById('transformInput').value;
    const fromDomain = document.getElementById('transformFrom').value;
    const toDomain = document.getElementById('transformTo').value;
    
    if (!content.trim()) {
        showAlert('Please enter content to transform', 'error');
        return;
    }
    
    try {
        const result = await fetchAPI('/transform', 'POST', {
            content: content,
            from_domain: fromDomain,
            to_domain: toDomain
        });
        
        const resultBox = document.getElementById('transformResult');
        document.getElementById('transformResultText').textContent = result.transformed || 'Transformation failed';
        resultBox.style.display = 'block';
        showAlert('✅ Transformation successful!', 'success');
    } catch (error) {
        showAlert('❌ Transformation failed: ' + error.message, 'error');
    }
}

// ============================================================================
// SIMILARITY FUNCTION
// ============================================================================

async function computeSimilarity() {
    const content1 = document.getElementById('sim1').value;
    const content2 = document.getElementById('sim2').value;
    
    if (!content1.trim() || !content2.trim()) {
        showAlert('Please enter both contents', 'error');
        return;
    }
    
    try {
        const result = await fetchAPI('/similarity', 'POST', {
            content1: content1,
            content2: content2
        });
        
        const score = result.similarity || 0;
        const resultBox = document.getElementById('similarityResult');
        document.getElementById('similarityScore').textContent = score.toFixed(3);
        document.getElementById('similarityBar').style.width = (score * 100) + '%';
        resultBox.style.display = 'block';
        showAlert('✅ Similarity calculated!', 'success');
    } catch (error) {
        showAlert('❌ Similarity calculation failed: ' + error.message, 'error');
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateStatus(true);
        } else {
            updateStatus(false);
        }
    } catch (error) {
        updateStatus(false);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    
    // Check API status every 5 seconds
    setInterval(checkAPIStatus, 5000);
    
    // Store original button text
    document.querySelectorAll('.btn').forEach(btn => {
        btn.setAttribute('data-original-text', btn.innerHTML);
    });
});

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

document.addEventListener('keydown', (e) => {
    // Ctrl+Enter to submit in textareas
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeTab = document.querySelector('.mode-content.active');
        if (activeTab.id === 'encode') encodeContent();
        else if (activeTab.id === 'search') performSearch();
        else if (activeTab.id === 'qa') generateAnswer();
        else if (activeTab.id === 'transform') transformContent();
        else if (activeTab.id === 'similarity') computeSimilarity();
    }
});

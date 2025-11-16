/**
 * GLM v3.0 - Web UI Application (Fixed)
 * =====================================
 * 
 * Main application logic for the GLM web interface
 * Backend: http://localhost:8081
 */

// Configuration
const API_BASE_URL = 'http://localhost:8081';
const REFRESH_INTERVAL = 5000; // 5 seconds

// State
let currentState = {
    sourceDomain: 'text',
    targetDomain: 'code',
    content: '',
    lastResult: null,
    apiOnline: false
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
    
    // Load initial data
    loadDomains();
});

// ============================================================================
// API STATUS CHECK
// ============================================================================

async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            currentState.apiOnline = true;
            updateAPIStatus(true);
            console.log('✅ API is online');
        } else {
            currentState.apiOnline = false;
            updateAPIStatus(false);
            console.warn('⚠️ API returned non-200 status');
        }
    } catch (error) {
        currentState.apiOnline = false;
        updateAPIStatus(false);
        console.error('❌ API is offline:', error.message);
    }
}

function updateAPIStatus(online) {
    const statusEl = document.getElementById('apiStatus');
    if (!statusEl) return;
    
    if (online) {
        statusEl.innerHTML = '✅ API Online';
        statusEl.className = 'api-status online';
    } else {
        statusEl.innerHTML = '❌ API Offline - Backend not responding on port 8081';
        statusEl.className = 'api-status offline';
    }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Domain selectors
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
}

// ============================================================================
// API CALLS
// ============================================================================

async function loadDomains() {
    try {
        const response = await fetch(`${API_BASE_URL}/domains`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Domains loaded:', data.domains);
        }
    } catch (error) {
        console.error('Error loading domains:', error);
    }
}

async function performTransform() {
    if (!currentState.apiOnline) {
        showError('❌ API is not online. Backend must be running on port 8081');
        return;
    }
    
    if (!currentState.content.trim()) {
        showError('Please enter content to transform.');
        return;
    }
    
    const btn = document.getElementById('transformBtn');
    if (!btn) return;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Transforming...';
    
    try {
        const payload = {
            content: currentState.content,
            source_domain: currentState.sourceDomain,
            target_domain: currentState.targetDomain
        };
        
        console.log('📤 Sending transform request:', payload);
        
        const response = await fetch(`${API_BASE_URL}/transform`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            currentState.lastResult = data;
            displayTransformResult(data);
            showSuccess('✅ Transformation completed successfully!');
            console.log('✅ Transform result:', data);
        } else {
            const error = await response.json();
            showError(`❌ Transformation failed: ${error.detail || 'Unknown error'}`);
            console.error('Transform error:', error);
        }
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
        console.error('Transform exception:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔄 Transform';
    }
}

async function performSimilarity() {
    if (!currentState.apiOnline) {
        showError('❌ API is not online. Backend must be running on port 8081');
        return;
    }
    
    const content1 = document.getElementById('similarityInput1')?.value.trim();
    const content2 = document.getElementById('similarityInput2')?.value.trim();
    
    if (!content1 || !content2) {
        showError('Please enter both contents for similarity comparison.');
        return;
    }
    
    const btn = document.getElementById('similarityBtn');
    if (!btn) return;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Calculating...';
    
    try {
        const payload = {
            content1: content1,
            content2: content2,
            domain: currentState.sourceDomain
        };
        
        console.log('📤 Sending similarity request:', payload);
        
        const response = await fetch(`${API_BASE_URL}/similarity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySimilarityResult(data);
            showSuccess('✅ Similarity calculated successfully!');
            console.log('✅ Similarity result:', data);
        } else {
            const error = await response.json();
            showError(`❌ Similarity calculation failed: ${error.detail || 'Unknown error'}`);
            console.error('Similarity error:', error);
        }
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
        console.error('Similarity exception:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Calculate Similarity';
    }
}

// ============================================================================
// DISPLAY FUNCTIONS
// ============================================================================

function updateInputContainer() {
    const container = document.getElementById('inputContainer');
    if (!container) return;
    
    const domain = currentState.sourceDomain;
    
    let inputHTML = '';
    
    switch(domain) {
        case 'code':
            inputHTML = `<textarea id="textInput" placeholder="Enter Python code..." class="input-field">def hello(name):
    return f"Hello, {name}!"</textarea>`;
            break;
        case 'text':
            inputHTML = `<textarea id="textInput" placeholder="Enter text..." class="input-field">Artificial intelligence is revolutionizing technology.</textarea>`;
            break;
        case 'geometry':
            inputHTML = `<textarea id="textInput" placeholder="Enter geometry description..." class="input-field">triangle</textarea>`;
            break;
        case 'image':
            inputHTML = `<textarea id="textInput" placeholder="Enter image description..." class="input-field">A red square on a white background</textarea>`;
            break;
        default:
            inputHTML = `<textarea id="textInput" placeholder="Enter content..." class="input-field"></textarea>`;
    }
    
    container.innerHTML = inputHTML;
    
    // Re-attach event listener
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
            <h3>Transformation Result</h3>
            <pre>${escapeHtml(data.result)}</pre>
            <div class="metadata">
                <p><strong>Source Domain:</strong> ${data.source_domain}</p>
                <p><strong>Target Domain:</strong> ${data.target_domain}</p>
                <div class="triad-display">
                    <p><strong>Triad (∆∞Θ):</strong></p>
                    <ul>
                        <li>Delta (∆): ${(data.triad.delta * 100).toFixed(1)}%</li>
                        <li>Infinity (∞): ${(data.triad.infinity * 100).toFixed(1)}%</li>
                        <li>Theta (Θ): ${(data.triad.theta * 100).toFixed(1)}%</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function displaySimilarityResult(data) {
    const resultContent = document.getElementById('resultContent');
    if (!resultContent) return;
    
    resultContent.innerHTML = `
        <div class="result-section">
            <h3>Similarity Result</h3>
            <div class="similarity-score">
                <p><strong>Similarity Score:</strong> ${(data.similarity * 100).toFixed(1)}%</p>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${data.similarity * 100}%"></div>
                </div>
            </div>
            <div class="metadata">
                <p><strong>Domain:</strong> ${data.domain}</p>
            </div>
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
        alertEl.style.display = 'block';
        setTimeout(() => {
            alertEl.style.display = 'none';
        }, 5000);
    }
}

function showSuccess(message) {
    console.log('✅', message);
    const alertEl = document.getElementById('alert');
    if (alertEl) {
        alertEl.innerHTML = `<div class="alert alert-success">${message}</div>`;
        alertEl.style.display = 'block';
        setTimeout(() => {
            alertEl.style.display = 'none';
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

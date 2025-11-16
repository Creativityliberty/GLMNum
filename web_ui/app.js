/**
 * GLM v4.0 Web UI - Complete Application Logic
 * Handles all interactions with the unified backend API
 */

const API_BASE_URL = "http://localhost:8081";
const API_TIMEOUT = 10000;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showAlert(message, type = "info") {
  const alertEl = document.getElementById("alert");
  alertEl.textContent = message;
  alertEl.className = `alert show ${type}`;
  setTimeout(() => alertEl.classList.remove("show"), 5000);
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem(
    "darkMode",
    document.body.classList.contains("dark-mode")
  );
}

function switchTab(tabName, event) {
  // Hide all tabs
  document.querySelectorAll(".mode-content").forEach((el) => {
    el.classList.remove("active");
  });

  // Remove active from all buttons
  document.querySelectorAll(".tab-button").forEach((el) => {
    el.classList.remove("active");
  });

  // Show selected tab
  document.getElementById(tabName).classList.add("active");

  // Mark button as active
  event.target.closest(".tab-button").classList.add("active");
}

function updateStatus(online = false) {
  const dot = document.getElementById("statusDot");
  const text = document.getElementById("statusText");

  if (online) {
    dot.classList.remove("offline");
    dot.classList.add("online");
    text.textContent = "✅ API Online";
  } else {
    dot.classList.remove("online");
    dot.classList.add("offline");
    text.textContent = "❌ API Offline";
  }
}

function displayTriad(triad, containerId) {
  const container = document.getElementById(containerId);
  if (!triad) return;

  const delta = triad.delta || 0;
  const infinity = triad.infinity || 0;
  const theta = triad.theta || 0;

  const html = `
        <div class="triad-item">
            <div class="triad-label">∆ Delta</div>
            <div class="triad-value">${delta.toFixed(3)}</div>
            <div class="triad-bar">
                <div class="triad-bar-fill" style="width: ${
                  delta * 100
                }%"></div>
            </div>
        </div>
        <div class="triad-item">
            <div class="triad-label">∞ Infinity</div>
            <div class="triad-value">${infinity.toFixed(3)}</div>
            <div class="triad-bar">
                <div class="triad-bar-fill" style="width: ${
                  infinity * 100
                }%"></div>
            </div>
        </div>
        <div class="triad-item">
            <div class="triad-label">Θ Theta</div>
            <div class="triad-value">${theta.toFixed(3)}</div>
            <div class="triad-bar">
                <div class="triad-bar-fill" style="width: ${
                  theta * 100
                }%"></div>
            </div>
        </div>
    `;
  container.innerHTML = html;
}

async function fetchAPI(endpoint, method = "GET", data = null) {
  try {
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
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
    console.error("API Error:", error);
    throw error;
  }
}

// ============================================================================
// ENCODE FUNCTION
// ============================================================================

async function encodeContent() {
  const content = document.getElementById("encodeInput").value;
  const domain = document.getElementById("encodeDomain").value;

  if (!content.trim()) {
    showAlert("❌ Please enter content to encode", "error");
    return;
  }

  try {
    showAlert("⏳ Encoding...", "info");
    const result = await fetchAPI("/transform", "POST", {
      content: content,
      source_domain: domain,
      target_domain: domain,
    });

    const resultBox = document.getElementById("encodeResult");
    const embeddingSize = result.embedding ? result.embedding.length : "N/A";

    document.getElementById("encodeResultText").innerHTML = `
            <strong>✅ Encoding Successful</strong><br>
            <strong>Embedding Size:</strong> ${embeddingSize}<br>
            <strong>Content Type:</strong> ${
              result.content_type || "unknown"
            }<br>
            <strong>Domain:</strong> ${result.domain || "auto"}
        `;

    if (result.triad) {
      displayTriad(result.triad, "encodeTriad");
    }

    resultBox.style.display = "block";
    resultBox.classList.add("success");
    showAlert("✅ Encoding successful!", "success");
  } catch (error) {
    showAlert("❌ Encoding failed: " + error.message, "error");
  }
}

// ============================================================================
// SEARCH FUNCTION
// ============================================================================

async function performSearch() {
  const query = document.getElementById("searchQuery").value;
  const mode = document.getElementById("searchMode").value;
  const k = parseInt(document.getElementById("searchK").value);

  if (!query.trim()) {
    showAlert("❌ Please enter a search query", "error");
    return;
  }

  try {
    showAlert("⏳ Searching...", "info");
    const result = await fetchAPI("/unified/search", "POST", {
      query: query,
      triad_target: mode,
      k: parseInt(k),
    });

    const resultsDiv = document.getElementById("searchResults");
    const resultsList = document.getElementById("searchResultsList");

    if (result.results && result.results.length > 0) {
      resultsList.innerHTML = result.results
        .map(
          (r, idx) => `
                <div class="result-item">
                    <h4>${idx + 1}. ${r.doc_id}</h4>
                    <p>${r.content || "No content available"}</p>
                    <span class="score-badge">
                        <i class="fas fa-star"></i> Score: ${(
                          r.score || 0
                        ).toFixed(3)}
                    </span>
                </div>
            `
        )
        .join("");
    } else {
      resultsList.innerHTML = "<p>No results found</p>";
    }

    resultsDiv.style.display = "block";
    showAlert(
      `✅ Found ${result.results ? result.results.length : 0} results!`,
      "success"
    );
  } catch (error) {
    showAlert("❌ Search failed: " + error.message, "error");
  }
}

// ============================================================================
// Q&A FUNCTION
// ============================================================================

async function generateAnswer() {
  const query = document.getElementById("qaQuery").value;
  const k = parseInt(document.getElementById("qaContext").value);

  if (!query.trim()) {
    showAlert("❌ Please enter a question", "error");
    return;
  }

  try {
    showAlert("⏳ Generating answer...", "info");
    const result = await fetchAPI("/unified/answer", "POST", {
      query: query,
      k: parseInt(k),
      triad_target_mode: "auto",
    });

    const resultBox = document.getElementById("qaResult");
    document.getElementById("qaResultText").textContent =
      result.answer || "No answer generated";
    resultBox.style.display = "block";
    resultBox.classList.add("success");
    showAlert("✅ Answer generated!", "success");
  } catch (error) {
    showAlert("❌ Answer generation failed: " + error.message, "error");
  }
}

// ============================================================================
// TRANSFORM FUNCTION
// ============================================================================

async function transformContent() {
  const content = document.getElementById("transformInput").value;
  const fromDomain = document.getElementById("transformFrom").value;
  const toDomain = document.getElementById("transformTo").value;

  if (!content.trim()) {
    showAlert("❌ Please enter content to transform", "error");
    return;
  }

  try {
    showAlert("⏳ Transforming...", "info");
    const result = await fetchAPI("/transform", "POST", {
      content: content,
      source_domain: fromDomain,
      target_domain: toDomain,
    });

    const resultBox = document.getElementById("transformResult");
    document.getElementById("transformResultText").textContent =
      result.transformed || "Transformation failed";
    resultBox.style.display = "block";
    resultBox.classList.add("success");
    showAlert("✅ Transformation successful!", "success");
  } catch (error) {
    showAlert("❌ Transformation failed: " + error.message, "error");
  }
}

// ============================================================================
// SIMILARITY FUNCTION
// ============================================================================

async function computeSimilarity() {
  const content1 = document.getElementById("sim1").value;
  const content2 = document.getElementById("sim2").value;

  if (!content1.trim() || !content2.trim()) {
    showAlert("❌ Please enter both contents", "error");
    return;
  }

  try {
    showAlert("⏳ Computing similarity...", "info");
    const result = await fetchAPI("/similarity", "POST", {
      content1: content1,
      content2: content2,
      domain: "text",
    });

    const score = result.similarity || 0;
    const resultBox = document.getElementById("similarityResult");
    document.getElementById("similarityScore").textContent = score.toFixed(3);

    const percentage = Math.round(score * 100);
    const barFill = document.getElementById("similarityBar");
    barFill.style.width = score * 100 + "%";
    document.getElementById("similarityPercent").textContent = percentage + "%";

    resultBox.style.display = "block";
    resultBox.classList.add("success");
    showAlert("✅ Similarity calculated!", "success");
  } catch (error) {
    showAlert("❌ Similarity calculation failed: " + error.message, "error");
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
document.addEventListener("DOMContentLoaded", () => {
  // Check dark mode preference
  if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark-mode");
  }

  // Check API status
  checkAPIStatus();

  // Check API status every 5 seconds
  setInterval(checkAPIStatus, 5000);

  // Add keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const activeTab = document.querySelector(".mode-content.active");
      if (activeTab.id === "encode") encodeContent();
      else if (activeTab.id === "search") performSearch();
      else if (activeTab.id === "qa") generateAnswer();
      else if (activeTab.id === "transform") transformContent();
      else if (activeTab.id === "similarity") computeSimilarity();
    }
  });
});

// Configuration
const API_URL = 'http://localhost:8000/recommend';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const toggleExamples = document.getElementById('toggleExamples');
const examplesGrid = document.getElementById('examplesGrid');
const resultsSection = document.getElementById('resultsSection');
const resultsTitle = document.getElementById('resultsTitle');
const resultsContainer = document.getElementById('resultsContainer');
const noResults = document.getElementById('noResults');
const errorMessage = document.getElementById('errorMessage');

// State
let isSearching = false;

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isSearching) {
        handleSearch();
    }
});

toggleExamples.addEventListener('click', () => {
    const isVisible = examplesGrid.style.display === 'grid';
    examplesGrid.style.display = isVisible ? 'none' : 'grid';
    toggleExamples.textContent = isVisible ? '💡 Try example queries' : '❌ Hide examples';
});

// Example tags click handlers
document.querySelectorAll('.example-tag').forEach(tag => {
    tag.addEventListener('click', () => {
        searchInput.value = tag.textContent;
        examplesGrid.style.display = 'none';
        toggleExamples.textContent = '💡 Try example queries';
        handleSearch();
    });
});

// Main search handler
async function handleSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        showError('Please enter a hiring description');
        return;
    }

    if (isSearching) return;

    // Reset UI
    hideError();
    hideNoResults();
    hideResults();
    
    // Show loading state
    setLoadingState(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 10  // Request only top 10 results
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Search error:', error);
        if (error.message.includes('Failed to fetch')) {
            showError('Cannot connect to backend. Please ensure the FastAPI server is running on http://127.0.0.1:8000');
        } else {
            showError(`Error: ${error.message}`);
        }
    } finally {
        setLoadingState(false);
    }
}

// Display results
function displayResults(data) {
    const { query, total_found, results } = data;

    if (total_found === 0) {
        showNoResults();
        return;
    }

    // Show results section
    resultsSection.style.display = 'block';
    resultsTitle.textContent = `Found ${total_found} recommended assessment${total_found > 1 ? 's' : ''} for: "${query}"`;
    
    // Clear previous results
    resultsContainer.innerHTML = '';

    // Create result cards
    results.forEach((result, index) => {
        const card = createResultCard(result, index + 1);
        resultsContainer.appendChild(card);
    });

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create individual result card
function createResultCard(result, rank) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    const scorePercent = (result.score * 100).toFixed(1);
    
    card.innerHTML = `
        <div class="result-header">
            <a href="${result.url}" target="_blank" class="result-title">
                ${result.name}
            </a>
            <div class="result-rank">${rank}</div>
        </div>

        <div class="score-section">
            <div class="score-label">Match Score</div>
            <div class="score-bar">
                <div class="score-fill" style="width: ${scorePercent}%"></div>
            </div>
            <div class="score-value">${scorePercent}%</div>
        </div>

        <div class="result-description">
            ${result.description || 'No description available'}
        </div>

        <div class="metadata-grid">
            <div class="metadata-item">
                <div class="metadata-label">Test Type</div>
                <div class="metadata-value">${result.test_type || 'N/A'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Duration</div>
                <div class="metadata-value">${result.duration || 'N/A'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Remote Testing</div>
                <div class="metadata-value">${result.remote_testing || 'N/A'}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Adaptive/IRT</div>
                <div class="metadata-value">${result.adaptive || 'N/A'}</div>
            </div>
        </div>
    `;

    // Animate score bar
    setTimeout(() => {
        const scoreFill = card.querySelector('.score-fill');
        scoreFill.style.width = `${scorePercent}%`;
    }, 100);

    return card;
}

// UI Helper Functions
function setLoadingState(loading) {
    isSearching = loading;
    searchBtn.disabled = loading;
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
    } else {
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showNoResults() {
    noResults.style.display = 'block';
    resultsSection.style.display = 'none';
}

function hideNoResults() {
    noResults.style.display = 'none';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch('http://127.0.0.1:8000/health');
        if (response.ok) {
            console.log('✅ Backend API is running');
        }
    } catch (error) {
        console.warn('⚠️ Backend API may not be running');
    }
}

// Initialize
checkAPIHealth();
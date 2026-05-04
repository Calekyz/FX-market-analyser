// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const analyzeContainer = document.getElementById('analyzeContainer');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const signalContent = document.getElementById('signalContent');

let currentImageFile = null;

// Upload area click
if (uploadArea) {
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImage(file);
        }
    });
}

// File input change
if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleImage(e.target.files[0]);
        }
    });
}

function handleImage(file) {
    currentImageFile = file;
    const reader = new FileReader();
    
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        previewContainer.style.display = 'block';
        analyzeContainer.style.display = 'block';
        if (uploadArea) uploadArea.style.display = 'none';
        results.style.display = 'none';
    };
    
    reader.readAsDataURL(file);
}

// Analyze button
if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
        if (!currentImageFile) return;
        
        const formData = new FormData();
        formData.append('image', currentImageFile);
        formData.append('risk_percent', '1.0');
        
        loading.style.display = 'block';
        results.style.display = 'none';
        analyzeBtn.disabled = true;
        
        try {
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            signalContent.innerHTML = `
                <div class="signal-card" style="color: #ff4444;">
                    <strong>❌ Error</strong><br>
                    Failed to analyze chart. Please check your connection and try again.
                </div>
            `;
            results.style.display = 'block';
        } finally {
            loading.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });
}

function displayResults(data) {
    if (data.status === 'success' && data.analysis) {
        const analysis = data.analysis;
        const trade = analysis.trade;
        
        const signalClass = trade.action === 'BUY' ? 'signal-buy' : 
                           (trade.action === 'SELL' ? 'signal-sell' : 'signal-wait');
        
        const actionColor = trade.action === 'BUY' ? '#00ff88' : 
                           (trade.action === 'SELL' ? '#ff4444' : '#ffaa00');
        
        let html = `
            <div class="signal-card ${signalClass}">
                <div style="font-size: 2.5rem; text-align: center; margin-bottom: 20px;">
                    ${trade.action === 'BUY' ? '📈 BUY' : (trade.action === 'SELL' ? '📉 SELL' : '⏳ WAIT')}
                </div>
                
                <div class="price-grid">
                    <div class="price-item">
                        <div class="price-label">Current Price</div>
                        <div class="price-value">${analysis.current_price || 'N/A'}</div>
                    </div>
                    ${analysis.pattern ? `
                    <div class="price-item">
                        <div class="price-label">Pattern</div>
                        <div class="price-value" style="font-size: 1rem;">${analysis.pattern}</div>
                    </div>
                    ` : ''}
                    <div class="price-item">
                        <div class="price-label">Confidence</div>
                        <div class="price-value">${Math.round((trade.confidence || 0) * 100)}%</div>
                    </div>
                </div>
        `;
        
        if (trade.action !== 'WAIT' && trade.entry) {
            html += `
                <div class="price-grid">
                    <div class="price-item">
                        <div class="price-label">📍 Entry</div>
                        <div class="price-value" style="color: ${actionColor};">${trade.entry}</div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">🛑 Stop Loss</div>
                        <div class="price-value" style="color: #ff6666;">${trade.sl || 'N/A'}</div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">✅ Take Profit 1</div>
                        <div class="price-value" style="color: #66ff66;">${trade.tp1 || 'N/A'}</div>
                    </div>
                    <div class="price-item">
                        <div class="price-label">🎯 Take Profit 2</div>
                        <div class="price-value" style="color: #66ff66;">${trade.tp2 || 'N/A'}</div>
                    </div>
                </div>
            `;
            
            if (trade.risk_reward) {
                html += `
                    <div style="text-align: center; margin: 20px 0;">
                        <span class="rr-badge">📐 Risk:Reward = 1:${trade.risk_reward}</span>
                    </div>
                `;
            }
        }
        
        if (trade.reasoning) {
            html += `
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                    <strong>💡 Analysis</strong><br>
                    ${trade.reasoning}
                </div>
            `;
        }
        
        if (analysis.support_levels && analysis.support_levels.length > 0) {
            html += `
                <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 10px; font-size: 0.8rem;">
                    <strong>🛡️ Key Supports:</strong> ${analysis.support_levels.join(' | ')}<br>
                    <strong>⚔️ Key Resistances:</strong> ${analysis.resistance_levels.join(' | ')}
                </div>
            `;
        }
        
        html += `</div>`;
        signalContent.innerHTML = html;
        
    } else {
        signalContent.innerHTML = `
            <div class="signal-card" style="color: #ffaa00;">
                <strong>⚠️ Unable to Analyze</strong><br>
                ${data.error || 'Could not extract clear trading data from this chart. Please try a clearer screenshot.'}
            </div>
        `;
    }
    
    results.style.display = 'block';
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Reset function
window.resetUpload = function() {
    currentImageFile = null;
    if (previewContainer) previewContainer.style.display = 'none';
    if (analyzeContainer) analyzeContainer.style.display = 'none';
    if (uploadArea) uploadArea.style.display = 'block';
    if (results) results.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (imagePreview) imagePreview.src = '';
};

// Check API health on load
async function checkHealth() {
    try {
        const response = await fetch('/api/v1/health');
        if (response.ok) {
            console.log('API is healthy');
        }
    } catch (error) {
        console.warn('API health check failed:', error);
    }
}

checkHealth();

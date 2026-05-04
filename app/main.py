from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

from app.services.image_processor import ImageProcessor
from app.services.vision_analyzer import VisionAnalyzer
from app.services.strategy_engine import StrategyEngine
from app.models.trade_signal import AnalysisResponse, TradeSignal, ChartAnalysis

load_dotenv()

app = FastAPI(
    title="Forex Chart Intelligence System",
    description="Analyze forex charts from photos and get trading signals",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Initialize services
image_processor = ImageProcessor()
vision_analyzer = VisionAnalyzer()
strategy_engine = StrategyEngine()

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# HTML response for main page
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Forex Chart Analyzer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 40px 20px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .header p {
            color: rgba(255,255,255,0.7);
            font-size: 1.1rem;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .upload-area {
            border: 2px dashed rgba(255,255,255,0.3);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #00d2ff;
            background: rgba(0,210,255,0.1);
        }
        
        .upload-area.drag-over {
            border-color: #00d2ff;
            background: rgba(0,210,255,0.2);
        }
        
        #imagePreview {
            max-width: 100%;
            max-height: 400px;
            margin: 20px 0;
            border-radius: 10px;
            display: none;
        }
        
        button {
            background: linear-gradient(135deg, #00d2ff, #3a7bd5);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 10px 0;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .results {
            display: none;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .signal-card {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        }
        
        .signal-buy {
            border-left: 5px solid #00ff88;
        }
        
        .signal-sell {
            border-left: 5px solid #ff4444;
        }
        
        .signal-wait {
            border-left: 5px solid #ffaa00;
        }
        
        .price-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .price-item {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .price-label {
            font-size: 0.8rem;
            color: rgba(255,255,255,0.6);
            text-transform: uppercase;
        }
        
        .price-value {
            font-size: 1.5rem;
            font-weight: bold;
            margin-top: 5px;
        }
        
        .rr-badge {
            background: #00ff88;
            color: #000;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: #00d2ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 1.8rem; }
            .card { padding: 20px; }
            .price-value { font-size: 1.2rem; }
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.5);
            font-size: 0.8rem;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .camera-btn {
            background: rgba(255,255,255,0.2);
            margin-left: 10px;
        }
        
        .disclaimer {
            background: rgba(255,0,0,0.1);
            border: 1px solid rgba(255,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            font-size: 0.8rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Forex Chart Analyzer</h1>
            <p>Take a photo or upload a chart → Get Entry, SL & TP instantly</p>
        </div>
        
        <div class="card">
            <div class="upload-area" id="uploadArea">
                <div style="font-size: 48px;">📸</div>
                <h3>Upload Chart Image</h3>
                <p>Click or drag & drop a chart screenshot/photo</p>
                <p style="font-size: 0.8rem; margin-top: 10px;">Supported: JPG, PNG, JPEG</p>
                <input type="file" id="fileInput" accept="image/*" capture="environment">
                <button class="camera-btn" onclick="document.getElementById('fileInput').click()">📷 Choose File</button>
            </div>
            
            <img id="imagePreview" alt="Preview">
            
            <div style="text-align: center; margin-top: 20px;">
                <button id="analyzeBtn" style="display: none;">🔍 Analyze Chart</button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing chart with AI...</p>
        </div>
        
        <div class="results card" id="results">
            <h2>🎯 Trade Signal</h2>
            <div id="signalContent"></div>
        </div>
        
        <div class="disclaimer">
            ⚠️ DISCLAIMER: This is AI-generated analysis for educational purposes only. 
            Always do your own research and never trade more than you can afford to lose.
        </div>
        
        <div class="footer">
            Powered by Google Gemini AI | Forex Chart Intelligence System v1.0
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const signalContent = document.getElementById('signalContent');
        
        let currentImageFile = null;
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
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
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files[0]) {
                handleImage(e.target.files[0]);
            }
        });
        
        function handleImage(file) {
            currentImageFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                analyzeBtn.style.display = 'inline-block';
                uploadArea.style.display = 'none';
                results.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
        
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
                signalContent.innerHTML = '<div class="signal-card" style="color: #ff4444;">❌ Error analyzing chart. Please try again.</div>';
                results.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        });
        
        function displayResults(data) {
            if (data.status === 'success') {
                const analysis = data.analysis;
                const trade = analysis.trade;
                
                const signalClass = trade.action === 'BUY' ? 'signal-buy' : (trade.action === 'SELL' ? 'signal-sell' : 'signal-wait');
                const actionColor = trade.action === 'BUY' ? '#00ff88' : (trade.action === 'SELL' ? '#ff4444' : '#ffaa00');
                
                let html = `
                    <div class="signal-card ${signalClass}">
                        <div style="font-size: 2rem; text-align: center; margin-bottom: 20px;">
                            ${trade.action === 'BUY' ? '📈 BUY' : (trade.action === 'SELL' ? '📉 SELL' : '⏳ WAIT')}
                        </div>
                        
                        <div class="price-grid">
                            <div class="price-item">
                                <div class="price-label">Current Price</div>
                                <div class="price-value">${analysis.current_price || 'N/A'}</div>
                            </div>
                            ${analysis.pattern ? `
                            <div class="price-item">
                                <div class="price-label">Pattern Detected</div>
                                <div class="price-value" style="font-size: 1rem;">${analysis.pattern}</div>
                            </div>
                            ` : ''}
                        </div>
                `;
                
                if (trade.action !== 'WAIT') {
                    html += `
                        <div class="price-grid">
                            <div class="price-item">
                                <div class="price-label">📍 Entry</div>
                                <div class="price-value" style="color: ${actionColor};">${trade.entry || 'N/A'}</div>
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
                        
                        <div style="text-align: center; margin-top: 15px;">
                            ${trade.risk_reward ? `<span class="rr-badge">Risk:Reward = 1:${trade.risk_reward}</span>` : ''}
                        </div>
                    `;
                }
                
                if (trade.reasoning) {
                    html += `<div style="margin-top: 20px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                        <strong>💡 Analysis:</strong> ${trade.reasoning}
                    </div>`;
                }
                
                html += `</div>`;
                signalContent.innerHTML = html;
            } else {
                signalContent.innerHTML = '<div class="signal-card" style="color: #ff4444;">❌ Failed to analyze chart. Please try again.</div>';
            }
            
            results.style.display = 'block';
        }
        
        // Reset functionality
        function resetUpload() {
            currentImageFile = null;
            imagePreview.style.display = 'none';
            analyzeBtn.style.display = 'none';
            uploadArea.style.display = 'block';
            results.style.display = 'none';
            fileInput.value = '';
        }
        
        // Add reset button if needed
        if (imagePreview) {
            imagePreview.addEventListener('click', resetUpload);
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(HTML_CONTENT)

@app.get("/dashboard")
async def dashboard():
    return HTMLResponse(HTML_CONTENT)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "forex-analyzer", "version": "1.0.0"}

@app.post("/api/v1/analyze")
async def analyze_chart(
    image: UploadFile = File(...),
    risk_percent: float = Form(1.0)
):
    start_time = time.time()
    
    # Validate file type
    if not image.content_type in ["image/jpeg", "image/png", "image/jpg"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Please upload JPEG or PNG"}
        )
    
    # Save temporary file
    temp_filename = f"uploads/{uuid.uuid4()}.jpg"
    
    with open(temp_filename, "wb") as f:
        f.write(await image.read())
    
    try:
        # Process image
        processed = image_processor.preprocess(temp_filename)
        
        # Analyze with Vision AI
        vision_data = await vision_analyzer.extract_chart_data(processed)
        
        # Generate trade signal
        trade_signal = strategy_engine.generate_signal(vision_data, risk_percent)
        
        # Build response
        analysis = ChartAnalysis(
            current_price=vision_data.get("current_price", 0),
            pattern=vision_data.get("pattern_detected"),
            support_levels=vision_data.get("support_levels", []),
            resistance_levels=vision_data.get("resistance_levels", []),
            indicators=vision_data.get("indicators", {}),
            trade=TradeSignal(**trade_signal)
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return AnalysisResponse(
            status="success",
            analysis=analysis,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    
    finally:
        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

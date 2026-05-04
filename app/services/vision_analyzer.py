import os
import json
import base64
import google.generativeai as genai
from loguru import logger

class VisionAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def extract_chart_data(self, image_array) -> dict:
        """Send chart image to Gemini for analysis"""
        
        # Convert numpy array to base64
        _, buffer = cv2.imencode('.png', image_array)
        image_base64 = base64.b64encode(buffer).decode()
        
        prompt = """
        Analyze this forex chart carefully. Return ONLY valid JSON with EXACTLY this structure.
        Do not add any other text before or after the JSON.
        
        {
            "current_price": 1.08945,
            "support_levels": [1.08500, 1.08200, 1.07800],
            "resistance_levels": [1.09200, 1.09500, 1.09850],
            "pattern_detected": "Double Bottom" or null,
            "trend": "bullish" or "bearish" or "sideways",
            "indicators": {
                "rsi": 45.5,
                "trend_strength": 0.7
            }
        }
        
        Rules:
        - current_price: the current market price on the chart
        - support_levels: 2-3 price levels where price has bounced up
        - resistance_levels: 2-3 price levels where price has bounced down
        - pattern_detected: name of any chart pattern or null
        - trend: overall direction of price movement
        - indicators: estimate RSI (0-100) and trend strength (0-1)
        
        If you cannot determine a value, use null or empty arrays.
        """
        
        try:
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/png", "data": image_base64}
            ])
            
            text = response.text.strip()
            # Remove markdown code blocks if present
            text = text.replace('```json', '').replace('```', '').strip()
            result = json.loads(text)
            
            logger.info(f"Vision analysis complete: pattern={result.get('pattern_detected')}, trend={result.get('trend')}")
            return result
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                "current_price": None,
                "support_levels": [],
                "resistance_levels": [],
                "pattern_detected": None,
                "trend": "sideways",
                "indicators": {}
            }

# Import cv2 here to avoid circular import
import cv2

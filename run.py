#!/usr/bin/env python3
"""
Forex Chart Intelligence System
Run with: python run.py
"""

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 FOREX CHART INTELLIGENCE SYSTEM")
    print("="*60)
    print("\n🚀 Starting server...")
    print("📍 Web interface: http://localhost:8000")
    print("📍 API docs: http://localhost:8000/docs")
    print("📍 Dashboard: http://localhost:8000/dashboard")
    print("\n⚠️  Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

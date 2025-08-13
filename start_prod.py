#!/usr/bin/env python3
"""
Production startup script for DigitalOcean App Platform
"""

import os
import uvicorn
from pathlib import Path

# Create uploads directory
Path("uploads").mkdir(exist_ok=True)

# Get port from environment (DigitalOcean sets this)
port = int(os.getenv("PORT", 8000))

# Production settings
if __name__ == "__main__":
    print(f"🚀 Starting Financial Statement Analysis API on port {port}...")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"🔑 API Key configured: {bool(os.getenv('GOOGLE_API_KEY'))}")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True,
        workers=1  # Single worker for App Platform
    )

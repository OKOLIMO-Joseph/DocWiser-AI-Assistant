import uvicorn
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("  WARNING: GEMINI_API_KEY not found in .env file")
        print("   Please add your Gemini API key to the .env file\n")
    else:
        print(" GEMINI_API_KEY found")
    
    print(" Starting DocWiser Backend Server...")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health\n")
    
    # Run with reload=False to prevent reload loops
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload to avoid loops
        log_level="info"
    )
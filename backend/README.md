# DocWiser Backend API

FastAPI backend for DocWiser AI Assistant with Google Gemini AI integration.

## Prerequisites

- Python 3.9+
- Google Gemini API Key

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo GEMINI_API_KEY=your_api_key_here > .env

# Run the server
python run.py
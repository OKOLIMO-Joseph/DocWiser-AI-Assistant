# 📄 DocWiser AI Assistant

An AI-powered document assistant that extracts text from PDF and Word documents, then uses Google's Gemini AI to generate summaries and extract key information like titles and authors.

## Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | [docwiser-frontend-875768844875.us-central1.run.app](https://docwiser-frontend-875768844875.us-central1.run.app) |
| **Backend API** | [docwiser-backend-875768844875.us-central1.run.app](https://docwiser-backend-875768844875.us-central1.run.app) |
| **API Docs** | [docwiser-backend-875768844875.us-central1.run.app/docs](https://docwiser-backend-875768844875.us-central1.run.app/docs) |

## Features

- 📁 Upload PDF and Word documents
- 📝 Automatically extracts text from documents
- 🤖 Uses Google Gemini AI to identify title, author, and summary
- 🎨 Clean, responsive web interface with drag-and-drop
- ⚡ Real-time analysis with loading states
- 🐳 Docker containerization for easy deployment

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React.js |
| Backend | FastAPI (Python) |
| AI/LLM | Google Gemini AI |
| Document Parsing | PyPDF2, python-docx |
| Deployment | Google Cloud Run, Docker |

## Prerequisites

- Python 3.9+
- Node.js 16+
- Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

## How to Run the Project

### 1. Clone the Repository
```bash
git clone https://github.com/OKOLIMO-Joseph/DocWiser-AI-Assistant.git
cd DocWiser-AI-Assistant



#Running the Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
echo GEMINI_API_KEY=your_api_key_here > .env
python run.py

#Running Frontend
cd frontend
npm install
npm start
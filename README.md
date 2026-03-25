# DocWiser AI Assistant

An AI-powered document assistant that extracts text from PDF and Word documents, then uses Google's Gemini AI to generate summaries and extract key information like titles and authors.

## Features

- **Document Upload**: Support for PDF and DOCX files
- **Text Extraction**: Automatically extracts text from uploaded documents
- **AI Analysis**: Uses Google Gemini AI to:
  - Extract document title
  - Identify author information
  - Generate concise summaries
- **Clean Interface**: Modern, responsive web interface
- **Real-time Processing**: Instant analysis with loading states

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **Google Gemini AI**: LLM for document analysis
- **PyPDF2 & python-docx**: Document parsing
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI framework
- **Axios**: HTTP client
- **React Dropzone**: File upload handling

## Prerequisites

- Python 3.9+
- Node.js 16+
- Google Gemini API Key

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/OKOLIMO-Joseph/docwiser-ai-assistant.git
cd docwiser-ai-assistant
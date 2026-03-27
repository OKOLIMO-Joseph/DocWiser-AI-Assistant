import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Backend URLs - both working
  const BACKEND_URLS = [
    'https://docwiser-backend-875768844875.us-central1.run.app',  // Cloud Run (Primary)
    'https://docwiser-backend.onrender.com'                       // Render (Fallback)
  ];

  const onDrop = useCallback((acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setError(null);
    setResult(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    maxSize: 10485760, // 10MB
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    // Try each backend URL until one works
    for (const backendUrl of BACKEND_URLS) {
      try {
        const response = await axios.post(`${backendUrl}/analyze`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000, // 30 second timeout
        });

        setResult(response.data);
        setLoading(false);
        return; // Success, exit the function
      } catch (err) {
        console.log(`Failed to connect to ${backendUrl}:`, err.message);
        // Continue to try next backend
      }
    }

    // If all backends fail
    setError('Unable to connect to the analysis service. Please try again later.');
    setLoading(false);
  };

  return (
    <div className="file-upload-container">
      <div className="upload-section">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>Drop your document here...</p>
          ) : (
            <div>
              <p>Drag & drop a document here, or click to select</p>
              <small>Supports PDF, DOCX (Max 10MB)</small>
            </div>
          )}
        </div>

        {file && (
          <div className="file-info">
            <p>Selected: {file.name}</p>
            <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
            <button
              onClick={handleUpload}
              disabled={loading}
              className="upload-button"
            >
              {loading ? 'Analyzing...' : 'Analyze Document'}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="result-section">
          <h2>Analysis Results</h2>
          <div className="result-card">
            <div className="result-item">
              <strong>Title:</strong>
              <p>{result.analysis.title}</p>
            </div>
            <div className="result-item">
              <strong>Author:</strong>
              <p>{result.analysis.author}</p>
            </div>
            <div className="result-item">
              <strong>Summary:</strong>
              <p>{result.analysis.summary}</p>
            </div>
            <div className="result-metadata">
              <small>
                Document: {result.filename} | 
                Words: {result.metadata.text_length} | 
                AI: {result.metadata.llm_provider}
              </small>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
import React from 'react';
import FileUpload from './components/FileUpload';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>📄 DocWiser AI Assistant</h1>
          <p>Upload your documents and let AI analyze them</p>
        </div>
      </header>
      <main className="app-main">
        <FileUpload />
      </main>
      <footer className="app-footer">
        <p>Powered by Google Gemini AI | DocWiser © 2026</p>
      </footer>
    </div>
  );
}

export default App;
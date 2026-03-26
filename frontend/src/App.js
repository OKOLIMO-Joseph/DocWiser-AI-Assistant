import React from 'react';
import FileUpload from './components/FileUpload';
import logo from './assets/docwiser-logo.png';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-title-container">
            <img src={logo} alt="DocWiser Logo" className="app-logo" />
            <div className="title-wrapper">
              <h1 className="app-title">DocWiser AI Assistant</h1>
              <p className="header-subtitle">Upload your documents and let AI analyze them</p>
            </div>
          </div>
        </div>
      </header>
      <main className="app-main">
        <FileUpload />
      </main>
      <footer className="app-footer">
        <div className="footer-content">
          <p className="creator-line">
            Created with ❤️ by <strong>Okolimo Joseph</strong>
          </p>
          <div className="social-links">
            <a href="https://github.com/OKOLIMO-Joseph" target="_blank" rel="noopener noreferrer">GitHub</a>
            <span className="separator">|</span>
            <a href="https://www.linkedin.com/in/joseph-okolimo-4b24b12b0" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            <span className="separator">|</span>
            <span>okolimojoseph1@gmail.com</span>
          </div>
          <p>Powered by Google Gemini AI | DocWiser © 2026</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
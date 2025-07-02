import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');

  useEffect(() => {
    // Fetch from the Nginx proxy endpoint which forwards to FastAPI backend
    fetch('/api/health')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setBackendStatus(`Backend Status: ${data.status}`);
      })
      .catch(error => {
        console.error("Error fetching backend status:", error);
        setBackendStatus(`Error: ${error.message}. Check backend logs.`);
      });
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          HealthMate-AI Frontend
        </p>
        <p>
          {backendStatus}
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
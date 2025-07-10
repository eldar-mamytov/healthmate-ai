import React, { useState } from 'react';
import api from '../api'; // Import the axios instance

const Login = ({ onLoginSuccess }) => { // onLoginSuccess prop to handle redirection/state update
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission
    setError('');
    setMessage('');

    try {
      // The /token endpoint expects x-www-form-urlencoded data, not JSON
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // Store the access token in localStorage
      localStorage.setItem('access_token', response.data.access_token);
      setMessage('Login successful!');
      setUsername('');
      setPassword('');

      // Call the success callback, e.g., to redirect user or update app state
      if (onLoginSuccess) {
        onLoginSuccess();
      }

    } catch (err) {
      console.error('Login error:', err.response ? err.response.data : err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail); // Display backend error message
      } else {
        setError('An unexpected error occurred during login.');
      }
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="loginUsername">Username or Email:</label>
          <input
            type="text"
            id="loginUsername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="loginPassword">Password:</label>
          <input
            type="password"
            id="loginPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Login;
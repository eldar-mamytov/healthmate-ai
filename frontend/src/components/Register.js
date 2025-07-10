import React, { useState } from 'react';
import api from '../api'; // Import the axios instance

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    setMessage(''); // Clear previous messages
    setError('');   // Clear previous errors

    try {
      const response = await api.post('/auth/register/', {
        username,
        email,
        password,
      });
      setMessage(`User registered successfully: ${response.data.username}`);
      setUsername('');
      setEmail('');
      setPassword('');
      // Optionally, redirect to login page after successful registration
      // history.push('/login');
    } catch (err) {
      console.error('Registration error:', err.response ? err.response.data : err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail); // Display backend error message
      } else {
        setError('An unexpected error occurred during registration.');
      }
    }
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Register</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Register;
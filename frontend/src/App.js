// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'; // NEW IMPORTS
import AuthForm from './components/AuthForm'; // Your existing login/register component
import ChatPage from './components/ChatPage'; // NEW IMPORT
import api from './api'; // Ensure your Axios instance is imported
import MedicalBackground from './components/MedicalBackground';
import './components/AuthForm.css'; 
import './components/ChatPage.css'; 
import './App.css'; // Your existing CSS

function App() {
    // State to track login status
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));

    // Function to call on successful login/registration
    const handleLoginSuccess = () => {
        setIsLoggedIn(true);
    };

    // Function to call on logout
    const handleLogout = () => {
        localStorage.removeItem('token'); // Clear token from local storage
        api.defaults.headers.common['Authorization'] = ''; // Clear Authorization header
        setIsLoggedIn(false); // Update login state
    };

    // Re-check login status on app load or whenever the token might change externally
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setIsLoggedIn(true);
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            setIsLoggedIn(false);
        }
    }, []); // Run once on component mount

    return (
        <BrowserRouter> {/* Wrap your entire app in BrowserRouter */}
            <div className="App" style={{ position: "relative", minHeight: "100vh", overflow: "hidden" }}>
                <MedicalBackground count={72}/>
                <div style={{ position: "relative", zIndex: 10 }}>
                <Routes>
                    {/* Route for the Login/Register page */}
                    <Route
                        path="/"
                        element={
                            isLoggedIn ? (
                                <Navigate to="/chat" replace /> // If logged in, redirect to chat
                            ) : (
                                <AuthForm onLoginSuccess={handleLoginSuccess} /> // Otherwise, show auth form
                            )
                        }
                    />

                    {/* Route for the Chat page */}
                    <Route
                        path="/chat"
                        element={
                            isLoggedIn ? (
                                <ChatPage onLogout={handleLogout} /> // If logged in, show chat page
                            ) : (
                                <Navigate to="/" replace /> // If not logged in, redirect to login
                            )
                        }
                    />

                    {/* Optional: Add a catch-all route for 404 (or redirect home) */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
                </div>
            </div>
        </BrowserRouter>
    );
}

export default App;
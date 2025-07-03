// frontend/src/components/AuthForm.js
import React, { useState } from 'react';
import Login from './Login'; // Import your existing Login component
import Register from './Register'; // Import your existing Register component
import './AuthForm.css'; // We'll create this CSS file next

const AuthForm = ({ onLoginSuccess }) => {
    const [isLoginView, setIsLoginView] = useState(true); // State to switch between login/register

    const toggleView = () => {
        setIsLoginView(!isLoginView);
    };

    return (
        <div className="auth-container">
            <div className="auth-tabs">
                <button
                    className={`tab-button ${isLoginView ? 'active' : ''}`}
                    onClick={() => setIsLoginView(true)}
                >
                    Login
                </button>
                <button
                    className={`tab-button ${!isLoginView ? 'active' : ''}`}
                    onClick={() => setIsLoginView(false)}
                >
                    Register
                </button>
            </div>

            <div className="auth-form-content">
                {isLoginView ? (
                    <Login onLoginSuccess={onLoginSuccess} />
                ) : (
                    <Register onLoginSuccess={onLoginSuccess} />
                )}
            </div>

            {/* You can remove or keep this toggle button if the tabs are sufficient */}
            {/*
            <p className="toggle-message">
                {isLoginView ? "Don't have an account?" : "Already have an account?"}{' '}
                <button onClick={toggleView} className="toggle-link">
                    {isLoginView ? 'Register here' : 'Login here'}
                </button>
            </p>
            */}
        </div>
    );
};

export default AuthForm;
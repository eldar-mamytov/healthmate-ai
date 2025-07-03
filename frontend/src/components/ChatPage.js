// frontend/src/components/ChatPage.js
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api'; // Your Axios instance
import './ChatPage.css'; // We'll create this file for styling

const ChatPage = ({ onLogout }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const messagesEndRef = useRef(null); // Ref for auto-scrolling to the bottom

    // Function to scroll to the bottom of messages
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Effect to scroll to bottom whenever messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Fetch chat history on component mount
    useEffect(() => {
        const fetchChatHistory = async () => {
            try {
                setLoading(true);
                const response = await api.get('/chat/history/');
                setMessages(response.data);
                setError('');
            } catch (err) {
                console.error("Failed to fetch chat history:", err);
                if (err.response && err.response.status === 401) {
                    // If unauthorized, navigate back to login (token expired or invalid)
                    navigate('/');
                } else {
                    setError('Failed to load chat history. Please try again.');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchChatHistory();
    }, [navigate]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        const userMessage = { role: 'user', content: newMessage.trim(), timestamp: new Date().toISOString() };
        // Optimistically update UI with user's message
        setMessages(prevMessages => [...prevMessages, userMessage]);
        setNewMessage(''); // Clear input immediately
        setError(''); // Clear any previous errors

        try {
            setLoading(true);
            const response = await api.post('/chat/', {
                role: 'user', // ADD THIS LINE: Specify the role as 'user'
                content: userMessage.content
            });
            // Replace or add the actual assistant response
            // The backend returns the assistant's message directly, so we just add it
            setMessages(prevMessages => [...prevMessages, response.data]); 
        } catch (err) {
            console.error("Error sending message:", err);
            // Revert optimistic update or show specific error for this message
            setError('Failed to send message. Please try again.');
            // For now, just remove the optimistic update if an error occurred for simplicity
            setMessages(prevMessages => prevMessages.filter(msg => msg !== userMessage)); 
            if (err.response && err.response.status === 401) {
                navigate('/'); // Redirect to login if token is expired
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <header className="chat-header">
                <h2>HealthMate AI Chat</h2>
                <button onClick={onLogout} className="logout-button">Logout</button>
            </header>
            <div className="messages-display">
                {loading && <p>Loading chat history...</p>}
                {error && <p className="error-message">{error}</p>}
                {messages.length === 0 && !loading && !error && (
                    <p className="no-messages">Start your conversation with HealthMate AI!</p>
                )}
                {messages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.role}`}>
                        <div className="message-bubble">
                            <span className="message-role">{msg.role === 'user' ? 'You' : 'AI'}:</span> {msg.content}
                            <div className="message-timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</div>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} /> {/* For auto-scrolling */}
            </div>
            <form onSubmit={handleSendMessage} className="message-input-form">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    disabled={loading}
                />
                <button type="submit" disabled={loading}>
                    Send
                </button>
            </form>
        </div>
    );
};

export default ChatPage;
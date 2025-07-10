// frontend/src/components/ChatPage.js
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api'; // Your Axios instance
import './ChatPage.css'; // We'll create this file for styling

const MODEL_OPTIONS = [
    { value: 'openai', label: 'OpenAI (GPT-3.5)' },
    { value: 'flan-t5', label: 'FLAN-T5' },
    { value: 'embedding', label: 'Embedding Model' }
];

const ChatPage = ({ onLogout }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [modelChoice, setModelChoice] = useState(MODEL_OPTIONS[0].value);
    const navigate = useNavigate();
    const messagesEndRef = useRef(null);

    // Function to scroll to the bottom of messages
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        setError('');
    }, []);

    // Effect to scroll to bottom whenever messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // // Fetch chat history on component mount
    // useEffect(() => {
    //     const fetchChatHistory = async () => {
    //         try {
    //             setLoading(true);
    //             const response = await api.get('/chat/history/');
    //             setMessages(response.data);
    //             setError('');
    //         } catch (err) {
    //             console.error("Failed to fetch chat history:", err);
    //             if (err.response && err.response.status === 401) {
    //                 // If unauthorized, navigate back to login (token expired or invalid)
    //                 navigate('/');
    //             } else {
    //                 setError('Failed to load chat history. Please try again.');
    //             }
    //         } finally {
    //             setLoading(false);
    //         }
    //     };

    //     fetchChatHistory();
    // }, [navigate]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        const userMessage = { role: 'user', content: newMessage.trim(), timestamp: new Date().toISOString() };
        setMessages(prevMessages => [...prevMessages, userMessage]);
        setNewMessage('');
        setError('');

        try {
            setLoading(true);
            const response = await api.post('/ai/chat/', {
                message: userMessage.content, // NOT "content", your backend expects "message"
                model_choice: modelChoice
            });
            setMessages(prevMessages => [...prevMessages, response.data]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
            setMessages(prevMessages => prevMessages.filter(msg => msg !== userMessage));
            if (err.response && err.response.status === 401) {
                navigate('/');
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
                {messages.length === 0 && (
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
        {error && <p className="error-message">{error}</p>}

            <div className="model-selector">
                <label htmlFor="modelChoice"><b>Model:</b></label>
                    <select
                        id="modelChoice"
                        value={modelChoice}
                        onChange={e => setModelChoice(e.target.value)}
                        className="model-dropdown"
                        disable={loading}
    >
                        {MODEL_OPTIONS.map(opt => (
                            <option value={opt.value} key={opt.value}>{opt.label}</option>
                        ))}
                    </select>
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
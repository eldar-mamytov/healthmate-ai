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
    const inputRef = useRef(null);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [modelChoice, setModelChoice] = useState(MODEL_OPTIONS[0].value);
    const [isListening, setIsListening] = useState(false);
    const recognitionRef = useRef(null);
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

    // Keep input focused when messages update
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, [messages]);

    // // Text-to-Speech: Speak the last AI message
    // useEffect(() => {
    //     if (messages.length === 0) return;

    //     const lastMsg = messages[messages.length - 1];
    //     if ((lastMsg.role === 'assistant' || lastMsg.role === 'ai') && lastMsg.content) {
    //         // Prevent overlapping speech: cancel first
    //         window.speechSynthesis.cancel();
    //         const utterance = new window.SpeechSynthesisUtterance(lastMsg.content);
    //         utterance.rate = 1.03; // adjust speed (1 = normal)
    //         utterance.pitch = 1.01; // adjust pitch (1 = normal)
    //         utterance.volume = 1;
    //         window.speechSynthesis.speak(utterance);
    //     }
    // }, [messages]);

    // // Fetch chat history on component mount
    // useEffect(() => {
    //     // 
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

    // ----------- Speech Recognition (Speech-to-Text) -----------
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    const handleMicClick = () => {
        if (!SpeechRecognition) {
            setError("Speech recognition is not supported in this browser.");
            return;
        }
        if (isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
            return;
        }
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setNewMessage(transcript);
            setIsListening(false);
        };
        recognition.onend = () => {
            setIsListening(false);
        };
        recognition.onerror = (event) => {
            setError("Speech recognition error: " + event.error);
            setIsListening(false);
        };

        recognition.start();
        setIsListening(true);
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
                            {msg.role !== 'user' && msg.content && (
                                <button
                                    className="tts-btn"
                                    title="Play text-to-speech"
                                    style={{
                                        marginLeft: 10,
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        fontSize: "1.1em"
                                    }}
                                    onClick={() => {
                                        window.speechSynthesis.cancel();
                                        const utterance = new window.SpeechSynthesisUtterance(msg.content);
                                        utterance.rate = 1.03;
                                        utterance.pitch = 1.01;
                                        utterance.volume = 1;
                                        window.speechSynthesis.speak(utterance);
                                    }}
                                >
                                    <svg width="22" height="22" viewBox="0 0 22 22" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M3 9v4h4l5 5V4l-5 5H3z"/>
                                        <path d="M16 8.82a4 4 0 010 4.36" fill="none" stroke="#23b15a" strokeWidth="2" strokeLinecap="round"/>
                                        <path d="M18 7a7 7 0 010 8" fill="none" stroke="#23b15a" strokeWidth="2" strokeLinecap="round"/>
                                    </svg>
                                </button>
                            )}
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
                    disabled={loading}
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
                    ref={inputRef}
                />
                <button
                    type="button"
                    onClick={handleMicClick}
                    className={`mic-btn${isListening ? ' listening' : ''}`}
                    title={isListening ? "Listening..." : "Click to speak"}
                    disabled={loading}
                >
                    🎤︎︎
                </button>
                <button type="submit" disabled={loading}>
                    Send
                </button>
            </form>
        </div>
    );
};

export default ChatPage;
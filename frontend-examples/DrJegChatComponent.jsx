// Dr. Jeg AI Chatbot - React Component Example

import React, { useState, useEffect, useRef } from 'react';
import './DrJegChat.css';

// API Client Class
class DrJegAPI {
  constructor(baseURL = 'http://0.0.0.0:8000/api/v1/dr-jeg', token = null) {
    this.baseURL = baseURL;
    this.token = token;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 429) {
        throw new Error('Rate limit exceeded. Please try again later.');
      }
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || error.detail || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Send message to Dr. Jeg
  async sendMessage(message, conversationId = null) {
    return this.request('/conversation/', {
      method: 'POST',
      body: JSON.stringify({
        message,
        ...(conversationId && { conversation_id: conversationId }),
      }),
    });
  }

  // Get all conversations
  async getConversations(page = 1, pageSize = 20) {
    return this.request(`/conversations/?page=${page}&page_size=${pageSize}`);
  }

  // Get conversation details
  async getConversationDetails(conversationId) {
    return this.request(`/conversation/${conversationId}/`);
  }

  // Delete conversation
  async deleteConversation(conversationId) {
    return this.request(`/conversation/${conversationId}/delete/`, {
      method: 'DELETE',
    });
  }

  // Get service status
  async getServiceStatus() {
    return this.request('/status/');
  }

  // Get analytics
  async getAnalytics() {
    return this.request('/analytics/');
  }
}

// Main Chat Component
const DrJegChat = ({ jwtToken, onError }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [serviceStatus, setServiceStatus] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [showConversations, setShowConversations] = useState(false);
  
  const messagesEndRef = useRef(null);
  const drJegAPI = new DrJegAPI('http://0.0.0.0:8000/api/v1/dr-jeg', jwtToken);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load service status on mount
  useEffect(() => {
    loadServiceStatus();
    loadConversations();
  }, []);

  const loadServiceStatus = async () => {
    try {
      const status = await drJegAPI.getServiceStatus();
      setServiceStatus(status);
    } catch (error) {
      console.error('Failed to load service status:', error);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await drJegAPI.getConversations();
      setConversations(data.results || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { 
      sender: 'user', 
      content: input, 
      timestamp: new Date().toISOString(),
      id: `user-${Date.now()}`
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const response = await drJegAPI.sendMessage(currentInput, conversationId);
      
      const botMessage = {
        sender: 'bot',
        content: response.response,
        timestamp: response.timestamp,
        tokens_used: response.tokens_used,
        response_time_ms: response.response_time_ms,
        id: `bot-${Date.now()}`
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Refresh conversations list
      loadConversations();
      
    } catch (error) {
      console.error('Error sending message:', error);
      onError?.(error.message);
      
      // Add error message to chat
      const errorMessage = {
        sender: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
        id: `error-${Date.now()}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setShowConversations(false);
  };

  const loadConversation = async (convId) => {
    try {
      setLoading(true);
      const conversation = await drJegAPI.getConversationDetails(convId);
      
      const loadedMessages = conversation.messages.map(msg => ({
        ...msg,
        id: msg.id || `${msg.sender}-${msg.timestamp}`
      }));
      
      setMessages(loadedMessages);
      setConversationId(convId);
      setShowConversations(false);
    } catch (error) {
      console.error('Failed to load conversation:', error);
      onError?.(error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (convId) => {
    try {
      await drJegAPI.deleteConversation(convId);
      loadConversations();
      
      if (convId === conversationId) {
        startNewConversation();
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      onError?.(error.message);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="dr-jeg-chat">
      {/* Header */}
      <div className="chat-header">
        <div className="header-left">
          <h2>🤖 Dr. Jeg AI Assistant</h2>
          {serviceStatus && (
            <span className="status">
              {serviceStatus.service_status === 'active' ? '🟢' : '🔴'} 
              {serviceStatus.gemini_model}
            </span>
          )}
        </div>
        <div className="header-buttons">
          <button 
            onClick={() => setShowConversations(!showConversations)}
            className="btn-secondary"
          >
            📋 Conversations ({conversations.length})
          </button>
          <button onClick={startNewConversation} className="btn-primary">
            ➕ New Chat
          </button>
        </div>
      </div>

      {/* Conversations Sidebar */}
      {showConversations && (
        <div className="conversations-sidebar">
          <h3>Your Conversations</h3>
          {conversations.length === 0 ? (
            <p>No conversations yet</p>
          ) : (
            conversations.map(conv => (
              <div key={conv.id} className="conversation-item">
                <div 
                  className="conversation-title"
                  onClick={() => loadConversation(conv.id)}
                >
                  {conv.title || 'Untitled Conversation'}
                </div>
                <div className="conversation-meta">
                  {conv.message_count} messages • {new Date(conv.created_at).toLocaleDateString()}
                </div>
                <button 
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conv.id);
                  }}
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Messages Area */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>👋 Welcome to Dr. Jeg AI Assistant!</h3>
            <p>I'm here to help you with health-related questions and concerns. Feel free to ask me anything about:</p>
            <ul>
              <li>🩺 Symptoms and general health advice</li>
              <li>💊 Medication information</li>
              <li>🏃‍♀️ Lifestyle and wellness tips</li>
              <li>🧘‍♀️ Mental health and stress management</li>
            </ul>
            <p><strong>Disclaimer:</strong> I provide general information only. For serious concerns, please consult a healthcare professional.</p>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.sender}`}>
                <div className="message-header">
                  <span className="sender">
                    {msg.sender === 'user' ? '👤 You' : 
                     msg.sender === 'bot' ? '🤖 Dr. Jeg' : '⚠️ System'}
                  </span>
                  <span className="timestamp">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">
                  {msg.content}
                </div>
                {msg.tokens_used && (
                  <div className="message-meta">
                    🔢 {msg.tokens_used} tokens • ⏱️ {msg.response_time_ms}ms
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="message bot loading">
                <div className="message-header">
                  <span className="sender">🤖 Dr. Jeg</span>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="input-area">
        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Dr. Jeg about your health concerns..."
            disabled={loading}
            rows={1}
            style={{ resize: 'none' }}
          />
          <button 
            onClick={sendMessage} 
            disabled={loading || !input.trim()}
            className="send-button"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
        {serviceStatus && (
          <div className="rate-limit-info">
            Rate limit: {serviceStatus.user_statistics?.current_hourly_requests || 0}/
            {serviceStatus.user_statistics?.rate_limit || 60} requests per hour
          </div>
        )}
      </div>
    </div>
  );
};

// Usage Example
const App = () => {
  const [jwtToken, setJwtToken] = useState(localStorage.getItem('jwt_token'));
  const [error, setError] = useState(null);

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  if (!jwtToken) {
    return (
      <div className="login-prompt">
        <h2>Please log in to use Dr. Jeg AI Assistant</h2>
        {/* Add your login component here */}
      </div>
    );
  }

  return (
    <div className="app">
      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}
      <DrJegChat 
        jwtToken={jwtToken} 
        onError={handleError}
      />
    </div>
  );
};

export default App;

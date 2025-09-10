# Dr. Jeg AI Chatbot - Frontend Implementation Guide

## 🤖 Complete API Endpoints Reference

All endpoints require JWT authentication via the `Authorization: Bearer {token}` header.

### Base URL
```
http://0.0.0.0:8000/api/v1/dr-jeg/
```

---

## 📋 API Endpoints

### 1. **Start/Continue Conversation**
**POST** `/conversation/`

Send a message to Dr. Jeg and receive an AI response.

**Request Body:**
```json
{
  "message": "I've been having headaches lately. What could be causing them?",
  "conversation_id": "optional-uuid-for-existing-conversation"
}
```

**Response (Success - 200):**
```json
{
  "response": "I understand your concern about headaches. There can be several causes including stress, dehydration, lack of sleep, or tension. However, if headaches persist or are severe, I recommend consulting with a healthcare professional for proper evaluation.",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-09-08T00:45:00Z",
  "tokens_used": 150,
  "response_time_ms": 1200
}
```

**Error Responses:**
- `400` - Invalid message or conversation ID
- `401` - Authentication required
- `429` - Rate limit exceeded (60 requests per hour)
- `503` - AI service unavailable

---

### 2. **List User Conversations**
**GET** `/conversations/`

Get a paginated list of all conversations for the authenticated user.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response (200):**
```json
{
  "count": 5,
  "next": "http://0.0.0.0:8000/api/v1/dr-jeg/conversations/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Headaches and stress management",
      "created_at": "2025-09-08T17:00:00Z",
      "updated_at": "2025-09-08T17:30:00Z",
      "message_count": 8,
      "last_message_time": "2025-09-08T17:30:00Z",
      "is_active": true
    }
  ]
}
```

---

### 3. **Get Conversation Details**
**GET** `/conversation/{conversation_id}/`

Retrieve full message history for a specific conversation.

**Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Headaches and stress management",
  "created_at": "2025-09-08T17:00:00Z",
  "updated_at": "2025-09-08T17:30:00Z",
  "message_count": 4,
  "is_active": true,
  "messages": [
    {
      "id": "msg-1",
      "sender": "user",
      "content": "I've been having headaches lately",
      "timestamp": "2025-09-08T17:00:00Z"
    },
    {
      "id": "msg-2",
      "sender": "bot",
      "content": "I understand your concern about headaches...",
      "timestamp": "2025-09-08T17:00:30Z",
      "ai_model": "gemini-pro",
      "response_time_ms": 1200,
      "tokens_used": 150
    }
  ]
}
```

**Error Responses:**
- `404` - Conversation not found or not accessible

---

### 4. **Delete Conversation**
**DELETE** `/conversation/{conversation_id}/delete/`

Delete a specific conversation and all its messages (soft delete).

**Response (200):**
```json
{
  "status": "success",
  "message": "Conversation deleted successfully"
}
```

**Error Responses:**
- `404` - Conversation not found
- `500` - Server error

---

### 5. **Clear All Conversations**
**DELETE** `/conversations/clear/`

Delete all conversations for the authenticated user.

**Request Body:**
```json
{
  "confirm": true
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "All conversations cleared (3 deleted)"
}
```

**Error Responses:**
- `400` - Confirmation required

---

### 6. **Get Analytics**
**GET** `/analytics/`

Get analytics data for user's conversations.

**Response (200):**
```json
{
  "count": 3,
  "results": [
    {
      "conversation_title": "Headaches and stress management",
      "total_messages": 8,
      "total_user_messages": 4,
      "total_bot_messages": 4,
      "total_tokens_used": 600,
      "average_response_time_ms": 1150.5,
      "health_topics": ["headaches", "stress", "sleep"],
      "created_at": "2025-09-08T17:00:00Z",
      "updated_at": "2025-09-08T17:30:00Z"
    }
  ]
}
```

---

### 7. **Service Status**
**GET** `/status/`

Check Dr. Jeg service status and user statistics.

**Response (200):**
```json
{
  "service_status": "active",
  "user_statistics": {
    "total_conversations": 3,
    "total_messages": 24,
    "recent_successful_calls": 8,
    "recent_failed_calls": 0,
    "current_hourly_requests": 12,
    "rate_limit": 60
  },
  "gemini_model": "gemini-pro",
  "features": [
    "health_focused_responses",
    "conversation_history",
    "safety_filtering",
    "rate_limiting"
  ]
}
```

---

## 🔧 Frontend Implementation Examples

### JavaScript/React Example

```javascript
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

    const response = await fetch(url, config);
    
    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please try again later.');
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || `HTTP ${response.status}`);
    }
    
    return response.json();
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

  // Clear all conversations
  async clearAllConversations() {
    return this.request('/conversations/clear/', {
      method: 'DELETE',
      body: JSON.stringify({ confirm: true }),
    });
  }

  // Get analytics
  async getAnalytics() {
    return this.request('/analytics/');
  }

  // Get service status
  async getServiceStatus() {
    return this.request('/status/');
  }
}

// Usage Example
const drJegAPI = new DrJegAPI();

// Set JWT token after user login
drJegAPI.setToken('your-jwt-token-here');

// Send a message
try {
  const response = await drJegAPI.sendMessage('I have a headache, what should I do?');
  console.log('Dr. Jeg:', response.response);
  console.log('Tokens used:', response.tokens_used);
} catch (error) {
  console.error('Error:', error.message);
}

// Get conversations
try {
  const conversations = await drJegAPI.getConversations();
  console.log('Conversations:', conversations.results);
} catch (error) {
  console.error('Error:', error.message);
}
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const DrJegChat = ({ token }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  const drJegAPI = new DrJegAPI('http://0.0.0.0:8000/api/v1/dr-jeg', token);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await drJegAPI.sendMessage(input, conversationId);
      
      const botMessage = {
        sender: 'bot',
        content: response.response,
        timestamp: new Date(response.timestamp),
        tokens_used: response.tokens_used,
        response_time_ms: response.response_time_ms
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Handle error - show user-friendly message
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dr-jeg-chat">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className="content">{msg.content}</div>
            <div className="timestamp">{msg.timestamp.toLocaleTimeString()}</div>
            {msg.tokens_used && (
              <div className="meta">Tokens: {msg.tokens_used} | Response time: {msg.response_time_ms}ms</div>
            )}
          </div>
        ))}
        {loading && <div className="loading">Dr. Jeg is typing...</div>}
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask Dr. Jeg about your health..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default DrJegChat;
```

### cURL Examples

```bash
# 1. Send message to Dr. Jeg
curl -X POST "http://0.0.0.0:8000/api/v1/dr-jeg/conversation/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have been feeling tired lately, what could be the cause?"
  }'

# 2. List conversations
curl -X GET "http://0.0.0.0:8000/api/v1/dr-jeg/conversations/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. Get conversation details
curl -X GET "http://0.0.0.0:8000/api/v1/dr-jeg/conversation/CONVERSATION_ID/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. Delete conversation
curl -X DELETE "http://0.0.0.0:8000/api/v1/dr-jeg/conversation/CONVERSATION_ID/delete/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. Clear all conversations
curl -X DELETE "http://0.0.0.0:8000/api/v1/dr-jeg/conversations/clear/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

# 6. Get service status
curl -X GET "http://0.0.0.0:8000/api/v1/dr-jeg/status/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. Get analytics
curl -X GET "http://0.0.0.0:8000/api/v1/dr-jeg/analytics/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔒 Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

Get JWT token from the auth endpoint:
```bash
curl -X POST "http://0.0.0.0:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

## ⚡ Rate Limiting

- **Rate Limit:** 60 requests per hour per user
- **Response Header:** Check `X-RateLimit-Remaining` header
- **Rate Limit Exceeded:** Returns HTTP 429 with retry-after information

---

## 🛡️ Error Handling

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (access denied)
- `404` - Not Found (conversation doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (AI service issues)

Error response format:
```json
{
  "error": "Detailed error message",
  "detail": "Additional context if available"
}
```

---

## 🎯 Best Practices

### Frontend Implementation
1. **Handle rate limiting** gracefully with user-friendly messages
2. **Implement conversation threading** for better UX
3. **Cache conversation list** to reduce API calls
4. **Show loading states** during AI response generation
5. **Handle network errors** appropriately
6. **Store conversation ID** for continuing conversations
7. **Implement auto-retry** for failed requests with exponential backoff

### Security
1. **Store JWT tokens securely** (httpOnly cookies recommended)
2. **Refresh tokens** before expiration
3. **Validate user input** before sending to API
4. **Sanitize AI responses** before displaying (XSS prevention)

### Performance
1. **Paginate conversation lists** for better performance
2. **Debounce user input** to prevent excessive API calls
3. **Use WebSockets** for real-time updates (if implemented)
4. **Implement offline support** with local storage

---

This comprehensive guide provides everything needed to integrate the Dr. Jeg AI chatbot into your frontend application! 🤖✨

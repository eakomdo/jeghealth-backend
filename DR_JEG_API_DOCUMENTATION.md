# Dr. Jeg AI Assistant API Documentation

## Overview

The Dr. Jeg AI Assistant is a conversational healthcare AI powered by Google Gemini's API. It provides users with health-focused conversations, maintaining chat history and offering empathetic health guidance.

## Features

- **Conversational AI**: Health-focused conversations using Google Gemini
- **Chat History**: Persistent conversation storage and retrieval
- **Rate Limiting**: Prevents API abuse with hourly limits
- **Safety Filtering**: Healthcare-appropriate content filtering
- **Analytics**: Conversation insights and usage statistics
- **Multi-conversation Support**: Users can maintain multiple conversation threads

## API Endpoints

### 1. Start/Continue Conversation

**POST** `/api/v1/dr-jeg/conversation/`

Send a message to Dr. Jeg AI and receive a response.

**Authentication**: Required (JWT Bearer token)

**Request Body:**
```json
{
  "message": "I've been having headaches lately. What could be causing them?",
  "conversation_id": "optional-uuid-for-existing-conversation"
}
```

**Response (Success):**
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I understand your concern about headaches. There can be several causes...",
  "timestamp": "2025-08-06T17:30:00Z",
  "message_id": "456e7890-e89b-12d3-a456-426614174001",
  "tokens_used": 150,
  "response_time_ms": 1200
}
```

**Error Responses:**
- `400` - Invalid message or conversation ID
- `401` - Authentication required
- `429` - Rate limit exceeded (60 requests per hour)
- `500` - AI service error

### 2. List User Conversations

**GET** `/api/v1/dr-jeg/conversations/`

Get a list of all conversations for the authenticated user.

**Authentication**: Required

**Query Parameters:**
- `limit` (optional): Number of conversations to return (default: 50, max: 100)
- `offset` (optional): Number of conversations to skip (default: 0)

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Headaches and stress management",
      "created_at": "2025-08-06T17:00:00Z",
      "updated_at": "2025-08-06T17:30:00Z",
      "message_count": 8,
      "last_message_time": "2025-08-06T17:30:00Z"
    }
  ]
}
```

### 3. Get Conversation Details

**GET** `/api/v1/dr-jeg/conversation/{conversation_id}/`

Retrieve full message history for a specific conversation.

**Authentication**: Required

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Headaches and stress management",
  "created_at": "2025-08-06T17:00:00Z",
  "updated_at": "2025-08-06T17:30:00Z",
  "message_count": 4,
  "messages": [
    {
      "id": "msg-1",
      "sender": "user",
      "content": "I've been having headaches lately",
      "timestamp": "2025-08-06T17:00:00Z"
    },
    {
      "id": "msg-2",
      "sender": "bot",
      "content": "I understand your concern about headaches...",
      "timestamp": "2025-08-06T17:00:30Z",
      "ai_model": "gemini-pro",
      "response_time_ms": 1200,
      "tokens_used": 150
    }
  ]
}
```

### 4. Delete Conversation

**DELETE** `/api/v1/dr-jeg/conversation/{conversation_id}/delete/`

Delete a specific conversation and all its messages.

**Authentication**: Required

**Response:**
```json
{
  "status": "success",
  "message": "Conversation deleted successfully"
}
```

### 5. Clear All Conversations

**DELETE** `/api/v1/dr-jeg/conversations/clear/`

Delete all conversations for the authenticated user.

**Authentication**: Required

**Request Body:**
```json
{
  "confirm": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "All conversations cleared (3 deleted)"
}
```

### 6. Get Analytics

**GET** `/api/v1/dr-jeg/analytics/`

Get analytics data for user's conversations.

**Authentication**: Required

**Response:**
```json
[
  {
    "conversation_title": "Headaches and stress management",
    "total_messages": 8,
    "total_user_messages": 4,
    "total_bot_messages": 4,
    "total_tokens_used": 600,
    "average_response_time_ms": 1150.5,
    "health_topics": ["headaches", "stress", "sleep"],
    "created_at": "2025-08-06T17:00:00Z",
    "updated_at": "2025-08-06T17:30:00Z"
  }
]
```

### 7. Service Status

**GET** `/api/v1/dr-jeg/status/`

Check Dr. Jeg service status and user statistics.

**Authentication**: Required

**Response:**
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

## Usage Examples

### cURL Examples

**Start a new conversation:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/dr-jeg/conversation/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have been feeling tired lately, what could be the cause?"
  }'
```

**Continue existing conversation:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/dr-jeg/conversation/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The fatigue is worse in the mornings",
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

**List conversations:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/dr-jeg/conversations/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### JavaScript/React Native Example

```javascript
const DrJegAPI = {
  baseURL: 'http://127.0.0.1:8000/api/v1/dr-jeg',
  
  async sendMessage(token, message, conversationId = null) {
    const response = await fetch(`${this.baseURL}/conversation/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      })
    });
    
    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please try again later.');
    }
    
    return response.json();
  },
  
  async getConversations(token, limit = 50, offset = 0) {
    const response = await fetch(
      `${this.baseURL}/conversations/?limit=${limit}&offset=${offset}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });
    
    return response.json();
  },
  
  async getConversationDetails(token, conversationId) {
    const response = await fetch(`${this.baseURL}/conversation/${conversationId}/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });
    
    return response.json();
  },
  
  async deleteConversation(token, conversationId) {
    const response = await fetch(`${this.baseURL}/conversation/${conversationId}/delete/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });
    
    return response.json();
  }
};
```

## Database Schema

### Conversation Model
- `id`: UUID (Primary Key)
- `user`: Foreign Key to User
- `title`: String (auto-generated from first message)
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean (for soft deletion)

### Message Model
- `id`: UUID (Primary Key)
- `conversation`: Foreign Key to Conversation
- `sender`: Choice ('user', 'bot')
- `content`: Text
- `timestamp`: DateTime
- `ai_model`: String (e.g., 'gemini-pro')
- `response_time_ms`: Integer (for AI responses)
- `tokens_used`: Integer (for AI responses)

### ConversationAnalytics Model
- Analytics data per conversation
- Message counts, token usage, response times
- Health topics discussed

### APIUsageLog Model
- Logs all Gemini API calls
- Success/failure tracking
- Cost and performance monitoring

## Security & Rate Limiting

### Authentication
- All endpoints require JWT authentication
- User can only access their own conversations
- API keys are stored securely server-side

### Rate Limiting
- 60 requests per hour per user
- Cached using Redis for performance
- Returns 429 status when exceeded

### Safety Features
- Content filtering for healthcare appropriateness
- Gemini API safety settings enabled
- No storage of sensitive medical data
- HIPAA-aware conversation guidelines

## Error Handling

### Common Error Codes
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (access denied)
- `404` - Not Found (conversation doesn't exist)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error (AI service issues)

### Error Response Format
```json
{
  "error": "Detailed error message",
  "status": "error",
  "code": "ERROR_CODE"
}
```

## Configuration

### Environment Variables
```bash
# Google Gemini API Configuration
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
DR_JEG_RATE_LIMIT_PER_HOUR=60

# Redis for rate limiting
REDIS_URL=redis://localhost:6379/0
```

### Django Settings
```python
# Google Gemini API Configuration
GOOGLE_GEMINI_API_KEY = env('GOOGLE_GEMINI_API_KEY', default='')
GEMINI_MODEL = env('GEMINI_MODEL', default='gemini-pro')
DR_JEG_RATE_LIMIT_PER_HOUR = env.int('DR_JEG_RATE_LIMIT_PER_HOUR', default=60)
```

## Testing

### Test the API endpoints with authentication:

1. **Get JWT token** from `/api/v1/auth/login/`
2. **Test conversation** endpoint with health-related queries
3. **Verify rate limiting** by making multiple requests
4. **Check conversation history** persistence

### Health Check
Use the `/api/v1/dr-jeg/status/` endpoint to monitor service health and user statistics.

## Best Practices

### For Frontend Integration
1. **Handle rate limiting** gracefully with user-friendly messages
2. **Implement conversation threading** for better UX
3. **Cache conversation list** to reduce API calls
4. **Show loading states** during AI response generation
5. **Handle errors** appropriately (network, API, rate limits)

### For AI Conversations
1. **Keep conversations focused** on health topics
2. **Encourage professional consultation** for serious symptoms
3. **Respect user privacy** and data sensitivity
4. **Provide clear disclaimers** about AI limitations

## Support

For technical support or questions about the Dr. Jeg AI Assistant API, please refer to the main API documentation or contact the development team.

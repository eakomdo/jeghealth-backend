# JWT Token Validation API

## Overview
The JWT token validation endpoint allows frontend applications to validate access tokens without making authenticated requests.

## Endpoint

### POST `/api/v1/auth/token/validate/`

**Description:** Validates a JWT access token and returns its validity status.

**Authentication:** None required (public endpoint)

**Request Body:**
```json
{
  "token": "your_jwt_access_token_here"
}
```

**Response (Valid Token):**
```json
{
  "valid": true,
  "user_id": 3,
  "expires_at": 1754505343
}
```

**Response (Invalid Token):**
```json
{
  "valid": false,
  "error": "Token is invalid or expired"
}
```

**Response (Missing Token):**
```json
{
  "valid": false,
  "error": "Token is required"
}
```

## Usage Examples

### cURL
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token/validate/" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### JavaScript (Frontend)
```javascript
const validateToken = async (token) => {
  try {
    const response = await fetch('/api/v1/auth/token/validate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token })
    });
    
    const data = await response.json();
    return data.valid;
  } catch (error) {
    console.error('Token validation error:', error);
    return false;
  }
};
```

### React Native
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const validateStoredToken = async () => {
  try {
    const token = await AsyncStorage.getItem('access_token');
    if (!token) return false;
    
    const isValid = await validateToken(token);
    if (!isValid) {
      // Clear invalid token
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
    }
    return isValid;
  } catch (error) {
    return false;
  }
};
```

## Use Cases

1. **Frontend Authentication State Management**
   - Check if stored tokens are still valid on app startup
   - Validate tokens before making authenticated requests
   - Determine if user needs to log in again

2. **Token Refresh Logic**
   - Check access token validity before attempting refresh
   - Avoid unnecessary refresh attempts with expired refresh tokens

3. **Security Validation**
   - Validate tokens received from external sources
   - Ensure token integrity before processing

## Error Handling

The endpoint handles various error scenarios:

- **Missing Token**: Returns 400 Bad Request
- **Invalid Format**: Returns 401 Unauthorized  
- **Expired Token**: Returns 401 Unauthorized
- **Malformed Token**: Returns 401 Unauthorized

## Security Considerations

- This is a public endpoint (no authentication required)
- Only validates token format and expiration, doesn't expose sensitive data
- Returns minimal information (user_id and expiration timestamp only)
- Does not perform blacklist checking (use logout endpoint for that)

## Integration with Frontend Authentication

This endpoint solves the common frontend issue where `validateToken` function is missing or undefined. Instead of implementing client-side JWT validation, frontends can use this API endpoint for reliable server-side validation.

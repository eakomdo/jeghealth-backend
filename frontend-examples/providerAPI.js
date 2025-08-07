// Healthcare Provider API Service
// File: services/providerAPI.js

class ProviderAPIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api/v1';
    this.authURL = `${this.baseURL}/auth`;
    this.providerURL = `${this.baseURL}/providers`;
  }

  // Token Management
  getAccessToken() {
    return localStorage.getItem('access_token');
  }

  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }

  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isTokenExpired(token) {
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }

  // Headers
  getAuthHeaders(token = null) {
    const authToken = token || this.getAccessToken();
    return {
      'Content-Type': 'application/json',
      ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
    };
  }

  getFileUploadHeaders(token = null) {
    const authToken = token || this.getAccessToken();
    return {
      ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
      // Don't set Content-Type for FormData
    };
  }

  // Generic Request Handler
  async makeRequest(url, options = {}) {
    let token = this.getAccessToken();

    // Check if token needs refresh
    if (token && this.isTokenExpired(token)) {
      const newToken = await this.refreshToken();
      if (!newToken) {
        this.clearTokens();
        window.location.href = '/provider/login';
        throw new Error('Authentication required');
      }
      token = newToken;
    }

    // Make the request
    let response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(token),
        ...options.headers
      }
    });

    // Handle 401 - token expired
    if (response.status === 401) {
      const newToken = await this.refreshToken();
      if (newToken) {
        // Retry request with new token
        response = await fetch(url, {
          ...options,
          headers: {
            ...this.getAuthHeaders(newToken),
            ...options.headers
          }
        });
      } else {
        this.clearTokens();
        window.location.href = '/provider/login';
        throw new Error('Authentication expired');
      }
    }

    return response;
  }

  // Authentication Methods
  async register(registrationData) {
    const response = await fetch(`${this.authURL}/provider/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(registrationData)
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async login(credentials) {
    const response = await fetch(`${this.authURL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    });

    const data = await response.json();

    if (response.ok && data.access && data.refresh) {
      this.setTokens(data.access, data.refresh);
    }

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async logout() {
    try {
      const response = await this.makeRequest(`${this.authURL}/logout/`, {
        method: 'POST'
      });

      this.clearTokens();
      
      return {
        success: response.ok,
        status: response.status
      };
    } catch (error) {
      this.clearTokens();
      throw error;
    }
  }

  async refreshToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return null;

    try {
      const response = await fetch(`${this.authURL}/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          refresh: refreshToken
        })
      });

      const data = await response.json();

      if (response.ok && data.access) {
        this.setTokens(data.access, refreshToken);
        return data.access;
      } else {
        this.clearTokens();
        return null;
      }
    } catch (error) {
      this.clearTokens();
      return null;
    }
  }

  async validateToken(token = null) {
    const authToken = token || this.getAccessToken();
    if (!authToken) return false;

    try {
      const response = await fetch(`${this.authURL}/token/validate/`, {
        method: 'POST',
        headers: this.getAuthHeaders(authToken)
      });

      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Provider Profile Methods
  async getProfile() {
    const response = await this.makeRequest(`${this.authURL}/provider/profile/`);
    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async updateProfile(profileData, isPartialUpdate = true) {
    const method = isPartialUpdate ? 'PATCH' : 'PUT';
    
    const response = await this.makeRequest(`${this.authURL}/provider/profile/`, {
      method: method,
      body: JSON.stringify(profileData)
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async getDashboard() {
    const response = await this.makeRequest(`${this.authURL}/provider/dashboard/`);
    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  // Provider Directory Methods
  async getProviders(params = {}) {
    const queryParams = new URLSearchParams();
    
    // Add pagination params
    if (params.page) queryParams.append('page', params.page);
    if (params.limit) queryParams.append('limit', params.limit);
    
    // Add filter params
    if (params.professional_role) queryParams.append('professional_role', params.professional_role);
    if (params.specialization) queryParams.append('specialization', params.specialization);
    if (params.organization_facility) queryParams.append('organization_facility', params.organization_facility);
    if (params.professional_title) queryParams.append('professional_title', params.professional_title);
    if (params.license_verified !== undefined) queryParams.append('license_verified', params.license_verified);
    
    const url = `${this.providerURL}/?${queryParams.toString()}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async searchProviders(query, filters = {}) {
    const params = new URLSearchParams();
    
    if (query) params.append('q', query);
    
    // Add filter params
    Object.keys(filters).forEach(key => {
      if (filters[key]) {
        params.append(key, filters[key]);
      }
    });

    const url = `${this.providerURL}/search/?${params.toString()}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async getProviderDetail(providerId) {
    const response = await fetch(`${this.providerURL}/${providerId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async getProviderDropdown() {
    const response = await fetch(`${this.providerURL}/dropdown/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  async getProvidersByHospital(hospitalId) {
    const response = await fetch(`${this.providerURL}/hospital/${hospitalId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  // File Upload Methods
  async uploadLicenseDocument(file, providerId = null) {
    const formData = new FormData();
    formData.append('license_document', file);
    
    if (providerId) {
      formData.append('provider_id', providerId);
    }

    const response = await this.makeRequest(`${this.authURL}/provider/upload-license/`, {
      method: 'POST',
      headers: this.getFileUploadHeaders(),
      body: formData
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  // Password Management
  async changePassword(passwordData) {
    const response = await this.makeRequest(`${this.authURL}/change-password/`, {
      method: 'POST',
      body: JSON.stringify(passwordData)
    });

    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  // User Account Methods
  async getCurrentUser() {
    const response = await this.makeRequest(`${this.authURL}/current-user/`);
    const data = await response.json();

    return {
      success: response.ok,
      data: data,
      status: response.status
    };
  }

  // Utility Methods
  async checkEmailAvailability(email) {
    try {
      const response = await fetch(`${this.authURL}/check-email/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
      });

      const data = await response.json();

      return {
        success: response.ok,
        available: data.available || false,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        available: false,
        error: 'Network error occurred'
      };
    }
  }

  async checkLicenseAvailability(licenseNumber) {
    try {
      const response = await fetch(`${this.authURL}/check-license/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ license_number: licenseNumber })
      });

      const data = await response.json();

      return {
        success: response.ok,
        available: data.available || false,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        available: false,
        error: 'Network error occurred'
      };
    }
  }

  // Error Handling Utility
  handleApiError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    if (error.message === 'Authentication required' || error.message === 'Authentication expired') {
      // Redirect to login
      window.location.href = '/provider/login';
      return;
    }

    // Return user-friendly error message
    return {
      success: false,
      error: this.getErrorMessage(error),
      context: context
    };
  }

  getErrorMessage(error) {
    if (error.message) {
      return error.message;
    }

    if (typeof error === 'string') {
      return error;
    }

    return 'An unexpected error occurred. Please try again.';
  }

  // Network Status Check
  async checkNetworkStatus() {
    try {
      const response = await fetch(`${this.baseURL}/health/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return {
        online: response.ok,
        status: response.status
      };
    } catch (error) {
      return {
        online: false,
        error: error.message
      };
    }
  }
}

// Create and export singleton instance
const providerAPI = new ProviderAPIService();

// React Hook for API calls
export const useProviderAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callAPI = useCallback(async (apiMethod, ...args) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiMethod.apply(providerAPI, args);
      
      if (!result.success) {
        setError(result.data || result.error || 'API call failed');
      }
      
      return result;
    } catch (error) {
      const errorResult = providerAPI.handleApiError(error);
      setError(errorResult.error);
      return errorResult;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    clearError,
    callAPI
  };
};

// Authentication Hook
export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = providerAPI.getAccessToken();
    
    if (!token) {
      setIsAuthenticated(false);
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const isValid = await providerAPI.validateToken();
      
      if (isValid) {
        const userResult = await providerAPI.getCurrentUser();
        
        if (userResult.success) {
          setIsAuthenticated(true);
          setUser(userResult.data);
        } else {
          setIsAuthenticated(false);
          setUser(null);
          providerAPI.clearTokens();
        }
      } else {
        setIsAuthenticated(false);
        setUser(null);
        providerAPI.clearTokens();
      }
    } catch (error) {
      setIsAuthenticated(false);
      setUser(null);
      providerAPI.clearTokens();
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const result = await providerAPI.login(credentials);
    
    if (result.success) {
      setIsAuthenticated(true);
      setUser(result.data.user);
    }
    
    return result;
  };

  const logout = async () => {
    try {
      await providerAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const register = async (registrationData) => {
    return await providerAPI.register(registrationData);
  };

  return {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    register,
    checkAuthStatus
  };
};

export { providerAPI };
export default providerAPI;

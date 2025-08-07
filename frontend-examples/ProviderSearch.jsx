// React Component for Provider Search and Directory
// File: components/provider/ProviderSearch.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { providerAPI } from '../../services/api';

const ProviderSearch = () => {
  const [providers, setProviders] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    professional_role: '',
    specialization: '',
    organization_facility: '',
    professional_title: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null
  });

  // Filter options (should be fetched from backend or defined as constants)
  const professionalRoleOptions = [
    { value: '', label: 'All Roles' },
    { value: 'Physician', label: 'Physician' },
    { value: 'Registered Nurse', label: 'Registered Nurse' },
    { value: 'Specialist', label: 'Specialist' },
    { value: 'Healthcare Administrator', label: 'Healthcare Administrator' },
    { value: 'Medical Technician', label: 'Medical Technician' },
    { value: 'Other', label: 'Other' }
  ];

  const professionalTitleOptions = [
    { value: '', label: 'All Titles' },
    { value: 'Dr.', label: 'Dr. (Doctor)' },
    { value: 'Prof.', label: 'Prof. (Professor)' },
    { value: 'RN', label: 'RN (Registered Nurse)' },
    { value: 'NP', label: 'NP (Nurse Practitioner)' },
    { value: 'PA', label: 'PA (Physician Assistant)' }
  ];

  // Debounced search function
  const debounceSearch = useCallback(
    debounce((query, currentFilters) => {
      performSearch(query, currentFilters);
    }, 500),
    []
  );

  useEffect(() => {
    // Load initial providers
    fetchProviders();
  }, []);

  useEffect(() => {
    // Debounce search when query or filters change
    if (searchQuery.trim() || Object.values(filters).some(filter => filter)) {
      debounceSearch(searchQuery, filters);
    } else {
      fetchProviders();
    }
  }, [searchQuery, filters, debounceSearch]);

  const fetchProviders = async (url = null) => {
    setLoading(true);
    setError(null);

    try {
      let response;
      if (url) {
        response = await fetch(url);
      } else {
        response = await providerAPI.getProviders();
      }
      
      const data = await response.json();

      if (response.ok) {
        setProviders(data.results || data);
        setPagination({
          count: data.count || data.length,
          next: data.next,
          previous: data.previous
        });
      } else {
        setError(data.detail || 'Failed to load providers');
      }
    } catch (error) {
      console.error('Fetch providers error:', error);
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async (query, searchFilters) => {
    setLoading(true);
    setError(null);

    try {
      const response = await providerAPI.searchProviders(query, searchFilters);
      const data = await response.json();

      if (response.ok) {
        setProviders(data);
        setPagination({
          count: data.length,
          next: null,
          previous: null
        });
      } else {
        setError(data.detail || 'Search failed');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const clearFilters = () => {
    setSearchQuery('');
    setFilters({
      professional_role: '',
      specialization: '',
      organization_facility: '',
      professional_title: ''
    });
  };

  const handleProviderSelect = (provider) => {
    // Navigate to provider detail or trigger callback
    window.location.href = `/providers/${provider.id}`;
  };

  return (
    <div className="provider-search">
      <div className="search-header">
        <h1>Find Healthcare Providers</h1>
        <p>Search our directory of verified healthcare professionals</p>
      </div>

      {/* Search and Filters */}
      <div className="search-section">
        <div className="search-bar">
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="Search by name, specialization, or organization..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="search-input"
            />
            <div className="search-icon">🔍</div>
          </div>
        </div>

        <div className="filters-section">
          <div className="filters-row">
            <div className="filter-group">
              <label>Professional Title</label>
              <select
                value={filters.professional_title}
                onChange={(e) => handleFilterChange('professional_title', e.target.value)}
              >
                {professionalTitleOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Professional Role</label>
              <select
                value={filters.professional_role}
                onChange={(e) => handleFilterChange('professional_role', e.target.value)}
              >
                {professionalRoleOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Organization</label>
              <input
                type="text"
                placeholder="Hospital or clinic name"
                value={filters.organization_facility}
                onChange={(e) => handleFilterChange('organization_facility', e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Specialization</label>
              <input
                type="text"
                placeholder="e.g., Cardiology, Pediatrics"
                value={filters.specialization}
                onChange={(e) => handleFilterChange('specialization', e.target.value)}
              />
            </div>
          </div>

          <div className="filter-actions">
            <button onClick={clearFilters} className="btn btn-outline">
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="search-results">
        <div className="results-header">
          <div className="results-count">
            {loading ? (
              'Searching...'
            ) : (
              `${pagination.count} provider${pagination.count !== 1 ? 's' : ''} found`
            )}
          </div>
        </div>

        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => fetchProviders()} className="btn btn-primary">
              Try Again
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Searching providers...</p>
          </div>
        ) : (
          <div className="providers-grid">
            {providers.length > 0 ? (
              providers.map(provider => (
                <ProviderCard
                  key={provider.id}
                  provider={provider}
                  onSelect={() => handleProviderSelect(provider)}
                />
              ))
            ) : (
              !loading && (
                <div className="empty-state">
                  <div className="empty-icon">👨‍⚕️</div>
                  <h3>No providers found</h3>
                  <p>Try adjusting your search criteria or filters</p>
                </div>
              )
            )}
          </div>
        )}

        {/* Pagination */}
        {(pagination.next || pagination.previous) && (
          <div className="pagination">
            {pagination.previous && (
              <button
                onClick={() => fetchProviders(pagination.previous)}
                className="btn btn-outline"
                disabled={loading}
              >
                Previous
              </button>
            )}
            
            {pagination.next && (
              <button
                onClick={() => fetchProviders(pagination.next)}
                className="btn btn-outline"
                disabled={loading}
              >
                Next
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Provider Card Component
const ProviderCard = ({ provider, onSelect }) => {
  return (
    <div className="provider-card" onClick={onSelect}>
      <div className="provider-header">
        <div className="provider-avatar">
          {provider.professional_title?.charAt(0) || provider.first_name?.charAt(0)}
        </div>
        <div className="provider-name">
          <h3>
            {provider.professional_title} {provider.first_name} {provider.last_name}
          </h3>
          <p className="provider-role">{provider.professional_role}</p>
        </div>
        {provider.license_verified && (
          <div className="verified-badge">
            <span className="verified-icon">✓</span>
            Verified
          </div>
        )}
      </div>

      <div className="provider-details">
        {provider.specialization && (
          <div className="detail-item">
            <span className="detail-label">Specialization:</span>
            <span className="detail-value">{provider.specialization}</span>
          </div>
        )}

        <div className="detail-item">
          <span className="detail-label">Organization:</span>
          <span className="detail-value">{provider.organization_facility}</span>
        </div>

        {provider.years_of_experience > 0 && (
          <div className="detail-item">
            <span className="detail-label">Experience:</span>
            <span className="detail-value">{provider.years_of_experience} years</span>
          </div>
        )}

        {provider.phone_number && (
          <div className="detail-item">
            <span className="detail-label">Phone:</span>
            <span className="detail-value">{provider.phone_number}</span>
          </div>
        )}
      </div>

      <div className="provider-actions">
        <button className="btn btn-primary btn-sm">
          View Profile
        </button>
        <button className="btn btn-outline btn-sm">
          Book Appointment
        </button>
      </div>
    </div>
  );
};

// Debounce utility function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export default ProviderSearch;

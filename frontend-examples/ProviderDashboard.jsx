// React Component for Healthcare Provider Dashboard
// File: components/provider/ProviderDashboard.jsx

import React, { useState, useEffect } from 'react';
import { providerAPI } from '../../services/api';

const ProviderDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await providerAPI.getDashboard();
      const data = await response.json();

      if (response.ok) {
        setDashboardData(data);
      } else {
        setError(data.detail || 'Failed to load dashboard data');
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-message">
          <h3>Unable to load dashboard</h3>
          <p>{error}</p>
          <button onClick={fetchDashboardData} className="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="dashboard-empty">
        <p>No dashboard data available</p>
      </div>
    );
  }

  const { provider_profile, stats, recent_activities = [], notifications = [] } = dashboardData;

  return (
    <div className="provider-dashboard">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="provider-info">
          <div className="provider-avatar">
            {provider_profile.professional_title.charAt(0)}
          </div>
          <div className="provider-details">
            <h1>
              Welcome, {provider_profile.professional_title} {provider_profile.first_name} {provider_profile.last_name}
            </h1>
            <p className="provider-role">
              {provider_profile.professional_role} • {provider_profile.organization_facility}
            </p>
            {provider_profile.specialization && (
              <p className="provider-specialization">
                Specialization: {provider_profile.specialization}
              </p>
            )}
          </div>
        </div>

        {/* License Verification Status */}
        <div className="license-status">
          <div className={`status-badge ${provider_profile.license_verified ? 'verified' : 'pending'}`}>
            {provider_profile.license_verified ? (
              <>
                <span className="status-icon">✓</span>
                License Verified
              </>
            ) : (
              <>
                <span className="status-icon">⏳</span>
                Verification Pending
              </>
            )}
          </div>
          {!provider_profile.license_verified && (
            <p className="verification-note">
              Your professional license is under review. This typically takes 1-3 business days.
            </p>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="dashboard-stats">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📅</div>
            <div className="stat-content">
              <h3>{stats.total_appointments || 0}</h3>
              <p>Total Appointments</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🕒</div>
            <div className="stat-content">
              <h3>{stats.upcoming_appointments || 0}</h3>
              <p>Upcoming Appointments</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>{stats.completed_appointments || 0}</h3>
              <p>Completed Appointments</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>{stats.patients_count || 0}</h3>
              <p>Total Patients</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <button className="action-btn" onClick={() => window.location.href = '/provider/profile'}>
            <span className="action-icon">👤</span>
            Edit Profile
          </button>
          
          <button className="action-btn" onClick={() => window.location.href = '/provider/appointments'}>
            <span className="action-icon">📅</span>
            View Appointments
          </button>
          
          <button className="action-btn" onClick={() => window.location.href = '/provider/patients'}>
            <span className="action-icon">👥</span>
            My Patients
          </button>
          
          <button className="action-btn" onClick={() => window.location.href = '/provider/schedule'}>
            <span className="action-icon">⏰</span>
            Manage Schedule
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content">
        {/* Recent Activities */}
        <div className="content-section">
          <div className="section-header">
            <h2>Recent Activities</h2>
            <button className="view-all-btn">View All</button>
          </div>
          
          <div className="activities-list">
            {recent_activities.length > 0 ? (
              recent_activities.slice(0, 5).map((activity, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-icon">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="activity-content">
                    <p className="activity-description">{activity.description}</p>
                    <span className="activity-time">{formatTime(activity.timestamp)}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>No recent activities</p>
                <small>Your recent actions and appointments will appear here</small>
              </div>
            )}
          </div>
        </div>

        {/* Notifications */}
        <div className="content-section">
          <div className="section-header">
            <h2>Notifications</h2>
            {notifications.length > 0 && (
              <span className="notification-count">{notifications.length}</span>
            )}
          </div>
          
          <div className="notifications-list">
            {notifications.length > 0 ? (
              notifications.slice(0, 5).map((notification, index) => (
                <div key={index} className={`notification-item ${notification.priority || 'normal'}`}>
                  <div className="notification-icon">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="notification-content">
                    <p className="notification-title">{notification.title}</p>
                    <p className="notification-message">{notification.message}</p>
                    <span className="notification-time">{formatTime(notification.created_at)}</span>
                  </div>
                  {!notification.read && <div className="unread-indicator"></div>}
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>No new notifications</p>
                <small>Important updates and alerts will appear here</small>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Profile Completion Prompt */}
      {!isProfileComplete(provider_profile) && (
        <div className="profile-completion-prompt">
          <div className="prompt-content">
            <h3>Complete Your Profile</h3>
            <p>
              Help patients find you by completing your professional profile. 
              Add your specialization, bio, and other details.
            </p>
            <button 
              className="btn btn-primary"
              onClick={() => window.location.href = '/provider/profile'}
            >
              Complete Profile
            </button>
          </div>
          <div className="completion-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{width: `${getProfileCompletionPercentage(provider_profile)}%`}}
              ></div>
            </div>
            <span>{getProfileCompletionPercentage(provider_profile)}% Complete</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
const getActivityIcon = (type) => {
  const icons = {
    appointment: '📅',
    patient: '👤',
    profile: '✏️',
    system: '🔧',
    default: '📋'
  };
  return icons[type] || icons.default;
};

const getNotificationIcon = (type) => {
  const icons = {
    appointment: '📅',
    system: '🔔',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅',
    default: '📢'
  };
  return icons[type] || icons.default;
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  
  const date = new Date(timestamp);
  const now = new Date();
  const diffInHours = (now - date) / (1000 * 60 * 60);
  
  if (diffInHours < 1) {
    return 'Just now';
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)} hours ago`;
  } else if (diffInHours < 48) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString();
  }
};

const isProfileComplete = (profile) => {
  const requiredFields = ['specialization', 'bio', 'phone_number'];
  return requiredFields.every(field => profile[field] && profile[field].trim());
};

const getProfileCompletionPercentage = (profile) => {
  const allFields = ['specialization', 'bio', 'phone_number', 'additional_information'];
  const completedFields = allFields.filter(field => profile[field] && profile[field].trim());
  return Math.round((completedFields.length / allFields.length) * 100);
};

export default ProviderDashboard;

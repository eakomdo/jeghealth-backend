// React Components for Healthcare Provider Integration
// File: components/provider/ProviderRegistration.jsx

import React, { useState, useEffect } from 'react';
import { providerAPI } from '../../services/api';

const ProviderRegistration = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Personal Information
    professional_title: '',
    first_name: '',
    last_name: '',
    
    // Step 2: Contact Information
    email: '',
    phone_number: '',
    
    // Step 3: Account Security
    username: '',
    password: '',
    password_confirm: '',
    
    // Step 4: Professional Information
    organization_facility: '',
    professional_role: '',
    specialization: '',
    
    // Step 5: License Information
    license_number: '',
    
    // Step 6: Additional Information (Optional)
    additional_information: '',
    
    // Legacy fields (optional)
    years_of_experience: 0,
    consultation_fee: 0.00,
    bio: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const professionalTitleOptions = [
    { value: 'Dr.', label: 'Dr. (Doctor)' },
    { value: 'Prof.', label: 'Prof. (Professor)' },
    { value: 'RN', label: 'RN (Registered Nurse)' },
    { value: 'LPN', label: 'LPN (Licensed Practical Nurse)' },
    { value: 'NP', label: 'NP (Nurse Practitioner)' },
    { value: 'PA', label: 'PA (Physician Assistant)' },
    { value: 'RPh', label: 'RPh (Pharmacist)' },
    { value: 'PT', label: 'PT (Physical Therapist)' },
    { value: 'OT', label: 'OT (Occupational Therapist)' },
    { value: 'RT', label: 'RT (Respiratory Therapist)' },
    { value: 'MT', label: 'MT (Medical Technologist)' },
    { value: 'RD', label: 'RD (Registered Dietitian)' },
    { value: 'MSW', label: 'MSW (Medical Social Worker)' },
    { value: 'Mr.', label: 'Mr.' },
    { value: 'Ms.', label: 'Ms.' },
    { value: 'Mrs.', label: 'Mrs.' }
  ];

  const professionalRoleOptions = [
    { value: 'Physician', label: 'Physician' },
    { value: 'Registered Nurse', label: 'Registered Nurse' },
    { value: 'Specialist', label: 'Specialist' },
    { value: 'Healthcare Administrator', label: 'Healthcare Administrator' },
    { value: 'Medical Technician', label: 'Medical Technician' },
    { value: 'Other', label: 'Other' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateStep = (step) => {
    const stepErrors = {};

    switch (step) {
      case 1: // Personal Information
        if (!formData.professional_title) stepErrors.professional_title = 'Professional title is required';
        if (!formData.first_name) stepErrors.first_name = 'First name is required';
        if (!formData.last_name) stepErrors.last_name = 'Last name is required';
        break;
        
      case 2: // Contact Information
        if (!formData.email) {
          stepErrors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
          stepErrors.email = 'Please enter a valid email address';
        }
        break;
        
      case 3: // Account Security
        if (!formData.password) {
          stepErrors.password = 'Password is required';
        } else if (formData.password.length < 8) {
          stepErrors.password = 'Password must be at least 8 characters long';
        }
        
        if (!formData.password_confirm) {
          stepErrors.password_confirm = 'Please confirm your password';
        } else if (formData.password !== formData.password_confirm) {
          stepErrors.password_confirm = 'Passwords do not match';
        }
        break;
        
      case 4: // Professional Information
        if (!formData.organization_facility) stepErrors.organization_facility = 'Organization/Facility is required';
        if (!formData.professional_role) stepErrors.professional_role = 'Professional role is required';
        break;
        
      case 5: // License Information
        if (!formData.license_number) stepErrors.license_number = 'License number is required';
        break;
        
      case 6: // Additional Information (Optional - no validation needed)
        break;
    }

    setErrors(stepErrors);
    return Object.keys(stepErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all steps
    let hasErrors = false;
    for (let step = 1; step <= 6; step++) {
      if (!validateStep(step)) {
        hasErrors = true;
      }
    }
    
    if (hasErrors) {
      setCurrentStep(1); // Go to first step with errors
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await providerAPI.register(formData);
      const data = await response.json();

      if (response.ok) {
        alert('Registration successful! Please check your email for verification.');
        // Redirect to login page
        window.location.href = '/provider/login';
      } else {
        setErrors(data);
        // Go to step with errors
        if (data.email) setCurrentStep(2);
        else if (data.password) setCurrentStep(3);
        else if (data.license_number) setCurrentStep(5);
        else setCurrentStep(1);
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ general: 'Network error occurred. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="step-content">
            <h3>Personal Information</h3>
            <p>Let's start with your basic details</p>
            
            <div className="form-group">
              <label htmlFor="professional_title">Professional Title *</label>
              <select
                id="professional_title"
                name="professional_title"
                value={formData.professional_title}
                onChange={handleInputChange}
                className={errors.professional_title ? 'error' : ''}
              >
                <option value="">Select Title</option>
                {professionalTitleOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {errors.professional_title && <span className="error-message">{errors.professional_title}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="first_name">First Name *</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                placeholder="Joseph"
                className={errors.first_name ? 'error' : ''}
              />
              {errors.first_name && <span className="error-message">{errors.first_name}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Last Name *</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                placeholder="Ewool"
                className={errors.last_name ? 'error' : ''}
              />
              {errors.last_name && <span className="error-message">{errors.last_name}</span>}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="step-content">
            <h3>Contact Information</h3>
            <p>How can patients and colleagues reach you?</p>
            
            <div className="form-group">
              <label htmlFor="email">Professional Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="joseph.ewool@hospital.com"
                className={errors.email ? 'error' : ''}
              />
              {errors.email && <span className="error-message">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="phone_number">Phone Number</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-content">
            <h3>Account Security</h3>
            <p>Create a secure account</p>
            
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Auto-generated from email if left empty"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Minimum 8 characters"
                className={errors.password ? 'error' : ''}
              />
              {errors.password && <span className="error-message">{errors.password}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="password_confirm">Confirm Password *</label>
              <input
                type="password"
                id="password_confirm"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleInputChange}
                placeholder="Re-enter password"
                className={errors.password_confirm ? 'error' : ''}
              />
              {errors.password_confirm && <span className="error-message">{errors.password_confirm}</span>}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="step-content">
            <h3>Professional Details</h3>
            <p>Tell us about your professional background</p>
            
            <div className="form-group">
              <label htmlFor="organization_facility">Organization/Facility *</label>
              <input
                type="text"
                id="organization_facility"
                name="organization_facility"
                value={formData.organization_facility}
                onChange={handleInputChange}
                placeholder="General Hospital, Private Practice, Clinic Name"
                className={errors.organization_facility ? 'error' : ''}
              />
              {errors.organization_facility && <span className="error-message">{errors.organization_facility}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="professional_role">Professional Role *</label>
              <select
                id="professional_role"
                name="professional_role"
                value={formData.professional_role}
                onChange={handleInputChange}
                className={errors.professional_role ? 'error' : ''}
              >
                <option value="">Select Role</option>
                {professionalRoleOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {errors.professional_role && <span className="error-message">{errors.professional_role}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="specialization">Specialization</label>
              <input
                type="text"
                id="specialization"
                name="specialization"
                value={formData.specialization}
                onChange={handleInputChange}
                placeholder="Cardiology, Pediatrics, General Practice, etc."
              />
            </div>
          </div>
        );

      case 5:
        return (
          <div className="step-content">
            <h3>License Verification</h3>
            <p>Professional license for verification</p>
            
            <div className="form-group">
              <label htmlFor="license_number">Professional License Number *</label>
              <input
                type="text"
                id="license_number"
                name="license_number"
                value={formData.license_number}
                onChange={handleInputChange}
                placeholder="Enter your medical license number"
                className={errors.license_number ? 'error' : ''}
              />
              {errors.license_number && <span className="error-message">{errors.license_number}</span>}
              <small>This will be used for professional verification</small>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="step-content">
            <h3>Additional Information</h3>
            <p>Anything else you'd like us to know? (Optional)</p>
            
            <div className="form-group">
              <label htmlFor="additional_information">Additional Information</label>
              <textarea
                id="additional_information"
                name="additional_information"
                value={formData.additional_information}
                onChange={handleInputChange}
                placeholder="Tell us about your specific IoT monitoring needs or any questions you might have"
                rows="4"
              />
            </div>

            <div className="form-group">
              <label htmlFor="years_of_experience">Years of Experience</label>
              <input
                type="number"
                id="years_of_experience"
                name="years_of_experience"
                value={formData.years_of_experience}
                onChange={handleInputChange}
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="bio">Professional Biography</label>
              <textarea
                id="bio"
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                placeholder="Brief description of your background and expertise"
                rows="3"
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="provider-registration">
      <div className="registration-container">
        <div className="progress-bar">
          <div className="progress-steps">
            {[1, 2, 3, 4, 5, 6].map(step => (
              <div
                key={step}
                className={`step ${step <= currentStep ? 'active' : ''} ${step < currentStep ? 'completed' : ''}`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="progress-text">
            Step {currentStep} of 6
          </div>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          {errors.general && (
            <div className="alert alert-error">
              {errors.general}
            </div>
          )}

          {renderStep()}

          <div className="form-actions">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={handlePrevious}
                className="btn btn-secondary"
                disabled={isSubmitting}
              >
                Previous
              </button>
            )}

            {currentStep < 6 ? (
              <button
                type="button"
                onClick={handleNext}
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                className="btn btn-success"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Registering...' : 'Complete Registration'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProviderRegistration;

/**
 * Security Configuration
 * 
 * Centralized security settings and constants
 */

export const SECURITY_CONFIG = {
  // Input validation limits
  MAX_ANIMAL_NAME_LENGTH: 100,
  MAX_SPECIES_LENGTH: 200,
  MAX_PERSONALITY_LENGTH: 2000,
  MAX_ANIMAL_ID_LENGTH: 100,
  
  // Rate limiting
  MIN_FORM_SUBMISSION_INTERVAL: 1000, // 1 second
  
  // Allowed characters patterns
  ANIMAL_ID_PATTERN: /^[a-zA-Z0-9_-]+$/,
  ANIMAL_NAME_PATTERN: /^[a-zA-Z0-9\s'\-]+$/,
  SPECIES_PATTERN: /^[a-zA-Z0-9\s()\-\.]+$/,
  
  // Content Security Policy settings
  CSP_DIRECTIVES: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'", "http://localhost:8080", "http://localhost:3001"],
  },
  
  // Environment-specific settings
  DEBUG_LOGGING: process.env.NODE_ENV === 'development',
  SENSITIVE_LOGGING: process.env.NODE_ENV === 'development' && process.env.DEBUG_SECURITY === 'true',
};

export const VALIDATION_MESSAGES = {
  REQUIRED_FIELD: 'This field is required',
  INVALID_LENGTH: 'Field length is invalid',
  INVALID_CHARACTERS: 'Field contains invalid characters',
  RATE_LIMITED: 'Please wait before submitting again',
  GENERIC_ERROR: 'An error occurred. Please try again.',
};

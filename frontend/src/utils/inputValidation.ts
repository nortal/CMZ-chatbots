/**
 * Input Validation and Sanitization Utilities
 * 
 * Provides secure validation and sanitization for user inputs
 * to prevent XSS, injection, and other security vulnerabilities.
 */

import DOMPurify from 'dompurify';

// Validation schemas
export interface AnimalConfigValidation {
  name: string;
  species: string;
  personality: string;
  active: boolean;
  educationalFocus: boolean;
  ageAppropriate: boolean;
  maxResponseLength: number;
  scientificAccuracy: 'strict' | 'moderate' | 'flexible';
  tone: 'playful' | 'wise' | 'energetic' | 'calm' | 'mysterious';
  formality: 'casual' | 'friendly' | 'professional';
  enthusiasm: number;
}

export class ValidationError extends Error {
  constructor(message: string, public field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Validates and sanitizes animal ID
 */
export function validateAnimalId(animalId: string): string {
  if (!animalId || typeof animalId !== 'string') {
    throw new ValidationError('Animal ID must be a non-empty string');
  }
  
  const trimmed = animalId.trim();
  
  // Only allow alphanumeric, hyphens, and underscores
  if (!/^[a-zA-Z0-9_-]+$/.test(trimmed)) {
    throw new ValidationError('Animal ID contains invalid characters');
  }
  
  if (trimmed.length > 100) {
    throw new ValidationError('Animal ID too long (max 100 characters)');
  }
  
  return trimmed;
}

/**
 * Validates and sanitizes animal name
 */
export function validateAnimalName(name: string): string {
  if (!name || typeof name !== 'string') {
    throw new ValidationError('Animal name is required', 'name');
  }
  
  const trimmed = name.trim();
  
  if (trimmed.length < 1) {
    throw new ValidationError('Animal name cannot be empty', 'name');
  }
  
  if (trimmed.length > 100) {
    throw new ValidationError('Animal name too long (max 100 characters)', 'name');
  }
  
  // Allow letters, numbers, spaces, apostrophes, and hyphens
  if (!/^[a-zA-Z0-9\s'\-]+$/.test(trimmed)) {
    throw new ValidationError('Animal name contains invalid characters', 'name');
  }
  
  // Sanitize any potential HTML
  return DOMPurify.sanitize(trimmed, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
}

/**
 * Validates and sanitizes species name
 */
export function validateSpecies(species: string): string {
  if (!species || typeof species !== 'string') {
    throw new ValidationError('Species is required', 'species');
  }
  
  const trimmed = species.trim();
  
  if (trimmed.length < 1) {
    throw new ValidationError('Species cannot be empty', 'species');
  }
  
  if (trimmed.length > 200) {
    throw new ValidationError('Species name too long (max 200 characters)', 'species');
  }
  
  // Allow letters, numbers, spaces, parentheses, and scientific notation
  if (!/^[a-zA-Z0-9\s()\-\.]+$/.test(trimmed)) {
    throw new ValidationError('Species name contains invalid characters', 'species');
  }
  
  return DOMPurify.sanitize(trimmed, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
}

/**
 * Validates and sanitizes personality description
 */
export function validatePersonality(personality: string): string {
  if (!personality) {
    return ''; // Personality is optional
  }
  
  if (typeof personality !== 'string') {
    throw new ValidationError('Personality must be text', 'personality');
  }
  
  const trimmed = personality.trim();
  
  if (trimmed.length > 2000) {
    throw new ValidationError('Personality description too long (max 2000 characters)', 'personality');
  }
  
  // Sanitize HTML but allow basic formatting
  return DOMPurify.sanitize(trimmed, {
    ALLOWED_TAGS: [], // No HTML tags allowed for security
    ALLOWED_ATTR: []
  });
}

/**
 * Validates numeric values
 */
export function validateNumber(value: any, min: number, max: number, fieldName: string): number {
  const num = typeof value === 'string' ? parseInt(value, 10) : Number(value);
  
  if (isNaN(num)) {
    throw new ValidationError(`${fieldName} must be a valid number`, fieldName);
  }
  
  if (num < min || num > max) {
    throw new ValidationError(`${fieldName} must be between ${min} and ${max}`, fieldName);
  }
  
  return num;
}

/**
 * Validates enum values
 */
export function validateEnum<T extends string>(
  value: string, 
  allowedValues: readonly T[], 
  fieldName: string
): T {
  if (!allowedValues.includes(value as T)) {
    throw new ValidationError(
      `${fieldName} must be one of: ${allowedValues.join(', ')}`, 
      fieldName
    );
  }
  
  return value as T;
}

/**
 * Validates boolean values
 */
export function validateBoolean(value: any, fieldName: string): boolean {
  if (typeof value === 'boolean') {
    return value;
  }
  
  if (typeof value === 'string') {
    if (value.toLowerCase() === 'true') return true;
    if (value.toLowerCase() === 'false') return false;
  }
  
  throw new ValidationError(`${fieldName} must be true or false`, fieldName);
}

/**
 * Comprehensive animal configuration validation
 */
export function validateAnimalConfig(data: any): AnimalConfigValidation {
  const errors: string[] = [];
  
  try {
    const validated: AnimalConfigValidation = {
      name: validateAnimalName(data.name),
      species: validateSpecies(data.species),
      personality: validatePersonality(data.personality || ''),
      active: validateBoolean(data.active, 'active'),
      educationalFocus: validateBoolean(data.educationalFocus, 'educationalFocus'),
      ageAppropriate: validateBoolean(data.ageAppropriate, 'ageAppropriate'),
      maxResponseLength: validateNumber(data.maxResponseLength, 50, 2000, 'maxResponseLength'),
      scientificAccuracy: validateEnum(
        data.scientificAccuracy, 
        ['strict', 'moderate', 'flexible'] as const, 
        'scientificAccuracy'
      ),
      tone: validateEnum(
        data.tone,
        ['playful', 'wise', 'energetic', 'calm', 'mysterious'] as const,
        'tone'
      ),
      formality: validateEnum(
        data.formality,
        ['casual', 'friendly', 'professional'] as const,
        'formality'
      ),
      enthusiasm: validateNumber(data.enthusiasm, 1, 10, 'enthusiasm'),
    };
    
    return validated;
    
  } catch (error) {
    if (error instanceof ValidationError) {
      errors.push(error.message);
    } else {
      errors.push('Unexpected validation error');
    }
  }
  
  if (errors.length > 0) {
    throw new ValidationError(`Validation failed: ${errors.join(', ')}`);
  }
  
  // This should never be reached due to the structure above, but TypeScript needs it
  throw new ValidationError('Validation failed unexpectedly');
}

/**
 * Safely extracts form data from DOM elements
 */
export function extractFormDataSafely(formElement: HTMLFormElement): Record<string, any> {
  if (!formElement || !(formElement instanceof HTMLFormElement)) {
    throw new ValidationError('Invalid form element');
  }
  
  const formData = new FormData(formElement);
  const data: Record<string, any> = {};
  
  for (const [key, value] of formData.entries()) {
    // Sanitize all form values
    if (typeof value === 'string') {
      data[key] = DOMPurify.sanitize(value.trim(), { 
        ALLOWED_TAGS: [], 
        ALLOWED_ATTR: [] 
      });
    } else {
      data[key] = value;
    }
  }
  
  return data;
}

/**
 * Rate limiting for form submissions
 */
class RateLimiter {
  private lastSubmission = 0;
  private readonly minInterval = 1000; // 1 second minimum between submissions
  
  public checkRateLimit(): void {
    const now = Date.now();
    if (now - this.lastSubmission < this.minInterval) {
      throw new ValidationError('Please wait before submitting again');
    }
    this.lastSubmission = now;
  }
}

export const formRateLimiter = new RateLimiter();
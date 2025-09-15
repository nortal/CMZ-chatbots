/**
 * Secure Form Handling Hook
 * 
 * Provides secure form data extraction, validation, and submission
 * to prevent XSS, injection, and other security vulnerabilities.
 */

import { useState, useCallback } from 'react';
import {
  ValidationError,
  formRateLimiter
} from '../utils/inputValidation';

interface FormError {
  message: string;
  field?: string;
}

interface UseSecureFormHandlingResult {
  errors: FormError[];
  isSubmitting: boolean;
  submitForm: (formData: any) => Promise<any>;
  clearErrors: () => void;
  getFieldError: (fieldName: string) => string | undefined;
}

export function useSecureFormHandling(
  onSubmit: (validatedData: any) => Promise<any>
): UseSecureFormHandlingResult {
  const [errors, setErrors] = useState<FormError[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const getFieldError = useCallback((fieldName: string): string | undefined => {
    const fieldError = errors.find(error => error.field === fieldName);
    return fieldError?.message;
  }, [errors]);

  const submitForm = useCallback(async (formData: any) => {
    setErrors([]);
    setIsSubmitting(true);

    try {
      // Rate limiting check
      formRateLimiter.checkRateLimit();

      // Validate and sanitize the form data using the new method
      const validatedData = validateSecureAnimalConfigData(formData);

      // Submit the validated data
      const result = await onSubmit(validatedData);
      
      return result;

    } catch (error) {
      if (error instanceof ValidationError) {
        setErrors([{
          message: error.message,
          field: error.field
        }]);
      } else if (error instanceof Error) {
        setErrors([{
          message: 'An unexpected error occurred. Please try again.',
        }]);
        
        // Log the actual error for debugging (but don't expose to user)
        if (process.env.NODE_ENV === 'development') {
          console.error('Form submission error:', error);
        }
      } else {
        setErrors([{
          message: 'An unknown error occurred. Please try again.',
        }]);
      }
      
      throw error; // Re-throw so caller can handle it
      
    } finally {
      setIsSubmitting(false);
    }
  }, [onSubmit]);

  return {
    errors,
    isSubmitting,
    submitForm,
    clearErrors,
    getFieldError,
  };
}

/**
 * Secure DOM element value extraction with optional existence check
 */
export function getSecureElementValue(elementId: string, required: boolean = true): string | null {
  const element = document.getElementById(elementId);

  if (!element) {
    if (required) {
      throw new ValidationError(`Element with ID '${elementId}' not found`);
    }
    return null; // Element doesn't exist, return null for optional elements
  }

  if (element instanceof HTMLInputElement ||
      element instanceof HTMLTextAreaElement ||
      element instanceof HTMLSelectElement) {
    return element.value.trim();
  }

  throw new ValidationError(`Element '${elementId}' is not a form input`);
}

/**
 * Secure checkbox value extraction with optional existence check
 */
export function getSecureCheckboxValue(elementId: string, required: boolean = true): boolean | null {
  const element = document.getElementById(elementId);

  if (!element) {
    if (required) {
      throw new ValidationError(`Checkbox with ID '${elementId}' not found`);
    }
    return null; // Element doesn't exist, return null for optional elements
  }

  if (element instanceof HTMLInputElement && element.type === 'checkbox') {
    return element.checked;
  }

  throw new ValidationError(`Element '${elementId}' is not a checkbox`);
}

/**
 * Secure form data validation for directly passed form data (no DOM extraction needed)
 * This replaces the previous DOM-dependent method with direct data validation.
 */
export function validateSecureAnimalConfigData(formData: any): any {
  try {
    if (!formData || typeof formData !== 'object') {
      throw new ValidationError('Invalid form data provided');
    }

    // Validate and sanitize the form data
    const result = {
      name: (formData.name || '').toString().trim(),
      species: (formData.species || '').toString().trim(),
      personality: (formData.personality || '').toString().trim(),
      active: Boolean(formData.active),
      educationalFocus: Boolean(formData.educationalFocus),
      ageAppropriate: Boolean(formData.ageAppropriate),
      maxResponseLength: Math.max(50, Math.min(2000, parseInt(formData.maxResponseLength) || 500)),
      scientificAccuracy: ['strict', 'moderate', 'flexible'].includes(formData.scientificAccuracy)
        ? formData.scientificAccuracy : 'moderate',
      tone: ['playful', 'wise', 'energetic', 'calm', 'mysterious'].includes(formData.tone)
        ? formData.tone : 'friendly',
      formality: ['casual', 'friendly', 'professional'].includes(formData.formality)
        ? formData.formality : 'friendly',
      enthusiasm: Math.max(1, Math.min(10, parseInt(formData.enthusiasm) || 5)),
      allowPersonalQuestions: Boolean(formData.allowPersonalQuestions),
      // AI Model Settings - ensure numeric types for temperature and topP
      voice: (formData.voice || 'alloy').toString().trim(),
      aiModel: (formData.aiModel || 'gpt-4o-mini').toString().trim(),
      temperature: typeof formData.temperature === 'number'
        ? formData.temperature
        : parseFloat(formData.temperature || '0.7'),
      topP: typeof formData.topP === 'number'
        ? formData.topP
        : parseFloat(formData.topP || '1.0'),
      toolsEnabled: Array.isArray(formData.toolsEnabled) ? formData.toolsEnabled : ['facts', 'media_lookup']
    };

    if (process.env.NODE_ENV === 'development') {
      console.debug('[DEBUG] Form data validated successfully:', Object.keys(result));
    }

    return result;
  } catch (error) {
    if (error instanceof ValidationError) {
      throw error;
    }
    throw new ValidationError('Failed to validate form data safely');
  }
}

/**
 * @deprecated Use validateSecureAnimalConfigData instead
 * Secure form data collection from animal configuration form with tab-aware extraction
 * This function is kept for backward compatibility but should not be used with the new form implementation.
 */
export function getSecureAnimalConfigData(): any {
  console.warn('[DEPRECATED] getSecureAnimalConfigData is deprecated. Use validateSecureAnimalConfigData with direct form data instead.');
  throw new ValidationError('DOM extraction is no longer supported. Please pass form data directly to validateSecureAnimalConfigData.');
}
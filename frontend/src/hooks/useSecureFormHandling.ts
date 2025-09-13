/**
 * Secure Form Handling Hook
 * 
 * Provides secure form data extraction, validation, and submission
 * to prevent XSS, injection, and other security vulnerabilities.
 */

import { useState, useCallback } from 'react';
import { 
  validateAnimalConfig, 
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

      // Validate and sanitize the form data
      const validatedData = validateAnimalConfig(formData);

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
 * Secure DOM element value extraction
 */
export function getSecureElementValue(elementId: string): string {
  const element = document.getElementById(elementId);
  
  if (!element) {
    throw new ValidationError(`Element with ID '${elementId}' not found`);
  }
  
  if (element instanceof HTMLInputElement || 
      element instanceof HTMLTextAreaElement || 
      element instanceof HTMLSelectElement) {
    return element.value.trim();
  }
  
  throw new ValidationError(`Element '${elementId}' is not a form input`);
}

/**
 * Secure checkbox value extraction
 */
export function getSecureCheckboxValue(elementId: string): boolean {
  const element = document.getElementById(elementId);
  
  if (!element) {
    throw new ValidationError(`Checkbox with ID '${elementId}' not found`);
  }
  
  if (element instanceof HTMLInputElement && element.type === 'checkbox') {
    return element.checked;
  }
  
  throw new ValidationError(`Element '${elementId}' is not a checkbox`);
}

/**
 * Secure form data collection from animal configuration form
 */
export function getSecureAnimalConfigData(): any {
  try {
    return {
      name: getSecureElementValue('animal-name-input') || '',
      species: getSecureElementValue('animal-species-input') || '',
      personality: getSecureElementValue('personality-textarea') || '',
      active: getSecureCheckboxValue('animal-active-checkbox'),
      educationalFocus: getSecureCheckboxValue('educational-focus-checkbox'),
      ageAppropriate: getSecureCheckboxValue('age-appropriate-checkbox'),
      maxResponseLength: parseInt(getSecureElementValue('max-response-length-input') || '500', 10),
      scientificAccuracy: getSecureElementValue('scientific-accuracy-select') || 'moderate',
      tone: getSecureElementValue('tone-select') || 'friendly',
      formality: getSecureElementValue('formality-select') || 'friendly',
      enthusiasm: parseInt(getSecureElementValue('enthusiasm-range') || '5', 10),
    };
  } catch (error) {
    if (error instanceof ValidationError) {
      throw error;
    }
    throw new ValidationError('Failed to extract form data safely');
  }
}
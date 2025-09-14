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
 * Secure form data collection from animal configuration form with tab-aware extraction
 */
export function getSecureAnimalConfigData(): any {
  try {
    // Collect data from elements that exist in the current tab
    // Basic Info Tab elements (may not be in DOM if Settings tab is active)
    const name = getSecureElementValue('animal-name-input', false);
    const species = getSecureElementValue('animal-species-input', false);
    const personality = getSecureElementValue('personality-textarea', false);
    const active = getSecureCheckboxValue('animal-active-checkbox', false);
    const educationalFocus = getSecureCheckboxValue('educational-focus-checkbox', false);
    const ageAppropriate = getSecureCheckboxValue('age-appropriate-checkbox', false);

    // Settings Tab elements (may not be in DOM if Basic Info tab is active)
    const maxResponseLengthStr = getSecureElementValue('max-response-length-input', false);
    const scientificAccuracy = getSecureElementValue('scientific-accuracy-select', false);
    const tone = getSecureElementValue('tone-select', false);
    const formality = getSecureElementValue('formality-select', false);
    const enthusiasmStr = getSecureElementValue('enthusiasm-range', false);
    const allowPersonalQuestions = getSecureCheckboxValue('allow-personal-questions-checkbox', false);

    // Build result object with only the data we can collect
    const result: any = {};

    // Add Basic Info data if available
    if (name !== null) result.name = name || '';
    if (species !== null) result.species = species || '';
    if (personality !== null) result.personality = personality || '';
    if (active !== null) result.active = active;
    if (educationalFocus !== null) result.educationalFocus = educationalFocus;
    if (ageAppropriate !== null) result.ageAppropriate = ageAppropriate;

    // Add Settings data if available
    if (maxResponseLengthStr !== null) {
      result.maxResponseLength = parseInt(maxResponseLengthStr || '500', 10);
    }
    if (scientificAccuracy !== null) {
      result.scientificAccuracy = scientificAccuracy || 'moderate';
    }
    if (tone !== null) result.tone = tone || 'friendly';
    if (formality !== null) result.formality = formality || 'friendly';
    if (enthusiasmStr !== null) {
      result.enthusiasm = parseInt(enthusiasmStr || '5', 10);
    }
    if (allowPersonalQuestions !== null) result.allowPersonalQuestions = allowPersonalQuestions;

    // Validate that we collected at least some data
    if (Object.keys(result).length === 0) {
      throw new ValidationError('No form data could be collected from any tab');
    }

    if (process.env.NODE_ENV === 'development') {
      console.debug('[DEBUG] Tab-aware form data collected:', Object.keys(result));
    }

    return result;
  } catch (error) {
    if (error instanceof ValidationError) {
      throw error;
    }
    throw new ValidationError('Failed to extract form data safely');
  }
}
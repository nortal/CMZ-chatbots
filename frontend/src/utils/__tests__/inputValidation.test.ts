/**
 * Security Validation Tests
 * 
 * Tests for input validation and sanitization functions
 */

import {
  validateAnimalId,
  validateAnimalName,
  validatePersonality,
  ValidationError,
} from '../inputValidation';

describe('Security Input Validation', () => {
  describe('validateAnimalId', () => {
    test('should accept valid animal IDs', () => {
      expect(validateAnimalId('test-animal-1')).toBe('test-animal-1');
      expect(validateAnimalId('test_animal_2')).toBe('test_animal_2');
      expect(validateAnimalId('TestAnimal3')).toBe('TestAnimal3');
    });

    test('should reject malicious input', () => {
      expect(() => validateAnimalId("'; DROP TABLE animals; --")).toThrow(ValidationError);
      expect(() => validateAnimalId('<script>alert("xss")</script>')).toThrow(ValidationError);
      expect(() => validateAnimalId('animal')).toThrow(ValidationError);
    });

    test('should reject empty or invalid input', () => {
      expect(() => validateAnimalId('')).toThrow(ValidationError);
      expect(() => validateAnimalId('   ')).toThrow(ValidationError);
      expect(() => validateAnimalId(null as any)).toThrow(ValidationError);
    });
  });

  describe('validatePersonality', () => {
    test('should sanitize HTML content', () => {
      const maliciousInput = '<script>alert("xss")</script>Friendly animal';
      const result = validatePersonality(maliciousInput);
      expect(result).not.toContain('<script>');
      expect(result).toContain('Friendly animal');
    });

    test('should enforce length limits', () => {
      const longInput = 'a'.repeat(2001);
      expect(() => validatePersonality(longInput)).toThrow(ValidationError);
    });
  });

  describe('validateAnimalName', () => {
    test('should accept valid names', () => {
      expect(validateAnimalName('Bella the Bear')).toBe('Bella the Bear');
      expect(validateAnimalName("O'Malley")).toBe("O'Malley");
      expect(validateAnimalName('Multi-word Name')).toBe('Multi-word Name');
    });

    test('should reject malicious input', () => {
      expect(() => validateAnimalName('<img src=x onerror=alert(1)>')).toThrow(ValidationError);
      expect(() => validateAnimalName('Name${evil}')).toThrow(ValidationError);
    });
  });
});

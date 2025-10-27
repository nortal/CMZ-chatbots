/**
 * AssistantForm Component
 *
 * Form component for creating and editing Animal Assistants
 * Handles personality and guardrail selection with validation
 *
 * T028 - User Story 1: Create and Deploy Live Animal Assistant
 */

import React, { useState, useEffect } from 'react';
import {
  AssistantFormProps,
  CreateAssistantRequest,
  UpdateAssistantRequest,
  AssistantStatus,
  AnimalAssistant
} from '../../types/AssistantTypes';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';

const AssistantForm: React.FC<AssistantFormProps> = ({
  assistant,
  animals,
  personalities,
  guardrails,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const isEditMode = !!assistant;

  // Form state
  const [formData, setFormData] = useState<CreateAssistantRequest | UpdateAssistantRequest>({
    animalId: assistant?.animalId || '',
    personalityId: assistant?.personalityId || '',
    guardrailId: assistant?.guardrailId || '',
    knowledgeBaseFileIds: assistant?.knowledgeBaseFileIds || [],
    ...(isEditMode && { status: assistant?.status || AssistantStatus.ACTIVE }),
  });

  const [errors, setErrors] = useState<string[]>([]);
  const [selectedPersonality, setSelectedPersonality] = useState(
    personalities.find(p => p.personalityId === formData.personalityId)
  );
  const [selectedGuardrail, setSelectedGuardrail] = useState(
    guardrails.find(g => g.guardrailId === formData.guardrailId)
  );

  // Update personality and guardrail details when selection changes
  useEffect(() => {
    if (formData.personalityId) {
      const personality = personalities.find(p => p.personalityId === formData.personalityId);
      setSelectedPersonality(personality);
    }
  }, [formData.personalityId, personalities]);

  useEffect(() => {
    if (formData.guardrailId) {
      const guardrail = guardrails.find(g => g.guardrailId === formData.guardrailId);
      setSelectedGuardrail(guardrail);
    }
  }, [formData.guardrailId, guardrails]);

  const validateForm = (): string[] => {
    const validationErrors: string[] = [];

    if (!formData.animalId?.trim()) {
      validationErrors.push('Animal selection is required');
    }
    if (!formData.personalityId?.trim()) {
      validationErrors.push('Personality selection is required');
    }
    if (!formData.guardrailId?.trim()) {
      validationErrors.push('Guardrail selection is required');
    }
    if (formData.knowledgeBaseFileIds && formData.knowledgeBaseFileIds.length > 50) {
      validationErrors.push('Maximum of 50 knowledge base files allowed');
    }

    return validationErrors;
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    // Clear errors when user starts typing
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      setErrors([]);
      await onSubmit(formData);
    } catch (error) {
      setErrors([error instanceof Error ? error.message : 'Failed to save assistant']);
    }
  };

  const selectedAnimal = animals.find(a => a.animalId === formData.animalId);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {isEditMode ? 'Edit Assistant' : 'Create New Assistant'}
          </CardTitle>
          <CardDescription>
            {isEditMode
              ? 'Update the configuration for this animal assistant'
              : 'Create a new digital ambassador for an animal with personality and safety guardrails'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Error Display */}
            {errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <h4 className="text-sm font-medium text-red-800 mb-2">
                  Please fix the following errors:
                </h4>
                <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Animal Selection */}
              <div className="space-y-2">
                <Label htmlFor="animal">Animal *</Label>
                <Select
                  value={formData.animalId}
                  onValueChange={(value) => handleInputChange('animalId', value)}
                  disabled={isEditMode} // Cannot change animal for existing assistant
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select an animal" />
                  </SelectTrigger>
                  <SelectContent>
                    {animals.map((animal) => (
                      <SelectItem key={animal.animalId} value={animal.animalId}>
                        {animal.name} ({animal.species})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedAnimal && (
                  <p className="text-sm text-gray-600">
                    Species: {selectedAnimal.species}
                    {selectedAnimal.scientificName && (
                      <span className="italic"> ({selectedAnimal.scientificName})</span>
                    )}
                  </p>
                )}
              </div>

              {/* Status (Edit Mode Only) */}
              {isEditMode && (
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) => handleInputChange('status', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={AssistantStatus.ACTIVE}>Active</SelectItem>
                      <SelectItem value={AssistantStatus.INACTIVE}>Inactive</SelectItem>
                      <SelectItem value={AssistantStatus.ERROR}>Error</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

            </div>

            {/* Personality Selection */}
            <div className="space-y-2">
              <Label htmlFor="personality">Personality Configuration *</Label>
              <Select
                value={formData.personalityId}
                onValueChange={(value) => handleInputChange('personalityId', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a personality configuration" />
                </SelectTrigger>
                <SelectContent>
                  {personalities.map((personality) => (
                    <SelectItem key={personality.personalityId} value={personality.personalityId}>
                      <div className="flex items-center gap-2">
                        {personality.name}
                        <Badge variant="outline">{personality.tone}</Badge>
                        <Badge variant="secondary">{personality.ageTarget}</Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {selectedPersonality && (
                <Card className="bg-blue-50 border-blue-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">{selectedPersonality.name}</CardTitle>
                    <div className="flex gap-2">
                      <Badge variant="outline">{selectedPersonality.animalType}</Badge>
                      <Badge variant="secondary">{selectedPersonality.tone}</Badge>
                      <Badge>{selectedPersonality.ageTarget}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-700 mb-2">{selectedPersonality.description}</p>
                    <details className="text-sm">
                      <summary className="cursor-pointer font-medium">View Personality Text</summary>
                      <p className="mt-2 text-gray-600 whitespace-pre-wrap bg-white p-2 rounded border">
                        {selectedPersonality.personalityText}
                      </p>
                    </details>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Guardrail Selection */}
            <div className="space-y-2">
              <Label htmlFor="guardrail">Safety Guardrails *</Label>
              <Select
                value={formData.guardrailId}
                onValueChange={(value) => handleInputChange('guardrailId', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select safety guardrails" />
                </SelectTrigger>
                <SelectContent>
                  {guardrails.map((guardrail) => (
                    <SelectItem key={guardrail.guardrailId} value={guardrail.guardrailId}>
                      <div className="flex items-center gap-2">
                        {guardrail.name}
                        <Badge variant="outline">{guardrail.category}</Badge>
                        <Badge variant={guardrail.severity === 'STRICT' ? 'destructive' : 'secondary'}>
                          {guardrail.severity}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {selectedGuardrail && (
                <Card className="bg-orange-50 border-orange-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">{selectedGuardrail.name}</CardTitle>
                    <div className="flex gap-2">
                      <Badge variant="outline">{selectedGuardrail.category}</Badge>
                      <Badge variant={selectedGuardrail.severity === 'STRICT' ? 'destructive' : 'secondary'}>
                        {selectedGuardrail.severity}
                      </Badge>
                      {selectedGuardrail.isDefault && (
                        <Badge variant="default">Default</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-700 mb-2">{selectedGuardrail.description}</p>
                    <p className="text-sm">
                      <strong>Age Groups:</strong> {selectedGuardrail.ageAppropriate.join(', ')}
                    </p>
                    <details className="text-sm mt-2">
                      <summary className="cursor-pointer font-medium">View Guardrail Rules</summary>
                      <p className="mt-2 text-gray-600 whitespace-pre-wrap bg-white p-2 rounded border">
                        {selectedGuardrail.guardrailText}
                      </p>
                    </details>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Knowledge Base Files (Future Enhancement) */}
            <div className="space-y-2">
              <Label>Knowledge Base Files</Label>
              <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-md p-4 text-center">
                <p className="text-sm text-gray-600">
                  Knowledge base file management will be available in Phase 5
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Current files: {formData.knowledgeBaseFileIds?.length || 0}
                </p>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end gap-3 pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isLoading
                  ? (isEditMode ? 'Updating...' : 'Creating...')
                  : (isEditMode ? 'Update Assistant' : 'Create Assistant')
                }
              </Button>
            </div>

          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default AssistantForm;
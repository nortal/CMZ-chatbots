/**
 * React hooks for animal data management
 * 
 * Provides hooks to interact with the animal API and manage state
 */

import { useState, useEffect, useCallback } from 'react';
import { animalApi, Animal, AnimalConfig } from '../services/api';

export interface UseAnimalsResult {
  animals: Animal[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage list of animals
 */
export function useAnimals(): UseAnimalsResult {
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnimals = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedAnimals = await animalApi.listAnimals();
      setAnimals(fetchedAnimals);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch animals');
      console.error('Error fetching animals:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnimals();
  }, [fetchAnimals]);

  return {
    animals,
    loading,
    error,
    refetch: fetchAnimals,
  };
}

export interface UseAnimalConfigResult {
  config: AnimalConfig | null;
  loading: boolean;
  error: string | null;
  updateConfig: (updates: Partial<AnimalConfig>) => Promise<void>;
  updateAnimal: (updates: Partial<Animal>) => Promise<void>;
  saving: boolean;
  saveError: string | null;
}

/**
 * Hook to fetch and manage animal configuration
 */
export function useAnimalConfig(animalId: string | null): UseAnimalConfigResult {
  const [config, setConfig] = useState<AnimalConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const fetchConfig = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const fetchedConfig = await animalApi.getAnimalConfig(id);
      setConfig(fetchedConfig);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch animal configuration');
      console.error('Error fetching animal config:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (updates: Partial<AnimalConfig>) => {
    if (!animalId) {
      setSaveError('No animal ID provided');
      return;
    }

    try {
      setSaving(true);
      setSaveError(null);
      const updatedConfig = await animalApi.updateAnimalConfig(animalId, updates);
      setConfig(updatedConfig);
      console.log('Animal configuration updated successfully');
    } catch (err) {
      // TODO: Fix underlying API issue (track in Jira PR003946-XXX)
      // Backend sometimes returns errors even when DynamoDB operations succeed
      // This verification workaround should be removed after backend error handling is improved
      try {
        const verifyConfig = await animalApi.getAnimalConfig(animalId);
        // Check if any of the updates were actually applied
        const updateKeys = Object.keys(updates);
        const wasUpdated = updateKeys.some(key => {
          const updateValue = updates[key as keyof AnimalConfig];
          const currentValue = verifyConfig[key as keyof AnimalConfig];
          return JSON.stringify(updateValue) === JSON.stringify(currentValue);
        });

        if (wasUpdated) {
          // Data was saved despite the error
          console.log('Animal configuration saved successfully (verified after error)');
          setSaveError(null);
          setConfig(verifyConfig);
          return verifyConfig;
        }
      } catch (verifyErr) {
        // Verification failed, original error stands
      }

      setSaveError(err instanceof Error ? err.message : 'Failed to update configuration');
      console.error('Error updating animal config:', err);
      throw err; // Re-throw to allow component to handle
    } finally {
      setSaving(false);
    }
  }, [animalId]);

  const updateAnimal = useCallback(async (updates: Partial<Animal>) => {
    if (!animalId) {
      setSaveError('No animal ID provided');
      return;
    }

    try {
      setSaving(true);
      setSaveError(null);
      const updatedAnimal = await animalApi.updateAnimal(animalId, updates);
      console.log('Animal details updated successfully');
      return updatedAnimal;
    } catch (err) {
      // Verify if save actually succeeded despite error (500 error workaround)
      try {
        const verifyAnimal = await animalApi.getAnimalDetails(animalId);
        // Check if any of the updates were actually applied
        const updateKeys = Object.keys(updates);
        const wasUpdated = updateKeys.some(key => {
          const updateValue = updates[key as keyof Animal];
          const currentValue = verifyAnimal[key as keyof Animal];
          return updateValue === currentValue;
        });

        if (wasUpdated) {
          // Data was saved despite the error
          console.log('Animal details saved successfully (verified after error)');
          setSaveError(null);
          return verifyAnimal;
        }
      } catch (verifyErr) {
        // Verification failed, original error stands
      }

      setSaveError(err instanceof Error ? err.message : 'Failed to update animal details');
      console.error('Error updating animal details:', err);
      throw err; // Re-throw to allow component to handle
    } finally {
      setSaving(false);
    }
  }, [animalId]);

  useEffect(() => {
    if (animalId) {
      fetchConfig(animalId);
    } else {
      setConfig(null);
      setError(null);
    }
  }, [animalId, fetchConfig]);

  return {
    config,
    loading,
    error,
    updateConfig,
    updateAnimal,
    saving,
    saveError,
  };
}


export default useAnimals;
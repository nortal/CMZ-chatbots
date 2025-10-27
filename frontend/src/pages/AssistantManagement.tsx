/**
 * AssistantManagement Page
 *
 * Main dashboard for managing Animal Assistants
 * Provides CRUD operations and overview of active assistants
 *
 * T029 - User Story 1: Create and Deploy Live Animal Assistant
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AnimalAssistant,
  Personality,
  Guardrail,
  Animal,
  CreateAssistantRequest,
  UpdateAssistantRequest,
  AssistantStatus
} from '../types/AssistantTypes';
import { assistantApi, personalityApi, guardrailApi, assistantUtils } from '../services/AssistantService';
import { animalApi } from '../services/api';
import AssistantForm from '../components/assistants/AssistantForm';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const AssistantManagement: React.FC = () => {
  const navigate = useNavigate();

  // State management
  const [assistants, setAssistants] = useState<AnimalAssistant[]>([]);
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [guardrails, setGuardrails] = useState<Guardrail[]>([]);
  const [animals, setAnimals] = useState<Animal[]>([]);

  const [loading, setLoading] = useState({
    assistants: true,
    personalities: true,
    guardrails: true,
    animals: true,
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAssistant, setSelectedAssistant] = useState<AnimalAssistant | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load initial data
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    await Promise.all([
      loadAssistants(),
      loadPersonalities(),
      loadGuardrails(),
      loadAnimals(),
    ]);
  };

  const loadAssistants = async () => {
    try {
      setLoading(prev => ({ ...prev, assistants: true }));
      setErrors(prev => ({ ...prev, assistants: '' }));
      const response = await assistantApi.listAssistants();
      setAssistants(response.assistants || []);
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        assistants: error instanceof Error ? error.message : 'Failed to load assistants'
      }));
    } finally {
      setLoading(prev => ({ ...prev, assistants: false }));
    }
  };

  const loadPersonalities = async () => {
    try {
      setLoading(prev => ({ ...prev, personalities: true }));
      setErrors(prev => ({ ...prev, personalities: '' }));
      const response = await personalityApi.listPersonalities();
      setPersonalities(response.personalities || []);
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        personalities: error instanceof Error ? error.message : 'Failed to load personalities'
      }));
    } finally {
      setLoading(prev => ({ ...prev, personalities: false }));
    }
  };

  const loadGuardrails = async () => {
    try {
      setLoading(prev => ({ ...prev, guardrails: true }));
      setErrors(prev => ({ ...prev, guardrails: '' }));
      const response = await guardrailApi.listGuardrails();
      setGuardrails(response.guardrails || []);
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        guardrails: error instanceof Error ? error.message : 'Failed to load guardrails'
      }));
    } finally {
      setLoading(prev => ({ ...prev, guardrails: false }));
    }
  };

  const loadAnimals = async () => {
    try {
      setLoading(prev => ({ ...prev, animals: true }));
      setErrors(prev => ({ ...prev, animals: '' }));
      const animalsData = await animalApi.listAnimals();
      setAnimals(animalsData || []);
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        animals: error instanceof Error ? error.message : 'Failed to load animals'
      }));
    } finally {
      setLoading(prev => ({ ...prev, animals: false }));
    }
  };

  // Assistant CRUD operations
  const handleCreateAssistant = async (data: CreateAssistantRequest) => {
    try {
      setIsSubmitting(true);
      const newAssistant = await assistantApi.createAssistant(data);
      setAssistants(prev => [...prev, newAssistant]);
      setShowCreateForm(false);
    } catch (error) {
      throw error; // Let form handle the error
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateAssistant = async (data: UpdateAssistantRequest) => {
    if (!selectedAssistant) return;

    try {
      setIsSubmitting(true);
      const updatedAssistant = await assistantApi.updateAssistant(selectedAssistant.assistantId, data);
      setAssistants(prev =>
        prev.map(a => a.assistantId === selectedAssistant.assistantId ? updatedAssistant : a)
      );
      setSelectedAssistant(null);
      setShowEditForm(false);
    } catch (error) {
      throw error; // Let form handle the error
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteAssistant = async (assistantId: string) => {
    if (!confirm('Are you sure you want to delete this assistant? This action cannot be undone.')) {
      return;
    }

    try {
      await assistantApi.deleteAssistant(assistantId);
      setAssistants(prev => prev.filter(a => a.assistantId !== assistantId));
    } catch (error) {
      alert(`Failed to delete assistant: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleRefreshPrompt = async (assistant: AnimalAssistant) => {
    try {
      const refreshedAssistant = await assistantApi.refreshAssistantPrompt(assistant.assistantId);
      setAssistants(prev =>
        prev.map(a => a.assistantId === assistant.assistantId ? refreshedAssistant : a)
      );
    } catch (error) {
      alert(`Failed to refresh prompt: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Filtered assistants for search
  const filteredAssistants = assistants.filter(assistant => {
    const animal = animals.find(a => a.animalId === assistant.animalId);
    const personality = personalities.find(p => p.personalityId === assistant.personalityId);
    const searchLower = searchTerm.toLowerCase();

    return (
      animal?.name.toLowerCase().includes(searchLower) ||
      animal?.species.toLowerCase().includes(searchLower) ||
      personality?.name.toLowerCase().includes(searchLower) ||
      assistant.status.toLowerCase().includes(searchLower)
    );
  });

  // Available animals for new assistants (those without existing assistants)
  const availableAnimals = animals.filter(animal =>
    !assistants.some(assistant => assistant.animalId === animal.animalId)
  );

  // Statistics
  const stats = {
    total: assistants.length,
    active: assistants.filter(a => a.status === AssistantStatus.ACTIVE).length,
    inactive: assistants.filter(a => a.status === AssistantStatus.INACTIVE).length,
    error: assistants.filter(a => a.status === AssistantStatus.ERROR).length,
  };

  const isDataLoading = Object.values(loading).some(Boolean);

  return (
    <div className="container mx-auto p-6 space-y-6">

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Assistant Management</h1>
          <p className="text-gray-600 mt-1">
            Manage digital animal ambassadors with personality and safety configurations
          </p>
        </div>
        <Button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700"
          disabled={isDataLoading || availableAnimals.length === 0}
        >
          Create New Assistant
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Assistants</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Inactive</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.inactive}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Errors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.error}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Assistant Directory</CardTitle>
          <CardDescription>Search and manage your animal assistants</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Input
              placeholder="Search by animal name, species, or personality..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <Button
              variant="outline"
              onClick={loadAllData}
              disabled={isDataLoading}
            >
              {isDataLoading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>

          {/* Error Messages */}
          {Object.entries(errors).map(([key, error]) => (
            error && (
              <div key={key} className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
                <p className="text-sm text-red-700">
                  <strong>{key}:</strong> {error}
                </p>
              </div>
            )
          ))}

          {/* Assistant Table */}
          {isDataLoading ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Loading assistants...</p>
            </div>
          ) : filteredAssistants.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">
                {searchTerm ? 'No assistants match your search' : 'No assistants configured yet'}
              </p>
              {!searchTerm && availableAnimals.length > 0 && (
                <Button
                  className="mt-2"
                  onClick={() => setShowCreateForm(true)}
                >
                  Create Your First Assistant
                </Button>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Animal</TableHead>
                  <TableHead>Personality</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAssistants.map((assistant) => {
                  const animal = animals.find(a => a.animalId === assistant.animalId);
                  const personality = personalities.find(p => p.personalityId === assistant.personalityId);
                  const guardrail = guardrails.find(g => g.guardrailId === assistant.guardrailId);
                  const formattedAssistant = assistantUtils.formatAssistantForDisplay(assistant);

                  return (
                    <TableRow key={assistant.assistantId}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{animal?.name || 'Unknown Animal'}</div>
                          <div className="text-sm text-gray-500">{animal?.species}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{personality?.name || 'Unknown Personality'}</div>
                          <div className="flex gap-1 mt-1">
                            {personality && (
                              <Badge variant="outline" className="text-xs">
                                {personality.tone}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            assistant.status === AssistantStatus.ACTIVE ? 'default' :
                            assistant.status === AssistantStatus.INACTIVE ? 'secondary' : 'destructive'
                          }
                        >
                          {formattedAssistant.statusDisplay}
                        </Badge>
                      </TableCell>
                      <TableCell>{formattedAssistant.lastUpdated}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedAssistant(assistant);
                              setShowEditForm(true);
                            }}
                          >
                            Edit
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRefreshPrompt(assistant)}
                          >
                            Refresh
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteAssistant(assistant.assistantId)}
                          >
                            Delete
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Create Assistant Dialog */}
      <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Assistant</DialogTitle>
            <DialogDescription>
              Configure a new digital ambassador for an animal
            </DialogDescription>
          </DialogHeader>
          <AssistantForm
            animals={availableAnimals}
            personalities={personalities}
            guardrails={guardrails}
            onSubmit={handleCreateAssistant}
            onCancel={() => setShowCreateForm(false)}
            isLoading={isSubmitting}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Assistant Dialog */}
      <Dialog open={showEditForm} onOpenChange={setShowEditForm}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Assistant</DialogTitle>
            <DialogDescription>
              Update assistant configuration
            </DialogDescription>
          </DialogHeader>
          {selectedAssistant && (
            <AssistantForm
              assistant={selectedAssistant}
              animals={animals}
              personalities={personalities}
              guardrails={guardrails}
              onSubmit={handleUpdateAssistant}
              onCancel={() => {
                setSelectedAssistant(null);
                setShowEditForm(false);
              }}
              isLoading={isSubmitting}
            />
          )}
        </DialogContent>
      </Dialog>

    </div>
  );
};

export default AssistantManagement;
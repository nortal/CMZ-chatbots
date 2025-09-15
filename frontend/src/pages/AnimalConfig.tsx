import React, { useState, useEffect } from 'react';
import { Zap, Settings, Eye, Edit, Plus, Save, BookOpen, Shield, Brain, MessageSquare, Database, AlertTriangle } from 'lucide-react';
import { useAnimals, useAnimalConfig } from '../hooks/useAnimals';
import { Animal as BackendAnimal, AnimalConfig as BackendAnimalConfig } from '../services/api';
import { utils } from '../services/api';
import { useSecureFormHandling } from '../hooks/useSecureFormHandling';
import { ValidationError } from '../utils/inputValidation';

interface KnowledgeEntry {
  id: string;
  category: 'biology' | 'behavior' | 'conservation' | 'habitat' | 'diet' | 'reproduction' | 'interaction';
  title: string;
  content: string;
  tags: string[];
  verified: boolean;
  lastUpdated: string;
}

interface Guardrail {
  id: string;
  type: 'content' | 'safety' | 'educational' | 'behavioral';
  rule: string;
  enabled: boolean;
  severity: 'low' | 'medium' | 'high';
}

// Frontend animal interface that extends backend animal with UI-specific fields
interface Animal extends BackendAnimal {
  id: string;
  lastUpdated: string;
  conversations: number;
  personality?: string;
  systemPrompt?: string;
  knowledgeBase?: KnowledgeEntry[];
  guardrails?: Record<string, any>;
  conversationSettings?: {
    maxResponseLength: number;
    educationalFocus: boolean;
    allowPersonalQuestions: boolean;
    scientificAccuracy: 'strict' | 'moderate' | 'flexible';
    ageAppropriate: boolean;
  };
  voiceSettings?: {
    tone: 'playful' | 'wise' | 'energetic' | 'calm' | 'mysterious';
    formality: 'casual' | 'friendly' | 'professional';
    enthusiasm: number; // 1-10
  };
}

const AnimalConfig: React.FC = () => {
  // Use our API hooks
  const { animals: backendAnimals, loading: animalsLoading, error: animalsError, refetch } = useAnimals();
  
  // Transform backend animals to frontend format
  const [animals, setAnimals] = useState<Animal[]>([]);
  
  useEffect(() => {
    if (backendAnimals) {
      const transformedAnimals = backendAnimals.map(animal => utils.transformAnimalForFrontend(animal));
      setAnimals(transformedAnimals);
    }
  }, [backendAnimals]);
  
  // No fallback mock data - always use real data from DynamoDB

  const [selectedAnimal, setSelectedAnimal] = useState<Animal | null>(null);
  const [selectedAnimalId, setSelectedAnimalId] = useState<string | null>(null);
  
  // Use the animal config hook for the selected animal
  const {
    config: animalConfig,
    loading: configLoading,
    error: configError,
    updateConfig,
    updateAnimal,
    saving: configSaving,
    saveError
  } = useAnimalConfig(selectedAnimalId);
  
  // Handle animal selection
  const handleSelectAnimal = (animal: Animal) => {
    setSelectedAnimal(animal);
    setSelectedAnimalId(animal.animalId || animal.id);
  };
  
  // Handle configuration save with secure error handling
  const handleSaveConfig = async (configData: any) => {
    try {
      // Separate Animal fields from AnimalConfig fields
      const { name, species, status, ...configFields } = configData;

      // Update Animal fields (name, species, status) if they have changed
      const animalUpdates: any = {};
      if (name !== selectedAnimal?.name) animalUpdates.name = name;
      if (species !== selectedAnimal?.species) animalUpdates.species = species;
      if (status !== undefined && status !== selectedAnimal?.status) animalUpdates.status = status;

      // Update both entities in parallel
      const promises = [];

      // Only update Animal if there are changes
      if (Object.keys(animalUpdates).length > 0) {
        promises.push(updateAnimal(animalUpdates));
      }

      // Update AnimalConfig with remaining fields
      promises.push(updateConfig(configFields));

      // Wait for both updates to complete
      await Promise.all(promises);

      // Refresh the animals list to get updated data
      refetch();
    } catch (error) {
      // Secure error handling - don't expose sensitive details
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to save configuration:', error);
      }
      throw error; // Re-throw for form handler
    }
  };

  const AnimalCard: React.FC<{ animal: Animal }> = ({ animal }) => (
    <div className="bg-white rounded-lg border hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <Zap className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-900">{animal.name}</h3>
              <p className="text-sm text-gray-600 italic">{animal.species}</p>
            </div>
          </div>
          <div className="flex items-center">
            <span className={`px-2 py-1 rounded-full text-xs font-medium mr-3 ${
              animal.active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-600'
            }`}>
              {animal.active ? 'Active' : 'Inactive'}
            </span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={animal.active}
                readOnly
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Last Updated</p>
            <p className="font-medium">{animal.lastUpdated}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Conversations</p>
            <p className="font-medium">{animal.conversations}</p>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Personality</p>
          <p className="text-sm text-gray-800 bg-gray-50 p-3 rounded-lg">
            {animal.personality}
          </p>
        </div>

        <div className="flex space-x-2">
          <button 
            onClick={() => handleSelectAnimal(animal)}
            className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Edit className="w-4 h-4 mr-2" />
            Configure
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Eye className="w-4 h-4" />
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const ConfigurationModal: React.FC = () => {
    if (!selectedAnimal) return null;

    // Form state management - maintain state across all tabs
    const [formData, setFormData] = useState({
      name: '',
      species: '',
      personality: '',
      systemPrompt: '', // Added systemPrompt to formData
      active: false,
      educationalFocus: false,
      ageAppropriate: false,
      // AI Model Settings (required by API)
      voice: 'alloy',
      aiModel: 'gpt-4o-mini',
      temperature: 0.7,
      topP: 1.0,
      toolsEnabled: ['facts', 'media_lookup'],
      guardrails: {},
      // Conversation Settings
      maxResponseLength: 500,
      scientificAccuracy: 'moderate',
      tone: 'friendly',
      formality: 'friendly',
      enthusiasm: 5,
      allowPersonalQuestions: false
    });

    // Initialize form data when config loads or selectedAnimal changes
    useEffect(() => {
      // Don't reset form if we're in the middle of saving
      if (configSaving) {
        return;
      }

      // Only update form data if we have actual data to update with
      // This prevents clearing the form when animalConfig temporarily becomes null during refetch
      if (!selectedAnimal && !animalConfig) {
        return;
      }

      // Use selectedAnimal for name and species since they're not in animalConfig
      // Use animalConfig for all other configuration fields
      setFormData(prevData => ({
        name: selectedAnimal?.name || prevData.name || '',
        species: selectedAnimal?.species || prevData.species || '',
        personality: animalConfig?.personality || selectedAnimal?.personality || prevData.personality || '',
        systemPrompt: animalConfig?.systemPrompt || prevData.systemPrompt || '', // Added systemPrompt initialization
        active: animalConfig?.active !== undefined ? animalConfig.active : (selectedAnimal?.active !== undefined ? selectedAnimal.active : prevData.active),
        educationalFocus: animalConfig?.conversationSettings?.educationalFocus !== undefined ?
          animalConfig.conversationSettings.educationalFocus : prevData.educationalFocus,
        ageAppropriate: animalConfig?.conversationSettings?.ageAppropriate !== undefined ?
          animalConfig.conversationSettings.ageAppropriate : prevData.ageAppropriate,
        // AI Model Settings (required by API)
        voice: animalConfig?.voice || prevData.voice || 'alloy',
        aiModel: animalConfig?.aiModel || prevData.aiModel || 'gpt-4o-mini',
        temperature: animalConfig?.temperature !== undefined ?
          (typeof animalConfig.temperature === 'number' ? animalConfig.temperature : parseFloat(animalConfig.temperature))
          : (prevData.temperature || 0.7),
        topP: animalConfig?.topP !== undefined ?
          (typeof animalConfig.topP === 'number' ? animalConfig.topP : parseFloat(animalConfig.topP))
          : (prevData.topP || 1.0),
        toolsEnabled: animalConfig?.toolsEnabled || prevData.toolsEnabled || ['facts', 'media_lookup'],
        guardrails: animalConfig?.guardrails || prevData.guardrails || {},
        // Conversation Settings
        maxResponseLength: animalConfig?.conversationSettings?.maxResponseLength || prevData.maxResponseLength || 500,
        scientificAccuracy: animalConfig?.conversationSettings?.scientificAccuracy || prevData.scientificAccuracy || 'moderate',
        tone: animalConfig?.voiceSettings?.tone || prevData.tone || 'friendly',
        formality: animalConfig?.voiceSettings?.formality || prevData.formality || 'friendly',
        enthusiasm: animalConfig?.voiceSettings?.enthusiasm || prevData.enthusiasm || 5,
        allowPersonalQuestions: animalConfig?.conversationSettings?.allowPersonalQuestions !== undefined ?
          animalConfig.conversationSettings.allowPersonalQuestions : prevData.allowPersonalQuestions
      }));
    }, [animalConfig, selectedAnimal, configSaving]);

    // Use secure form handling with our form data
    const { isSubmitting, submitForm, clearErrors, getFieldError } = useSecureFormHandling(
      handleSaveConfig
    );

    const [activeTab, setActiveTab] = useState<'basic' | 'prompt' | 'knowledge' | 'guardrails' | 'settings'>('basic');

    // Form field update handler
    const updateField = (field: string, value: any) => {
      setFormData(prev => ({ ...prev, [field]: value }));
      clearErrors();
    };

    const getSeverityColor = (severity: string) => {
      switch (severity) {
        case 'high': return 'bg-red-100 text-red-800';
        case 'medium': return 'bg-yellow-100 text-yellow-800';
        case 'low': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    const getCategoryColor = (category: string) => {
      switch (category) {
        case 'biology': return 'bg-blue-100 text-blue-800';
        case 'behavior': return 'bg-green-100 text-green-800';
        case 'conservation': return 'bg-purple-100 text-purple-800';
        case 'habitat': return 'bg-orange-100 text-orange-800';
        case 'diet': return 'bg-pink-100 text-pink-800';
        case 'reproduction': return 'bg-indigo-100 text-indigo-800';
        case 'interaction': return 'bg-yellow-100 text-yellow-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Brain className="w-6 h-6 text-green-600 mr-3" />
                <h2 className="text-xl font-semibold">Configure {animalConfig?.name || selectedAnimal?.name || 'Animal'}</h2>
                {configLoading && <span className="ml-2 text-sm text-gray-500">Loading...</span>}
              </div>
              <button 
                onClick={() => {
                  setSelectedAnimal(null);
                  setSelectedAnimalId(null);
                }}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
          </div>
          
          {/* Tab Navigation */}
          <div className="border-b">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'basic', label: 'Basic Info', icon: Settings },
                { id: 'prompt', label: 'System Prompt', icon: Brain },
                { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
                { id: 'guardrails', label: 'Guardrails', icon: Shield },
                { id: 'settings', label: 'Settings', icon: MessageSquare }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as any)}
                  className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === id
                      ? 'border-green-500 text-green-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6 max-h-[calc(90vh-200px)] overflow-y-auto">
            {activeTab === 'basic' && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Animal Name
                    </label>
                    <input
                      id="animal-name-input"
                      type="text"
                      value={formData.name}
                      onChange={(e) => updateField('name', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                        getFieldError('name') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-green-500'
                      }`}
                    />
                    {getFieldError('name') && <p className="text-red-500 text-sm mt-1">{getFieldError('name')}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Species (Scientific Name)
                    </label>
                    <input
                      id="animal-species-input"
                      type="text"
                      value={formData.species}
                      onChange={(e) => updateField('species', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                        getFieldError('species') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-green-500'
                      }`}
                    />
                    {getFieldError('species') && <p className="text-red-500 text-sm mt-1">{getFieldError('species')}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Personality & Behavior
                  </label>
                  <textarea
                    rows={4}
                    value={formData.personality}
                    onChange={(e) => updateField('personality', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                      getFieldError('personality') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-green-500'
                    }`}
                    placeholder="Describe the animal's personality, how it should interact with visitors..."
                    id="personality-textarea"
                  />
                  {getFieldError('personality') && <p className="text-red-500 text-sm mt-1">{getFieldError('personality')}</p>}
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="flex items-center">
                      <input
                        id="animal-active-checkbox"
                        type="checkbox"
                        checked={formData.active}
                        onChange={(e) => updateField('active', e.target.checked)}
                        className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Active</span>
                    </label>
                  </div>
                  <div>
                    <label className="flex items-center">
                      <input
                        id="educational-focus-checkbox"
                        type="checkbox"
                        checked={formData.educationalFocus}
                        onChange={(e) => updateField('educationalFocus', e.target.checked)}
                        className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Educational Focus</span>
                    </label>
                  </div>
                  <div>
                    <label className="flex items-center">
                      <input
                        id="age-appropriate-checkbox"
                        type="checkbox"
                        checked={formData.ageAppropriate}
                        onChange={(e) => updateField('ageAppropriate', e.target.checked)}
                        className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Age Appropriate</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'prompt' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    System Prompt
                  </label>
                  <textarea
                    rows={12}
                    value={formData.systemPrompt}
                    onChange={(e) => updateField('systemPrompt', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-sm"
                    placeholder="System prompt that defines how the AI should behave as this animal..."
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    This prompt defines the animal's character, personality, and behavior patterns. Be specific about tone, knowledge areas, and interaction style.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'knowledge' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Knowledge Base ({animalConfig?.knowledgeBase?.length || 0} entries)</h3>
                  <button className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Entry
                  </button>
                </div>
                
                <div className="space-y-4">
                  {animalConfig?.knowledgeBase?.map(entry => (
                    <div key={entry.id} className="bg-gray-50 rounded-lg p-4 border">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(entry.category)}`}>
                              {entry.category}
                            </span>
                            {entry.verified && (
                              <span className="text-green-600 text-xs flex items-center">
                                <Database className="w-3 h-3 mr-1" />
                                Verified
                              </span>
                            )}
                          </div>
                          <h4 className="font-medium text-gray-900">{entry.title}</h4>
                          <p className="text-sm text-gray-700 mt-1">{entry.content}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {entry.tags.map((tag, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                                {tag}
                              </span>
                            ))}
                          </div>
                          <p className="text-xs text-gray-500 mt-2">Last updated: {entry.lastUpdated}</p>
                        </div>
                        <div className="flex space-x-2 ml-4">
                          <button className="p-2 text-gray-400 hover:text-gray-600">
                            <Edit className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'guardrails' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Safety Guardrails ({animalConfig?.guardrails ? Object.keys(animalConfig.guardrails).length : 0} active)</h3>
                  <button className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Guardrail
                  </button>
                </div>
                
                <div className="space-y-4">
                  {animalConfig?.guardrails && Object.keys(animalConfig.guardrails).length > 0 ? (
                    Object.entries(animalConfig.guardrails).map(([key, value]) => (
                      <div key={key} className="bg-gray-50 rounded-lg p-4 border">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {key}
                              </span>
                            </div>
                            <p className="text-sm text-gray-900">
                              {typeof value === 'boolean' ? (value ? 'Enabled' : 'Disabled') : String(value)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2 ml-4">
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                className="sr-only peer"
                                checked={typeof value === 'boolean' ? value : false}
                                readOnly
                              />
                              <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-600"></div>
                            </label>
                            <button className="p-2 text-gray-400 hover:text-gray-600">
                              <Edit className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <p>No guardrails configured</p>
                      <p className="text-sm">Click "Add Guardrail" to create safety rules</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                {/* AI Model Settings Section */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-medium mb-4">AI Model Settings</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Voice
                      </label>
                      <select
                        value={formData.voice}
                        onChange={(e) => updateField('voice', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="alloy">Alloy</option>
                        <option value="echo">Echo</option>
                        <option value="fable">Fable</option>
                        <option value="onyx">Onyx</option>
                        <option value="nova">Nova</option>
                        <option value="shimmer">Shimmer</option>
                        <option value="ruth">Ruth</option>
                        <option value="joanna">Joanna</option>
                        <option value="matthew">Matthew</option>
                        <option value="amy">Amy</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        AI Model
                      </label>
                      <select
                        value={formData.aiModel}
                        onChange={(e) => updateField('aiModel', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="gpt-4o-mini">GPT-4o Mini</option>
                        <option value="gpt-4o">GPT-4o</option>
                        <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                        <option value="claude-3-haiku">Claude 3 Haiku</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Temperature ({formData.temperature})
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="2"
                        step="0.1"
                        value={formData.temperature}
                        onChange={(e) => updateField('temperature', parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Deterministic</span>
                        <span>Creative</span>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Top P ({formData.topP})
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={formData.topP}
                        onChange={(e) => updateField('topP', parseFloat(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Enabled Tools
                      </label>
                      <div className="space-y-2">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.toolsEnabled.includes('facts')}
                            onChange={(e) => {
                              const tools = e.target.checked
                                ? [...formData.toolsEnabled, 'facts']
                                : formData.toolsEnabled.filter(t => t !== 'facts');
                              updateField('toolsEnabled', tools);
                            }}
                            className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                          />
                          <span className="text-sm">Facts Lookup</span>
                        </label>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.toolsEnabled.includes('media_lookup')}
                            onChange={(e) => {
                              const tools = e.target.checked
                                ? [...formData.toolsEnabled, 'media_lookup']
                                : formData.toolsEnabled.filter(t => t !== 'media_lookup');
                              updateField('toolsEnabled', tools);
                            }}
                            className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                          />
                          <span className="text-sm">Media Lookup</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Conversation Settings</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Response Length
                      </label>
                      <input
                        id="max-response-length-input"
                        type="number"
                        value={formData.maxResponseLength}
                        onChange={(e) => updateField('maxResponseLength', parseInt(e.target.value) || 500)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Scientific Accuracy
                      </label>
                      <select
                        id="scientific-accuracy-select"
                        value={formData.scientificAccuracy}
                        onChange={(e) => updateField('scientificAccuracy', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="strict">Strict</option>
                        <option value="moderate">Moderate</option>
                        <option value="flexible">Flexible</option>
                      </select>
                    </div>

                    <div>
                      <label className="flex items-center">
                        <input
                          id="allow-personal-questions-checkbox"
                          type="checkbox"
                          checked={formData.allowPersonalQuestions}
                          onChange={(e) => updateField('allowPersonalQuestions', e.target.checked)}
                          className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                        />
                        <span className="text-sm font-medium text-gray-700">Allow Personal Questions</span>
                      </label>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Voice & Personality</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tone
                      </label>
                      <select
                        id="tone-select"
                        value={formData.tone}
                        onChange={(e) => updateField('tone', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="playful">Playful</option>
                        <option value="wise">Wise</option>
                        <option value="energetic">Energetic</option>
                        <option value="calm">Calm</option>
                        <option value="mysterious">Mysterious</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Formality
                      </label>
                      <select
                        id="formality-select"
                        value={formData.formality}
                        onChange={(e) => updateField('formality', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="casual">Casual</option>
                        <option value="friendly">Friendly</option>
                        <option value="professional">Professional</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Enthusiasm Level ({formData.enthusiasm}/10)
                      </label>
                      <input
                        id="enthusiasm-range"
                        type="range"
                        min="1"
                        max="10"
                        value={formData.enthusiasm}
                        onChange={(e) => updateField('enthusiasm', parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-6 border-t bg-gray-50 flex justify-between">
            <button
              onClick={() => {
                setSelectedAnimal(null);
                setSelectedAnimalId(null);
              }}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <div className="space-x-3">
              <button className="px-6 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors">
                Test Chatbot
              </button>
              <button
                onClick={() => {
                  try {
                    // Use our managed form data instead of DOM extraction
                    submitForm(formData);
                  } catch (error) {
                    if (error instanceof ValidationError) {
                      console.debug('Form validation error:', error.message);
                    }
                  }
                }}
                disabled={configSaving || isSubmitting}
                className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-4 h-4 mr-2" />
                {configSaving || isSubmitting ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Animal Configuration</h1>
          <p className="text-gray-600">Manage animal personalities and chatbot behaviors</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          <Plus className="w-4 h-4 mr-2" />
          Add New Animal
        </button>
      </div>

      
      {/* Error handling */}
      {animalsError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-sm text-red-800">Error loading animals: {animalsError}</span>
          </div>
        </div>
      )}
      
      {/* Configuration error handling */}
      {configError && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-800">Error loading configuration: {configError}</span>
          </div>
        </div>
      )}

      {/* Save error handling */}
      {saveError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-sm text-red-800">Error saving: {saveError}</span>
          </div>
        </div>
      )}

      {animalsLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="text-gray-500">Loading animals...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {animals.length > 0 ? (
            animals.map(animal => (
              <AnimalCard key={animal.id || animal.animalId} animal={animal} />
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Animals Found</h3>
              <p className="text-gray-500">
                No animals are currently configured in the system.
              </p>
            </div>
          )}
        </div>
      )}

      <ConfigurationModal />
    </div>
  );
};

export default AnimalConfig;
import React, { useState, useEffect } from 'react';
import { Zap, Settings, Eye, Edit, Plus, Save, BookOpen, Shield, Brain, MessageSquare, Database, AlertTriangle } from 'lucide-react';
import { useAnimals, useAnimalConfig, useApiHealth } from '../hooks/useAnimals';
import { Animal as BackendAnimal, AnimalConfig as BackendAnimalConfig } from '../services/api';
import { utils } from '../services/api';

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
  guardrails?: Guardrail[];
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
  const { isHealthy, checkHealth } = useApiHealth();
  
  // Transform backend animals to frontend format
  const [animals, setAnimals] = useState<Animal[]>([]);
  
  useEffect(() => {
    if (backendAnimals) {
      const transformedAnimals = backendAnimals.map(animal => utils.transformAnimalForFrontend(animal));
      setAnimals(transformedAnimals);
    }
  }, [backendAnimals]);
  
  // Fallback to mock data if API is not available
  const [mockAnimals] = useState<Animal[]>([
    {
      id: 'cheetah-1',
      name: 'Cheetah',
      species: 'Acinonyx jubatus',
      active: true,
      lastUpdated: 'Today at 9:24 AM',
      conversations: 156,
      personality: 'Energetic and educational, loves talking about speed and hunting techniques',
      systemPrompt: `You are Kesi, a cheetah at Cougar Mountain Zoo. You are the fastest land animal on Earth, capable of reaching speeds up to 70 mph. You're energetic, educational, and passionate about conservation. 

Your key traits:
- Enthusiastic about speed and hunting techniques
- Educational focus on African savanna ecosystems
- Concerned about cheetah conservation (only 7,000 left in the wild)
- Friendly but maintain your wild nature
- Use your incredible eyesight and agility as teaching points

Always stay in character as a cheetah. Be educational but engaging, especially when discussing speed, hunting, or conservation. Keep responses appropriate for all ages.`,
      knowledgeBase: [
        {
          id: 'kb-1',
          category: 'biology',
          title: 'Cheetah Speed Mechanics',
          content: 'Cheetahs can accelerate from 0-60 mph in 3 seconds. Their flexible spine, large heart, and non-retractable claws provide the biomechanical advantages needed for extreme speed.',
          tags: ['speed', 'biomechanics', 'anatomy'],
          verified: true,
          lastUpdated: '2024-03-01'
        },
        {
          id: 'kb-2',
          category: 'conservation',
          title: 'Cheetah Conservation Status',
          content: 'Only 7,000 cheetahs remain in the wild. Primary threats include habitat loss, human-wildlife conflict, and genetic bottlenecking. Conservation efforts focus on corridor protection.',
          tags: ['endangered', 'threats', 'protection'],
          verified: true,
          lastUpdated: '2024-02-15'
        },
        {
          id: 'kb-3',
          category: 'behavior',
          title: 'Hunting Techniques',
          content: 'Cheetahs hunt during daylight to avoid competition with larger predators. They use their exceptional eyesight to spot prey from up to 3 miles away.',
          tags: ['hunting', 'behavior', 'daylight'],
          verified: true,
          lastUpdated: '2024-03-05'
        }
      ],
      guardrails: [
        {
          id: 'gr-1',
          type: 'educational',
          rule: 'Always provide accurate scientific information about cheetah biology and behavior',
          enabled: true,
          severity: 'high'
        },
        {
          id: 'gr-2',
          type: 'safety',
          rule: 'Never encourage visitors to attempt dangerous activities or approach wild animals',
          enabled: true,
          severity: 'high'
        },
        {
          id: 'gr-3',
          type: 'content',
          rule: 'Keep all content age-appropriate and educational',
          enabled: true,
          severity: 'medium'
        }
      ],
      conversationSettings: {
        maxResponseLength: 300,
        educationalFocus: true,
        allowPersonalQuestions: true,
        scientificAccuracy: 'strict',
        ageAppropriate: true
      },
      voiceSettings: {
        tone: 'energetic',
        formality: 'friendly',
        enthusiasm: 8
      }
    },
    {
      id: 'tiger-1', 
      name: 'Siberian Tiger',
      species: 'Panthera tigris altaica',
      active: true,
      lastUpdated: 'Yesterday at 3:15 PM',
      conversations: 203,
      personality: 'Wise and powerful, enjoys discussing conservation and habitat protection',
      systemPrompt: `You are Bayu, a Siberian tiger at Cougar Mountain Zoo. You are the largest living cat species and an apex predator from the forests of Siberia and Northeast China. You embody wisdom, power, and deep concern for conservation.

Your key traits:
- Wise and contemplative, with years of experience
- Passionate advocate for tiger conservation
- Knowledgeable about forest ecosystems and apex predator roles
- Respectful but powerful presence
- Patient teacher about wildlife protection

Stay in character as a Siberian tiger. Share your wisdom about conservation, forest ecosystems, and the importance of apex predators. Be educational while maintaining your majestic, powerful nature.`,
      knowledgeBase: [
        {
          id: 'kb-t1',
          category: 'biology',
          title: 'Siberian Tiger Adaptations',
          content: 'Siberian tigers are the largest cats, weighing up to 660 pounds. Their thick fur and fat layer help them survive temperatures as low as -40°F.',
          tags: ['size', 'adaptations', 'cold-weather'],
          verified: true,
          lastUpdated: '2024-03-01'
        },
        {
          id: 'kb-t2',
          category: 'conservation',
          title: 'Tiger Population Recovery',
          content: 'Siberian tiger population has increased from 30 in the 1930s to about 400-500 today through strict protection measures in Russia.',
          tags: ['population', 'recovery', 'success-story'],
          verified: true,
          lastUpdated: '2024-02-20'
        }
      ],
      guardrails: [
        {
          id: 'gr-t1',
          type: 'educational',
          rule: 'Emphasize conservation success stories while acknowledging ongoing threats',
          enabled: true,
          severity: 'high'
        },
        {
          id: 'gr-t2',
          type: 'behavioral',
          rule: 'Maintain dignity and wisdom befitting an apex predator',
          enabled: true,
          severity: 'medium'
        }
      ],
      conversationSettings: {
        maxResponseLength: 350,
        educationalFocus: true,
        allowPersonalQuestions: true,
        scientificAccuracy: 'strict',
        ageAppropriate: true
      },
      voiceSettings: {
        tone: 'wise',
        formality: 'professional',
        enthusiasm: 6
      }
    },
    {
      id: 'elephant-1',
      name: 'African Elephant',
      species: 'Loxodonta africana',
      active: false,
      lastUpdated: '3 days ago',
      conversations: 89,
      personality: 'Gentle giant with stories about family bonds and memory',
      systemPrompt: `You are Tembo, an African elephant at Cougar Mountain Zoo. You are one of the most intelligent animals on Earth, with an exceptional memory and strong family bonds. You represent wisdom, empathy, and the importance of family.

Your key traits:
- Gentle and wise, with incredible memory
- Strong emphasis on family bonds and social connections
- Knowledgeable about African ecosystems and elephant behavior
- Empathetic and emotionally intelligent
- Patient storyteller about elephant culture

Share your wisdom about family, memory, and the importance of protecting elephant habitats. Be gentle and nurturing in your interactions while educating about elephant intelligence and social behavior.`,
      knowledgeBase: [
        {
          id: 'kb-e1',
          category: 'behavior',
          title: 'Elephant Memory and Intelligence',
          content: 'Elephants have excellent memories and can remember individuals for decades. They show empathy, self-awareness, and complex problem-solving abilities.',
          tags: ['memory', 'intelligence', 'emotions'],
          verified: true,
          lastUpdated: '2024-02-28'
        },
        {
          id: 'kb-e2',
          category: 'behavior',
          title: 'Matriarchal Society',
          content: 'Elephant herds are led by the oldest female (matriarch). Family groups can include 3-4 generations of related females and their young.',
          tags: ['family', 'matriarchy', 'social-structure'],
          verified: true,
          lastUpdated: '2024-03-01'
        }
      ],
      guardrails: [
        {
          id: 'gr-e1',
          type: 'educational',
          rule: 'Emphasize emotional intelligence and family bonds in explanations',
          enabled: true,
          severity: 'medium'
        },
        {
          id: 'gr-e2',
          type: 'content',
          rule: 'Be gentle and nurturing in all interactions, especially with children',
          enabled: true,
          severity: 'high'
        }
      ],
      conversationSettings: {
        maxResponseLength: 400,
        educationalFocus: true,
        allowPersonalQuestions: true,
        scientificAccuracy: 'moderate',
        ageAppropriate: true
      },
      voiceSettings: {
        tone: 'calm',
        formality: 'friendly',
        enthusiasm: 5
      }
    }
  ]);

  const [selectedAnimal, setSelectedAnimal] = useState<Animal | null>(null);
  const [selectedAnimalId, setSelectedAnimalId] = useState<string | null>(null);
  
  // Use the animal config hook for the selected animal
  const { 
    config: animalConfig, 
    loading: configLoading, 
    error: configError, 
    updateConfig,
    saving: configSaving,
    saveError 
  } = useAnimalConfig(selectedAnimalId);
  
  // Handle animal selection
  const handleSelectAnimal = (animal: Animal) => {
    setSelectedAnimal(animal);
    setSelectedAnimalId(animal.animalId || animal.id);
  };
  
  // Handle configuration save
  const handleSaveConfig = async (configData: any) => {
    try {
      await updateConfig(configData);
      // Refresh the animals list to get updated data
      refetch();
    } catch (error) {
      console.error('Failed to save configuration:', error);
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

    const [activeTab, setActiveTab] = useState<'basic' | 'prompt' | 'knowledge' | 'guardrails' | 'settings'>('basic');

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
                <h2 className="text-xl font-semibold">Configure {selectedAnimal.name}</h2>
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
                      type="text"
                      defaultValue={selectedAnimal.name}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Species (Scientific Name)
                    </label>
                    <input
                      type="text"
                      defaultValue={selectedAnimal.species}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Personality & Behavior
                  </label>
                  <textarea
                    rows={4}
                    defaultValue={animalConfig?.personality || selectedAnimal.personality}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Describe the animal's personality, how it should interact with visitors..."
                    id="personality-textarea"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked={selectedAnimal.active}
                        className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Active</span>
                    </label>
                  </div>
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked={selectedAnimal.conversationSettings.educationalFocus}
                        className="mr-2 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Educational Focus</span>
                    </label>
                  </div>
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked={selectedAnimal.conversationSettings.ageAppropriate}
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
                    defaultValue={selectedAnimal.systemPrompt}
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
                  <h3 className="text-lg font-medium">Knowledge Base ({selectedAnimal.knowledgeBase.length} entries)</h3>
                  <button className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Entry
                  </button>
                </div>
                
                <div className="space-y-4">
                  {selectedAnimal.knowledgeBase.map(entry => (
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
                  <h3 className="text-lg font-medium">Safety Guardrails ({selectedAnimal.guardrails.length} active)</h3>
                  <button className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Guardrail
                  </button>
                </div>
                
                <div className="space-y-4">
                  {selectedAnimal.guardrails.map(guardrail => (
                    <div key={guardrail.id} className="bg-gray-50 rounded-lg p-4 border">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(guardrail.severity)}`}>
                              {guardrail.severity} priority
                            </span>
                            <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                              {guardrail.type}
                            </span>
                          </div>
                          <p className="text-sm text-gray-900">{guardrail.rule}</p>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              className="sr-only peer"
                              checked={guardrail.enabled}
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
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Conversation Settings</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Response Length
                      </label>
                      <input
                        type="number"
                        defaultValue={selectedAnimal.conversationSettings.maxResponseLength}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Scientific Accuracy
                      </label>
                      <select 
                        defaultValue={selectedAnimal.conversationSettings.scientificAccuracy}
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
                          type="checkbox"
                          defaultChecked={selectedAnimal.conversationSettings.allowPersonalQuestions}
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
                        defaultValue={selectedAnimal.voiceSettings.tone}
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
                        defaultValue={selectedAnimal.voiceSettings.formality}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        <option value="casual">Casual</option>
                        <option value="friendly">Friendly</option>
                        <option value="professional">Professional</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Enthusiasm Level ({selectedAnimal.voiceSettings.enthusiasm}/10)
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        defaultValue={selectedAnimal.voiceSettings.enthusiasm}
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
                  // Get form data and save
                  const personalityEl = document.getElementById('personality-textarea') as HTMLTextAreaElement;
                  const configData = {
                    personality: personalityEl?.value || animalConfig?.personality,
                    // Add other form fields as needed
                  };
                  handleSaveConfig(configData);
                }}
                disabled={configSaving}
                className="flex items-center px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-4 h-4 mr-2" />
                {configSaving ? 'Saving...' : 'Save Configuration'}
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

      {/* API Status Indicator */}
      {!isHealthy && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-800">
              Backend API unavailable. Using offline mode with limited functionality.
            </span>
            <button 
              onClick={checkHealth}
              className="ml-auto text-sm text-yellow-600 hover:text-yellow-800 underline"
            >
              Retry
            </button>
          </div>
        </div>
      )}
      
      {/* Error handling */}
      {animalsError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-sm text-red-800">Error loading animals: {animalsError}</span>
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
          {(animals.length > 0 ? animals : mockAnimals).map(animal => (
            <AnimalCard key={animal.id || animal.animalId} animal={animal} />
          ))}
        </div>
      )}

      <ConfigurationModal />
    </div>
  );
};

export default AnimalConfig;
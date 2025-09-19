import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Search, Filter, Eye, Edit, MessageCircle, MapPin, Heart, Activity, Save, X } from 'lucide-react';

interface Animal {
  animalId: string;
  name: string;
  species: string;
  status: string;
  personality?: {
    traits?: string[];
    description?: string;
  };
  configuration?: {
    chatbotActive?: boolean;
    voice?: string;
    responseStyle?: string;
  };
  created?: {
    at?: string;
    by?: {
      userId?: string;
      email?: string;
    };
  };
  modified?: {
    at?: string;
    by?: {
      userId?: string;
      email?: string;
    };
  };
}

interface EditableAnimal extends Animal {
  // Additional fields for editing
  commonName?: string;
  age?: number;
  gender?: 'Male' | 'Female' | 'Unknown';
  weight?: string;
  habitat?: string;
  conservationStatus?: string;
  dateArrived?: string;
  birthDate?: string;
  origin?: string;
  dietaryNeeds?: string[];
  medicalHistory?: string[];
  behaviors?: string[];
  enrichmentActivities?: string[];
  careNotes?: string;
  totalConversations?: number;
  lastInteraction?: string;
  images?: string[];
  caretakers?: string[];
}

const AnimalDetails: React.FC = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const animalIdFromQuery = queryParams.get('animalId');

  const [animals, setAnimals] = useState<EditableAnimal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedAnimal, setSelectedAnimal] = useState<EditableAnimal | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState<EditableAnimal | null>(null);
  const [saveLoading, setSaveLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');

  // Fetch animals from API
  const fetchAnimals = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('cmz_token');
      if (!token) {
        setError('Authentication required');
        return;
      }

      const response = await fetch('http://localhost:8080/animal_list', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch animals: ${response.status}`);
      }

      const data = await response.json();
      console.log('Fetched animals:', data);
      
      // Transform API data to frontend format
      const transformedAnimals: EditableAnimal[] = (data || []).map((animal: any) => ({
        animalId: animal.animalId || animal.animal_id,
        name: animal.name,
        species: animal.species,
        status: animal.status,
        created: animal.created,
        modified: animal.modified,
        // Handle personality - API returns it as a string directly
        personality: typeof animal.personality === 'string'
          ? { description: animal.personality }
          : (animal.personality || {}),
        configuration: animal.configuration || {},
        // Add default fields for display
        commonName: animal.species || 'Unknown',
        age: 5,
        gender: 'Unknown' as const,
        weight: 'Unknown',
        habitat: 'Zoo Exhibit',
        conservationStatus: 'Unknown',
        dateArrived: '2020-01-01',
        birthDate: '2018-01-01',
        origin: 'Unknown',
        dietaryNeeds: [],
        medicalHistory: [],
        behaviors: [],
        enrichmentActivities: [],
        careNotes: 'No notes available',
        totalConversations: 0,
        lastInteraction: 'Never',
        images: [],
        caretakers: []
      }));
      
      setAnimals(transformedAnimals);
    } catch (err) {
      console.error('Error fetching animals:', err);
      setError(err instanceof Error ? err.message : 'Failed to load animals');
    } finally {
      setLoading(false);
    }
  };

  // Save animal changes
  const saveAnimalChanges = async () => {
    if (!editedData) return;

    try {
      setSaveLoading(true);
      const token = localStorage.getItem('cmz_token');
      
      if (!token) {
        throw new Error('Authentication required');
      }

      // Prepare data for API (match the AnimalUpdate schema)
      const updateData = {
        name: editedData.name,
        species: editedData.species,
        status: editedData.status || 'active'
      };

      const response = await fetch(`http://localhost:8080/animal/${editedData.animalId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        throw new Error(`Failed to save changes: ${response.status}`);
      }

      const updatedAnimal = await response.json();
      console.log('Animal updated:', updatedAnimal);

      // Update local state
      setAnimals(prev => prev.map(animal => 
        animal.animalId === editedData.animalId 
          ? { ...animal, ...editedData }
          : animal
      ));
      
      setSelectedAnimal({ ...editedData });
      setIsEditing(false);
      setEditedData(null);
      
      alert('Animal details saved successfully!');
    } catch (err) {
      console.error('Error saving animal:', err);
      alert(`Failed to save changes: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setSaveLoading(false);
    }
  };

  // Cancel editing
  const cancelEditing = () => {
    setIsEditing(false);
    setEditedData(null);
  };

  // Start editing
  const startEditing = () => {
    if (selectedAnimal) {
      setEditedData({ ...selectedAnimal });
      setIsEditing(true);
    }
  };

  // Load animals on component mount
  useEffect(() => {
    fetchAnimals();
  }, []);

  // When animals are loaded or animalId changes, auto-select the animal
  useEffect(() => {
    if (animalIdFromQuery && animals.length > 0) {
      const targetAnimal = animals.find(a => a.animalId === animalIdFromQuery);
      if (targetAnimal) {
        setSelectedAnimal(targetAnimal);
      }
    }
  }, [animalIdFromQuery, animals]);

  const filteredAnimals = animals.filter(animal => {
    // If animalIdFromQuery is provided, only return that specific animal
    if (animalIdFromQuery) {
      return animal.animalId === animalIdFromQuery;
    }

    // Otherwise apply normal filters
    const matchesSearch = animal.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         animal.species?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         animal.commonName?.toLowerCase().includes(searchTerm.toLowerCase());

    const isActive = animal.configuration?.chatbotActive || animal.status === 'active';
    const matchesFilter = filterStatus === 'all' ||
                         (filterStatus === 'active' && isActive) ||
                         (filterStatus === 'inactive' && !isActive);

    return matchesSearch && matchesFilter;
  });

  const AnimalCard: React.FC<{ animal: EditableAnimal }> = ({ animal }) => (
    <div className="bg-white rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
         onClick={() => setSelectedAnimal(animal)}>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mr-4">
              <span className="text-2xl">🦁</span>
            </div>
            <div>
              <h3 className="font-semibold text-xl text-gray-900">{animal.name}</h3>
              <p className="text-sm text-gray-600 italic">{animal.species}</p>
              <p className="text-sm text-gray-500">{animal.commonName}</p>
            </div>
          </div>
          <div className="text-right">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              (animal.configuration?.chatbotActive || animal.status === 'active')
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-600'
            }`}>
              {(animal.configuration?.chatbotActive || animal.status === 'active') ? 'Active' : 'Inactive'}
            </span>
            <p className="text-xs text-gray-500 mt-1">ID: {animal.animalId}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
          <div>
            <p className="text-gray-600">Species</p>
            <p className="font-medium">{animal.species}</p>
          </div>
          <div>
            <p className="text-gray-600">Status</p>
            <p className="font-medium">{animal.status}</p>
          </div>
          <div>
            <p className="text-gray-600">Created</p>
            <p className="font-medium">{animal.created?.at ? new Date(animal.created.at).toLocaleDateString() : 'Unknown'}</p>
          </div>
          <div>
            <p className="text-gray-600">Modified</p>
            <p className="font-medium">{animal.modified?.at ? new Date(animal.modified.at).toLocaleDateString() : 'Never'}</p>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-1">Personality</p>
          <p className="text-sm font-medium flex items-center">
            <Heart className="w-4 h-4 mr-1" />
            {animal.personality?.description || 'No personality description'}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button className="flex-1 flex items-center justify-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
            <Eye className="w-4 h-4 mr-2" />
            View Details
          </button>
          <button className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <MessageCircle className="w-4 h-4" />
          </button>
          <button className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Edit className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const AnimalDetailsModal: React.FC = () => {
    if (!selectedAnimal) return null;

    const currentData = isEditing ? editedData : selectedAnimal;
    if (!currentData) return null;

    const handleFieldChange = (field: keyof EditableAnimal, value: any) => {
      if (isEditing && editedData) {
        setEditedData({ ...editedData, [field]: value });
      }
    };

    const handleNestedChange = (parent: string, field: string, value: any) => {
      if (isEditing && editedData) {
        setEditedData({
          ...editedData,
          [parent]: {
            ...((editedData as any)[parent] || {}),
            [field]: value
          }
        });
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-20 h-20 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                  <span className="text-3xl">🦁</span>
                </div>
                <div className="flex-1">
                  {isEditing ? (
                    <>
                      <input
                        type="text"
                        value={currentData.name || ''}
                        onChange={(e) => handleFieldChange('name', e.target.value)}
                        className="text-2xl font-bold text-gray-900 border rounded px-2 py-1 mb-2 w-full"
                        placeholder="Animal name"
                      />
                      <input
                        type="text"
                        value={currentData.species || ''}
                        onChange={(e) => handleFieldChange('species', e.target.value)}
                        className="text-gray-600 italic border rounded px-2 py-1 mb-1 w-full"
                        placeholder="Scientific species name"
                      />
                      <input
                        type="text"
                        value={currentData.commonName || ''}
                        onChange={(e) => handleFieldChange('commonName', e.target.value)}
                        className="text-gray-500 border rounded px-2 py-1 w-full"
                        placeholder="Common name"
                      />
                    </>
                  ) : (
                    <>
                      <h2 className="text-2xl font-bold text-gray-900">{currentData.name}</h2>
                      <p className="text-gray-600 italic">{currentData.species}</p>
                      <p className="text-gray-500">{currentData.commonName}</p>
                    </>
                  )}
                </div>
              </div>
              {isEditing ? (
                <div className="flex space-x-2">
                  <button 
                    onClick={cancelEditing}
                    className="text-gray-400 hover:text-gray-600 p-2 rounded"
                    title="Cancel editing"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <button 
                  onClick={() => setSelectedAnimal(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              )}
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Basic Information */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Activity className="w-5 h-5 mr-2" />
                    Basic Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Status</p>
                      {isEditing ? (
                        <select
                          value={currentData.status || 'active'}
                          onChange={(e) => handleFieldChange('status', e.target.value)}
                          className="font-medium border rounded px-2 py-1"
                        >
                          <option value="active">Active</option>
                          <option value="inactive">Inactive</option>
                          <option value="archived">Archived</option>
                        </select>
                      ) : (
                        <p className="font-medium">{currentData.status}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-gray-600">Animal ID</p>
                      <p className="font-medium text-xs">{currentData.animalId}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Age</p>
                      {isEditing ? (
                        <input
                          type="number"
                          value={currentData.age || 0}
                          onChange={(e) => handleFieldChange('age', parseInt(e.target.value) || 0)}
                          className="font-medium border rounded px-2 py-1 w-full"
                          placeholder="Age in years"
                        />
                      ) : (
                        <p className="font-medium">{currentData.age || 'Unknown'} years old</p>
                      )}
                    </div>
                    <div>
                      <p className="text-gray-600">Gender</p>
                      {isEditing ? (
                        <select
                          value={currentData.gender || 'Unknown'}
                          onChange={(e) => handleFieldChange('gender', e.target.value)}
                          className="font-medium border rounded px-2 py-1"
                        >
                          <option value="Male">Male</option>
                          <option value="Female">Female</option>
                          <option value="Unknown">Unknown</option>
                        </select>
                      ) : (
                        <p className="font-medium">{currentData.gender}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-gray-600">Weight</p>
                      {isEditing ? (
                        <input
                          type="text"
                          value={currentData.weight || ''}
                          onChange={(e) => handleFieldChange('weight', e.target.value)}
                          className="font-medium border rounded px-2 py-1 w-full"
                          placeholder="Weight (e.g., 95 lbs)"
                        />
                      ) : (
                        <p className="font-medium">{currentData.weight}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-gray-600">Conservation Status</p>
                      {isEditing ? (
                        <input
                          type="text"
                          value={currentData.conservationStatus || ''}
                          onChange={(e) => handleFieldChange('conservationStatus', e.target.value)}
                          className="font-medium border rounded px-2 py-1 w-full"
                          placeholder="e.g., Vulnerable, Endangered"
                        />
                      ) : (
                        <p className="font-medium text-orange-600">{currentData.conservationStatus}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                    <MapPin className="w-4 h-4 mr-2" />
                    Location & Origin
                  </h4>
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm text-gray-600">Current Habitat</p>
                      {isEditing ? (
                        <input
                          type="text"
                          value={currentData.habitat || ''}
                          onChange={(e) => handleFieldChange('habitat', e.target.value)}
                          className="text-sm border rounded px-2 py-1 w-full"
                          placeholder="Habitat location"
                        />
                      ) : (
                        <p className="text-sm text-gray-700 font-medium">{currentData.habitat}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Origin</p>
                      {isEditing ? (
                        <input
                          type="text"
                          value={currentData.origin || ''}
                          onChange={(e) => handleFieldChange('origin', e.target.value)}
                          className="text-sm border rounded px-2 py-1 w-full"
                          placeholder="Where the animal came from"
                        />
                      ) : (
                        <p className="text-sm text-gray-700 font-medium">{currentData.origin}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Personality</h4>
                  {isEditing ? (
                    <textarea
                      value={currentData.personality?.description || ''}
                      onChange={(e) => handleNestedChange('personality', 'description', e.target.value)}
                      className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg w-full border"
                      rows={3}
                      placeholder="Describe the animal's personality..."
                    />
                  ) : (
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                      {currentData.personality?.description || 'No personality description available'}
                    </p>
                  )}
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Care Notes</h4>
                  {isEditing ? (
                    <textarea
                      value={currentData.careNotes || ''}
                      onChange={(e) => handleFieldChange('careNotes', e.target.value)}
                      className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg w-full border"
                      rows={3}
                      placeholder="Special care instructions..."
                    />
                  ) : (
                    <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg">
                      {currentData.careNotes}
                    </p>
                  )}
                </div>
              </div>

              {/* Configuration & Advanced */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <MessageCircle className="w-5 h-5 mr-2" />
                    Chatbot Configuration
                  </h3>
                  <div className="bg-green-50 p-4 rounded-lg space-y-4">
                    <div>
                      <p className="text-gray-600 mb-2">Chatbot Status</p>
                      {isEditing ? (
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={currentData.configuration?.chatbotActive || false}
                            onChange={(e) => handleNestedChange('configuration', 'chatbotActive', e.target.checked)}
                            className="mr-2"
                          />
                          <span className={`font-medium ${currentData.configuration?.chatbotActive ? 'text-green-600' : 'text-red-600'}`}>
                            {currentData.configuration?.chatbotActive ? 'Active' : 'Inactive'}
                          </span>
                        </label>
                      ) : (
                        <p className={`font-medium ${currentData.configuration?.chatbotActive ? 'text-green-600' : 'text-red-600'}`}>
                          {currentData.configuration?.chatbotActive ? 'Active' : 'Inactive'}
                        </p>
                      )}
                    </div>
                    
                    <div>
                      <p className="text-gray-600 mb-2">Voice Style</p>
                      {isEditing ? (
                        <select
                          value={currentData.configuration?.voice || 'friendly'}
                          onChange={(e) => handleNestedChange('configuration', 'voice', e.target.value)}
                          className="font-medium border rounded px-2 py-1 w-full"
                        >
                          <option value="friendly">Friendly</option>
                          <option value="educational">Educational</option>
                          <option value="playful">Playful</option>
                          <option value="calm">Calm</option>
                        </select>
                      ) : (
                        <p className="font-medium">{currentData.configuration?.voice || 'Not set'}</p>
                      )}
                    </div>
                    
                    <div>
                      <p className="text-gray-600 mb-2">Response Style</p>
                      {isEditing ? (
                        <select
                          value={currentData.configuration?.responseStyle || 'conversational'}
                          onChange={(e) => handleNestedChange('configuration', 'responseStyle', e.target.value)}
                          className="font-medium border rounded px-2 py-1 w-full"
                        >
                          <option value="conversational">Conversational</option>
                          <option value="educational">Educational</option>
                          <option value="story-telling">Story-telling</option>
                          <option value="facts-focused">Facts-focused</option>
                        </select>
                      ) : (
                        <p className="font-medium">{currentData.configuration?.responseStyle || 'Not set'}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Personality Traits</h4>
                  {isEditing ? (
                    <textarea
                      value={(currentData.personality?.traits || []).join(', ')}
                      onChange={(e) => handleNestedChange('personality', 'traits', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
                      className="text-sm border rounded px-3 py-2 w-full"
                      rows={3}
                      placeholder="Enter personality traits separated by commas (e.g., friendly, curious, energetic)"
                    />
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {(currentData.personality?.traits || []).length > 0 ? (
                        (currentData.personality?.traits || []).map((trait, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            {trait}
                          </span>
                        ))
                      ) : (
                        <p className="text-sm text-gray-500">No personality traits defined</p>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Dates</h4>
                  <div className="grid grid-cols-1 gap-3 text-sm">
                    <div>
                      <p className="text-gray-600">Created</p>
                      <p className="font-medium">
                        {currentData.created?.at ? new Date(currentData.created.at).toLocaleString() : 'Unknown'}
                      </p>
                      {currentData.created?.by?.email && (
                        <p className="text-xs text-gray-500">by {currentData.created.by.email}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-gray-600">Modified</p>
                      <p className="font-medium">
                        {currentData.modified?.at ? new Date(currentData.modified.at).toLocaleString() : 'Never'}
                      </p>
                      {currentData.modified?.by?.email && (
                        <p className="text-xs text-gray-500">by {currentData.modified.by.email}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 border-t bg-gray-50 flex space-x-3">
            {isEditing ? (
              <>
                <button
                  onClick={cancelEditing}
                  disabled={saveLoading}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={saveAnimalChanges}
                  disabled={saveLoading}
                  className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {saveLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setSelectedAnimal(null)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                <button 
                  onClick={startEditing}
                  className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Animal Details
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading animals...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">⚠️</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading animals</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchAnimals}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  // If a specific animal is requested and found, show only that animal's details
  if (animalIdFromQuery && filteredAnimals.length === 1) {
    const animal = filteredAnimals[0];

    // Automatically set this animal as selected to show its details
    if (!selectedAnimal || selectedAnimal.animalId !== animal.animalId) {
      setSelectedAnimal(animal);
    }
  }

  return (
    <div>
      {/* Only show header and controls if not viewing single animal */}
      {!animalIdFromQuery && (
        <>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Animal Management</h1>
              <p className="text-gray-600">Manage animal profiles and chatbot configurations</p>
            </div>
            <button
              onClick={fetchAnimals}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Refresh
            </button>
          </div>

          {/* Search and Filter Controls */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search animals by name, species, or common name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as 'all' | 'active' | 'inactive')}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="all">All Animals</option>
                <option value="active">Chatbot Active</option>
                <option value="inactive">Chatbot Inactive</option>
              </select>
            </div>
          </div>
        </>
      )}

      {/* Animals Grid */}
      {!animalIdFromQuery && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredAnimals.map(animal => (
            <AnimalCard key={animal.id} animal={animal} />
          ))}
        </div>
      )}

      {filteredAnimals.length === 0 && !animalIdFromQuery && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No animals found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}

      {/* For single animal view, auto-open the modal */}
      {animalIdFromQuery && filteredAnimals.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Animal not found</h3>
          <p className="text-gray-600">The requested animal could not be found.</p>
        </div>
      )}

      <AnimalDetailsModal />
    </div>
  );
};

export default AnimalDetails;
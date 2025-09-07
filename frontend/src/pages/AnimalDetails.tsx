import React, { useState, useEffect } from 'react';
import { Search, Filter, Eye, Edit, MessageCircle, Calendar, MapPin, Heart, Activity } from 'lucide-react';

interface AnimalDetail {
  id: string;
  name: string;
  species: string;
  commonName: string;
  age: number;
  gender: 'Male' | 'Female' | 'Unknown';
  weight: string;
  habitat: string;
  conservationStatus: string;
  dateArrived: string;
  birthDate: string;
  origin: string;
  personality: string;
  dietaryNeeds: string[];
  medicalHistory: string[];
  behaviors: string[];
  enrichmentActivities: string[];
  careNotes: string;
  chatbotActive: boolean;
  totalConversations: number;
  lastInteraction: string;
  images: string[];
  caretakers: string[];
}

const AnimalDetails: React.FC = () => {
  const [animals] = useState<AnimalDetail[]>([
    {
      id: 'cheetah-1',
      name: 'Kesi',
      species: 'Acinonyx jubatus',
      commonName: 'Cheetah',
      age: 8,
      gender: 'Female',
      weight: '95 lbs',
      habitat: 'African Savanna Exhibit',
      conservationStatus: 'Vulnerable',
      dateArrived: '2019-03-15',
      birthDate: '2016-05-20',
      origin: 'Smithsonian National Zoo',
      personality: 'Energetic and curious, loves interactive enrichment activities. Known for her speed demonstrations and educational engagement.',
      dietaryNeeds: ['High-protein diet', 'Supplements for joint health', '4-5 lbs meat daily'],
      medicalHistory: ['Annual vaccinations current', 'Dental cleaning 2024-01', 'Minor injury treated 2023-08'],
      behaviors: ['Morning sprint sessions', 'Afternoon rest periods', 'Social with caretakers'],
      enrichmentActivities: ['Lure coursing', 'Puzzle feeders', 'Scent trails', 'Educational demonstrations'],
      careNotes: 'Responds well to positive reinforcement training. Prefers morning feeding times.',
      chatbotActive: true,
      totalConversations: 156,
      lastInteraction: '2 hours ago',
      images: ['/animal-photos/kesi-1.jpg', '/animal-photos/kesi-2.jpg'],
      caretakers: ['Sarah Johnson', 'Mike Rodriguez']
    },
    {
      id: 'tiger-1',
      name: 'Bayu',
      species: 'Panthera tigris altaica',
      commonName: 'Siberian Tiger',
      age: 12,
      gender: 'Male',
      weight: '420 lbs',
      habitat: 'Tiger Territory',
      conservationStatus: 'Endangered',
      dateArrived: '2015-07-10',
      birthDate: '2012-04-03',
      origin: 'Wildlife Conservation Society',
      personality: 'Wise and calm, enjoys quiet observation. Excellent ambassador for conservation education.',
      dietaryNeeds: ['15-20 lbs meat daily', 'Calcium supplements', 'Varied protein sources'],
      medicalHistory: ['Arthritis management plan', 'Regular geriatric checkups', 'Cataract surgery 2023'],
      behaviors: ['Territory patrol patterns', 'Swimming for exercise', 'Solitary nature'],
      enrichmentActivities: ['Pool time', 'Large bone treats', 'Scent marking logs', 'Platform perching'],
      careNotes: 'Senior animal requiring specialized care. Monitor joint mobility and vision.',
      chatbotActive: true,
      totalConversations: 203,
      lastInteraction: 'Yesterday',
      images: ['/animal-photos/bayu-1.jpg', '/animal-photos/bayu-2.jpg'],
      caretakers: ['David Chen', 'Lisa Martinez']
    },
    {
      id: 'elephant-1',
      name: 'Tembo',
      species: 'Loxodonta africana',
      commonName: 'African Elephant',
      age: 25,
      gender: 'Female',
      weight: '8,500 lbs',
      habitat: 'Elephant Meadows',
      conservationStatus: 'Endangered',
      dateArrived: '2010-09-22',
      birthDate: '1999-08-15',
      origin: 'Orphaned in Kenya, rescued by conservation program',
      personality: 'Gentle matriarch with strong memory and emotional intelligence. Forms deep bonds with caretakers.',
      dietaryNeeds: ['300-400 lbs vegetation daily', 'Hay, fruits, vegetables', 'Mineral supplements'],
      medicalHistory: ['Foot care routine', 'Trunk injury healed 2022', 'Reproductive health monitoring'],
      behaviors: ['Dust bathing rituals', 'Social interaction needs', 'Problem-solving abilities'],
      enrichmentActivities: ['Mud wallows', 'Tree branch manipulation', 'Musical enrichment', 'Painting activities'],
      careNotes: 'Requires consistent routine and familiar caretakers. Sensitive to environmental changes.',
      chatbotActive: false,
      totalConversations: 89,
      lastInteraction: '1 week ago',
      images: ['/animal-photos/tembo-1.jpg', '/animal-photos/tembo-2.jpg'],
      caretakers: ['Jennifer Adams', 'Robert Kim', 'Maria Gonzalez']
    }
  ]);

  const [selectedAnimal, setSelectedAnimal] = useState<AnimalDetail | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');

  const filteredAnimals = animals.filter(animal => {
    const matchesSearch = animal.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         animal.species.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         animal.commonName.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || 
                         (filterStatus === 'active' && animal.chatbotActive) ||
                         (filterStatus === 'inactive' && !animal.chatbotActive);
    
    return matchesSearch && matchesFilter;
  });

  const AnimalCard: React.FC<{ animal: AnimalDetail }> = ({ animal }) => (
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
              animal.chatbotActive 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-600'
            }`}>
              {animal.chatbotActive ? 'Chatbot Active' : 'Chatbot Inactive'}
            </span>
            <p className="text-xs text-gray-500 mt-1">Last chat: {animal.lastInteraction}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
          <div>
            <p className="text-gray-600">Age</p>
            <p className="font-medium">{animal.age} years</p>
          </div>
          <div>
            <p className="text-gray-600">Gender</p>
            <p className="font-medium">{animal.gender}</p>
          </div>
          <div>
            <p className="text-gray-600">Weight</p>
            <p className="font-medium">{animal.weight}</p>
          </div>
          <div>
            <p className="text-gray-600">Conversations</p>
            <p className="font-medium">{animal.totalConversations}</p>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-1">Habitat</p>
          <p className="text-sm font-medium flex items-center">
            <MapPin className="w-4 h-4 mr-1" />
            {animal.habitat}
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

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-20 h-20 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                  <span className="text-3xl">🦁</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedAnimal.name}</h2>
                  <p className="text-gray-600 italic">{selectedAnimal.species}</p>
                  <p className="text-gray-500">{selectedAnimal.commonName}</p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedAnimal(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
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
                      <p className="text-gray-600">Age</p>
                      <p className="font-medium">{selectedAnimal.age} years old</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Gender</p>
                      <p className="font-medium">{selectedAnimal.gender}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Weight</p>
                      <p className="font-medium">{selectedAnimal.weight}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Conservation Status</p>
                      <p className="font-medium text-orange-600">{selectedAnimal.conservationStatus}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Birth Date</p>
                      <p className="font-medium">{new Date(selectedAnimal.birthDate).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Arrived</p>
                      <p className="font-medium">{new Date(selectedAnimal.dateArrived).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                    <MapPin className="w-4 h-4 mr-2" />
                    Location & Origin
                  </h4>
                  <p className="text-sm text-gray-700 mb-2">
                    <strong>Current Habitat:</strong> {selectedAnimal.habitat}
                  </p>
                  <p className="text-sm text-gray-700">
                    <strong>Origin:</strong> {selectedAnimal.origin}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Personality</h4>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {selectedAnimal.personality}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Care Notes</h4>
                  <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg">
                    {selectedAnimal.careNotes}
                  </p>
                </div>
              </div>

              {/* Detailed Care Information */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Heart className="w-5 h-5 mr-2" />
                    Care & Enrichment
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Dietary Needs</h4>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {selectedAnimal.dietaryNeeds.map((need, index) => (
                          <li key={index} className="flex items-start">
                            <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                            {need}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Enrichment Activities</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedAnimal.enrichmentActivities.map((activity, index) => (
                          <span key={index} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                            {activity}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Behaviors</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedAnimal.behaviors.map((behavior, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            {behavior}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Primary Caretakers</h4>
                      <div className="space-y-1">
                        {selectedAnimal.caretakers.map((caretaker, index) => (
                          <p key={index} className="text-sm text-gray-700 flex items-center">
                            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                            {caretaker}
                          </p>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <MessageCircle className="w-5 h-5 mr-2" />
                    Chatbot Statistics
                  </h3>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Status</p>
                        <p className={`font-medium ${selectedAnimal.chatbotActive ? 'text-green-600' : 'text-red-600'}`}>
                          {selectedAnimal.chatbotActive ? 'Active' : 'Inactive'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Total Conversations</p>
                        <p className="font-medium">{selectedAnimal.totalConversations}</p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-gray-600">Last Interaction</p>
                        <p className="font-medium">{selectedAnimal.lastInteraction}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Medical History</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {selectedAnimal.medicalHistory.map((record, index) => (
                      <li key={index} className="flex items-start">
                        <Calendar className="w-3 h-3 mt-1 mr-2 flex-shrink-0" />
                        {record}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 border-t bg-gray-50 flex space-x-3">
            <button
              onClick={() => setSelectedAnimal(null)}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            <button className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
              <Edit className="w-4 h-4 mr-2" />
              Edit Animal Details
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Animal Details</h1>
          <p className="text-gray-600">Comprehensive animal profiles and care information</p>
        </div>
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

      {/* Animals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredAnimals.map(animal => (
          <AnimalCard key={animal.id} animal={animal} />
        ))}
      </div>

      {filteredAnimals.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No animals found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}

      <AnimalDetailsModal />
    </div>
  );
};

export default AnimalDetails;
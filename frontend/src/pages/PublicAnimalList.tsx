import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, Info, Heart, MapPin, Loader2 } from 'lucide-react';

interface Animal {
  animalId: string;
  name: string;
  species: string;
  habitat: string;
  personality: string;
  status: string;
  image?: string;
  age?: number;
  favoriteFood?: string;
}

const PublicAnimalList: React.FC = () => {
  const navigate = useNavigate();
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnimals = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8080/animal_list');
        if (!response.ok) {
          throw new Error('Failed to fetch animals');
        }
        const data = await response.json();

        // Filter for active animals only (API already returns animalId correctly)
        const activeAnimals = data.filter((animal: Animal) =>
          animal.status === 'active' || animal.status === 'Active'
        );
        setAnimals(activeAnimals);
      } catch (err) {
        setError('Unable to load animals. Please try again later.');
        console.error('Error fetching animals:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnimals();
  }, []);

  const handleViewDetails = (animalId: string) => {
    navigate(`/animals/details?animalId=${animalId}`);
  };

  const handleChat = (animalId: string) => {
    navigate(`/chat?animalId=${animalId}`);
  };

  const truncatePersonality = (text: string, maxLength: number = 100) => {
    if (!text) return 'A wonderful animal waiting to meet you!';
    return text.length > maxLength
      ? text.substring(0, maxLength) + '...'
      : text;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-50 to-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-800 mb-4">
              Meet Our Animal Ambassadors
            </h1>
            <p className="text-green-600 text-lg">
              Connect with our amazing animals through interactive chat!
            </p>
          </div>

          <div className="flex justify-center items-center py-20">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin text-green-600 mx-auto mb-4" />
              <p className="text-green-600">Loading our wonderful animals...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-50 to-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-20">
            <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-4xl">🦁</span>
            </div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
              Our animals are resting
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-green-800 mb-4">
            Meet Our Animal Ambassadors
          </h1>
          <p className="text-green-600 text-lg mb-2">
            Connect with our amazing animals through interactive chat!
          </p>
          <p className="text-green-500 text-sm">
            Click "Chat with Me!" to start a conversation with any of our animal friends
          </p>
        </div>

        {/* Animal Cards Grid */}
        {animals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {animals.map((animal) => (
              <div
                key={animal.animalId}
                className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group"
              >
                {/* Card Header with Image or Placeholder */}
                <div className="relative h-48 bg-gradient-to-br from-green-100 to-green-200 overflow-hidden">
                  {animal.image ? (
                    <img
                      src={animal.image}
                      alt={animal.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <span className="text-6xl opacity-50">
                        {animal.species?.toLowerCase().includes('lion') ? '🦁' :
                         animal.species?.toLowerCase().includes('panda') ? '🐼' :
                         animal.species?.toLowerCase().includes('elephant') ? '🐘' :
                         animal.species?.toLowerCase().includes('tiger') ? '🐅' :
                         animal.species?.toLowerCase().includes('giraffe') ? '🦒' :
                         animal.species?.toLowerCase().includes('monkey') ? '🐵' :
                         animal.species?.toLowerCase().includes('bird') ? '🦜' :
                         animal.species?.toLowerCase().includes('bear') ? '🐻' : '🦊'}
                      </span>
                    </div>
                  )}
                  <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded-full text-xs font-semibold">
                    Active
                  </div>
                  <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded-full p-2">
                    <Heart className="w-4 h-4 text-red-500" />
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-5">
                  {/* Animal Name & Species */}
                  <div className="mb-3">
                    <h3 className="text-xl font-bold text-gray-800 mb-1">
                      {animal.name}
                    </h3>
                    <p className="text-green-600 font-medium">
                      {animal.species}
                    </p>
                  </div>

                  {/* Habitat */}
                  {animal.habitat && (
                    <div className="flex items-center gap-2 text-gray-600 mb-3">
                      <MapPin className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{animal.habitat}</span>
                    </div>
                  )}

                  {/* Personality Preview */}
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {truncatePersonality(animal.personality)}
                    </p>
                  </div>

                  {/* Additional Info */}
                  {(animal.age || animal.favoriteFood) && (
                    <div className="mb-4 text-xs text-gray-500 space-y-1">
                      {animal.age && <div>Age: {animal.age} years old</div>}
                      {animal.favoriteFood && <div>Loves: {animal.favoriteFood}</div>}
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleViewDetails(animal.animalId)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                    >
                      <Info className="w-4 h-4" />
                      View Details
                    </button>
                    <button
                      onClick={() => handleChat(animal.animalId)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      <MessageCircle className="w-4 h-4" />
                      Chat with Me!
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-20">
            <div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-6xl">🦒</span>
            </div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-3">
              No Animals Available
            </h2>
            <p className="text-gray-600 max-w-md mx-auto">
              Our animal ambassadors are currently offline. Please check back later to meet our amazing zoo family!
            </p>
          </div>
        )}

        {/* Footer Section */}
        <div className="text-center mt-12 p-8 bg-green-100 rounded-xl">
          <h3 className="text-2xl font-bold text-green-800 mb-3">
            🌿 Visit Cougar Mountain Zoo Today! 🌿
          </h3>
          <p className="text-green-700 mb-4 max-w-2xl mx-auto">
            Experience the wonder of wildlife in person! Our zoo is home to over 200 amazing animals
            from around the world. Come meet them and learn about conservation efforts.
          </p>
          <div className="text-green-600 font-medium">
            Open Daily: 9:00 AM - 6:00 PM
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicAnimalList;
import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Users, Calendar, Mail, Phone, MapPin, Eye, Lock } from 'lucide-react';
import AddFamilyModal from '../components/AddFamilyModal';
import {
  Family,
  User,
  listFamilies,
  deleteFamily,
  canEditFamilies,
  getCurrentUser,
  formatUserDisplay,
  getFamilyActions
} from '../services/familyApi';

const FamilyManagementBidirectional: React.FC = () => {
  const [families, setFamilies] = useState<Family[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedFamily, setSelectedFamily] = useState<Family | null>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Load current user and check permissions
  useEffect(() => {
    loadUserAndPermissions();
  }, []);

  // Load families
  useEffect(() => {
    loadFamilies();
  }, []);

  const loadUserAndPermissions = async () => {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      setIsAdmin(user.role === 'admin');
    } catch (err) {
      console.error('Failed to load user:', err);
      setError('Failed to load user information');
    }
  };

  const loadFamilies = async () => {
    setLoading(true);
    try {
      const data = await listFamilies();
      setFamilies(data);
      setError(null);
    } catch (err) {
      setError('Failed to load families');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFamily = async (familyId: string) => {
    if (!isAdmin) {
      alert('Only administrators can delete families');
      return;
    }

    if (window.confirm('Are you sure you want to delete this family?')) {
      try {
        await deleteFamily(familyId);
        await loadFamilies();
      } catch (err) {
        alert('Failed to delete family');
        console.error(err);
      }
    }
  };

  const handleViewFamily = (family: Family) => {
    setSelectedFamily(family);
    setIsViewModalOpen(true);
    setIsEditMode(false);
  };

  const handleEditFamily = (family: Family) => {
    if (!isAdmin) {
      alert('Only administrators can edit families');
      return;
    }
    setSelectedFamily(family);
    setIsViewModalOpen(true);
    setIsEditMode(true);
  };

  // Filter families based on search
  const filteredFamilies = families.filter(family =>
    family.familyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    family.parents?.some(p =>
      p.displayName.toLowerCase().includes(searchTerm.toLowerCase())
    ) ||
    family.students?.some(s =>
      s.displayName.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  if (loading) return <div className="flex justify-center p-8">Loading families...</div>;
  if (error) return <div className="text-red-500 p-8">{error}</div>;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Family Management</h1>
        <p className="text-gray-600 mt-2">
          {isAdmin
            ? 'Manage family groups, student associations, and program enrollments'
            : 'View your family information and program enrollments'}
        </p>
      </div>

      {/* User Info Bar */}
      {currentUser && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-semibold">Logged in as:</span>{' '}
              {formatUserDisplay(currentUser)}
            </div>
            <div>
              <span className="font-semibold">Role:</span>{' '}
              <span className={`px-2 py-1 rounded text-sm ${
                isAdmin
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-green-100 text-green-800'
              }`}>
                {currentUser.role}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Actions Bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-4">
          {isAdmin && (
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-green-700"
            >
              <Plus className="h-5 w-5 mr-2" />
              Add New Family
            </button>
          )}

          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search families..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>

        <div className="text-sm text-gray-600">
          Showing {filteredFamilies.length} of {families.length} families
        </div>
      </div>

      {/* Families Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFamilies.map((family) => (
          <div key={family.familyId} className="bg-white rounded-lg shadow-md p-6">
            {/* Family Header */}
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">
                  {family.familyName}
                </h3>
                <span className={`inline-block px-2 py-1 text-xs rounded mt-1 ${
                  family.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : family.status === 'inactive'
                    ? 'bg-gray-100 text-gray-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {family.status}
                </span>
              </div>
              <div className="flex space-x-2">
                {family.canView && (
                  <button
                    onClick={() => handleViewFamily(family)}
                    className="text-blue-600 hover:text-blue-800"
                    title="View Details"
                  >
                    <Eye className="h-5 w-5" />
                  </button>
                )}
                {family.canEdit ? (
                  <>
                    <button
                      onClick={() => handleEditFamily(family)}
                      className="text-green-600 hover:text-green-800"
                      title="Edit Family"
                    >
                      <Edit className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteFamily(family.familyId)}
                      className="text-red-600 hover:text-red-800"
                      title="Delete Family"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </>
                ) : (
                  <div className="text-gray-400" title="Admin access required">
                    <Lock className="h-5 w-5" />
                  </div>
                )}
              </div>
            </div>

            {/* Family Members */}
            <div className="space-y-3">
              {/* Parents */}
              <div>
                <div className="flex items-center text-gray-600 mb-1">
                  <Users className="h-4 w-4 mr-1" />
                  <span className="text-sm font-medium">Parents</span>
                </div>
                {family.parents && family.parents.length > 0 ? (
                  <div className="space-y-1">
                    {family.parents.slice(0, 2).map((parent) => (
                      <div key={parent.userId} className="text-sm text-gray-700">
                        {parent.displayName}
                        {parent.isPrimaryContact && (
                          <span className="ml-1 text-xs text-blue-600">(Primary)</span>
                        )}
                      </div>
                    ))}
                    {family.parents.length > 2 && (
                      <div className="text-xs text-gray-500">
                        +{family.parents.length - 2} more
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">No parents listed</div>
                )}
              </div>

              {/* Students */}
              <div>
                <div className="flex items-center text-gray-600 mb-1">
                  <Users className="h-4 w-4 mr-1" />
                  <span className="text-sm font-medium">Students</span>
                </div>
                {family.students && family.students.length > 0 ? (
                  <div className="space-y-1">
                    {family.students.slice(0, 2).map((student) => (
                      <div key={student.userId} className="text-sm text-gray-700">
                        {student.displayName}
                        {student.grade && (
                          <span className="ml-1 text-xs text-gray-500">
                            ({student.grade})
                          </span>
                        )}
                      </div>
                    ))}
                    {family.students.length > 2 && (
                      <div className="text-xs text-gray-500">
                        +{family.students.length - 2} more
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">No students listed</div>
                )}
              </div>

              {/* Contact Info */}
              {family.parents?.[0]?.email && (
                <div className="flex items-center text-sm text-gray-600">
                  <Mail className="h-4 w-4 mr-2" />
                  {family.parents[0].email}
                </div>
              )}

              {family.parents?.[0]?.phone && (
                <div className="flex items-center text-sm text-gray-600">
                  <Phone className="h-4 w-4 mr-2" />
                  {family.parents[0].phone}
                </div>
              )}

              {family.address && (
                <div className="flex items-start text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2 mt-0.5" />
                  <div>
                    {family.address.city && family.address.state && (
                      <span>{family.address.city}, {family.address.state}</span>
                    )}
                  </div>
                </div>
              )}

              {/* Member Since */}
              {family.memberSince && (
                <div className="flex items-center text-sm text-gray-600">
                  <Calendar className="h-4 w-4 mr-2" />
                  Member since {new Date(family.memberSince).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* No families message */}
      {filteredFamilies.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            {searchTerm
              ? 'No families found matching your search'
              : isAdmin
              ? 'No families have been added yet'
              : 'You are not associated with any families'}
          </p>
          {isAdmin && !searchTerm && (
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="mt-4 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              Add First Family
            </button>
          )}
        </div>
      )}

      {/* Add Family Modal */}
      {isAddModalOpen && (
        <AddFamilyModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onSuccess={loadFamilies}
        />
      )}

      {/* View/Edit Family Modal */}
      {isViewModalOpen && selectedFamily && (
        <FamilyDetailsModal
          family={selectedFamily}
          isOpen={isViewModalOpen}
          onClose={() => {
            setIsViewModalOpen(false);
            setSelectedFamily(null);
            setIsEditMode(false);
          }}
          isEditMode={isEditMode}
          canEdit={selectedFamily.canEdit || false}
          onSuccess={loadFamilies}
        />
      )}
    </div>
  );
};

// Family Details Modal Component
const FamilyDetailsModal: React.FC<{
  family: Family;
  isOpen: boolean;
  onClose: () => void;
  isEditMode: boolean;
  canEdit: boolean;
  onSuccess: () => void;
}> = ({ family, isOpen, onClose, isEditMode, canEdit }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {isEditMode ? 'Edit Family' : 'Family Details'}
        </h2>

        <div className="space-y-4">
          <div>
            <h3 className="font-semibold">Family Name:</h3>
            <p>{family.familyName}</p>
          </div>

          <div>
            <h3 className="font-semibold">Status:</h3>
            <span className={`px-2 py-1 rounded text-sm ${
              family.status === 'active'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {family.status}
            </span>
          </div>

          <div>
            <h3 className="font-semibold">Parents:</h3>
            {family.parents?.map(parent => (
              <div key={parent.userId} className="ml-4">
                {parent.displayName} - {parent.email}
              </div>
            ))}
          </div>

          <div>
            <h3 className="font-semibold">Students:</h3>
            {family.students?.map(student => (
              <div key={student.userId} className="ml-4">
                {student.displayName} {student.grade && `(${student.grade})`}
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 flex justify-end space-x-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default FamilyManagementBidirectional;
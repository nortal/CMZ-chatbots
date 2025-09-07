import React, { useState } from 'react';
import { Plus, Search, Edit, Trash2, Users, Calendar, Mail, Phone, MapPin, FileText, Eye } from 'lucide-react';

interface Student {
  id: string;
  firstName: string;
  lastName: string;
  age: number;
  grade: string;
  interests: string[];
  allergies?: string[];
}

interface Parent {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role: 'primary' | 'secondary';
  emergencyContact: boolean;
}

interface Family {
  id: string;
  familyName: string;
  students: Student[];
  parents: Parent[];
  registrationDate: string;
  status: 'active' | 'inactive' | 'pending';
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
  };
  emergencyContact: {
    name: string;
    phone: string;
    relationship: string;
  };
  medicalNotes?: string;
  educationalGoals: string[];
  preferredPrograms: string[];
  visitHistory: {
    date: string;
    program: string;
    attendance: number;
  }[];
  totalVisits: number;
  lastVisit: string;
}

const FamilyManagement: React.FC = () => {
  const [families] = useState<Family[]>([
    {
      id: 'fam-001',
      familyName: 'Johnson Family',
      students: [
        {
          id: 'std-001',
          firstName: 'Emma',
          lastName: 'Johnson',
          age: 8,
          grade: '3rd Grade',
          interests: ['Animals', 'Science', 'Drawing'],
          allergies: ['Peanuts']
        },
        {
          id: 'std-002',
          firstName: 'Liam',
          lastName: 'Johnson',
          age: 10,
          grade: '5th Grade',
          interests: ['Conservation', 'Photography', 'Reading']
        }
      ],
      parents: [
        {
          id: 'par-001',
          firstName: 'Sarah',
          lastName: 'Johnson',
          email: 'sarah.johnson@email.com',
          phone: '(555) 123-4567',
          role: 'primary',
          emergencyContact: true
        },
        {
          id: 'par-002',
          firstName: 'Michael',
          lastName: 'Johnson',
          email: 'mike.johnson@email.com',
          phone: '(555) 987-6543',
          role: 'secondary',
          emergencyContact: true
        }
      ],
      registrationDate: '2024-01-15',
      status: 'active',
      address: {
        street: '123 Oak Street',
        city: 'Seattle',
        state: 'WA',
        zipCode: '98101'
      },
      emergencyContact: {
        name: 'Jennifer Martinez',
        phone: '(555) 555-1234',
        relationship: 'Aunt'
      },
      medicalNotes: 'Emma has severe peanut allergy - carry EpiPen at all times.',
      educationalGoals: ['Wildlife Conservation Awareness', 'Scientific Observation Skills'],
      preferredPrograms: ['Junior Zookeeper', 'Conservation Club', 'Art & Animals'],
      visitHistory: [
        { date: '2024-01-20', program: 'Junior Zookeeper', attendance: 2 },
        { date: '2024-02-10', program: 'Conservation Club', attendance: 2 },
        { date: '2024-03-05', program: 'Art & Animals', attendance: 1 }
      ],
      totalVisits: 5,
      lastVisit: '2024-03-05'
    },
    {
      id: 'fam-002',
      familyName: 'Rodriguez Family',
      students: [
        {
          id: 'std-003',
          firstName: 'Sofia',
          lastName: 'Rodriguez',
          age: 6,
          grade: '1st Grade',
          interests: ['Elephants', 'Music', 'Dancing'],
          allergies: ['Dairy']
        }
      ],
      parents: [
        {
          id: 'par-003',
          firstName: 'Maria',
          lastName: 'Rodriguez',
          email: 'maria.rodriguez@email.com',
          phone: '(555) 234-5678',
          role: 'primary',
          emergencyContact: true
        }
      ],
      registrationDate: '2024-02-20',
      status: 'active',
      address: {
        street: '456 Pine Avenue',
        city: 'Bellevue',
        state: 'WA',
        zipCode: '98004'
      },
      emergencyContact: {
        name: 'Carlos Rodriguez',
        phone: '(555) 876-5432',
        relationship: 'Uncle'
      },
      medicalNotes: 'Sofia is lactose intolerant.',
      educationalGoals: ['Animal Behavior Understanding', 'Creative Expression'],
      preferredPrograms: ['Tiny Tots', 'Animal Art', 'Music with Animals'],
      visitHistory: [
        { date: '2024-02-25', program: 'Tiny Tots', attendance: 1 },
        { date: '2024-03-10', program: 'Animal Art', attendance: 1 }
      ],
      totalVisits: 2,
      lastVisit: '2024-03-10'
    },
    {
      id: 'fam-003',
      familyName: 'Chen Family',
      students: [
        {
          id: 'std-004',
          firstName: 'David',
          lastName: 'Chen',
          age: 12,
          grade: '7th Grade',
          interests: ['Marine Biology', 'Technology', 'Environmental Science']
        },
        {
          id: 'std-005',
          firstName: 'Ashley',
          lastName: 'Chen',
          age: 9,
          grade: '4th Grade',
          interests: ['Birds', 'Math', 'Puzzles']
        }
      ],
      parents: [
        {
          id: 'par-004',
          firstName: 'Kevin',
          lastName: 'Chen',
          email: 'kevin.chen@email.com',
          phone: '(555) 345-6789',
          role: 'primary',
          emergencyContact: true
        }
      ],
      registrationDate: '2023-11-10',
      status: 'active',
      address: {
        street: '789 Maple Drive',
        city: 'Redmond',
        state: 'WA',
        zipCode: '98052'
      },
      emergencyContact: {
        name: 'Linda Chen',
        phone: '(555) 678-9012',
        relationship: 'Grandmother'
      },
      educationalGoals: ['STEM Education', 'Environmental Stewardship'],
      preferredPrograms: ['Science Club', 'Teen Naturalist', 'Eco Warriors'],
      visitHistory: [
        { date: '2023-11-15', program: 'Science Club', attendance: 2 },
        { date: '2023-12-20', program: 'Teen Naturalist', attendance: 1 },
        { date: '2024-01-10', program: 'Eco Warriors', attendance: 2 },
        { date: '2024-02-28', program: 'Science Club', attendance: 2 }
      ],
      totalVisits: 7,
      lastVisit: '2024-02-28'
    }
  ]);

  const [selectedFamily, setSelectedFamily] = useState<Family | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'pending'>('all');
  const [showAddFamily, setShowAddFamily] = useState(false);

  const filteredFamilies = families.filter(family => {
    const matchesSearch = family.familyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         family.students.some(student => 
                           `${student.firstName} ${student.lastName}`.toLowerCase().includes(searchTerm.toLowerCase())
                         ) ||
                         family.parents.some(parent =>
                           `${parent.firstName} ${parent.lastName}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           parent.email.toLowerCase().includes(searchTerm.toLowerCase())
                         );
    
    const matchesStatus = statusFilter === 'all' || family.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const FamilyCard: React.FC<{ family: Family }> = ({ family }) => (
    <div className="bg-white rounded-lg border hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-900">{family.familyName}</h3>
              <p className="text-sm text-gray-600">
                {family.students.length} student{family.students.length !== 1 ? 's' : ''} • {family.parents.length} parent{family.parents.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <div className="text-right">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              family.status === 'active' ? 'bg-green-100 text-green-800' :
              family.status === 'inactive' ? 'bg-gray-100 text-gray-600' :
              'bg-yellow-100 text-yellow-800'
            }`}>
              {family.status.charAt(0).toUpperCase() + family.status.slice(1)}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Students</p>
            <div className="space-y-1">
              {family.students.map(student => (
                <p key={student.id} className="text-sm font-medium">
                  {student.firstName} {student.lastName} ({student.age})
                </p>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600">Primary Contact</p>
            <p className="text-sm font-medium">
              {family.parents.find(p => p.role === 'primary')?.firstName} {family.parents.find(p => p.role === 'primary')?.lastName}
            </p>
            <p className="text-xs text-gray-500">
              {family.parents.find(p => p.role === 'primary')?.email}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
          <div>
            <p className="text-gray-600">Total Visits</p>
            <p className="font-medium">{family.totalVisits}</p>
          </div>
          <div>
            <p className="text-gray-600">Last Visit</p>
            <p className="font-medium">{new Date(family.lastVisit).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-gray-600">Member Since</p>
            <p className="font-medium">{new Date(family.registrationDate).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-1">Preferred Programs</p>
          <div className="flex flex-wrap gap-1">
            {family.preferredPrograms.slice(0, 3).map((program, index) => (
              <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                {program}
              </span>
            ))}
            {family.preferredPrograms.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                +{family.preferredPrograms.length - 3} more
              </span>
            )}
          </div>
        </div>

        <div className="flex space-x-2">
          <button 
            onClick={() => setSelectedFamily(family)}
            className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Eye className="w-4 h-4 mr-2" />
            View Details
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Edit className="w-4 h-4" />
          </button>
          <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const FamilyDetailsModal: React.FC = () => {
    if (!selectedFamily) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                  <Users className="w-8 h-8 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedFamily.familyName}</h2>
                  <p className="text-gray-600">
                    {selectedFamily.students.length} students • Registered {new Date(selectedFamily.registrationDate).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedFamily(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Students Information */}
              <div className="lg:col-span-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Students
                </h3>
                <div className="space-y-4">
                  {selectedFamily.students.map(student => (
                    <div key={student.id} className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900">{student.firstName} {student.lastName}</h4>
                      <div className="text-sm text-gray-600 space-y-1 mt-2">
                        <p><strong>Age:</strong> {student.age} years old</p>
                        <p><strong>Grade:</strong> {student.grade}</p>
                        <div>
                          <strong>Interests:</strong>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {student.interests.map((interest, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {interest}
                              </span>
                            ))}
                          </div>
                        </div>
                        {student.allergies && student.allergies.length > 0 && (
                          <div>
                            <strong className="text-red-600">Allergies:</strong>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {student.allergies.map((allergy, index) => (
                                <span key={index} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                                  {allergy}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {selectedFamily.medicalNotes && (
                  <div className="mt-6">
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-red-500" />
                      Medical Notes
                    </h4>
                    <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
                      <p className="text-sm text-red-800">{selectedFamily.medicalNotes}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Parents & Contact Information */}
              <div className="lg:col-span-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Mail className="w-5 h-5 mr-2" />
                  Parents & Contacts
                </h3>
                <div className="space-y-4">
                  {selectedFamily.parents.map(parent => (
                    <div key={parent.id} className="bg-gray-50 p-4 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{parent.firstName} {parent.lastName}</h4>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          parent.role === 'primary' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {parent.role}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        <p className="flex items-center">
                          <Mail className="w-3 h-3 mr-2" />
                          {parent.email}
                        </p>
                        <p className="flex items-center">
                          <Phone className="w-3 h-3 mr-2" />
                          {parent.phone}
                        </p>
                        {parent.emergencyContact && (
                          <p className="text-green-600 text-xs">✓ Emergency Contact</p>
                        )}
                      </div>
                    </div>
                  ))}

                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Emergency Contact</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p><strong>Name:</strong> {selectedFamily.emergencyContact.name}</p>
                      <p><strong>Phone:</strong> {selectedFamily.emergencyContact.phone}</p>
                      <p><strong>Relationship:</strong> {selectedFamily.emergencyContact.relationship}</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                    <MapPin className="w-4 h-4 mr-2" />
                    Address
                  </h4>
                  <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700">
                    <p>{selectedFamily.address.street}</p>
                    <p>{selectedFamily.address.city}, {selectedFamily.address.state} {selectedFamily.address.zipCode}</p>
                  </div>
                </div>
              </div>

              {/* Programs & Activities */}
              <div className="lg:col-span-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Programs & Activities
                </h3>
                
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Educational Goals</h4>
                    <div className="space-y-1">
                      {selectedFamily.educationalGoals.map((goal, index) => (
                        <p key={index} className="text-sm text-gray-700 flex items-start">
                          <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {goal}
                        </p>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Preferred Programs</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedFamily.preferredPrograms.map((program, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {program}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Visit History</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {selectedFamily.visitHistory.map((visit, index) => (
                        <div key={index} className="bg-green-50 p-3 rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-sm font-medium text-gray-900">{visit.program}</p>
                              <p className="text-xs text-gray-600">{new Date(visit.date).toLocaleDateString()}</p>
                            </div>
                            <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">
                              {visit.attendance} attended
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Total Visits</p>
                        <p className="text-2xl font-bold text-blue-600">{selectedFamily.totalVisits}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Last Visit</p>
                        <p className="font-medium text-gray-900">{new Date(selectedFamily.lastVisit).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 border-t bg-gray-50 flex space-x-3">
            <button
              onClick={() => setSelectedFamily(null)}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            <button className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Edit className="w-4 h-4 mr-2" />
              Edit Family Details
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
          <h1 className="text-2xl font-bold text-gray-900">Family Management</h1>
          <p className="text-gray-600">Manage family registrations and educational program participation</p>
        </div>
        <button 
          onClick={() => setShowAddFamily(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add New Family
        </button>
      </div>

      {/* Search and Filter Controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search families by name, parent, or student..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive' | 'pending')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Families</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
          </select>
          <div className="text-sm text-gray-600">
            {filteredFamilies.length} of {families.length} families
          </div>
        </div>
      </div>

      {/* Families Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredFamilies.map(family => (
          <FamilyCard key={family.id} family={family} />
        ))}
      </div>

      {filteredFamilies.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No families found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}

      <FamilyDetailsModal />
    </div>
  );
};

export default FamilyManagement;
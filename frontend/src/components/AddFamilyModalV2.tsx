import React, { useState, useEffect, useCallback } from 'react';
import { X, Search, UserPlus, Trash2, Check, AlertCircle } from 'lucide-react';
import { debounce } from '../utils/debounce';

interface User {
  userId: string;
  email: string;
  displayName: string;
  role: 'parent' | 'student' | 'admin';
  phone?: string;
  age?: string;
  grade?: string;
}

interface AddFamilyModalV2Props {
  isOpen: boolean;
  onClose: () => void;
  onSave: (familyData: any) => void;
}

const AddFamilyModalV2: React.FC<AddFamilyModalV2Props> = ({ isOpen, onClose, onSave }) => {
  const [familyName, setFamilyName] = useState('');
  const [selectedParents, setSelectedParents] = useState<User[]>([]);
  const [selectedStudents, setSelectedStudents] = useState<User[]>([]);
  const [address, setAddress] = useState({ street: '', city: '', state: '', zip: '' });
  const [preferredPrograms, setPreferredPrograms] = useState<string[]>([]);

  // Search states
  const [parentSearchTerm, setParentSearchTerm] = useState('');
  const [studentSearchTerm, setStudentSearchTerm] = useState('');
  const [parentSearchResults, setParentSearchResults] = useState<User[]>([]);
  const [studentSearchResults, setStudentSearchResults] = useState<User[]>([]);
  const [isSearchingParents, setIsSearchingParents] = useState(false);
  const [isSearchingStudents, setIsSearchingStudents] = useState(false);

  const availablePrograms = [
    'Junior Zookeeper', 'Conservation Club', 'Art & Animals',
    'Science Club', 'Teen Naturalist', 'Eco Warriors',
    'Tiny Tots', 'Animal Art', 'Music with Animals'
  ];

  // Search users using the actual API
  const searchUsers = async (term: string, role: 'parent' | 'student'): Promise<User[]> => {
    try {
      // Build query params
      const params = new URLSearchParams({
        query: term,
        role: role,
        page_size: '15' // Limit to 15 results as requested
      });

      // Call the API - adjust the URL based on your environment
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8080';
      const response = await fetch(`${apiUrl}/user?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Add auth headers if needed
        }
      });

      if (!response.ok) {
        console.error('User search failed:', response.status);
        return [];
      }

      const data = await response.json();

      // The API returns a PagedUsers object with items array
      const users = data.items || [];

      // Map the backend user format to our component's User interface
      return users.map((user: any) => ({
        userId: user.userId || user.user_id,
        email: user.email,
        displayName: user.displayName || user.display_name,
        role: user.role,
        phone: user.phoneNumber || user.phone_number,
        age: user.age?.toString(),
        grade: user.grade
      }));
    } catch (error) {
      console.error('Error searching users:', error);
      return [];
    }
  };

  // Debounced search for parents
  const debouncedParentSearch = useCallback(
    debounce(async (term: string) => {
      if (term.length < 2) {
        setParentSearchResults([]);
        return;
      }
      setIsSearchingParents(true);
      try {
        const results = await searchUsers(term, 'parent');
        // Filter out already selected parents
        const filtered = results.filter(
          user => !selectedParents.some(p => p.userId === user.userId)
        );
        setParentSearchResults(filtered);
      } catch (error) {
        console.error('Error searching parents:', error);
        setParentSearchResults([]);
      } finally {
        setIsSearchingParents(false);
      }
    }, 300),
    [selectedParents]
  );

  // Debounced search for students
  const debouncedStudentSearch = useCallback(
    debounce(async (term: string) => {
      if (term.length < 2) {
        setStudentSearchResults([]);
        return;
      }
      setIsSearchingStudents(true);
      try {
        const results = await searchUsers(term, 'student');
        // Filter out already selected students
        const filtered = results.filter(
          user => !selectedStudents.some(s => s.userId === user.userId)
        );
        setStudentSearchResults(filtered);
      } catch (error) {
        console.error('Error searching students:', error);
        setStudentSearchResults([]);
      } finally {
        setIsSearchingStudents(false);
      }
    }, 300),
    [selectedStudents]
  );

  useEffect(() => {
    debouncedParentSearch(parentSearchTerm);
  }, [parentSearchTerm, debouncedParentSearch]);

  useEffect(() => {
    debouncedStudentSearch(studentSearchTerm);
  }, [studentSearchTerm, debouncedStudentSearch]);

  const handleSelectParent = (parent: User) => {
    setSelectedParents([...selectedParents, parent]);
    setParentSearchTerm('');
    setParentSearchResults([]);
  };

  const handleRemoveParent = (userId: string) => {
    setSelectedParents(selectedParents.filter(p => p.userId !== userId));
  };

  const handleSelectStudent = (student: User) => {
    setSelectedStudents([...selectedStudents, student]);
    setStudentSearchTerm('');
    setStudentSearchResults([]);
  };

  const handleRemoveStudent = (userId: string) => {
    setSelectedStudents(selectedStudents.filter(s => s.userId !== userId));
  };

  const handleProgramToggle = (program: string) => {
    setPreferredPrograms(prev =>
      prev.includes(program)
        ? prev.filter(p => p !== program)
        : [...prev, program]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!familyName.trim()) {
      alert('Please enter a family name');
      return;
    }

    if (selectedParents.length === 0) {
      alert('Please add at least one parent to the family');
      return;
    }

    if (selectedStudents.length === 0) {
      alert('Please add at least one student to the family');
      return;
    }

    const familyData = {
      familyName,
      parentIds: selectedParents.map(p => p.userId),
      studentIds: selectedStudents.map(s => s.userId),
      address,
      preferredPrograms,
      status: 'active',
      memberSince: new Date().toISOString()
    };

    onSave(familyData);
    handleClose();
  };

  const handleClose = () => {
    // Reset form
    setFamilyName('');
    setSelectedParents([]);
    setSelectedStudents([]);
    setAddress({ street: '', city: '', state: '', zip: '' });
    setPreferredPrograms([]);
    setParentSearchTerm('');
    setStudentSearchTerm('');
    setParentSearchResults([]);
    setStudentSearchResults([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Create New Family</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Family Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Family Name *
            </label>
            <input
              type="text"
              value={familyName}
              onChange={(e) => setFamilyName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
              placeholder="e.g., Johnson Family"
              required
            />
          </div>

          {/* Parents Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Parents / Guardians</h3>

            {/* Parent Search */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search and Add Parents
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={parentSearchTerm}
                  onChange={(e) => setParentSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Search by name or email..."
                />
                {isSearchingParents && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <div className="animate-spin h-4 w-4 border-2 border-green-500 border-t-transparent rounded-full"></div>
                  </div>
                )}
              </div>

              {/* Parent Search Results */}
              {parentSearchResults.length > 0 && (
                <div className="mt-2 border border-gray-200 rounded-md max-h-48 overflow-y-auto">
                  {parentSearchResults.map(parent => (
                    <button
                      key={parent.userId}
                      type="button"
                      onClick={() => handleSelectParent(parent)}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-0"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium text-gray-900">{parent.displayName}</div>
                          <div className="text-sm text-gray-500">{parent.email}</div>
                          {parent.phone && <div className="text-sm text-gray-500">{parent.phone}</div>}
                        </div>
                        <UserPlus className="h-4 w-4 text-green-600" />
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {parentSearchTerm.length >= 2 && !isSearchingParents && parentSearchResults.length === 0 && (
                <div className="mt-2 p-3 bg-yellow-50 rounded-md flex items-center">
                  <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
                  <span className="text-sm text-yellow-800">No parents found. Try a different search term.</span>
                </div>
              )}
            </div>

            {/* Selected Parents */}
            {selectedParents.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm font-medium text-gray-700">Selected Parents:</div>
                {selectedParents.map(parent => (
                  <div key={parent.userId} className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                    <div>
                      <div className="font-medium text-gray-900">{parent.displayName}</div>
                      <div className="text-sm text-gray-500">{parent.email}</div>
                      {parent.phone && <div className="text-sm text-gray-500">{parent.phone}</div>}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveParent(parent.userId)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Students Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Students</h3>

            {/* Student Search */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search and Add Students
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={studentSearchTerm}
                  onChange={(e) => setStudentSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Search by name or email..."
                />
                {isSearchingStudents && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <div className="animate-spin h-4 w-4 border-2 border-green-500 border-t-transparent rounded-full"></div>
                  </div>
                )}
              </div>

              {/* Student Search Results */}
              {studentSearchResults.length > 0 && (
                <div className="mt-2 border border-gray-200 rounded-md max-h-48 overflow-y-auto">
                  {studentSearchResults.map(student => (
                    <button
                      key={student.userId}
                      type="button"
                      onClick={() => handleSelectStudent(student)}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-0"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium text-gray-900">{student.displayName}</div>
                          <div className="text-sm text-gray-500">{student.email}</div>
                          {student.age && student.grade && (
                            <div className="text-sm text-gray-500">Age {student.age}, Grade {student.grade}</div>
                          )}
                        </div>
                        <UserPlus className="h-4 w-4 text-green-600" />
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {studentSearchTerm.length >= 2 && !isSearchingStudents && studentSearchResults.length === 0 && (
                <div className="mt-2 p-3 bg-yellow-50 rounded-md flex items-center">
                  <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
                  <span className="text-sm text-yellow-800">No students found. Try a different search term.</span>
                </div>
              )}
            </div>

            {/* Selected Students */}
            {selectedStudents.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm font-medium text-gray-700">Selected Students:</div>
                {selectedStudents.map(student => (
                  <div key={student.userId} className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                    <div>
                      <div className="font-medium text-gray-900">{student.displayName}</div>
                      <div className="text-sm text-gray-500">{student.email}</div>
                      {student.age && student.grade && (
                        <div className="text-sm text-gray-500">Age {student.age}, Grade {student.grade}</div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveStudent(student.userId)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Address Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Address (Optional)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <input
                  type="text"
                  value={address.street}
                  onChange={(e) => setAddress({ ...address, street: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Street Address"
                />
              </div>
              <input
                type="text"
                value={address.city}
                onChange={(e) => setAddress({ ...address, city: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                placeholder="City"
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={address.state}
                  onChange={(e) => setAddress({ ...address, state: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="State"
                  maxLength={2}
                />
                <input
                  type="text"
                  value={address.zip}
                  onChange={(e) => setAddress({ ...address, zip: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="ZIP"
                  maxLength={10}
                />
              </div>
            </div>
          </div>

          {/* Preferred Programs */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Preferred Programs (Optional)</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {availablePrograms.map(program => (
                <button
                  key={program}
                  type="button"
                  onClick={() => handleProgramToggle(program)}
                  className={`px-4 py-2 rounded-full border transition-all ${
                    preferredPrograms.includes(program)
                      ? 'bg-green-100 border-green-600 text-green-800'
                      : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400'
                  }`}
                >
                  <span className="flex items-center justify-center">
                    {preferredPrograms.includes(program) && (
                      <Check className="h-4 w-4 mr-1" />
                    )}
                    {program}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!familyName || selectedParents.length === 0 || selectedStudents.length === 0}
            >
              Create Family
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddFamilyModalV2;
import React, { useState } from 'react';
import { X, Plus, Trash2, UserPlus } from 'lucide-react';

interface Student {
  name: string;
  age: string;
  grade: string;
  interests: string;
  allergies: string;
}

interface Parent {
  name: string;
  email: string;
  phone: string;
  isPrimary: boolean;
  isEmergencyContact: boolean;
}

interface AddFamilyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (familyData: any) => void;
}

const AddFamilyModal: React.FC<AddFamilyModalProps> = ({ isOpen, onClose, onSave }) => {
  const [familyName, setFamilyName] = useState('');
  const [students, setStudents] = useState<Student[]>([
    { name: '', age: '', grade: '', interests: '', allergies: '' }
  ]);
  const [parents, setParents] = useState<Parent[]>([
    { name: '', email: '', phone: '', isPrimary: true, isEmergencyContact: true }
  ]);
  const [address, setAddress] = useState({ street: '', city: '', state: '', zip: '' });
  const [preferredPrograms, setPreferredPrograms] = useState<string[]>([]);

  const availablePrograms = [
    'Junior Zookeeper', 'Conservation Club', 'Art & Animals',
    'Science Club', 'Teen Naturalist', 'Eco Warriors',
    'Tiny Tots', 'Animal Art', 'Music with Animals'
  ];

  const handleAddStudent = () => {
    setStudents([...students, { name: '', age: '', grade: '', interests: '', allergies: '' }]);
  };

  const handleRemoveStudent = (index: number) => {
    setStudents(students.filter((_, i) => i !== index));
  };

  const handleStudentChange = (index: number, field: keyof Student, value: string) => {
    const updated = [...students];
    updated[index][field] = value;
    setStudents(updated);
  };

  const handleAddParent = () => {
    setParents([...parents, { name: '', email: '', phone: '', isPrimary: false, isEmergencyContact: false }]);
  };

  const handleRemoveParent = (index: number) => {
    if (parents.length > 1) {
      setParents(parents.filter((_, i) => i !== index));
    }
  };

  const handleParentChange = (index: number, field: keyof Parent, value: any) => {
    const updated = [...parents];
    updated[index] = { ...updated[index], [field]: value };

    // Ensure only one primary contact
    if (field === 'isPrimary' && value === true) {
      updated.forEach((p, i) => {
        if (i !== index) p.isPrimary = false;
      });
    }

    setParents(updated);
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

    const familyData = {
      familyName,
      students: students.filter(s => s.name),
      parents: parents.filter(p => p.name),
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
    setStudents([{ name: '', age: '', grade: '', interests: '', allergies: '' }]);
    setParents([{ name: '', email: '', phone: '', isPrimary: true, isEmergencyContact: true }]);
    setAddress({ street: '', city: '', state: '', zip: '' });
    setPreferredPrograms([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Add New Family</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Family Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Family Name *
            </label>
            <input
              type="text"
              required
              value={familyName}
              onChange={(e) => setFamilyName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Johnson Family"
            />
          </div>

          {/* Students Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Students</h3>
              <button
                type="button"
                onClick={handleAddStudent}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Student
              </button>
            </div>

            <div className="space-y-4">
              {students.map((student, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">Student {index + 1}</span>
                    {students.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveStudent(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Student Name *"
                      value={student.name}
                      onChange={(e) => handleStudentChange(index, 'name', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required={index === 0}
                    />
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Age"
                        value={student.age}
                        onChange={(e) => handleStudentChange(index, 'age', e.target.value)}
                        className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder="Grade"
                        value={student.grade}
                        onChange={(e) => handleStudentChange(index, 'grade', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <input
                      type="text"
                      placeholder="Interests (comma separated)"
                      value={student.interests}
                      onChange={(e) => handleStudentChange(index, 'interests', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <input
                      type="text"
                      placeholder="Allergies/Medical Notes"
                      value={student.allergies}
                      onChange={(e) => handleStudentChange(index, 'allergies', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Parents Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Parents & Contacts</h3>
              <button
                type="button"
                onClick={handleAddParent}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              >
                <UserPlus className="w-4 h-4" />
                Add Parent
              </button>
            </div>

            <div className="space-y-4">
              {parents.map((parent, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">
                      Parent {index + 1}
                      {parent.isPrimary && <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Primary</span>}
                    </span>
                    {parents.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveParent(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Parent Name *"
                      value={parent.name}
                      onChange={(e) => handleParentChange(index, 'name', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required={index === 0}
                    />
                    <input
                      type="email"
                      placeholder="Email *"
                      value={parent.email}
                      onChange={(e) => handleParentChange(index, 'email', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required={index === 0}
                    />
                    <input
                      type="tel"
                      placeholder="Phone"
                      value={parent.phone}
                      onChange={(e) => handleParentChange(index, 'phone', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <div className="flex items-center gap-4">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={parent.isPrimary}
                          onChange={(e) => handleParentChange(index, 'isPrimary', e.target.checked)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-700">Primary Contact</span>
                      </label>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={parent.isEmergencyContact}
                          onChange={(e) => handleParentChange(index, 'isEmergencyContact', e.target.checked)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-700">Emergency Contact</span>
                      </label>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Address Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Address</h3>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Street Address"
                value={address.street}
                onChange={(e) => setAddress({ ...address, street: e.target.value })}
                className="col-span-2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="text"
                placeholder="City"
                value={address.city}
                onChange={(e) => setAddress({ ...address, city: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="State"
                  value={address.state}
                  onChange={(e) => setAddress({ ...address, state: e.target.value })}
                  className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="text"
                  placeholder="ZIP Code"
                  value={address.zip}
                  onChange={(e) => setAddress({ ...address, zip: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Preferred Programs */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferred Programs</h3>
            <div className="grid grid-cols-3 gap-3">
              {availablePrograms.map(program => (
                <label key={program} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={preferredPrograms.includes(program)}
                    onChange={() => handleProgramToggle(program)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-sm text-gray-700">{program}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Family
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddFamilyModal;
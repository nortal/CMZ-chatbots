import React, { useState, useEffect, useRef } from 'react';
import { X, Plus, Search } from 'lucide-react';
import { debounce } from '../utils/debounce';
import '../styles/AddFamilyModalV3.css';

interface User {
  userId: string;
  email: string;
  displayName: string;
  role: string;
  phone?: string;
  age?: string;
  grade?: string;
}

interface AddFamilyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (familyData: FamilyFormData) => void;
}

interface FamilyFormData {
  familyName: string;
  children: User[];
  parents: User[];
  address: {
    streetAddress: string;
    city: string;
    state: string;
    zipCode: string;
  };
}

const AddFamilyModalV3: React.FC<AddFamilyModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [familyName, setFamilyName] = useState('');
  const [selectedChildren, setSelectedChildren] = useState<User[]>([]);
  const [selectedParents, setSelectedParents] = useState<User[]>([]);
  const [address, setAddress] = useState({
    streetAddress: '',
    city: '',
    state: '',
    zipCode: ''
  });

  // Typeahead states
  const [showChildSearch, setShowChildSearch] = useState(false);
  const [showParentSearch, setShowParentSearch] = useState(false);
  const [childSearchTerm, setChildSearchTerm] = useState('');
  const [parentSearchTerm, setParentSearchTerm] = useState('');
  const [childSearchResults, setChildSearchResults] = useState<User[]>([]);
  const [parentSearchResults, setParentSearchResults] = useState<User[]>([]);
  const [isSearchingChildren, setIsSearchingChildren] = useState(false);
  const [isSearchingParents, setIsSearchingParents] = useState(false);

  const modalContentRef = useRef<HTMLDivElement>(null);
  const childSearchInputRef = useRef<HTMLInputElement>(null);
  const parentSearchInputRef = useRef<HTMLInputElement>(null);

  // API search function
  const searchUsers = async (query: string, role: 'student' | 'parent'): Promise<User[]> => {
    if (query.length < 2) return [];

    try {
      const params = new URLSearchParams({
        query: query,
        role: role,
        page_size: '5'
      });

      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8080';
      const response = await fetch(`${apiUrl}/user?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        console.error('User search failed:', response.status);
        return [];
      }

      const data = await response.json();
      const users = data.items || [];

      return users.map((user: any) => ({
        userId: user.userId || user.user_id,
        email: user.email,
        displayName: user.displayName || user.display_name || `${user.firstName} ${user.lastName}`,
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

  // Debounced search functions
  const debouncedChildSearch = useRef(
    debounce(async (term: string) => {
      setIsSearchingChildren(true);
      const results = await searchUsers(term, 'student');
      setChildSearchResults(results);
      setIsSearchingChildren(false);
    }, 300)
  ).current;

  const debouncedParentSearch = useRef(
    debounce(async (term: string) => {
      setIsSearchingParents(true);
      const results = await searchUsers(term, 'parent');
      setParentSearchResults(results);
      setIsSearchingParents(false);
    }, 300)
  ).current;

  // Handle search term changes
  useEffect(() => {
    if (childSearchTerm) {
      debouncedChildSearch(childSearchTerm);
    } else {
      setChildSearchResults([]);
    }
  }, [childSearchTerm]);

  useEffect(() => {
    if (parentSearchTerm) {
      debouncedParentSearch(parentSearchTerm);
    } else {
      setParentSearchResults([]);
    }
  }, [parentSearchTerm]);

  // Focus management
  useEffect(() => {
    if (showChildSearch && childSearchInputRef.current) {
      childSearchInputRef.current.focus();
    }
  }, [showChildSearch]);

  useEffect(() => {
    if (showParentSearch && parentSearchInputRef.current) {
      parentSearchInputRef.current.focus();
    }
  }, [showParentSearch]);

  const handleAddChild = (child: User) => {
    if (!selectedChildren.find(c => c.userId === child.userId)) {
      setSelectedChildren([...selectedChildren, child]);
    }
    setShowChildSearch(false);
    setChildSearchTerm('');
    setChildSearchResults([]);
  };

  const handleRemoveChild = (childId: string) => {
    setSelectedChildren(selectedChildren.filter(c => c.userId !== childId));
  };

  const handleAddParent = (parent: User) => {
    if (!selectedParents.find(p => p.userId === parent.userId)) {
      setSelectedParents([...selectedParents, parent]);
    }
    setShowParentSearch(false);
    setParentSearchTerm('');
    setParentSearchResults([]);
  };

  const handleRemoveParent = (parentId: string) => {
    setSelectedParents(selectedParents.filter(p => p.userId !== parentId));
  };

  const isFormValid = () => {
    return familyName.trim() !== '' &&
           selectedParents.length > 0 &&
           address.streetAddress.trim() !== '' &&
           address.city.trim() !== '' &&
           address.state.trim() !== '' &&
           address.zipCode.trim() !== '';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isFormValid()) {
      onSubmit({
        familyName,
        children: selectedChildren,
        parents: selectedParents,
        address
      });
      handleClose();
    }
  };

  const handleClose = () => {
    // Reset form
    setFamilyName('');
    setSelectedChildren([]);
    setSelectedParents([]);
    setAddress({
      streetAddress: '',
      city: '',
      state: '',
      zipCode: ''
    });
    setShowChildSearch(false);
    setShowParentSearch(false);
    setChildSearchTerm('');
    setParentSearchTerm('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="afm-overlay" onClick={handleClose} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="afm-container" onClick={(e) => e.stopPropagation()}>
        <div className="afm-header">
          <h2 id="modal-title">Add New Family</h2>
          <button className="afm-close-btn" onClick={handleClose} aria-label="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="afm-content" ref={modalContentRef}>
          <form onSubmit={handleSubmit} noValidate>
            {/* Family Name */}
            <div className="afm-section">
              <label htmlFor="familyName" className="afm-label">
                Family Name <span className="afm-required">*</span>
              </label>
              <input
                type="text"
                id="familyName"
                className="afm-input"
                value={familyName}
                onChange={(e) => setFamilyName(e.target.value)}
                placeholder="e.g., Johnson Family"
                required
                aria-required="true"
              />
            </div>

            {/* Children Section */}
            <div className="afm-section">
              <div className="afm-section-header">
                <h3>Children</h3>
              </div>

              {/* Selected Children Chips */}
              {selectedChildren.length > 0 && (
                <div className="afm-chips" role="list" aria-label="Selected children">
                  {selectedChildren.map((child) => (
                    <div key={child.userId} className="afm-chip" role="listitem">
                      <span className="afm-chip-text">
                        {child.displayName} {child.age && `(${child.age})`}
                      </span>
                      <button
                        type="button"
                        className="afm-chip-remove"
                        onClick={() => handleRemoveChild(child.userId)}
                        aria-label={`Remove ${child.displayName}`}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Add Child Button/Search */}
              {!showChildSearch ? (
                <button
                  type="button"
                  className="afm-add-btn"
                  onClick={() => setShowChildSearch(true)}
                  aria-expanded="false"
                >
                  <Plus size={16} /> Add Child
                </button>
              ) : (
                <div className="afm-search-container">
                  <div className="afm-search-wrapper">
                    <Search size={16} className="afm-search-icon" />
                    <input
                      ref={childSearchInputRef}
                      type="text"
                      className="afm-search-input"
                      placeholder="Search for a child..."
                      value={childSearchTerm}
                      onChange={(e) => setChildSearchTerm(e.target.value)}
                      aria-label="Search for children"
                      aria-describedby="child-search-help"
                      aria-autocomplete="list"
                      aria-controls="child-search-results"
                    />
                    <button
                      type="button"
                      className="afm-cancel-link"
                      onClick={() => {
                        setShowChildSearch(false);
                        setChildSearchTerm('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                  <span id="child-search-help" className="afm-sr-only">
                    Type at least 2 characters to search
                  </span>

                  {/* Search Results Dropdown */}
                  {(isSearchingChildren || childSearchResults.length > 0 || childSearchTerm.length >= 2) && (
                    <div
                      id="child-search-results"
                      className="afm-search-results"
                      role="listbox"
                      aria-label="Search results"
                    >
                      {isSearchingChildren ? (
                        <div className="afm-search-loading" role="status">
                          <span>Searching...</span>
                        </div>
                      ) : childSearchResults.length > 0 ? (
                        childSearchResults.map((child) => (
                          <button
                            key={child.userId}
                            type="button"
                            className="afm-result-item"
                            onClick={() => handleAddChild(child)}
                            role="option"
                            aria-selected="false"
                          >
                            <div className="afm-result-info">
                              <div className="afm-result-name">{child.displayName}</div>
                              <div className="afm-result-email">{child.email}</div>
                            </div>
                          </button>
                        ))
                      ) : childSearchTerm.length >= 2 ? (
                        <div className="afm-no-results">No children found</div>
                      ) : null}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Parents Section */}
            <div className="afm-section">
              <div className="afm-section-header">
                <h3>Parents & Contacts <span className="afm-required">*</span></h3>
              </div>

              {/* Selected Parents Chips */}
              {selectedParents.length > 0 && (
                <div className="afm-chips" role="list" aria-label="Selected parents">
                  {selectedParents.map((parent) => (
                    <div key={parent.userId} className="afm-chip" role="listitem">
                      <span className="afm-chip-text">{parent.displayName}</span>
                      <button
                        type="button"
                        className="afm-chip-remove"
                        onClick={() => handleRemoveParent(parent.userId)}
                        aria-label={`Remove ${parent.displayName}`}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Add Parent Button/Search */}
              {!showParentSearch ? (
                <button
                  type="button"
                  className="afm-add-btn"
                  onClick={() => setShowParentSearch(true)}
                  aria-expanded="false"
                >
                  <Plus size={16} /> Add Parent
                </button>
              ) : (
                <div className="afm-search-container">
                  <div className="afm-search-wrapper">
                    <Search size={16} className="afm-search-icon" />
                    <input
                      ref={parentSearchInputRef}
                      type="text"
                      className="afm-search-input"
                      placeholder="Search for a parent..."
                      value={parentSearchTerm}
                      onChange={(e) => setParentSearchTerm(e.target.value)}
                      aria-label="Search for parents"
                      aria-describedby="parent-search-help"
                      aria-autocomplete="list"
                      aria-controls="parent-search-results"
                    />
                    <button
                      type="button"
                      className="afm-cancel-link"
                      onClick={() => {
                        setShowParentSearch(false);
                        setParentSearchTerm('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                  <span id="parent-search-help" className="afm-sr-only">
                    Type at least 2 characters to search
                  </span>

                  {/* Search Results Dropdown */}
                  {(isSearchingParents || parentSearchResults.length > 0 || parentSearchTerm.length >= 2) && (
                    <div
                      id="parent-search-results"
                      className="afm-search-results"
                      role="listbox"
                      aria-label="Search results"
                    >
                      {isSearchingParents ? (
                        <div className="afm-search-loading" role="status">
                          <span>Searching...</span>
                        </div>
                      ) : parentSearchResults.length > 0 ? (
                        parentSearchResults.map((parent) => (
                          <button
                            key={parent.userId}
                            type="button"
                            className="afm-result-item"
                            onClick={() => handleAddParent(parent)}
                            role="option"
                            aria-selected="false"
                          >
                            <div className="afm-result-info">
                              <div className="afm-result-name">{parent.displayName}</div>
                              <div className="afm-result-email">{parent.email}</div>
                            </div>
                          </button>
                        ))
                      ) : parentSearchTerm.length >= 2 ? (
                        <div className="afm-no-results">No parents found</div>
                      ) : null}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Address Section */}
            <div className="afm-section">
              <div className="afm-section-header">
                <h3>Address <span className="afm-required">*</span></h3>
              </div>

              <div className="afm-address-fields">
                <div className="afm-field-group afm-full-width">
                  <label htmlFor="streetAddress" className="afm-label">
                    Street Address
                  </label>
                  <input
                    type="text"
                    id="streetAddress"
                    className="afm-input"
                    value={address.streetAddress}
                    onChange={(e) => setAddress({...address, streetAddress: e.target.value})}
                    required
                    aria-required="true"
                  />
                </div>

                <div className="afm-address-row">
                  <div className="afm-field-group afm-city">
                    <label htmlFor="city" className="afm-label">
                      City
                    </label>
                    <input
                      type="text"
                      id="city"
                      className="afm-input"
                      value={address.city}
                      onChange={(e) => setAddress({...address, city: e.target.value})}
                      required
                      aria-required="true"
                    />
                  </div>

                  <div className="afm-field-group afm-state">
                    <label htmlFor="state" className="afm-label">
                      State
                    </label>
                    <input
                      type="text"
                      id="state"
                      className="afm-input"
                      value={address.state}
                      onChange={(e) => setAddress({...address, state: e.target.value.toUpperCase()})}
                      maxLength={2}
                      placeholder="WA"
                      required
                      aria-required="true"
                    />
                  </div>

                  <div className="afm-field-group afm-zip">
                    <label htmlFor="zipCode" className="afm-label">
                      ZIP Code
                    </label>
                    <input
                      type="text"
                      id="zipCode"
                      className="afm-input"
                      value={address.zipCode}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '');
                        setAddress({...address, zipCode: value});
                      }}
                      pattern="[0-9]{5}"
                      maxLength={5}
                      placeholder="98101"
                      required
                      aria-required="true"
                    />
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>

        <div className="afm-footer">
          <button type="button" className="afm-btn-secondary" onClick={handleClose}>
            Cancel
          </button>
          <button
            type="submit"
            className="afm-btn-primary"
            onClick={handleSubmit}
            disabled={!isFormValid()}
            aria-disabled={!isFormValid()}
          >
            Add Family
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddFamilyModalV3;
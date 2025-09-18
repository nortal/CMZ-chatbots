import * as React from 'react';
import { Users, MapPin, Search, Plus, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { debounce } from '../utils/debounce';

interface User {
  userId: string;
  email: string;
  displayName: string;
  role: string;
  phone?: string;
  age?: string;
  grade?: string;
}

interface AddFamilyModalEnhancedProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit?: (familyData: FamilyFormData) => void;
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

interface TypeaheadProps {
  placeholder: string;
  selectedUsers: User[];
  onUserSelect: (user: User) => void;
  onUserRemove: (userId: string) => void;
  userType: 'parent' | 'student';
}

const Typeahead: React.FC<TypeaheadProps> = ({
  placeholder,
  selectedUsers,
  onUserSelect,
  onUserRemove,
  userType,
}) => {
  const [query, setQuery] = React.useState('');
  const [isOpen, setIsOpen] = React.useState(false);
  const [isAddingNew, setIsAddingNew] = React.useState(false);
  const [filteredUsers, setFilteredUsers] = React.useState<User[]>([]);
  const [isSearching, setIsSearching] = React.useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // API search function
  const searchUsers = async (searchQuery: string, role: string): Promise<User[]> => {
    if (searchQuery.length < 2) return [];

    try {
      const params = new URLSearchParams({
        query: searchQuery,
        role: role,
        page_size: '5'
      });

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
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

      return users.map((user: any) => {
        const mappedUser = {
          userId: user.user_id || user.userId,  // Check snake_case first since that's what API returns
          email: user.email,
          displayName: user.display_name || user.displayName || `${user.firstName} ${user.lastName}`,
          role: user.role,
          phone: user.phone_number || user.phoneNumber,
          age: user.age?.toString(),
          grade: user.grade
        };
        console.log('Mapped user:', mappedUser);
        return mappedUser;
      });
    } catch (error) {
      console.error('Error searching users:', error);
      return [];
    }
  };

  // Debounced search
  const debouncedSearch = React.useRef(
    debounce(async (searchQuery: string) => {
      setIsSearching(true);
      const results = await searchUsers(searchQuery, userType);
      const filtered = results.filter(
        user => !selectedUsers.some(selected => selected.userId === user.userId)
      );
      setFilteredUsers(filtered);
      setIsSearching(false);
      setIsOpen(filtered.length > 0);
    }, 300)
  ).current;

  React.useEffect(() => {
    if (query.length >= 2) {
      debouncedSearch(query);
    } else {
      setFilteredUsers([]);
      setIsOpen(false);
    }
  }, [query, selectedUsers]);

  React.useEffect(() => {
    if (isAddingNew && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isAddingNew]);

  const handleUserSelect = (user: User) => {
    onUserSelect(user);
    setQuery('');
    setIsOpen(false);
    setIsAddingNew(false);
  };

  const handleAddClick = () => {
    setIsAddingNew(true);
  };

  const handleCancelClick = () => {
    setIsAddingNew(false);
    setQuery('');
    setIsOpen(false);
  };

  if (!isAddingNew) {
    return (
      <div className="space-y-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAddClick}
          className="text-blue-600 border-blue-300 hover:bg-blue-50"
        >
          <Plus className="h-4 w-4 mr-1" />
          Add {userType === 'parent' ? 'Parent' : 'Child'}
        </Button>

        {selectedUsers.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedUsers.map((user) => (
              <Badge
                key={user.userId}
                variant="secondary"
                className="gap-1 pr-1"
              >
                <span>{user.displayName}</span>
                <button
                  type="button"
                  onClick={() => onUserRemove(user.userId)}
                  className="ml-1 rounded-full p-0.5 hover:bg-gray-300 transition-colors"
                  aria-label={`Remove ${user.displayName}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative space-y-2">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          ref={inputRef}
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {isSearching && (
        <div className="text-sm text-gray-500">Searching...</div>
      )}

      {isOpen && filteredUsers.length > 0 && (
        <div className="absolute top-full z-50 mt-1 w-full rounded-md border bg-white p-1 shadow-md max-h-60 overflow-auto">
          {filteredUsers.map((user) => (
            <button
              key={user.userId}
              type="button"
              onClick={() => handleUserSelect(user)}
              className="w-full rounded-sm px-2 py-2 text-left text-sm hover:bg-gray-100 transition-colors"
            >
              <div className="font-medium">{user.displayName}</div>
              <div className="text-xs text-gray-500">{user.email}</div>
            </button>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={handleCancelClick}
        className="text-sm text-gray-500 hover:text-gray-700 underline"
      >
        Cancel
      </button>

      {selectedUsers.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {selectedUsers.map((user) => (
            <Badge
              key={user.userId}
              variant="secondary"
              className="gap-1 pr-1"
            >
              <span>{user.displayName}</span>
              <button
                type="button"
                onClick={() => onUserRemove(user.userId)}
                className="ml-1 rounded-full p-0.5 hover:bg-gray-300 transition-colors"
                aria-label={`Remove ${user.displayName}`}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

const AddFamilyModalEnhanced: React.FC<AddFamilyModalEnhancedProps> = ({
  open,
  onOpenChange,
  onSubmit,
}) => {
  const [familyName, setFamilyName] = React.useState('');
  const [selectedParents, setSelectedParents] = React.useState<User[]>([]);
  const [selectedChildren, setSelectedChildren] = React.useState<User[]>([]);
  const [address, setAddress] = React.useState({
    streetAddress: '',
    city: '',
    state: '',
    zipCode: '',
  });

  const handleParentSelect = (user: User) => {
    setSelectedParents(prev => [...prev, user]);
  };

  const handleParentRemove = (userId: string) => {
    setSelectedParents(prev => prev.filter(user => user.userId !== userId));
  };

  const handleChildSelect = (user: User) => {
    setSelectedChildren(prev => [...prev, user]);
  };

  const handleChildRemove = (userId: string) => {
    setSelectedChildren(prev => prev.filter(user => user.userId !== userId));
  };

  const handleAddressChange = (field: keyof typeof address, value: string) => {
    setAddress(prev => ({ ...prev, [field]: value }));
  };

  const isFormValid = () => {
    return (
      familyName.trim() !== '' &&
      selectedParents.length > 0 &&
      address.streetAddress.trim() !== '' &&
      address.city.trim() !== '' &&
      address.state.trim() !== '' &&
      address.zipCode.trim() !== ''
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isFormValid() && onSubmit) {
      const submissionData = {
        familyName,
        parents: selectedParents,
        children: selectedChildren,
        address,
      };
      console.log('Submitting family data:', submissionData);
      console.log('Parent IDs:', selectedParents.map(p => p.userId));
      console.log('Child IDs:', selectedChildren.map(c => c.userId));
      onSubmit(submissionData);
      resetForm();
      onOpenChange(false);
    }
  };

  const resetForm = () => {
    setFamilyName('');
    setSelectedParents([]);
    setSelectedChildren([]);
    setAddress({
      streetAddress: '',
      city: '',
      state: '',
      zipCode: '',
    });
  };

  React.useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl font-bold">
              Add New Family
            </DialogTitle>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6 max-h-[60vh]">
            {/* Family Name */}
            <div className="space-y-2">
              <Label htmlFor="familyName">
                Family Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="familyName"
                placeholder="Enter family name"
                value={familyName}
                onChange={(e) => setFamilyName(e.target.value)}
                required
              />
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200" />

            {/* Children Section */}
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-900">Children</h3>
              <Typeahead
                placeholder="Search for children by name..."
                selectedUsers={selectedChildren}
                onUserSelect={handleChildSelect}
                onUserRemove={handleChildRemove}
                userType="student"
              />
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200" />

            {/* Parents Section */}
            <div className="space-y-3">
              <h3 className="font-semibold text-gray-900">
                Parents & Contacts <span className="text-red-500">*</span>
              </h3>
              <Typeahead
                placeholder="Search for parents by name..."
                selectedUsers={selectedParents}
                onUserSelect={handleParentSelect}
                onUserRemove={handleParentRemove}
                userType="parent"
              />
              {selectedParents.length === 0 && (
                <p className="text-sm text-gray-500">At least one parent is required</p>
              )}
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200" />

            {/* Address Section */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Address <span className="text-red-500">*</span>
              </h3>

              <div className="grid gap-4">
                <div className="space-y-2">
                  <Label htmlFor="street">Street Address</Label>
                  <Input
                    id="street"
                    placeholder="123 Main Street"
                    value={address.streetAddress}
                    onChange={(e) => handleAddressChange('streetAddress', e.target.value)}
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      placeholder="City"
                      value={address.city}
                      onChange={(e) => handleAddressChange('city', e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State</Label>
                    <Input
                      id="state"
                      placeholder="State"
                      value={address.state}
                      onChange={(e) => handleAddressChange('state', e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2 md:col-span-1">
                    <Label htmlFor="zipCode">ZIP Code</Label>
                    <Input
                      id="zipCode"
                      placeholder="12345"
                      value={address.zipCode}
                      onChange={(e) => handleAddressChange('zipCode', e.target.value)}
                      required
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="sticky bottom-0 bg-white border-t border-gray-200 mt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!isFormValid()}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Add Family
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddFamilyModalEnhanced;
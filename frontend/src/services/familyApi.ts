// Family API Service
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export interface FamilyFormData {
  familyName: string;
  children: Array<{
    userId: string;
    email: string;
    displayName: string;
    role: string;
  }>;
  parents: Array<{
    userId: string;
    email: string;
    displayName: string;
    role: string;
  }>;
  address: {
    streetAddress: string;
    city: string;
    state: string;
    zipCode: string;
  };
}

export interface User {
  userId: string;
  displayName: string;
  email: string;
  role: string;
  phone?: string;
  familyIds?: string[];
}

export interface Family {
  familyId: string;
  familyName: string;
  parentIds: string[];
  studentIds: string[];
  parents?: User[];
  students?: User[];
  address?: {
    streetAddress: string;
    city: string;
    state: string;
    zipCode: string;
  };
  createdAt?: string;
  modifiedAt?: string;
}

class FamilyApiService {
  private getAuthToken(): string | null {
    // Get token from localStorage or auth context
    return localStorage.getItem('authToken');
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Add X-User-Id header for backend authentication
    // Try to get the user ID from various sources
    const currentUser = localStorage.getItem('currentUser');
    console.log('FamilyAPI - currentUser from localStorage:', currentUser);

    if (currentUser) {
      try {
        const user = JSON.parse(currentUser);
        if (user.userId) {
          headers['X-User-Id'] = user.userId;
          console.log('FamilyAPI - Using userId from currentUser:', user.userId);
        }
      } catch (e) {
        // If not JSON, use as is
        headers['X-User-Id'] = currentUser;
        console.log('FamilyAPI - Using currentUser as string:', currentUser);
      }
    } else {
      // Fallback to a real admin user ID for testing
      headers['X-User-Id'] = '4fd19775-68bc-470e-a5d4-ceb70552c8d7';
      console.log('FamilyAPI - Using fallback admin user ID:', headers['X-User-Id']);
    }

    console.log('FamilyAPI - Final headers:', headers);
    return headers;
  }

  private async fetchUser(userId: string): Promise<User | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/user/${userId}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        console.warn('Failed to fetch user:', userId, response.statusText);
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching user:', userId, error);
      return null;
    }
  }

  private async batchGetUsers(userIds: string[]): Promise<Record<string, User>> {
    console.log('FamilyAPI - Batch fetching users:', userIds);
    const userMap: Record<string, User> = {};

    // Fetch all users in parallel
    const userPromises = userIds.map(userId => this.fetchUser(userId));
    const users = await Promise.all(userPromises);

    // Build user map
    users.forEach((user, index) => {
      if (user) {
        userMap[userIds[index]] = user;
      }
    });

    console.log('FamilyAPI - Fetched users:', Object.keys(userMap).length, 'out of', userIds.length);
    return userMap;
  }

  private async populateFamilyUsers(families: Family[]): Promise<Family[]> {
    // Extract all unique user IDs
    const allUserIds = families.flatMap(f => [...f.parentIds, ...f.studentIds]);
    const uniqueUserIds = [...new Set(allUserIds)];

    if (uniqueUserIds.length === 0) {
      return families;
    }

    // Batch fetch all users
    const userMap = await this.batchGetUsers(uniqueUserIds);

    // Populate each family with user details
    families.forEach(family => {
      family.parents = family.parentIds
        .map(id => userMap[id])
        .filter((user): user is User => user !== undefined);

      family.students = family.studentIds
        .map(id => userMap[id])
        .filter((user): user is User => user !== undefined);
    });

    return families;
  }

  async createFamily(familyData: FamilyFormData): Promise<Family> {
    try {
      console.log('FamilyAPI received data:', familyData);
      console.log('Parent objects:', familyData.parents);
      console.log('Children objects:', familyData.children);

      // Validate that we have at least one student (required by backend API specification)
      if (!familyData.children || familyData.children.length === 0) {
        throw new Error('At least one child is required to create a family. Please add a child before submitting.');
      }

      // Transform the data to match backend API structure
      const payload = {
        familyName: familyData.familyName,
        parentIds: familyData.parents.map(p => p.userId),  // Backend expects parentIds array
        studentIds: familyData.children.map(c => c.userId), // Backend expects studentIds array
        address: {
          street: familyData.address.streetAddress,  // Backend expects 'street' not 'streetAddress'
          city: familyData.address.city,
          state: familyData.address.state,
          zipCode: familyData.address.zipCode,  // This will be converted to zip_code in backend
        },
      };

      console.log('Sending to backend:', payload);
      console.log('Parent IDs being sent:', payload.parentIds);
      console.log('Student IDs being sent:', payload.studentIds);

      const response = await fetch(`${API_BASE_URL}/family`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Failed to create family: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating family:', error);
      throw error;
    }
  }

  async getFamilies(): Promise<Family[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/family`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch families: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('FamilyAPI - Raw response from /family:', data);

      // The API returns an array directly, not wrapped in 'items'
      const families = Array.isArray(data) ? data : (data.items || []);

      // Populate user details for all families
      console.log('FamilyAPI - Populating user details for', families.length, 'families');
      const populatedFamilies = await this.populateFamilyUsers(families);
      console.log('FamilyAPI - User population complete');

      return populatedFamilies;
    } catch (error) {
      console.error('Error fetching families:', error);
      throw error;
    }
  }

  async getFamilyById(familyId: string): Promise<Family> {
    try {
      const response = await fetch(`${API_BASE_URL}/family/${familyId}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch family: ${response.statusText}`);
      }

      const family = await response.json();

      // Populate user details for single family
      const populated = await this.populateFamilyUsers([family]);
      return populated[0];
    } catch (error) {
      console.error('Error fetching family:', error);
      throw error;
    }
  }

  async updateFamily(familyId: string, familyData: Partial<FamilyFormData>): Promise<Family> {
    try {
      const payload: any = {};

      if (familyData.familyName) {
        payload.familyName = familyData.familyName;
      }
      if (familyData.parents) {
        payload.parentIds = familyData.parents.map(p => p.userId);
      }
      if (familyData.children) {
        payload.studentIds = familyData.children.map(c => c.userId);
      }
      if (familyData.address) {
        payload.address = familyData.address;
      }

      const response = await fetch(`${API_BASE_URL}/family/${familyId}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Failed to update family: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating family:', error);
      throw error;
    }
  }

  async deleteFamily(familyId: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/family/${familyId}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to delete family: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting family:', error);
      throw error;
    }
  }

  async addFamilyMember(familyId: string, userId: string, role: 'parent' | 'student'): Promise<Family> {
    try {
      const endpoint = role === 'parent' ? 'parent' : 'student';
      const response = await fetch(`${API_BASE_URL}/family/${familyId}/${endpoint}/${userId}`, {
        method: 'POST',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to add family member: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error adding family member:', error);
      throw error;
    }
  }

  async removeFamilyMember(familyId: string, userId: string, role: 'parent' | 'student'): Promise<Family> {
    try {
      const endpoint = role === 'parent' ? 'parent' : 'student';
      const response = await fetch(`${API_BASE_URL}/family/${familyId}/${endpoint}/${userId}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Failed to remove family member: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error removing family member:', error);
      throw error;
    }
  }
}

export const familyApi = new FamilyApiService();
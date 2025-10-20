import React, { useState } from 'react';
import { Search, X, Users, Filter, AlertCircle, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../config/api';

/**
 * User Search Filter Interface
 * Supports comprehensive user search with multiple filter criteria
 */
interface UserSearchFilters {
  firstName: string;
  lastName: string;
  age: string;
  roleType: string;
  numberOfVisits: string;
}

/**
 * User Interface matching backend schema
 */
interface User {
  userId: string;
  email: string;
  displayName: string;
  role: 'parent' | 'student' | 'admin' | 'zookeeper' | 'visitor';
  phone?: string;
  age?: number;
  grade?: string;
  visits?: number;
  created?: {
    at: string;
  };
}

/**
 * API Response for paginated user results
 */
interface PagedUsers {
  items: User[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

/**
 * UserSearch Component
 *
 * Comprehensive user search page with multiple filter options:
 * - First Name (text)
 * - Last Name (text)
 * - Age (numeric)
 * - Role Type (select: parent, student, admin, zookeeper, visitor)
 * - Number of Visits to Zoo (numeric)
 *
 * Features:
 * - Responsive design for mobile and desktop
 * - Accessible ARIA labels and keyboard navigation
 * - Loading states and error handling
 * - Results table with user information
 * - Clear filters functionality
 */
const UserSearch: React.FC = () => {
  // Filter state
  const [filters, setFilters] = useState<UserSearchFilters>({
    firstName: '',
    lastName: '',
    age: '',
    roleType: '',
    numberOfVisits: ''
  });

  // Results and UI state
  const [results, setResults] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [totalResults, setTotalResults] = useState(0);

  /**
   * Handle filter input changes
   */
  const handleFilterChange = (field: keyof UserSearchFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null); // Clear error when user modifies filters
  };

  /**
   * Clear all filters and results
   */
  const handleClearFilters = () => {
    setFilters({
      firstName: '',
      lastName: '',
      age: '',
      roleType: '',
      numberOfVisits: ''
    });
    setResults([]);
    setError(null);
    setHasSearched(false);
    setTotalResults(0);
  };

  /**
   * Execute user search with current filters
   */
  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    // Validate at least one filter is provided
    const hasFilters = Object.values(filters).some(value => value.trim() !== '');
    if (!hasFilters) {
      setError('Please enter at least one search criterion');
      return;
    }

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      // Build query string from active filters
      const params = new URLSearchParams();

      // Combine first and last name into query parameter
      const nameQuery = [filters.firstName, filters.lastName]
        .filter(n => n.trim())
        .join(' ');

      if (nameQuery) {
        params.append('query', nameQuery);
      }

      if (filters.age) {
        params.append('age', filters.age);
      }

      if (filters.roleType) {
        params.append('role', filters.roleType);
      }

      if (filters.numberOfVisits) {
        params.append('visits', filters.numberOfVisits);
      }

      // Set reasonable page size
      params.append('page_size', '50');

      // Call backend API
      const response = await fetch(`${API_BASE_URL}/user?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data: PagedUsers = await response.json();

      setResults(data.items || []);
      setTotalResults(data.total || 0);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(`Unable to search users: ${errorMessage}`);
      setResults([]);
      setTotalResults(0);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Format role for display
   */
  const formatRole = (role: string): string => {
    return role.charAt(0).toUpperCase() + role.slice(1);
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Invalid Date';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center mb-2">
            <Users className="h-8 w-8 text-green-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">User Search</h1>
          </div>
          <p className="text-gray-600">
            Search for users by name, age, role, and visit history
          </p>
        </div>

        {/* Search Filters Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center mb-4">
            <Filter className="h-5 w-5 text-gray-700 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">Search Filters</h2>
          </div>

          <form onSubmit={handleSearch}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {/* First Name Filter */}
              <div>
                <label
                  htmlFor="firstName"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  First Name
                </label>
                <input
                  id="firstName"
                  type="text"
                  value={filters.firstName}
                  onChange={(e) => handleFilterChange('firstName', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter first name"
                  aria-label="Search by first name"
                />
              </div>

              {/* Last Name Filter */}
              <div>
                <label
                  htmlFor="lastName"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Last Name
                </label>
                <input
                  id="lastName"
                  type="text"
                  value={filters.lastName}
                  onChange={(e) => handleFilterChange('lastName', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter last name"
                  aria-label="Search by last name"
                />
              </div>

              {/* Age Filter */}
              <div>
                <label
                  htmlFor="age"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Age
                </label>
                <input
                  id="age"
                  type="number"
                  min="0"
                  max="120"
                  value={filters.age}
                  onChange={(e) => handleFilterChange('age', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter age"
                  aria-label="Search by age"
                />
              </div>

              {/* Role Type Filter */}
              <div>
                <label
                  htmlFor="roleType"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Role Type
                </label>
                <select
                  id="roleType"
                  value={filters.roleType}
                  onChange={(e) => handleFilterChange('roleType', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500 bg-white"
                  aria-label="Filter by role type"
                >
                  <option value="">All Roles</option>
                  <option value="parent">Parent</option>
                  <option value="student">Student</option>
                  <option value="admin">Admin</option>
                  <option value="zookeeper">Zookeeper</option>
                  <option value="visitor">Visitor</option>
                </select>
              </div>

              {/* Number of Visits Filter */}
              <div>
                <label
                  htmlFor="numberOfVisits"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Number of Visits
                </label>
                <input
                  id="numberOfVisits"
                  type="number"
                  min="0"
                  value={filters.numberOfVisits}
                  onChange={(e) => handleFilterChange('numberOfVisits', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter visit count"
                  aria-label="Search by number of visits"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="submit"
                disabled={isLoading}
                className="flex items-center justify-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                aria-label="Search users"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-5 w-5 mr-2" />
                    Search
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleClearFilters}
                disabled={isLoading}
                className="flex items-center justify-center px-6 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                aria-label="Clear all filters"
              >
                <X className="h-5 w-5 mr-2" />
                Clear Filters
              </button>
            </div>
          </form>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 rounded-md flex items-start" role="alert">
              <AlertCircle className="h-5 w-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Search Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        {hasSearched && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Search Results
                {!isLoading && (
                  <span className="ml-2 text-sm font-normal text-gray-600">
                    ({totalResults} {totalResults === 1 ? 'user' : 'users'} found)
                  </span>
                )}
              </h2>
            </div>

            {/* Results Table */}
            {results.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Name
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Email
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Role
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Age
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Visits
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Phone
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Created
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.map((user) => (
                      <tr key={user.userId} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {user.displayName}
                          </div>
                          {user.grade && (
                            <div className="text-sm text-gray-500">
                              Grade {user.grade}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{user.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {formatRole(user.role)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {user.age || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {user.visits !== undefined ? user.visits : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {user.phone || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(user.created?.at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No users found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your search filters to find different results
                </p>
              </div>
            )}
          </div>
        )}

        {/* Initial State - No Search Yet */}
        {!hasSearched && !isLoading && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Ready to search
            </h3>
            <p className="text-gray-600">
              Enter your search criteria above and click Search to find users
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserSearch;

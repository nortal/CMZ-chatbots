import React, { useState } from 'react';
import { Plus, Search, Edit, Trash2, Shield, Key, Mail, Calendar, Filter, Eye, UserCheck, UserX } from 'lucide-react';
import { UserRole } from '../types/roles';

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  role: UserRole;
  status: 'active' | 'inactive' | 'pending' | 'suspended';
  createdDate: string;
  lastLogin?: string;
  loginCount: number;
  permissions: string[];
  department?: string;
  notes?: string;
  twoFactorEnabled: boolean;
  emailVerified: boolean;
  profileComplete: boolean;
}

const UserManagement: React.FC = () => {
  const [users] = useState<User[]>([
    {
      id: 'user-001',
      firstName: 'John',
      lastName: 'Administrator',
      email: 'admin@cmz.org',
      phone: '(555) 100-0001',
      role: 'admin',
      status: 'active',
      createdDate: '2023-01-15',
      lastLogin: '2024-03-15T10:30:00Z',
      loginCount: 247,
      permissions: ['user_management', 'family_management', 'animal_config', 'analytics', 'billing', 'system_admin'],
      department: 'Administration',
      twoFactorEnabled: true,
      emailVerified: true,
      profileComplete: true,
      notes: 'Primary system administrator'
    },
    {
      id: 'user-002',
      firstName: 'Sarah',
      lastName: 'Johnson',
      email: 'sarah.johnson@cmz.org',
      phone: '(555) 200-0002',
      role: 'zookeeper',
      status: 'active',
      createdDate: '2023-03-20',
      lastLogin: '2024-03-14T16:45:00Z',
      loginCount: 189,
      permissions: ['animal_config', 'animal_details', 'conversations'],
      department: 'Animal Care',
      twoFactorEnabled: true,
      emailVerified: true,
      profileComplete: true,
      notes: 'Senior zookeeper, specializes in large mammals'
    },
    {
      id: 'user-003',
      firstName: 'Maria',
      lastName: 'Rodriguez',
      email: 'maria.rodriguez@cmz.org',
      phone: '(555) 300-0003',
      role: 'educator',
      status: 'active',
      createdDate: '2023-05-10',
      lastLogin: '2024-03-13T09:15:00Z',
      loginCount: 156,
      permissions: ['family_management', 'educational_content', 'conversations'],
      department: 'Education',
      twoFactorEnabled: false,
      emailVerified: true,
      profileComplete: true,
      notes: 'Lead educational coordinator'
    },
    {
      id: 'user-004',
      firstName: 'David',
      lastName: 'Chen',
      email: 'david.chen@email.com',
      role: 'member',
      status: 'active',
      createdDate: '2023-11-10',
      lastLogin: '2024-02-28T14:20:00Z',
      loginCount: 23,
      permissions: ['view_animals', 'chat_animals'],
      twoFactorEnabled: false,
      emailVerified: true,
      profileComplete: true,
      notes: 'Zoo member family - Chen family'
    },
    {
      id: 'user-005',
      firstName: 'Jennifer',
      lastName: 'Martinez',
      email: 'jennifer.martinez@cmz.org',
      phone: '(555) 400-0005',
      role: 'zookeeper',
      status: 'pending',
      createdDate: '2024-03-01',
      loginCount: 2,
      permissions: ['animal_details'],
      department: 'Animal Care',
      twoFactorEnabled: false,
      emailVerified: true,
      profileComplete: false,
      notes: 'New hire - pending full access approval'
    },
    {
      id: 'user-006',
      firstName: 'Robert',
      lastName: 'Kim',
      email: 'robert.kim@cmz.org',
      phone: '(555) 500-0006',
      role: 'zookeeper',
      status: 'suspended',
      createdDate: '2022-08-15',
      lastLogin: '2024-02-20T11:30:00Z',
      loginCount: 301,
      permissions: [],
      department: 'Animal Care',
      twoFactorEnabled: false,
      emailVerified: true,
      profileComplete: true,
      notes: 'Account suspended pending HR review'
    }
  ]);

  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<UserRole | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'pending' | 'suspended'>('all');

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (user.department && user.department.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'zookeeper': return 'bg-green-100 text-green-800';
      case 'educator': return 'bg-blue-100 text-blue-800';
      case 'member': return 'bg-purple-100 text-purple-800';
      case 'visitor': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'suspended': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const UserCard: React.FC<{ user: User }> = ({ user }) => (
    <div className="bg-white rounded-lg border hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mr-4">
              <Shield className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-900">{user.firstName} {user.lastName}</h3>
              <p className="text-sm text-gray-600">{user.email}</p>
              {user.department && <p className="text-xs text-gray-500">{user.department}</p>}
            </div>
          </div>
          <div className="text-right space-y-1">
            <div className="flex space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <p className="text-gray-600">Member Since</p>
            <p className="font-medium">{new Date(user.createdDate).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-gray-600">Login Count</p>
            <p className="font-medium">{user.loginCount}</p>
          </div>
          <div>
            <p className="text-gray-600">Last Login</p>
            <p className="font-medium">
              {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never'}
            </p>
          </div>
          <div>
            <p className="text-gray-600">2FA Status</p>
            <p className={`font-medium ${user.twoFactorEnabled ? 'text-green-600' : 'text-red-600'}`}>
              {user.twoFactorEnabled ? '✓ Enabled' : '✗ Disabled'}
            </p>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Permissions ({user.permissions.length})</p>
          <div className="flex flex-wrap gap-1">
            {user.permissions.slice(0, 3).map((permission, index) => (
              <span key={index} className="px-2 py-1 bg-indigo-50 text-indigo-700 text-xs rounded-full">
                {permission.replace('_', ' ')}
              </span>
            ))}
            {user.permissions.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                +{user.permissions.length - 3} more
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-1 mb-4">
          <div className={`w-2 h-2 rounded-full ${user.emailVerified ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-xs text-gray-600">Email Verified</span>
          <div className={`w-2 h-2 rounded-full ml-2 ${user.profileComplete ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
          <span className="text-xs text-gray-600">Profile Complete</span>
        </div>

        <div className="flex space-x-2">
          <button 
            onClick={() => setSelectedUser(user)}
            className="flex-1 flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Eye className="w-4 h-4 mr-2" />
            View Details
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Edit className="w-4 h-4" />
          </button>
          {user.status === 'active' ? (
            <button className="px-4 py-2 border border-orange-300 text-orange-600 rounded-lg hover:bg-orange-50 transition-colors">
              <UserX className="w-4 h-4" />
            </button>
          ) : user.status === 'suspended' ? (
            <button className="px-4 py-2 border border-green-300 text-green-600 rounded-lg hover:bg-green-50 transition-colors">
              <UserCheck className="w-4 h-4" />
            </button>
          ) : (
            <button className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );

  const UserDetailsModal: React.FC = () => {
    if (!selectedUser) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-lg flex items-center justify-center mr-4">
                  <Shield className="w-8 h-8 text-indigo-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedUser.firstName} {selectedUser.lastName}</h2>
                  <p className="text-gray-600">{selectedUser.email}</p>
                  <div className="flex space-x-2 mt-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(selectedUser.role)}`}>
                      {selectedUser.role.charAt(0).toUpperCase() + selectedUser.role.slice(1)}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedUser.status)}`}>
                      {selectedUser.status.charAt(0).toUpperCase() + selectedUser.status.slice(1)}
                    </span>
                  </div>
                </div>
              </div>
              <button 
                onClick={() => setSelectedUser(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Mail className="w-5 h-5 mr-2" />
                  Contact Information
                </h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">First Name</p>
                      <p className="font-medium">{selectedUser.firstName}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Last Name</p>
                      <p className="font-medium">{selectedUser.lastName}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Email Address</p>
                    <p className="font-medium">{selectedUser.email}</p>
                  </div>
                  {selectedUser.phone && (
                    <div>
                      <p className="text-sm text-gray-600">Phone Number</p>
                      <p className="font-medium">{selectedUser.phone}</p>
                    </div>
                  )}
                  {selectedUser.department && (
                    <div>
                      <p className="text-sm text-gray-600">Department</p>
                      <p className="font-medium">{selectedUser.department}</p>
                    </div>
                  )}
                </div>

                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">Account Status</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Account Status</p>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedUser.status)}`}>
                        {selectedUser.status.charAt(0).toUpperCase() + selectedUser.status.slice(1)}
                      </span>
                    </div>
                    <div>
                      <p className="text-gray-600">Email Verified</p>
                      <p className={`font-medium ${selectedUser.emailVerified ? 'text-green-600' : 'text-red-600'}`}>
                        {selectedUser.emailVerified ? '✓ Verified' : '✗ Not Verified'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Profile Complete</p>
                      <p className={`font-medium ${selectedUser.profileComplete ? 'text-green-600' : 'text-yellow-600'}`}>
                        {selectedUser.profileComplete ? '✓ Complete' : '⚠ Incomplete'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">2FA Enabled</p>
                      <p className={`font-medium ${selectedUser.twoFactorEnabled ? 'text-green-600' : 'text-red-600'}`}>
                        {selectedUser.twoFactorEnabled ? '✓ Enabled' : '✗ Disabled'}
                      </p>
                    </div>
                  </div>
                </div>

                {selectedUser.notes && (
                  <div className="mt-6">
                    <h4 className="font-medium text-gray-900 mb-2">Notes</h4>
                    <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
                      <p className="text-sm text-gray-700">{selectedUser.notes}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Permissions and Activity */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Key className="w-5 h-5 mr-2" />
                  Role & Permissions
                </h3>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">User Role</h4>
                    <span className={`inline-block px-3 py-2 rounded-lg text-sm font-medium ${getRoleColor(selectedUser.role)}`}>
                      {selectedUser.role.charAt(0).toUpperCase() + selectedUser.role.slice(1)}
                    </span>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Permissions ({selectedUser.permissions.length})</h4>
                    <div className="grid grid-cols-1 gap-2">
                      {selectedUser.permissions.length > 0 ? (
                        selectedUser.permissions.map((permission, index) => (
                          <div key={index} className="flex items-center p-2 bg-indigo-50 rounded-lg">
                            <Shield className="w-4 h-4 text-indigo-600 mr-2" />
                            <span className="text-sm font-medium text-indigo-800">
                              {permission.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-gray-500 italic">No permissions assigned</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      Activity Information
                    </h4>
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Created Date</p>
                          <p className="font-medium">{new Date(selectedUser.createdDate).toLocaleDateString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Total Logins</p>
                          <p className="font-medium">{selectedUser.loginCount}</p>
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600">Last Login</p>
                        <p className="font-medium">
                          {selectedUser.lastLogin ? (
                            <>
                              {new Date(selectedUser.lastLogin).toLocaleDateString()} at{' '}
                              {new Date(selectedUser.lastLogin).toLocaleTimeString()}
                            </>
                          ) : (
                            'Never logged in'
                          )}
                        </p>
                      </div>
                    </div>
                  </div>

                  {selectedUser.role === 'admin' && (
                    <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                      <div className="flex items-center">
                        <Shield className="w-5 h-5 text-red-600 mr-2" />
                        <div>
                          <h4 className="font-medium text-red-800">Administrator Account</h4>
                          <p className="text-sm text-red-700 mt-1">
                            This user has full system administrative privileges. Use caution when modifying permissions.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {selectedUser.status === 'pending' && (
                    <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                      <div className="flex items-center">
                        <Calendar className="w-5 h-5 text-yellow-600 mr-2" />
                        <div>
                          <h4 className="font-medium text-yellow-800">Pending Approval</h4>
                          <p className="text-sm text-yellow-700 mt-1">
                            This account is pending approval. Consider reviewing and activating if appropriate.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 border-t bg-gray-50 flex space-x-3">
            <button
              onClick={() => setSelectedUser(null)}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            <button className="flex-1 flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
              <Edit className="w-4 h-4 mr-2" />
              Edit User
            </button>
            {selectedUser.status === 'active' ? (
              <button className="flex-1 flex items-center justify-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
                <UserX className="w-4 h-4 mr-2" />
                Suspend User
              </button>
            ) : selectedUser.status === 'suspended' ? (
              <button className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                <UserCheck className="w-4 h-4 mr-2" />
                Activate User
              </button>
            ) : null}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage user accounts, roles, and system access</p>
        </div>
        <button 
          onClick={() => setShowAddUser(true)}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add New User
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <UserCheck className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Users</p>
              <p className="text-xl font-semibold text-gray-900">{users.filter(u => u.status === 'active').length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
              <Calendar className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-xl font-semibold text-gray-900">{users.filter(u => u.status === 'pending').length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
              <UserX className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Suspended</p>
              <p className="text-xl font-semibold text-gray-900">{users.filter(u => u.status === 'suspended').length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <Shield className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">2FA Enabled</p>
              <p className="text-xl font-semibold text-gray-900">{users.filter(u => u.twoFactorEnabled).length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="flex flex-col lg:flex-row gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search users by name, email, or department..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select 
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as UserRole | 'all')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Roles</option>
              <option value="admin">Administrator</option>
              <option value="zookeeper">Zookeeper</option>
              <option value="educator">Educator</option>
              <option value="member">Member</option>
              <option value="visitor">Visitor</option>
            </select>
          </div>
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive' | 'pending' | 'suspended')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
            <option value="suspended">Suspended</option>
          </select>
          <div className="text-sm text-gray-600">
            {filteredUsers.length} of {users.length} users
          </div>
        </div>
      </div>

      {/* Users Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredUsers.map(user => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>

      {filteredUsers.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}

      <UserDetailsModal />
    </div>
  );
};

export default UserManagement;
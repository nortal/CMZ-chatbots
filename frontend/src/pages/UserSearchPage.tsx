import React from 'react';
import UserSearch from '../components/UserSearch';

/**
 * User Search Page
 *
 * Admin and staff page for searching users across the CMZ platform.
 * Provides comprehensive filtering by name, age, role, and visit history.
 *
 * Route: /users/search or /admin/user-search
 * Requires: Admin or appropriate staff role
 */
const UserSearchPage: React.FC = () => {
  return <UserSearch />;
};

export default UserSearchPage;

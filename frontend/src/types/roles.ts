export type UserRole = 'admin' | 'zookeeper' | 'educator' | 'member' | 'visitor';

export interface User {
  userId: string;
  email: string;
  displayName: string;
  role: UserRole;
  created: {
    at: string;
    by: {
      userId: string;
      email: string;
      displayName: string;
    };
  };
  modified: {
    at: string;
    by: {
      userId: string;
      email: string;
      displayName: string;
    };
  };
  softDelete: boolean;
}

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon?: string;
  roles: UserRole[];
  children?: NavigationItem[];
}

// Role-based access control
export const roleHierarchy: Record<UserRole, number> = {
  admin: 5,
  zookeeper: 4, 
  educator: 3,
  member: 2,
  visitor: 1
};

export const hasAccess = (userRole: UserRole, requiredRoles: UserRole[]): boolean => {
  return requiredRoles.includes(userRole);
};

export const hasMinimumRole = (userRole: UserRole, minimumRole: UserRole): boolean => {
  return roleHierarchy[userRole] >= roleHierarchy[minimumRole];
};
import { NavigationItem, UserRole } from '../types/roles';

export const navigationConfig: NavigationItem[] = [
  // Dashboard - Available to all authenticated users (optional for public users)
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: 'Home',
    roles: ['admin', 'zookeeper', 'educator', 'member', 'visitor', 'parent', 'student']
  },

  // Animal Management - Core zoo operations
  {
    id: 'animals',
    label: 'Animal Management',
    path: '/animals',
    icon: 'Zap', // Represents animal/wildlife
    roles: ['admin', 'zookeeper', 'educator'],
    children: [
      {
        id: 'animal-config',
        label: 'Chatbot Personalities',
        path: '/animals/config',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'animal-details',
        label: 'Animal Details',
        path: '/animals/details',
        roles: ['admin', 'zookeeper', 'educator']
      }
    ]
  },

  // Family & Education Management
  {
    id: 'families',
    label: 'Family Groups',
    path: '/families',
    icon: 'Users',
    roles: ['admin', 'educator'],
    children: [
      {
        id: 'family-management',
        label: 'Manage Families',
        path: '/families/manage',
        roles: ['admin', 'educator']
      },
      {
        id: 'family-billing',
        label: 'Billing Information', 
        path: '/families/billing',
        roles: ['admin']
      },
      {
        id: 'educational-programs',
        label: 'Educational Programs',
        path: '/families/programs',
        roles: ['admin', 'educator']
      }
    ]
  },

  // Conversations & Chat Management - Available to all users with role-specific children
  {
    id: 'conversations',
    label: 'Conversations',
    path: '/conversations',
    icon: 'MessageCircle',
    roles: ['admin', 'zookeeper', 'educator', 'member', 'visitor', 'parent', 'student'],
    children: [
      {
        id: 'animal-ambassadors',
        label: 'Chat with Animals',
        path: '/animals',
        roles: ['admin', 'zookeeper', 'educator', 'member', 'visitor', 'parent', 'student']
      },
      {
        id: 'active-chat',
        label: 'Active Chat',
        path: '/chat',
        roles: ['admin', 'zookeeper', 'educator', 'member', 'visitor', 'parent', 'student']
      },
      {
        id: 'conversation-history',
        label: 'Chat History',
        path: '/conversations/history',
        roles: ['admin', 'zookeeper', 'educator']
      },
      {
        id: 'conversation-analytics',
        label: 'Chat Analytics',
        path: '/conversations/analytics',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'chat-search',
        label: 'Search Conversations',
        path: '/conversations/search',
        roles: ['admin']
      }
    ]
  },

  // Knowledge Base Management
  {
    id: 'knowledge',
    label: 'Knowledge Base',
    path: '/knowledge',
    icon: 'Book',
    roles: ['admin', 'zookeeper', 'educator'],
    children: [
      {
        id: 'knowledge-content',
        label: 'Manage Content',
        path: '/knowledge/content',
        roles: ['admin', 'zookeeper', 'educator']
      },
      {
        id: 'knowledge-prompts',
        label: 'System Prompts',
        path: '/knowledge/prompts',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'knowledge-guardrails',
        label: 'Guardrails',
        path: '/knowledge/guardrails',
        roles: ['admin']
      }
    ]
  },

  // User Management - Admin only
  {
    id: 'users',
    label: 'User Management',
    path: '/users',
    icon: 'UserCog',
    roles: ['admin'],
    children: [
      {
        id: 'user-accounts',
        label: 'User Accounts',
        path: '/users/accounts',
        roles: ['admin']
      },
      {
        id: 'user-roles',
        label: 'Roles & Permissions',
        path: '/users/roles',
        roles: ['admin']
      },
      {
        id: 'user-search',
        label: 'Search Users',
        path: '/users/search',
        roles: ['admin']
      }
    ]
  },

  // Analytics & Reporting
  {
    id: 'analytics',
    label: 'Analytics',
    path: '/analytics',
    icon: 'BarChart3',
    roles: ['admin', 'zookeeper'],
    children: [
      {
        id: 'usage-analytics',
        label: 'Usage Reports',
        path: '/analytics/usage',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'performance-metrics',
        label: 'Performance Metrics',
        path: '/analytics/performance',
        roles: ['admin']
      },
      {
        id: 'visitor-insights',
        label: 'Visitor Insights',
        path: '/analytics/visitors',
        roles: ['admin', 'zookeeper']
      }
    ]
  },

  // System Administration
  {
    id: 'system',
    label: 'System',
    path: '/system',
    icon: 'Settings',
    roles: ['admin'],
    children: [
      {
        id: 'system-health',
        label: 'System Health',
        path: '/system/health',
        roles: ['admin']
      },
      {
        id: 'system-logs',
        label: 'System Logs',
        path: '/system/logs',
        roles: ['admin']
      },
      {
        id: 'system-config',
        label: 'Configuration',
        path: '/system/config',
        roles: ['admin']
      },
      {
        id: 'system-backup',
        label: 'Backup & Recovery',
        path: '/system/backup',
        roles: ['admin']
      }
    ]
  },

  // Public/Visitor Portal
  {
    id: 'portal',
    label: 'Visitor Portal',
    path: '/portal',
    icon: 'Globe',
    roles: ['member', 'visitor'],
    children: [
      {
        id: 'chat-with-animals',
        label: 'Chat with Animals',
        path: '/portal/chat',
        roles: ['member', 'visitor']
      },
      {
        id: 'my-conversations',
        label: 'My Conversations',
        path: '/portal/conversations',
        roles: ['member']
      },
      {
        id: 'zoo-information',
        label: 'Zoo Information',
        path: '/portal/info',
        roles: ['member', 'visitor']
      }
    ]
  }
];

// Helper functions for navigation filtering
export const getNavigationForRole = (userRole: UserRole): NavigationItem[] => {
  return navigationConfig.filter(item => item.roles.includes(userRole))
    .map(item => ({
      ...item,
      children: item.children?.filter(child => child.roles.includes(userRole))
    }));
};

export const getAccessiblePaths = (userRole: UserRole): string[] => {
  const paths: string[] = [];
  
  navigationConfig.forEach(item => {
    if (item.roles.includes(userRole)) {
      paths.push(item.path);
      if (item.children) {
        item.children.forEach(child => {
          if (child.roles.includes(userRole)) {
            paths.push(child.path);
          }
        });
      }
    }
  });
  
  return paths;
};
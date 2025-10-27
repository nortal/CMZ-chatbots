import { NavigationItem, UserRole } from '../types/roles';

export const navigationConfig: NavigationItem[] = [
  // Dashboard - Simplified for MVP
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: 'Home',
    roles: ['admin', 'zookeeper', 'educator', 'member', 'visitor', 'parent', 'student']
  },

  // Animal Management - Core zoo operations with Guardrails
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
      },
      {
        id: 'animal-guardrails',
        label: 'Guardrails',
        path: '/animals/guardrails',
        roles: ['admin']
      }
    ]
  },

  // Animal Assistant Management - New feature from Phase 2
  {
    id: 'assistants',
    label: 'Assistant Management',
    path: '/assistants',
    icon: 'Bot', // Represents AI assistants
    roles: ['admin', 'zookeeper'],
    children: [
      {
        id: 'assistant-overview',
        label: 'Active Assistants',
        path: '/assistants/overview',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'assistant-create',
        label: 'Create Assistant',
        path: '/assistants/create',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'personality-templates',
        label: 'Personality Templates',
        path: '/assistants/personalities',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'guardrail-templates',
        label: 'Guardrail Templates',
        path: '/assistants/guardrails',
        roles: ['admin']
      },
      {
        id: 'sandbox-testing',
        label: 'Test Configurations',
        path: '/sandbox-testing',
        roles: ['admin', 'zookeeper']
      },
      {
        id: 'knowledge-base',
        label: 'Knowledge Base',
        path: '/assistants/knowledge',
        roles: ['admin', 'zookeeper']
      }
    ]
  },

  // Family Management - Simplified (removed billing and programs)
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
      }
    ]
  },

  // Conversations - Simplified
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
      }
    ]
  },

  // System - AI Provider Settings and Safety Management
  {
    id: 'system',
    label: 'System',
    path: '/system',
    icon: 'Settings',
    roles: ['admin'],
    children: [
      {
        id: 'ai-provider',
        label: 'AI Provider Settings',
        path: '/system/ai-provider',
        roles: ['admin']
      },
      {
        id: 'safety-management',
        label: 'Safety Management',
        path: '/system/safety',
        roles: ['admin']
      }
    ]
  },

  // Public/Visitor Portal - Simplified
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
import React, { useState } from 'react';
import { 
  Home, 
  Zap, 
  Users, 
  MessageCircle, 
  Book, 
  UserCog, 
  BarChart3, 
  Settings, 
  Globe,
  ChevronDown,
  ChevronRight,
  LogOut
} from 'lucide-react';
import { NavigationItem, User } from '../../types/roles';
import { getNavigationForRole } from '../../config/navigation';

interface SidebarProps {
  user: User;
  onNavigate: (path: string) => void;
  onLogout: () => void;
  currentPath: string;
}

const iconMap = {
  Home,
  Zap,
  Users,
  MessageCircle,
  Book,
  UserCog,
  BarChart3,
  Settings,
  Globe
};

const Sidebar: React.FC<SidebarProps> = ({ user, onNavigate, onLogout, currentPath }) => {
  const [expandedItems, setExpandedItems] = useState<string[]>(['dashboard']);
  const navigation = getNavigationForRole(user.role);

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const isActive = (path: string) => currentPath === path;
  const isParentActive = (item: NavigationItem) => {
    if (isActive(item.path)) return true;
    return item.children?.some(child => isActive(child.path)) || false;
  };

  const renderNavItem = (item: NavigationItem, level: number = 0) => {
    const Icon = item.icon ? iconMap[item.icon as keyof typeof iconMap] : null;
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.includes(item.id);
    const active = isParentActive(item);

    return (
      <div key={item.id} className="mb-1">
        <button
          onClick={() => {
            if (hasChildren) {
              toggleExpanded(item.id);
            } else {
              onNavigate(item.path);
            }
          }}
          className={`
            w-full flex items-center px-3 py-2.5 text-left rounded-lg transition-colors
            ${active 
              ? 'bg-green-100 text-green-800 border-l-4 border-green-600' 
              : 'text-gray-700 hover:bg-gray-100'
            }
            ${level > 0 ? 'ml-4 text-sm' : 'font-medium'}
          `}
          style={{ paddingLeft: `${12 + (level * 16)}px` }}
        >
          {Icon && <Icon size={level > 0 ? 16 : 18} className="mr-3 flex-shrink-0" />}
          <span className="flex-1">{item.label}</span>
          {hasChildren && (
            isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
          )}
        </button>

        {hasChildren && isExpanded && (
          <div className="mt-1">
            {item.children!.map(child => renderNavItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const getRoleDisplayName = (role: string) => {
    return role.charAt(0).toUpperCase() + role.slice(1);
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'zookeeper': return 'bg-green-100 text-green-800';
      case 'educator': return 'bg-blue-100 text-blue-800';
      case 'member': return 'bg-purple-100 text-purple-800';
      case 'visitor': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div 
      className="h-screen flex flex-col"
      style={{ 
        width: '280px', 
        backgroundColor: '#f9fafb',
        borderRight: '1px solid #e5e7eb'
      }}
    >
      {/* Header */}
      <div 
        className="p-6 border-b"
        style={{ 
          background: 'linear-gradient(135deg, #2d5a3d 0%, #3d6b4d 100%)',
          color: 'white'
        }}
      >
        <div className="flex items-center mb-3">
          <img 
            src="/cmz-logo.png" 
            alt="CMZ"
            className="h-8 w-auto mr-3"
          />
          <span className="font-semibold text-lg">CMZ Dashboard</span>
        </div>
        <div className="text-sm opacity-90">
          Welcome back, <span className="font-medium">{user.displayName}</span>
        </div>
        <div className="mt-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
            {getRoleDisplayName(user.role)}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto">
        {navigation.map(item => renderNavItem(item))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t bg-white">
        <button
          onClick={onLogout}
          className="w-full flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <LogOut size={18} className="mr-3" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
import React from 'react';
import { Bell, Search, Menu } from 'lucide-react';
import { User } from '../../types/roles';

interface TopBarProps {
  user: User;
  currentPageTitle: string;
  onMenuToggle?: () => void;
  showMenuToggle?: boolean;
}

const TopBar: React.FC<TopBarProps> = ({ 
  user, 
  currentPageTitle, 
  onMenuToggle, 
  showMenuToggle = false 
}) => {
  return (
    <div 
      className="h-16 flex items-center justify-between px-6 bg-white border-b"
      style={{ borderColor: '#e5e7eb' }}
    >
      <div className="flex items-center">
        {showMenuToggle && (
          <button
            onClick={onMenuToggle}
            className="p-2 hover:bg-gray-100 rounded-lg mr-4 lg:hidden"
          >
            <Menu size={20} />
          </button>
        )}
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            {currentPageTitle}
          </h1>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative hidden md:block">
          <Search 
            size={18} 
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
          />
          <input
            type="text"
            placeholder="Search..."
            className="pl-10 pr-4 py-2 w-64 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 hover:bg-gray-100 rounded-lg">
          <Bell size={20} className="text-gray-600" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* User Profile */}
        <div className="flex items-center space-x-3">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-medium text-gray-900">
              {user.displayName}
            </div>
            <div className="text-xs text-gray-500 capitalize">
              {user.role}
            </div>
          </div>
          <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">
              {user.displayName.charAt(0).toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
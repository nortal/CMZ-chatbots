import React, { useState } from 'react';
import { User } from '../../types/roles';
import Sidebar from '../navigation/Sidebar';
import TopBar from '../navigation/TopBar';

interface DashboardLayoutProps {
  user: User;
  children: React.ReactNode;
  currentPath: string;
  currentPageTitle: string;
  onNavigate: (path: string) => void;
  onLogout: () => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  user,
  children,
  currentPath,
  currentPageTitle,
  onNavigate,
  onLogout
}) => {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const handleMenuToggle = () => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar 
          user={user}
          onNavigate={onNavigate}
          onLogout={onLogout}
          currentPath={currentPath}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isMobileSidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div 
            className="fixed inset-0 bg-black opacity-50"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
          <div className="relative">
            <Sidebar 
              user={user}
              onNavigate={(path) => {
                onNavigate(path);
                setIsMobileSidebarOpen(false);
              }}
              onLogout={onLogout}
              currentPath={currentPath}
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar 
          user={user}
          currentPageTitle={currentPageTitle}
          onMenuToggle={handleMenuToggle}
          showMenuToggle={true}
        />
        
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
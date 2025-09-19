import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import DashboardLayout from './components/layout/DashboardLayout';
import CMZLoginPage from './components/auth/CMZLoginPage';
import Dashboard from './pages/Dashboard';
import AnimalConfig from './pages/AnimalConfig';
import AnimalDetails from './pages/AnimalDetails';
import FamilyManagement from './pages/FamilyManagement';
import UserManagement from './pages/UserManagement';
import TestFamilyModalEnhanced from './pages/TestFamilyModalEnhanced';
import Chat from './pages/Chat';
import ChatHistory from './pages/ChatHistory';
import ConversationViewer from './pages/ConversationViewer';
import PublicAnimalList from './pages/PublicAnimalList';
import './index.css';

const AppRoutes: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getPageTitle = (pathname: string): string => {
    switch (pathname) {
      case '/dashboard': return 'Dashboard';
      case '/animals': return 'Animal Ambassadors';
      case '/animals/config': return 'Animal Configuration';
      case '/animals/details': return 'Animal Details';
      case '/families/manage': return 'Family Management';
      case '/chat': return 'Chat with Animals';
      case '/conversations/history': return 'Conversation History';
      case '/users/accounts': return 'User Management';
      case '/analytics/usage': return 'Usage Analytics';
      case '/system/health': return 'System Health';
      default: return 'CMZ Dashboard';
    }
  };

  // Helper function to determine landing page based on user role
  const getRoleLandingPage = (userRole: string): string => {
    switch(userRole) {
      case 'admin':
      case 'zookeeper':
        return '/dashboard';
      case 'parent':
      case 'student':
      case 'visitor':
      default:
        return '/animals';
    }
  };

  return (
    <Routes>
      <Route path="/login" element={<CMZLoginPage />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <Navigate to={getRoleLandingPage(user?.role || 'visitor')} replace />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <Dashboard />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/animals/config" element={
        <ProtectedRoute requiredRoles={['admin', 'zookeeper']}>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <AnimalConfig />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/animals" element={
        <ProtectedRoute>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <PublicAnimalList />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/chat" element={
        <ProtectedRoute>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <Chat />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/conversations/history" element={
        <ProtectedRoute>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <ChatHistory />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/conversations/:sessionId" element={
        <ProtectedRoute>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle="Conversation Viewer"
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <ConversationViewer />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      {/* Test route for Enhanced Family Modal */}
      <Route path="/test/family-modal" element={<TestFamilyModalEnhanced />} />

      {/* Placeholder routes - to be implemented */}
      <Route path="/animals/details" element={
        <ProtectedRoute requiredRoles={['admin', 'zookeeper', 'educator']}>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <AnimalDetails />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/families/manage" element={
        <ProtectedRoute requiredRoles={['admin', 'educator']}>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <FamilyManagement />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/users/accounts" element={
        <ProtectedRoute requiredRoles={['admin']}>
          <DashboardLayout
            user={user!}
            currentPath={location.pathname}
            currentPageTitle={getPageTitle(location.pathname)}
            onNavigate={handleNavigate}
            onLogout={handleLogout}
          >
            <UserManagement />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      {/* Catch all route - redirects based on user role */}
      <Route path="*" element={
        <ProtectedRoute>
          <Navigate to={getRoleLandingPage(user?.role || 'visitor')} replace />
        </ProtectedRoute>
      } />
    </Routes>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
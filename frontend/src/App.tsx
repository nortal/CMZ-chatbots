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
      case '/animals/config': return 'Animal Configuration';
      case '/animals/details': return 'Animal Details';
      case '/families/manage': return 'Family Management';
      case '/conversations/history': return 'Conversation History';
      case '/users/accounts': return 'User Management';
      case '/analytics/usage': return 'Usage Analytics';
      case '/system/health': return 'System Health';
      default: return 'CMZ Dashboard';
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
            <Navigate to="/dashboard" replace />
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

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
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
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types/roles';
import { authApi } from '../services/api';
import { getUserFromToken, isTokenExpired } from '../utils/jwt';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing auth on mount
    const token = localStorage.getItem('cmz_token');
    
    if (token) {
      try {
        // Check if token is expired
        if (isTokenExpired(token)) {
          // Token expired, clear it
          localStorage.removeItem('cmz_token');
          localStorage.removeItem('cmz_user');
        } else {
          // Token is valid, decode user information
          const userInfo = getUserFromToken(token);
          if (userInfo) {
            // Convert JWT user info to our User type
            const user: User = {
              userId: userInfo.userId,
              email: userInfo.email,
              role: userInfo.role,
              displayName: userInfo.displayName,
              created: {
                at: new Date().toISOString(),
                by: {
                  userId: 'system',
                  email: 'system@cmz.org',
                  displayName: 'System'
                }
              },
              modified: {
                at: new Date().toISOString(),
                by: {
                  userId: userInfo.userId,
                  email: userInfo.email,
                  displayName: userInfo.displayName
                }
              },
              softDelete: false
            };
            setUser(user);
          } else {
            // Invalid token, clear it
            localStorage.removeItem('cmz_token');
            localStorage.removeItem('cmz_user');
          }
        }
      } catch (error) {
        // Clear invalid data
        localStorage.removeItem('cmz_token');
        localStorage.removeItem('cmz_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    
    try {
      // Call the real API
      const response = await authApi.login(email, password);
      const { token } = response;
      
      // Decode user information from the JWT token
      const userInfo = getUserFromToken(token);
      if (!userInfo) {
        throw new Error('Invalid token received from server');
      }
      
      // Convert JWT user info to our User type
      const user: User = {
        userId: userInfo.userId,
        email: userInfo.email,
        role: userInfo.role,
        displayName: userInfo.displayName,
        created: {
          at: new Date().toISOString(),
          by: {
            userId: 'system',
            email: 'system@cmz.org',
            displayName: 'System'
          }
        },
        modified: {
          at: new Date().toISOString(),
          by: {
            userId: userInfo.userId,
            email: userInfo.email,
            displayName: userInfo.displayName
          }
        },
        softDelete: false
      };
      
      // Store auth data
      localStorage.setItem('cmz_token', token);
      localStorage.setItem('cmz_user', JSON.stringify(user));
      setUser(user);
    } catch (error) {
      // Let the error bubble up to the login form
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('cmz_token');
    localStorage.removeItem('cmz_user');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
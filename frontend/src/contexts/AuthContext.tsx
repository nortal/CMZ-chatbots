import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types/roles';

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
    const savedUser = localStorage.getItem('cmz_user');
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
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
      // Mock authentication for development/testing
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
      
      // Mock user data based on email
      const mockUsers = {
        'admin@cmz.org': {
          userId: '1',
          email: 'admin@cmz.org',
          role: 'admin' as const,
          displayName: 'John Administrator',
          created: {
            at: '2023-01-01T00:00:00Z',
            by: {
              userId: 'system',
              email: 'system@cmz.org',
              displayName: 'System'
            }
          },
          modified: {
            at: new Date().toISOString(),
            by: {
              userId: '1',
              email: 'admin@cmz.org',
              displayName: 'John Administrator'
            }
          },
          softDelete: false
        },
        'zookeeper@cmz.org': {
          userId: '2',
          email: 'zookeeper@cmz.org',
          role: 'zookeeper' as const,
          displayName: 'Sarah Johnson (Zookeeper)',
          created: {
            at: '2023-03-01T00:00:00Z',
            by: {
              userId: '1',
              email: 'admin@cmz.org',
              displayName: 'John Administrator'
            }
          },
          modified: {
            at: new Date().toISOString(),
            by: {
              userId: '2',
              email: 'zookeeper@cmz.org',
              displayName: 'Sarah Johnson (Zookeeper)'
            }
          },
          softDelete: false
        },
        'educator@cmz.org': {
          userId: '3',
          email: 'educator@cmz.org',
          role: 'educator' as const,
          displayName: 'Maria Rodriguez (Educator)',
          created: {
            at: '2023-05-01T00:00:00Z',
            by: {
              userId: '1',
              email: 'admin@cmz.org',
              displayName: 'John Administrator'
            }
          },
          modified: {
            at: new Date().toISOString(),
            by: {
              userId: '3',
              email: 'educator@cmz.org',
              displayName: 'Maria Rodriguez (Educator)'
            }
          },
          softDelete: false
        },
        'member@cmz.org': {
          userId: '4',
          email: 'member@cmz.org',
          role: 'member' as const,
          displayName: 'John Member',
          created: {
            at: '2023-11-01T00:00:00Z',
            by: {
              userId: 'system',
              email: 'system@cmz.org',
              displayName: 'System'
            }
          },
          modified: {
            at: new Date().toISOString(),
            by: {
              userId: '4',
              email: 'member@cmz.org',
              displayName: 'John Member'
            }
          },
          softDelete: false
        },
        'visitor@cmz.org': {
          userId: '5',
          email: 'visitor@cmz.org',
          role: 'visitor' as const,
          displayName: 'Jane Visitor',
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
              userId: '5',
              email: 'visitor@cmz.org',
              displayName: 'Jane Visitor'
            }
          },
          softDelete: false
        }
      };

      const user = mockUsers[email as keyof typeof mockUsers];
      
      if (!user) {
        throw new Error('Invalid credentials');
      }

      const mockToken = 'mock-jwt-token-' + Date.now();
      
      // Store auth data
      localStorage.setItem('cmz_token', mockToken);
      localStorage.setItem('cmz_user', JSON.stringify(user));
      setUser(user);
    } catch (error) {
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
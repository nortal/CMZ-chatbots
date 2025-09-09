import React, { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

interface LoginFormData {
  email: string;
  password: string;
}

interface LoginFormErrors {
  email?: string;
  password?: string;
  general?: string;
}

const CMZLoginPage = () => {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<LoginFormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, authLoading, navigate, location]);

  const validateForm = (): boolean => {
    const newErrors: LoginFormErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    try {
      await login(formData.email, formData.password);
      // Navigation is handled by useEffect above
    } catch (error) {
      setErrors({
        general: 'Invalid email or password. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof LoginFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value,
    }));
    
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f5f1eb',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        maxWidth: '480px',
        width: '100%',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #2d5a3d 0%, #3d6b4d 100%)',
          color: 'white',
          padding: '32px',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '16px' }}>
            <img 
              src="/cmz-logo.png" 
              alt="Cougar Mountain Zoo"
              style={{ height: '64px', width: 'auto', margin: '0 auto', display: 'block' }}
              onError={(e) => {
                // Fallback if image doesn't load
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling!.style.display = 'flex';
              }}
            />
            <div style={{ 
              display: 'none', 
              width: '64px', 
              height: '64px', 
              backgroundColor: 'rgba(255,255,255,0.2)', 
              borderRadius: '8px',
              margin: '0 auto',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: 'bold'
            }}>
              CMZ
            </div>
          </div>
          <h1 style={{ margin: '0', fontSize: '28px', fontWeight: '600', letterSpacing: '-0.5px' }}>
            Animal Config Dashboard
          </h1>
          <p style={{ margin: '8px 0 0 0', opacity: '0.9', fontSize: '16px' }}>
            Sign in to access your zoo management tools
          </p>
        </div>

        {/* Form */}
        <div style={{ padding: '32px' }}>
          <form onSubmit={handleSubmit}>
            {errors.general && (
              <div style={{
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '6px',
                padding: '12px 16px',
                marginBottom: '20px',
                color: '#dc2626',
                fontSize: '14px'
              }}>
                {errors.general}
              </div>
            )}

            {/* Email Field */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#1a1a1a',
                fontWeight: '500',
                fontSize: '14px'
              }}>
                Email Address
              </label>
              <input
                type="email"
                placeholder="Enter your email address"
                value={formData.email}
                onChange={handleInputChange('email')}
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: errors.email ? '2px solid #dc2626' : '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '16px',
                  transition: 'all 0.2s ease',
                  backgroundColor: 'white',
                  boxSizing: 'border-box',
                  outline: 'none'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#2d5a3d';
                  e.target.style.boxShadow = '0 0 0 3px rgba(45, 90, 61, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = errors.email ? '#dc2626' : '#e5e7eb';
                  e.target.style.boxShadow = 'none';
                }}
              />
              {errors.email && (
                <div style={{ color: '#dc2626', fontSize: '14px', marginTop: '6px' }}>
                  {errors.email}
                </div>
              )}
            </div>

            {/* Password Field */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#1a1a1a',
                fontWeight: '500',
                fontSize: '14px'
              }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange('password')}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    padding: '12px 48px 12px 16px',
                    border: errors.password ? '2px solid #dc2626' : '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    transition: 'all 0.2s ease',
                    backgroundColor: 'white',
                    boxSizing: 'border-box',
                    outline: 'none'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#2d5a3d';
                    e.target.style.boxShadow = '0 0 0 3px rgba(45, 90, 61, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = errors.password ? '#dc2626' : '#e5e7eb';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: '#666',
                    cursor: 'pointer',
                    padding: '4px'
                  }}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <div style={{ color: '#dc2626', fontSize: '14px', marginTop: '6px' }}>
                  {errors.password}
                </div>
              )}
            </div>

            {/* Remember Me & Forgot Password */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              marginBottom: '24px',
              fontSize: '14px'
            }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ marginRight: '8px' }}
                />
                Remember me
              </label>
              
              <button
                type="button"
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#2d5a3d',
                  cursor: 'pointer',
                  textDecoration: 'none',
                  fontWeight: '500'
                }}
                onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
              >
                Forgot password?
              </button>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                background: '#2d5a3d',
                color: 'white',
                border: 'none',
                padding: '14px 24px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                marginBottom: '24px',
                opacity: isLoading ? 0.7 : 1
              }}
              onMouseEnter={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.background = '#1f3f2a';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(45, 90, 61, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.background = '#2d5a3d';
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.boxShadow = 'none';
                }
              }}
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Footer */}
          <div style={{
            textAlign: 'center',
            borderTop: '1px solid #e5e7eb',
            paddingTop: '20px'
          }}>
            <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
              Need help?{' '}
              <button
                type="button"
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#2d5a3d',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
                onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
              >
                Contact your system administrator
              </button>
            </p>
          </div>
        </div>
      </div>

      {/* Copyright */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        textAlign: 'center',
        fontSize: '14px',
        color: '#666'
      }}>
        © 2024 Cougar Mountain Zoo. All rights reserved.
      </div>
    </div>
  );
};

export default CMZLoginPage;
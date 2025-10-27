/**
 * JWT Token Utilities
 */

export interface JWTPayload {
  user_id: string;
  email: string;
  role: string;
  user_type: string;
  exp: number;
  iat: number;
}

/**
 * Decode JWT token without verification (client-side only)
 * Note: This is for extracting user info, not for security validation
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    // JWT has 3 parts: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];
    
    // Add padding if needed for base64 decoding
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    
    // Decode base64
    const decodedPayload = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
    
    // Parse JSON
    return JSON.parse(decodedPayload) as JWTPayload;
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
}

/**
 * Check if JWT token is expired
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload) {
    return true;
  }

  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
}

/**
 * Get user info from JWT token
 */
export function getUserFromToken(token: string) {
  const payload = decodeJWT(token);
  if (!payload) {
    return null;
  }

  return {
    userId: payload.user_id,
    email: payload.email,
    role: payload.role as 'admin' | 'keeper' | 'parent' | 'member',
    userType: payload.user_type,
    displayName: getDisplayNameFromEmail(payload.email, payload.role)
  };
}

/**
 * Generate display name from email and role
 */
function getDisplayNameFromEmail(email: string, role: string): string {
  const emailPart = email.split('@')[0];
  const roleName = role === 'keeper' ? 'Zookeeper' : 
                  role === 'parent' ? 'Parent' :
                  role === 'admin' ? 'Administrator' : 'Member';
  
  return `${emailPart.charAt(0).toUpperCase() + emailPart.slice(1)} (${roleName})`;
}
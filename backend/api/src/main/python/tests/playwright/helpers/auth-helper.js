/**
 * Authentication Helper for Playwright Tests
 * Provides reusable JWT authentication functions for E2E tests
 */

/**
 * Test user credentials
 */
export const TEST_USERS = {
    admin: {
        username: 'test@cmz.org',
        password: 'testpass123',
        role: 'admin',
        name: 'Test User'
    },
    parent1: {
        username: 'parent1@test.cmz.org',
        password: 'testpass123',
        role: 'parent',
        name: 'Test Parent One'
    },
    student1: {
        username: 'student1@test.cmz.org',
        password: 'testpass123',
        role: 'student',
        name: 'Test Student One'
    },
    student2: {
        username: 'student2@test.cmz.org',
        password: 'testpass123',
        role: 'student',
        name: 'Test Student Two'
    },
    parentUser: {
        username: 'user_parent_001@cmz.org',
        password: 'testpass123',
        role: 'parent',
        name: 'Parent User 001'
    }
};

/**
 * Login and get JWT token
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} username - User email/username
 * @param {string} password - User password
 * @returns {Promise<{token: string, user: object}>} Auth data with JWT token
 */
export async function loginAndGetToken(page, username, password) {
    const loginResponse = await page.request.post('http://localhost:8080/auth', {
        data: { username, password },
        headers: { 'Content-Type': 'application/json' }
    });

    if (loginResponse.status() !== 200) {
        const error = await loginResponse.json().catch(() => ({}));
        throw new Error(`Login failed: ${loginResponse.status()} - ${JSON.stringify(error)}`);
    }

    const authData = await loginResponse.json();
    if (!authData.token) {
        throw new Error('No token received from login');
    }

    return authData;
}

/**
 * Get authentication headers with JWT token
 * @param {string} token - JWT token
 * @returns {object} Headers object with Authorization
 */
export function getAuthHeaders(token) {
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

/**
 * Login as a test user and get auth headers
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} userType - User type key from TEST_USERS (e.g., 'admin', 'parent1')
 * @returns {Promise<{token: string, headers: object, user: object}>} Auth data and headers
 */
export async function loginAsUser(page, userType = 'admin') {
    const user = TEST_USERS[userType];
    if (!user) {
        throw new Error(`Unknown user type: ${userType}. Available: ${Object.keys(TEST_USERS).join(', ')}`);
    }

    const authData = await loginAndGetToken(page, user.username, user.password);
    const headers = getAuthHeaders(authData.token);

    return {
        token: authData.token,
        headers,
        user: authData.user
    };
}

/**
 * Make authenticated API request
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} method - HTTP method (GET, POST, PUT, PATCH, DELETE)
 * @param {string} url - API endpoint URL
 * @param {string} token - JWT token
 * @param {object} options - Additional request options (data, params, etc.)
 * @returns {Promise<Response>} Playwright API response
 */
export async function authenticatedRequest(page, method, url, token, options = {}) {
    const headers = {
        ...getAuthHeaders(token),
        ...options.headers
    };

    return await page.request[method.toLowerCase()](url, {
        ...options,
        headers
    });
}

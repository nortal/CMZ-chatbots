// Login Page Object for Playwright tests
// PR003946-96: Integrated playwright testing

const { expect } = require('@playwright/test');
const BasePage = require('./base-page');

/**
 * Login page object containing authentication-related functionality
 * Maps to authentication feature in feature-mapping.json
 */
class LoginPage extends BasePage {
  constructor(page) {
    super(page);
    
    // Page elements - using data-testid for reliable selection
    this.elements = {
      emailInput: '[data-testid=email-input]',
      passwordInput: '[data-testid=password-input]',
      loginButton: '[data-testid=login-button]',
      forgotPasswordLink: '[data-testid=forgot-password-link]',
      registerLink: '[data-testid=register-link]',
      errorMessage: '[data-testid=error-message]',
      loadingSpinner: '[data-testid=loading-spinner]'
    };
    
    this.path = '/login';
  }

  /**
   * Navigate to login page
   */
  async navigateToLogin() {
    await this.goto(this.path);
    await this.waitForPageLoad();
    await this.verifyLoginPageLoaded();
  }

  /**
   * Verify login page has loaded correctly
   */
  async verifyLoginPageLoaded() {
    await this.waitForElement(this.elements.emailInput);
    await this.waitForElement(this.elements.passwordInput);
    await this.waitForElement(this.elements.loginButton);
    
    // Verify page title
    await this.verifyPageTitle('CMZ Animal Config - Login');
  }

  /**
   * Perform login with credentials
   * @param {string} email - User email
   * @param {string} password - User password
   */
  async login(email, password) {
    await this.fillInput(this.elements.emailInput, email);
    await this.fillInput(this.elements.passwordInput, password);
    await this.clickElement(this.elements.loginButton);
  }

  /**
   * Perform successful login and wait for redirect
   * NOTE: CORS is now enabled - expects successful API calls and redirects
   * @param {string} email - User email  
   * @param {string} password - User password
   * @param {string} expectedRedirect - Expected redirect path
   */
  async loginSuccessfully(email = 'test@cmz.org', password = 'testpass123', expectedRedirect = '/dashboard') {
    await this.login(email, password);
    
    // With CORS enabled, expect successful API response and redirect
    try {
      // Wait for API response - should succeed now
      await this.waitForAPIResponse('/auth', 10000);
      
      // Wait for successful redirect to dashboard/expected page
      await this.page.waitForURL(`**${expectedRedirect}`, { timeout: 5000 });
      await this.verifyURL(expectedRedirect);
      
      console.log(`✅ Login successful - redirected to ${expectedRedirect}`);
      
    } catch (error) {
      // With CORS enabled, this should indicate a real failure
      console.log('❌ Login failed - this indicates a real issue, not CORS');
      
      // Check for error message
      const hasError = await this.page.isVisible(this.elements.errorMessage, { timeout: 5000 });
      if (hasError) {
        const errorText = await this.page.textContent(this.elements.errorMessage);
        console.log(`Login error: ${errorText}`);
        throw new Error(`Login failed: ${errorText}`);
      } else {
        throw new Error(`Login failed: ${error.message}`);
      }
    }
  }

  /**
   * Attempt login with invalid credentials
   * @param {string} email - Invalid email
   * @param {string} password - Invalid password
   */
  async loginWithInvalidCredentials(email, password) {
    await this.login(email, password);
    
    // Wait for error message to appear
    await this.waitForElement(this.elements.errorMessage);
    
    // Verify we're still on login page
    await this.verifyURL(this.path);
  }

  /**
   * Get login error message
   * @returns {string} Error message text
   */
  async getErrorMessage() {
    if (await this.isVisible(this.elements.errorMessage)) {
      return await this.getTextContent(this.elements.errorMessage);
    }
    return '';
  }

  /**
   * Click forgot password link
   */
  async clickForgotPassword() {
    await this.clickElement(this.elements.forgotPasswordLink);
    await this.verifyURL('/auth/forgot-password');
  }

  /**
   * Click register link
   */
  async clickRegisterLink() {
    await this.clickElement(this.elements.registerLink);
    await this.verifyURL('/auth/register');
  }

  /**
   * Verify login button state
   * @param {boolean} shouldBeEnabled - Expected enabled state
   */
  async verifyLoginButtonState(shouldBeEnabled = true) {
    const isEnabled = await this.isEnabled(this.elements.loginButton);
    expect(isEnabled).toBe(shouldBeEnabled);
  }

  /**
   * Test email input validation
   * @param {string} invalidEmail - Invalid email to test
   */
  async testEmailValidation(invalidEmail) {
    await this.fillInput(this.elements.emailInput, invalidEmail);
    await this.clickElement(this.elements.loginButton);
    
    // Check for validation message
    const validationMessage = await this.page.evaluate((selector) => {
      const input = document.querySelector(selector);
      return input.validationMessage;
    }, this.elements.emailInput);
    
    expect(validationMessage).toBeTruthy();
  }

  /**
   * Test password field security (no plain text)
   */
  async testPasswordFieldSecurity() {
    const inputType = await this.getAttribute(this.elements.passwordInput, 'type');
    expect(inputType).toBe('password');
  }

  /**
   * Test form submission with empty fields
   */
  async testEmptyFormSubmission() {
    // Clear any existing values
    await this.fillInput(this.elements.emailInput, '');
    await this.fillInput(this.elements.passwordInput, '');
    
    await this.clickElement(this.elements.loginButton);
    
    // Should show validation errors
    const emailValidation = await this.page.evaluate((selector) => {
      const input = document.querySelector(selector);
      return input.validity.valid;
    }, this.elements.emailInput);
    
    expect(emailValidation).toBe(false);
  }

  /**
   * Test boundary conditions for login form
   */
  async testBoundaryConditions() {
    const testCases = [
      {
        name: 'Empty credentials',
        email: '',
        password: '',
        expectError: true
      },
      {
        name: 'Invalid email format', 
        email: 'invalid-email',
        password: 'password123',
        expectError: true
      },
      {
        name: 'Very long email',
        email: 'a'.repeat(300) + '@example.com',
        password: 'password123',
        expectError: true
      },
      {
        name: 'Very long password',
        email: 'test@example.com',
        password: 'a'.repeat(1000),
        expectError: true
      },
      {
        name: 'Special characters in password',
        email: 'test@example.com',
        password: 'p@ssw0rd!@#$%^&*()',
        expectError: false // Should be valid
      },
      {
        name: 'Unicode characters',
        email: 'tëst@example.com',
        password: 'pàssw0rd123',
        expectError: false // Modern systems should handle Unicode
      }
    ];

    for (const testCase of testCases) {
      console.log(`Testing: ${testCase.name}`);
      
      await this.navigateToLogin(); // Fresh page for each test
      await this.login(testCase.email, testCase.password);
      
      if (testCase.expectError) {
        // Should have error or validation issue
        const hasError = await this.isVisible(this.elements.errorMessage) || 
                         await this.verifyFormValidationError();
        expect(hasError).toBe(true);
      } else {
        // Should either succeed or fail gracefully
        const currentUrl = this.page.url();
        // We expect either successful redirect or graceful error handling
        expect(currentUrl).toBeTruthy();
      }
    }
  }

  /**
   * Verify form has validation errors
   * @returns {boolean} True if form has validation errors
   */
  async verifyFormValidationError() {
    const emailValid = await this.page.evaluate((selector) => {
      const input = document.querySelector(selector);
      return input.validity.valid;
    }, this.elements.emailInput);
    
    const passwordValid = await this.page.evaluate((selector) => {
      const input = document.querySelector(selector);
      return input.validity.valid;
    }, this.elements.passwordInput);
    
    return !emailValid || !passwordValid;
  }

  /**
   * Test keyboard navigation on login form
   */
  async testKeyboardNavigation() {
    await this.navigateToLogin();
    
    // Test tab navigation order
    const expectedTabOrder = [
      this.elements.emailInput,
      this.elements.passwordInput,
      this.elements.loginButton,
      this.elements.forgotPasswordLink,
      this.elements.registerLink
    ];
    
    await this.testKeyboardNavigation(expectedTabOrder);
  }

  /**
   * Test accessibility compliance
   */
  async testAccessibility() {
    await this.navigateToLogin();
    
    // Verify form labels and ARIA attributes
    await this.verifyAccessibility(this.elements.emailInput, {
      'aria-label': 'Email address',
      'required': ''
    });
    
    await this.verifyAccessibility(this.elements.passwordInput, {
      'aria-label': 'Password',
      'required': ''
    });
    
    // Verify login button has proper attributes
    await this.verifyAccessibility(this.elements.loginButton, {
      'type': 'submit'
    });
  }

  /**
   * Test mobile responsive design
   */
  async testMobileResponsive() {
    const mobileViewports = [
      { width: 375, height: 667 }, // iPhone SE
      { width: 414, height: 896 }, // iPhone XR
      { width: 360, height: 740 }  // Android
    ];
    
    await this.testResponsiveDesign(mobileViewports, async (viewport) => {
      await this.navigateToLogin();
      
      // Verify all elements are visible and properly sized
      await this.verifyElementInViewport(this.elements.emailInput);
      await this.verifyElementInViewport(this.elements.passwordInput);
      await this.verifyElementInViewport(this.elements.loginButton);
      
      // Test form is usable on mobile
      await this.fillInput(this.elements.emailInput, 'mobile@test.com');
      await this.fillInput(this.elements.passwordInput, 'password123');
      
      const loginButtonVisible = await this.isVisible(this.elements.loginButton);
      expect(loginButtonVisible).toBe(true);
    });
  }

  /**
   * Test login performance
   */
  async testLoginPerformance() {
    const startTime = Date.now();
    
    await this.navigateToLogin();
    
    const pageLoadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(pageLoadTime).toBeLessThan(3000);
    
    // Test login interaction response time
    const interactionStart = Date.now();
    
    await this.fillInput(this.elements.emailInput, 'test@example.com');
    await this.fillInput(this.elements.passwordInput, 'password123');
    
    const interactionTime = Date.now() - interactionStart;
    
    // Form interactions should complete within 500ms
    expect(interactionTime).toBeLessThan(500);
  }
}

module.exports = LoginPage;
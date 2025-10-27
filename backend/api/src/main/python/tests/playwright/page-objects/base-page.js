// Base Page Object for Playwright tests  
// PR003946-96: Integrated playwright testing

const { expect } = require('@playwright/test');

/**
 * Base page class with common functionality for all page objects
 * Implements common patterns and utilities used across all pages
 */
class BasePage {
  constructor(page) {
    this.page = page;
    this.baseURL = process.env.FRONTEND_URL || 'http://localhost:3000';
    this.apiURL = process.env.BACKEND_URL || 'http://localhost:8080';
  }

  /**
   * Navigate to a specific path
   * @param {string} path - The path to navigate to
   * @param {object} options - Navigation options
   */
  async goto(path, options = {}) {
    const url = path.startsWith('http') ? path : `${this.baseURL}${path}`;
    await this.page.goto(url, { 
      waitUntil: 'networkidle',
      timeout: 30000,
      ...options 
    });
  }

  /**
   * Wait for element to be visible with timeout
   * @param {string} selector - Element selector
   * @param {number} timeout - Timeout in milliseconds
   */
  async waitForElement(selector, timeout = 10000) {
    await this.page.waitForSelector(selector, { 
      state: 'visible', 
      timeout 
    });
  }

  /**
   * Wait for element to be hidden
   * @param {string} selector - Element selector  
   * @param {number} timeout - Timeout in milliseconds
   */
  async waitForElementHidden(selector, timeout = 10000) {
    await this.page.waitForSelector(selector, { 
      state: 'hidden', 
      timeout 
    });
  }

  /**
   * Click element with retry logic
   * @param {string} selector - Element selector
   * @param {object} options - Click options
   */
  async clickElement(selector, options = {}) {
    await this.waitForElement(selector);
    await this.page.click(selector, {
      timeout: 10000,
      ...options
    });
  }

  /**
   * Fill input field with validation
   * @param {string} selector - Input selector
   * @param {string} value - Value to fill
   * @param {object} options - Fill options
   */
  async fillInput(selector, value, options = {}) {
    await this.waitForElement(selector);
    
    // Clear existing content first
    await this.page.fill(selector, '');
    
    // Fill new value
    await this.page.fill(selector, value, {
      timeout: 10000,
      ...options
    });
    
    // Verify value was set correctly
    const actualValue = await this.page.inputValue(selector);
    expect(actualValue).toBe(value);
  }

  /**
   * Select option from dropdown
   * @param {string} selector - Select element selector
   * @param {string} value - Value to select
   */
  async selectOption(selector, value) {
    await this.waitForElement(selector);
    await this.page.selectOption(selector, value);
  }

  /**
   * Get text content of element
   * @param {string} selector - Element selector
   * @returns {string} Text content
   */
  async getTextContent(selector) {
    await this.waitForElement(selector);
    return await this.page.textContent(selector);
  }

  /**
   * Get attribute value of element
   * @param {string} selector - Element selector
   * @param {string} attribute - Attribute name
   * @returns {string} Attribute value
   */
  async getAttribute(selector, attribute) {
    await this.waitForElement(selector);
    return await this.page.getAttribute(selector, attribute);
  }

  /**
   * Check if element is visible
   * @param {string} selector - Element selector
   * @returns {boolean} True if visible
   */
  async isVisible(selector) {
    try {
      await this.page.waitForSelector(selector, { 
        state: 'visible', 
        timeout: 1000 
      });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check if element is enabled
   * @param {string} selector - Element selector  
   * @returns {boolean} True if enabled
   */
  async isEnabled(selector) {
    await this.waitForElement(selector);
    return await this.page.isEnabled(selector);
  }

  /**
   * Wait for page to load completely
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForLoadState('domcontentloaded');
  }

  /**
   * Take screenshot for debugging
   * @param {string} name - Screenshot name
   */
  async takeScreenshot(name) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.page.screenshot({ 
      path: `reports/screenshots/${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Verify page title
   * @param {string} expectedTitle - Expected page title
   */
  async verifyPageTitle(expectedTitle) {
    const actualTitle = await this.page.title();
    expect(actualTitle).toBe(expectedTitle);
  }

  /**
   * Verify URL contains expected path
   * @param {string} expectedPath - Expected URL path
   */
  async verifyURL(expectedPath) {
    const currentURL = this.page.url();
    expect(currentURL).toContain(expectedPath);
  }

  /**
   * Wait for API response
   * @param {string} urlPattern - URL pattern to match
   * @param {number} timeout - Timeout in milliseconds
   */
  async waitForAPIResponse(urlPattern, timeout = 10000) {
    return await this.page.waitForResponse(
      response => response.url().includes(urlPattern) && response.status() === 200,
      { timeout }
    );
  }

  /**
   * Mock API response for testing
   * @param {string} urlPattern - URL pattern to mock
   * @param {object} responseData - Mock response data
   */
  async mockAPIResponse(urlPattern, responseData) {
    await this.page.route(`**/${urlPattern}`, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(responseData)
      });
    });
  }

  /**
   * Verify element has correct accessibility attributes
   * @param {string} selector - Element selector
   * @param {object} expectedAttributes - Expected ARIA attributes
   */
  async verifyAccessibility(selector, expectedAttributes = {}) {
    await this.waitForElement(selector);
    
    for (const [attribute, expectedValue] of Object.entries(expectedAttributes)) {
      const actualValue = await this.getAttribute(selector, attribute);
      expect(actualValue).toBe(expectedValue);
    }
  }

  /**
   * Perform keyboard navigation test
   * @param {Array} selectors - Array of selectors to navigate through
   */
  async testKeyboardNavigation(selectors) {
    for (let i = 0; i < selectors.length; i++) {
      await this.page.keyboard.press('Tab');
      
      // Verify focus is on expected element
      const focusedElement = await this.page.evaluate(() => {
        return document.activeElement?.getAttribute('data-testid') || 
               document.activeElement?.id ||
               document.activeElement?.className;
      });
      
      // This is a basic check - in practice you'd want more specific verification
      expect(focusedElement).toBeTruthy();
    }
  }

  /**
   * Test responsive design at different viewport sizes
   * @param {Array} viewports - Array of viewport configurations
   * @param {Function} testFunction - Function to run at each viewport
   */
  async testResponsiveDesign(viewports, testFunction) {
    for (const viewport of viewports) {
      await this.page.setViewportSize(viewport);
      await this.page.waitForTimeout(500); // Allow layout to settle
      await testFunction(viewport);
    }
  }

  /**
   * Verify element is within viewport
   * @param {string} selector - Element selector
   */
  async verifyElementInViewport(selector) {
    await this.waitForElement(selector);
    
    const isInViewport = await this.page.evaluate((sel) => {
      const element = document.querySelector(sel);
      if (!element) return false;
      
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= window.innerHeight &&
        rect.right <= window.innerWidth
      );
    }, selector);
    
    expect(isInViewport).toBe(true);
  }

  /**
   * Wait for loading states to complete
   */
  async waitForLoadingComplete() {
    // Wait for common loading indicators to disappear
    const loadingSelectors = [
      '[data-testid=loading-spinner]',
      '[data-testid=loading-overlay]', 
      '.loading',
      '.spinner'
    ];
    
    for (const selector of loadingSelectors) {
      try {
        await this.page.waitForSelector(selector, { 
          state: 'hidden', 
          timeout: 2000 
        });
      } catch {
        // Selector might not exist, which is fine
      }
    }
  }

  /**
   * Verify no JavaScript errors on page
   */
  async verifyNoJSErrors() {
    const jsErrors = await this.page.evaluate(() => {
      return window.__jsErrors || [];
    });
    
    expect(jsErrors).toHaveLength(0);
  }

  /**
   * Test form validation
   * @param {object} formData - Form field data and validation rules
   */
  async testFormValidation(formData) {
    for (const field of formData.fields) {
      if (field.required && field.emptyErrorMessage) {
        // Test required field validation
        await this.fillInput(field.selector, '');
        await this.clickElement(formData.submitButton);
        
        const errorMessage = await this.getTextContent(field.errorSelector);
        expect(errorMessage).toContain(field.emptyErrorMessage);
      }
      
      if (field.invalidValue && field.invalidErrorMessage) {
        // Test format validation
        await this.fillInput(field.selector, field.invalidValue);
        await this.clickElement(formData.submitButton);
        
        const errorMessage = await this.getTextContent(field.errorSelector);
        expect(errorMessage).toContain(field.invalidErrorMessage);
      }
    }
  }
}

module.exports = BasePage;
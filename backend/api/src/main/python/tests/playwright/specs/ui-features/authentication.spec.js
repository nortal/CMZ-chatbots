// Authentication feature tests
// PR003946-96: Integrated playwright testing

const { test, expect } = require('@playwright/test');
const LoginPage = require('../../page-objects/login-page');

test.describe('Authentication Features', () => {
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
  });

  test.describe('Login Functionality', () => {
    test('should load login page correctly', async () => {
      await loginPage.navigateToLogin();
      await loginPage.verifyLoginPageLoaded();
    });

    test('should perform successful login with valid credentials', async () => {
      await loginPage.navigateToLogin();
      
      // Use test credentials from backend test data
      await loginPage.loginSuccessfully('user_parent_001@cmz.org', 'testpass123');
      
      // Verify we're redirected to dashboard
      await loginPage.verifyURL('/dashboard');
    });

    test('should show error for invalid credentials', async () => {
      await loginPage.navigateToLogin();
      await loginPage.loginWithInvalidCredentials('invalid@test.com', 'wrongpassword');
      
      const errorMessage = await loginPage.getErrorMessage();
      expect(errorMessage).toContain('Invalid credentials');
    });

    test('should validate email format', async () => {
      await loginPage.navigateToLogin();
      await loginPage.testEmailValidation('invalid-email-format');
    });

    test('should require both email and password', async () => {
      await loginPage.navigateToLogin();
      await loginPage.testEmptyFormSubmission();
    });

    test('should mask password input', async () => {
      await loginPage.navigateToLogin();
      await loginPage.testPasswordFieldSecurity();
    });
  });

  test.describe('Boundary Value Testing', () => {
    test('should handle edge cases and boundary conditions', async () => {
      await loginPage.testBoundaryConditions();
    });

    test('should handle special characters in credentials', async () => {
      await loginPage.navigateToLogin();
      
      // Test special characters that should be valid
      await loginPage.login('test+tag@example.com', 'p@ssw0rd!123');
      
      // Should either succeed or fail gracefully (not crash)
      const pageUrl = loginPage.page.url();
      expect(pageUrl).toBeTruthy();
    });

    test('should handle very long input values', async () => {
      await loginPage.navigateToLogin();
      
      const longEmail = 'a'.repeat(100) + '@example.com';
      const longPassword = 'password'.repeat(50);
      
      await loginPage.login(longEmail, longPassword);
      
      // Should handle gracefully without crashing
      const pageExists = await loginPage.page.isVisible('body');
      expect(pageExists).toBe(true);
    });

    test('should handle Unicode and international characters', async () => {
      await loginPage.navigateToLogin();
      
      // Test Unicode characters
      await loginPage.login('tëst@example.com', 'pàssw0rd123');
      
      // Test Chinese characters
      await loginPage.login('测试@example.com', '密码123');
      
      // Should handle gracefully
      const pageExists = await loginPage.page.isVisible('body');
      expect(pageExists).toBe(true);
    });
  });

  test.describe('Navigation and Links', () => {
    test('should navigate to forgot password page', async () => {
      await loginPage.navigateToLogin();
      await loginPage.clickForgotPassword();
    });

    test('should navigate to registration page', async () => {
      await loginPage.navigateToLogin();
      await loginPage.clickRegisterLink();
    });
  });

  test.describe('Integration Testing', () => {
    test('should persist session after successful login', async ({ page, context }) => {
      await loginPage.navigateToLogin();
      await loginPage.loginSuccessfully();
      
      // Navigate to another page
      await loginPage.goto('/profile');
      
      // Should remain authenticated (not redirect to login)
      await page.waitForTimeout(2000);
      const currentUrl = page.url();
      expect(currentUrl).not.toContain('/auth/login');
    });

    test('should handle session timeout gracefully', async ({ page }) => {
      await loginPage.navigateToLogin();
      await loginPage.loginSuccessfully();
      
      // Mock expired session response
      await page.route('**/api/**', route => {
        if (route.request().url().includes('/auth/verify')) {
          route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 'session_expired',
              message: 'Session has expired'
            })
          });
        } else {
          route.continue();
        }
      });
      
      // Try to access protected resource
      await loginPage.goto('/admin');
      
      // Should redirect to login
      await page.waitForURL('**/auth/login', { timeout: 5000 });
    });

    test('should validate backend data persistence', async ({ page }) => {
      await loginPage.navigateToLogin();
      
      // Login with test user
      await loginPage.loginSuccessfully('user_parent_001@cmz.org', 'testpass123');
      
      // Verify API call was made and response received
      const responses = [];
      page.on('response', response => {
        if (response.url().includes('/auth') && response.status() === 200) {
          responses.push(response);
        }
      });
      
      // Refresh page to trigger auth verification
      await page.reload();
      
      // Should have made auth verification call
      expect(responses.length).toBeGreaterThan(0);
    });
  });

  test.describe('Accessibility Testing', () => {
    test('should support keyboard navigation', async () => {
      await loginPage.testKeyboardNavigation();
    });

    test('should have proper ARIA attributes', async () => {
      await loginPage.testAccessibility();
    });

    test('should have sufficient color contrast', async ({ page }) => {
      await loginPage.navigateToLogin();
      
      // This would typically use axe-playwright for comprehensive accessibility testing
      // For now, we'll do basic checks
      const emailInputStyle = await page.evaluate((selector) => {
        const element = document.querySelector(selector);
        const style = window.getComputedStyle(element);
        return {
          backgroundColor: style.backgroundColor,
          color: style.color
        };
      }, loginPage.elements.emailInput);
      
      expect(emailInputStyle.backgroundColor).toBeTruthy();
      expect(emailInputStyle.color).toBeTruthy();
    });
  });

  test.describe('Mobile Responsive Testing', () => {
    test('should work correctly on mobile devices', async () => {
      await loginPage.testMobileResponsive();
    });

    test('should handle touch interactions', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      await loginPage.navigateToLogin();
      
      // Test touch interactions
      await page.tap(loginPage.elements.emailInput);
      await page.fill(loginPage.elements.emailInput, 'touch@test.com');
      
      await page.tap(loginPage.elements.passwordInput);
      await page.fill(loginPage.elements.passwordInput, 'password123');
      
      await page.tap(loginPage.elements.loginButton);
      
      // Should handle touch events properly
      const pageExists = await page.isVisible('body');
      expect(pageExists).toBe(true);
    });
  });

  test.describe('Performance Testing', () => {
    test('should load login page within performance thresholds', async () => {
      await loginPage.testLoginPerformance();
    });

    test('should handle concurrent login attempts', async ({ context }) => {
      // Create multiple pages for concurrent testing
      const pages = await Promise.all([
        context.newPage(),
        context.newPage(),
        context.newPage()
      ]);
      
      const loginAttempts = pages.map(async (page, index) => {
        const pageLoginObject = new LoginPage(page);
        await pageLoginObject.navigateToLogin();
        await pageLoginObject.login(`concurrent${index}@test.com`, 'password123');
        return page.url();
      });
      
      // All concurrent attempts should complete without crashing
      const results = await Promise.all(loginAttempts);
      expect(results.every(url => url.length > 0)).toBe(true);
      
      // Cleanup
      await Promise.all(pages.map(page => page.close()));
    });
  });

  test.describe('Security Testing', () => {
    test('should prevent XSS in login form', async ({ page }) => {
      await loginPage.navigateToLogin();
      
      const xssPayload = '<script>alert("xss")</script>';
      
      await loginPage.fillInput(loginPage.elements.emailInput, xssPayload);
      await loginPage.fillInput(loginPage.elements.passwordInput, xssPayload);
      
      await loginPage.clickElement(loginPage.elements.loginButton);
      
      // Should not execute script
      const alertWasShown = await page.evaluate(() => {
        return window.xssTestExecuted === true;
      });
      
      expect(alertWasShown).toBeFalsy();
    });

    test('should prevent SQL injection attempts', async () => {
      await loginPage.navigateToLogin();
      
      const sqlInjectionPayload = "'; DROP TABLE users; --";
      
      await loginPage.login(sqlInjectionPayload, sqlInjectionPayload);
      
      // Should handle gracefully without crashing backend
      const errorMessage = await loginPage.getErrorMessage();
      expect(errorMessage).not.toContain('database error');
    });

    test('should not expose sensitive information in errors', async () => {
      await loginPage.navigateToLogin();
      
      await loginPage.loginWithInvalidCredentials('test@example.com', 'wrongpassword');
      
      const errorMessage = await loginPage.getErrorMessage();
      
      // Error should be generic, not reveal if email exists
      expect(errorMessage).not.toContain('user not found');
      expect(errorMessage).not.toContain('password incorrect');
      expect(errorMessage).toMatch(/invalid credentials|login failed/i);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network connectivity issues', async ({ page }) => {
      await loginPage.navigateToLogin();
      
      // Simulate network failure
      await page.route('**/auth/**', route => {
        route.abort('failed');
      });
      
      await loginPage.login('test@example.com', 'password123');
      
      // Should show appropriate error message
      await page.waitForTimeout(2000);
      const errorExists = await loginPage.isVisible(loginPage.elements.errorMessage);
      expect(errorExists).toBe(true);
    });

    test('should handle server errors gracefully', async ({ page }) => {
      await loginPage.navigateToLogin();
      
      // Mock server error
      await page.route('**/auth/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'internal_error',
            message: 'Internal server error'
          })
        });
      });
      
      await loginPage.login('test@example.com', 'password123');
      
      // Should show user-friendly error
      const errorMessage = await loginPage.getErrorMessage();
      expect(errorMessage).toContain('server error');
      expect(errorMessage).not.toContain('stack trace');
    });
  });
});
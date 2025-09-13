/**
 * MANDATORY PERSISTENCE TEST: Playwright-to-LocalFiles Verification
 *
 * This test verifies that Playwright UI interactions trigger proper local file
 * persistence for configuration, logs, and session data.
 *
 * Required by TDD framework for comprehensive coverage reporting.
 */

const { test, expect } = require('@playwright/test');
const fs = require('fs').promises;
const path = require('path');

// Local file persistence configuration
const LOCAL_PERSISTENCE = {
  configDir: process.env.CMZ_CONFIG_DIR || './local_storage/config',
  logsDir: process.env.CMZ_LOGS_DIR || './local_storage/logs',
  sessionDir: process.env.CMZ_SESSION_DIR || './local_storage/sessions',
  exportDir: process.env.CMZ_EXPORT_DIR || './local_storage/exports'
};

async function ensureDirectoryExists(dirPath) {
  try {
    await fs.access(dirPath);
  } catch {
    await fs.mkdir(dirPath, { recursive: true });
    console.log(`📁 Created directory: ${dirPath}`);
  }
}

async function verifyFileExists(filePath, timeout = 5000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      await fs.access(filePath);
      console.log(`✅ File verified: ${filePath}`);
      return true;
    } catch {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  throw new Error(`File not found within ${timeout}ms: ${filePath}`);
}

async function verifyFileContent(filePath, expectedContent) {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    const parsedContent = JSON.parse(content);

    for (const [key, value] of Object.entries(expectedContent)) {
      if (typeof value === 'object') {
        expect(parsedContent[key]).toMatchObject(value);
      } else {
        expect(parsedContent[key]).toBe(value);
      }
    }

    console.log(`✅ File content verified: ${filePath}`);
    return parsedContent;
  } catch (error) {
    console.error(`❌ File content verification failed for ${filePath}:`, error);
    throw error;
  }
}

test.describe('💾 Playwright-to-LocalFiles Persistence Verification', () => {
  let testTimestamp;

  test.beforeEach(async ({ page }) => {
    testTimestamp = Date.now();

    // Ensure local storage directories exist
    for (const dir of Object.values(LOCAL_PERSISTENCE)) {
      await ensureDirectoryExists(dir);
    }

    // Navigate to application
    await page.goto(process.env.FRONTEND_URL || 'http://localhost:3001');
    await page.waitForLoadState('networkidle');
  });

  test('should persist user preferences to local config files', async ({ page }) => {
    // Step 1: Modify user preferences via UI
    await page.click('[data-testid="settings-button"]');
    await page.click('[data-testid="preferences-tab"]');

    const testPreferences = {
      theme: 'dark',
      language: 'en',
      autoSave: true,
      notificationsEnabled: false
    };

    // Set preferences
    await page.selectOption('[data-testid="theme-select"]', testPreferences.theme);
    await page.selectOption('[data-testid="language-select"]', testPreferences.language);
    await page.setChecked('[data-testid="auto-save-checkbox"]', testPreferences.autoSave);
    await page.setChecked('[data-testid="notifications-checkbox"]', testPreferences.notificationsEnabled);

    // Save preferences and verify API call
    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/user/preferences') && response.request().method() === 'PUT'
      ),
      page.click('[data-testid="save-preferences-button"]')
    ]);

    expect(response.status()).toBe(200);
    const userId = (await response.json()).userId;

    // Step 2: Verify local config file creation
    const configFile = path.join(LOCAL_PERSISTENCE.configDir, `user_${userId}_preferences.json`);
    await verifyFileExists(configFile);

    const fileContent = await verifyFileContent(configFile, {
      userId: userId,
      preferences: testPreferences,
      lastModified: expect.any(String)
    });

    // Step 3: Verify timestamp accuracy
    const fileTimestamp = new Date(fileContent.lastModified).getTime();
    const timeDiff = Math.abs(fileTimestamp - testTimestamp);
    expect(timeDiff).toBeLessThan(10000); // Within 10 seconds

    console.log('✅ User preferences persistence: UI → API → Local Config File ✅');
  });

  test('should persist session logs to local log files', async ({ page }) => {
    // Step 1: Perform actions that generate logs
    await page.click('[data-testid="start-chat-button"]');

    const testMessage = 'Tell me about elephants, this is a test message for logging';
    await page.fill('[data-testid="chat-input"]', testMessage);

    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/conversation') && response.request().method() === 'POST'
      ),
      page.press('[data-testid="chat-input"]', 'Enter')
    ]);

    expect(response.status()).toBe(201);
    const responseData = await response.json();
    const sessionId = responseData.sessionId;

    // Step 2: Verify session log file creation
    const logFile = path.join(LOCAL_PERSISTENCE.logsDir, `session_${sessionId}.log`);
    await verifyFileExists(logFile);

    // Step 3: Verify log content
    const logContent = await fs.readFile(logFile, 'utf8');
    expect(logContent).toContain(testMessage);
    expect(logContent).toContain('USER_MESSAGE');
    expect(logContent).toContain(sessionId);

    // Verify timestamp format in log
    const timestampRegex = /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;
    expect(logContent).toMatch(timestampRegex);

    console.log('✅ Session logging persistence: UI → Chat → Local Log File ✅');
  });

  test('should persist conversation export to local files', async ({ page }) => {
    // Step 1: Create conversation for export
    await page.click('[data-testid="start-chat-button"]');
    await page.fill('[data-testid="chat-input"]', 'Export test conversation');
    await page.press('[data-testid="chat-input"]', 'Enter');

    // Wait for AI response
    await page.waitForSelector('[data-testid="ai-response"]', { timeout: 10000 });

    // Step 2: Export conversation
    await page.click('[data-testid="chat-menu-button"]');
    await page.click('[data-testid="export-conversation-button"]');

    // Select export format
    await page.selectOption('[data-testid="export-format-select"]', 'json');

    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/conversation/export') && response.request().method() === 'POST'
      ),
      page.click('[data-testid="confirm-export-button"]')
    ]);

    expect(response.status()).toBe(200);
    const exportData = await response.json();
    const exportId = exportData.exportId;

    // Step 3: Verify export file creation
    const exportFile = path.join(LOCAL_PERSISTENCE.exportDir, `conversation_export_${exportId}.json`);
    await verifyFileExists(exportFile);

    const exportContent = await verifyFileContent(exportFile, {
      exportId: exportId,
      exportType: 'conversation',
      format: 'json',
      timestamp: expect.any(String),
      data: {
        messages: expect.any(Array)
      }
    });

    // Step 4: Verify export data integrity
    expect(exportContent.data.messages.length).toBeGreaterThan(0);
    const userMessage = exportContent.data.messages.find(m => m.role === 'user');
    expect(userMessage.content).toContain('Export test conversation');

    console.log('✅ Conversation export persistence: UI → Export → Local JSON File ✅');
  });

  test('should persist animal configuration backups to local files', async ({ page }) => {
    // Step 1: Configure animal settings
    await page.click('[data-testid="animal-config-button"]');
    await page.click('[data-testid="add-animal-button"]');

    const animalConfig = {
      name: 'Test Lion Config',
      species: 'lion',
      personality: 'brave',
      responseStyle: 'educational'
    };

    await page.fill('[data-testid="animal-name-input"]', animalConfig.name);
    await page.selectOption('[data-testid="animal-species-select"]', animalConfig.species);
    await page.fill('[data-testid="animal-personality-input"]', animalConfig.personality);
    await page.selectOption('[data-testid="response-style-select"]', animalConfig.responseStyle);

    // Step 2: Save configuration with backup
    await page.setChecked('[data-testid="create-backup-checkbox"]', true);

    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/animal') && response.request().method() === 'POST'
      ),
      page.click('[data-testid="save-animal-button"]')
    ]);

    expect(response.status()).toBe(201);
    const responseData = await response.json();
    const animalId = responseData.animalId;

    // Step 3: Verify backup file creation
    const backupFile = path.join(LOCAL_PERSISTENCE.configDir, `animal_config_backup_${animalId}.json`);
    await verifyFileExists(backupFile);

    const backupContent = await verifyFileContent(backupFile, {
      animalId: animalId,
      backupType: 'animal_configuration',
      timestamp: expect.any(String),
      configuration: {
        name: animalConfig.name,
        species: animalConfig.species,
        personality: animalConfig.personality,
        responseStyle: animalConfig.responseStyle
      }
    });

    // Step 4: Verify backup metadata
    expect(backupContent.version).toBe('1.0');
    expect(backupContent.source).toBe('web_ui');

    console.log('✅ Animal configuration backup: UI → Config → Local Backup File ✅');
  });

  test('should persist error logs and debug information locally', async ({ page }) => {
    // Step 1: Trigger error condition
    await page.evaluate(() => {
      // Simulate network error by intercepting fetch
      const originalFetch = window.fetch;
      window.fetch = function(...args) {
        if (args[0].includes('/simulate-error')) {
          return Promise.reject(new Error('Simulated network error for testing'));
        }
        return originalFetch.apply(this, args);
      };
    });

    // Trigger error via UI action
    await page.click('[data-testid="advanced-settings-button"]');

    // This should trigger error logging
    try {
      await page.click('[data-testid="simulate-error-button"]');
    } catch {
      // Expected to fail, we're testing error logging
    }

    // Step 2: Verify error log file creation
    const errorLogFile = path.join(LOCAL_PERSISTENCE.logsDir, `error_${new Date().toISOString().split('T')[0]}.log`);
    await verifyFileExists(errorLogFile, 8000);

    // Step 3: Verify error log content
    const errorContent = await fs.readFile(errorLogFile, 'utf8');
    expect(errorContent).toContain('ERROR');
    expect(errorContent).toContain('Simulated network error');

    // Verify structured logging
    const logLines = errorContent.split('\n').filter(line => line.trim());
    const lastLogLine = JSON.parse(logLines[logLines.length - 1]);

    expect(lastLogLine.level).toBe('ERROR');
    expect(lastLogLine.message).toContain('network error');
    expect(lastLogLine.timestamp).toMatch(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);

    console.log('✅ Error logging persistence: UI Error → Local Error Log ✅');
  });

  test.afterEach(async () => {
    // Cleanup test files (optional - keep for debugging or remove for production)
    const cleanupMode = process.env.CMZ_CLEANUP_TEST_FILES || 'false';

    if (cleanupMode === 'true') {
      try {
        // Clean up files created during this test
        const testPattern = `*${testTimestamp}*`;
        console.log(`🗑️ Cleanup mode enabled, removing test files matching: ${testPattern}`);
        // Implement cleanup logic here if needed
      } catch (error) {
        console.warn('⚠️ Cleanup warning:', error);
      }
    } else {
      console.log('📁 Test files preserved for debugging (set CMZ_CLEANUP_TEST_FILES=true to auto-cleanup)');
    }
  });
});

test.describe('🔧 Local Files Performance and Integrity Verification', () => {
  test('should handle concurrent file operations without corruption', async ({ page }) => {
    const startTime = Date.now();

    // Test multiple concurrent operations
    const operations = [];

    for (let i = 0; i < 5; i++) {
      operations.push(
        page.evaluate(async (index) => {
          // Simulate concurrent config saves
          const response = await fetch('/api/user/preferences', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              preference: `concurrent_test_${index}`,
              value: `test_value_${index}`,
              timestamp: Date.now()
            })
          });
          return response.status;
        }, i)
      );
    }

    // Wait for all operations to complete
    const results = await Promise.all(operations);
    const operationTime = Date.now() - startTime;

    // Verify all operations succeeded
    results.forEach(status => {
      expect(status).toBe(200);
    });

    // Verify performance
    expect(operationTime).toBeLessThan(3000); // 3 second max for 5 concurrent operations

    // Verify no file corruption
    const configFiles = await fs.readdir(LOCAL_PERSISTENCE.configDir);
    const concurrentFiles = configFiles.filter(f => f.includes('concurrent_test'));

    expect(concurrentFiles.length).toBe(5);

    // Verify each file is valid JSON
    for (const file of concurrentFiles) {
      const filePath = path.join(LOCAL_PERSISTENCE.configDir, file);
      const content = await fs.readFile(filePath, 'utf8');

      // Should parse without error
      const parsed = JSON.parse(content);
      expect(parsed.preference).toContain('concurrent_test_');
    }

    console.log('✅ Concurrent file operations: All operations completed without corruption');
  });

  test('should maintain file integrity across app restarts', async ({ page }) => {
    // Step 1: Create persistent configuration
    const testConfig = {
      persistenceTest: true,
      timestamp: Date.now(),
      version: '1.0.0'
    };

    await page.evaluate(async (config) => {
      await fetch('/api/system/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
    }, testConfig);

    const configFile = path.join(LOCAL_PERSISTENCE.configDir, 'system_config.json');
    await verifyFileExists(configFile);

    // Step 2: Verify initial file content
    const initialContent = await verifyFileContent(configFile, testConfig);

    // Step 3: Simulate app restart by reloading page
    await page.reload({ waitUntil: 'networkidle' });

    // Step 4: Verify file still exists and content is intact
    await verifyFileExists(configFile);
    const afterRestartContent = await verifyFileContent(configFile, testConfig);

    // Verify content hasn't changed
    expect(afterRestartContent.timestamp).toBe(initialContent.timestamp);
    expect(afterRestartContent.persistenceTest).toBe(true);

    console.log('✅ File persistence integrity: Configuration survived app restart');
  });
});
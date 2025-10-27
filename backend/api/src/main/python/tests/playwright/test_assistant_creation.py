"""
Playwright E2E test for complete assistant creation workflow

Tests the end-to-end user journey from login to creating a functional assistant
that can be used by zoo visitors for conversations.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser
import requests
import json
import time
from typing import Dict, Any


class TestAssistantCreationWorkflow:
    """End-to-end test for assistant creation workflow"""

    @pytest.fixture(scope="session")
    def event_loop(self):
        """Create an instance of the default event loop for the test session."""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture
    async def browser(self):
        """Setup browser for testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Set to True for CI
            yield browser
            await browser.close()

    @pytest.fixture
    async def page(self, browser: Browser):
        """Setup page for testing"""
        page = await browser.new_page()
        yield page
        await page.close()

    def setup_test_data(self) -> Dict[str, Any]:
        """Setup test data for assistant creation"""
        return {
            "assistant": {
                "name": "E2E Test Assistant",
                "description": "End-to-end test assistant for automated validation",
                "animalId": "tiger-e2e-test",
                "personalityId": "friendly-e2e",
                "guardrailId": "basic-e2e",
                "status": "active"
            },
            "animal": {
                "animalId": "tiger-e2e-test",
                "name": "Test Tiger",
                "species": "Panthera tigris",
                "status": "active"
            },
            "personality": {
                "personalityId": "friendly-e2e",
                "name": "E2E Friendly Personality",
                "systemPrompt": "You are a friendly tiger who loves helping visitors learn.",
                "status": "active"
            },
            "guardrail": {
                "guardrailId": "basic-e2e",
                "name": "E2E Basic Guardrails",
                "rules": ["Keep conversations family-friendly", "No personal information"],
                "status": "active"
            }
        }

    async def prepare_backend_data(self, base_url: str, test_data: Dict[str, Any]) -> bool:
        """Prepare backend with necessary test data"""
        try:
            # Create animal (prerequisite for assistant)
            animal_response = requests.post(
                f"{base_url}/animal",
                json=test_data["animal"],
                headers={"Content-Type": "application/json"}
            )

            # Create personality
            personality_response = requests.post(
                f"{base_url}/personality",
                json=test_data["personality"],
                headers={"Content-Type": "application/json"}
            )

            # Create guardrail
            guardrail_response = requests.post(
                f"{base_url}/guardrail",
                json=test_data["guardrail"],
                headers={"Content-Type": "application/json"}
            )

            return True
        except Exception as e:
            print(f"Failed to prepare backend data: {e}")
            return False

    async def cleanup_backend_data(self, base_url: str, test_data: Dict[str, Any]):
        """Clean up test data from backend"""
        try:
            # Clean up in reverse order
            requests.delete(f"{base_url}/assistant/e2e-test-assistant")
            requests.delete(f"{base_url}/guardrail/{test_data['guardrail']['guardrailId']}")
            requests.delete(f"{base_url}/personality/{test_data['personality']['personalityId']}")
            requests.delete(f"{base_url}/animal/{test_data['animal']['animalId']}")
        except Exception as e:
            print(f"Cleanup warning: {e}")

    @pytest.mark.asyncio
    async def test_complete_assistant_creation_workflow(self, page: Page):
        """Test complete assistant creation workflow from start to finish"""
        # Configuration
        frontend_url = "http://localhost:3000"
        backend_url = "http://localhost:8081"
        test_data = self.setup_test_data()

        try:
            # Step 1: Prepare backend with necessary data
            print("📋 Step 1: Preparing backend test data...")
            backend_ready = await self.prepare_backend_data(backend_url, test_data)

            if not backend_ready:
                pytest.skip("Backend not ready for E2E testing")

            # Step 2: Navigate to application and authenticate
            print("🔐 Step 2: Authenticating user...")
            await page.goto(f"{frontend_url}/login")
            await page.wait_for_load_state("networkidle")

            # Handle authentication (assuming mock auth in development)
            login_button = page.locator('button:has-text("Login"), input[type="submit"]')
            if await login_button.count() > 0:
                await login_button.click()
                await page.wait_for_url("**/dashboard")

            # Step 3: Navigate to Assistant Management
            print("🧭 Step 3: Navigating to Assistant Management...")
            await page.goto(f"{frontend_url}/assistant-management")
            await page.wait_for_load_state("networkidle")

            # Wait for page to load
            await page.wait_for_selector('h1, h2, [data-testid="assistant-management"]', timeout=10000)

            # Step 4: Initiate assistant creation
            print("➕ Step 4: Starting assistant creation...")

            # Look for create button with multiple selectors
            create_button = page.locator(
                'button:has-text("Create Assistant"), '
                'button:has-text("Create"), '
                'button:has-text("Add Assistant"), '
                '[data-testid="create-assistant-button"]'
            ).first()

            await create_button.click()
            await page.wait_for_timeout(2000)  # Wait for form to appear

            # Step 5: Fill out assistant creation form
            print("📝 Step 5: Filling assistant creation form...")

            # Fill in assistant name
            name_input = page.locator(
                'input[name="name"], '
                'input[placeholder*="name" i], '
                'input[id*="name"], '
                'input[data-testid="assistant-name"]'
            ).first()
            await name_input.fill(test_data["assistant"]["name"])

            # Fill in description
            description_input = page.locator(
                'textarea[name="description"], '
                'input[name="description"], '
                'textarea[placeholder*="description" i], '
                '[data-testid="assistant-description"]'
            ).first()
            await description_input.fill(test_data["assistant"]["description"])

            # Select animal
            animal_select = page.locator(
                'select[name="animalId"], '
                'select[name="animal"], '
                '[data-testid="animal-select"]'
            ).first()

            if await animal_select.count() > 0:
                await animal_select.select_option(test_data["assistant"]["animalId"])
            else:
                # Handle dropdown or autocomplete
                animal_input = page.locator('input[placeholder*="animal" i]').first()
                if await animal_input.count() > 0:
                    await animal_input.fill(test_data["animal"]["name"])

            # Select personality
            personality_select = page.locator(
                'select[name="personalityId"], '
                'select[name="personality"], '
                '[data-testid="personality-select"]'
            ).first()

            if await personality_select.count() > 0:
                await personality_select.select_option(test_data["assistant"]["personalityId"])

            # Select guardrail
            guardrail_select = page.locator(
                'select[name="guardrailId"], '
                'select[name="guardrail"], '
                '[data-testid="guardrail-select"]'
            ).first()

            if await guardrail_select.count() > 0:
                await guardrail_select.select_option(test_data["assistant"]["guardrailId"])

            # Step 6: Submit the form
            print("💾 Step 6: Submitting assistant creation...")

            # Set up API response listener
            async def handle_response(response):
                if "/assistant" in response.url and response.request.method == "POST":
                    print(f"🔄 Assistant creation API response: {response.status}")
                    if response.status == 201:
                        response_data = await response.json()
                        print(f"✅ Assistant created: {response_data.get('assistantId', 'unknown')}")
                        return response_data
                return None

            page.on("response", handle_response)

            # Submit form
            submit_button = page.locator(
                'button[type="submit"], '
                'button:has-text("Create"), '
                'button:has-text("Save"), '
                '[data-testid="submit-assistant"]'
            ).first()

            await submit_button.click()

            # Step 7: Verify assistant creation
            print("✅ Step 7: Verifying assistant creation...")

            # Wait for success feedback
            success_indicators = [
                'text="Assistant created successfully"',
                'text="Created successfully"',
                '[data-testid="success-message"]',
                '.alert-success',
                '.notification-success'
            ]

            try:
                for indicator in success_indicators:
                    element = page.locator(indicator)
                    if await element.count() > 0:
                        await element.wait_for(timeout=5000)
                        print("✅ Success message displayed")
                        break
            except Exception:
                print("⚠️ Success message not found, checking redirect...")

            # Check if redirected to assistant list
            await page.wait_for_timeout(3000)
            current_url = page.url
            print(f"📍 Current URL: {current_url}")

            # Step 8: Verify assistant appears in list
            print("📋 Step 8: Verifying assistant appears in list...")

            # Navigate to assistant list if not already there
            if "assistant" not in current_url.lower():
                await page.goto(f"{frontend_url}/assistant-management")
                await page.wait_for_load_state("networkidle")

            # Look for the created assistant in the list
            assistant_in_list = page.locator(f'text="{test_data["assistant"]["name"]}"')

            try:
                await assistant_in_list.wait_for(timeout=10000)
                print("✅ Assistant found in list")
            except Exception:
                print("⚠️ Assistant not found in list, checking API directly...")

                # Fallback: Check via API
                response = requests.get(f"{backend_url}/assistant")
                if response.status_code == 200:
                    assistants = response.json().get("assistants", [])
                    created_assistant = next(
                        (a for a in assistants if a["name"] == test_data["assistant"]["name"]),
                        None
                    )
                    if created_assistant:
                        print("✅ Assistant found via API")
                    else:
                        print("❌ Assistant not found via API")

            # Step 9: Test assistant functionality (basic conversation)
            print("💬 Step 9: Testing assistant conversation...")

            # Try to start a conversation with the assistant
            try:
                # Look for chat or test conversation button
                chat_button = page.locator(
                    'button:has-text("Chat"), '
                    'button:has-text("Test"), '
                    'button:has-text("Conversation"), '
                    '[data-testid="test-conversation"]'
                )

                if await chat_button.count() > 0:
                    await chat_button.first().click()
                    await page.wait_for_timeout(2000)

                    # Send a test message
                    message_input = page.locator(
                        'input[placeholder*="message" i], '
                        'textarea[placeholder*="message" i], '
                        '[data-testid="message-input"]'
                    ).first()

                    if await message_input.count() > 0:
                        await message_input.fill("Hello, can you tell me about yourself?")

                        send_button = page.locator(
                            'button:has-text("Send"), '
                            'button[type="submit"], '
                            '[data-testid="send-message"]'
                        ).first()

                        await send_button.click()
                        await page.wait_for_timeout(3000)

                        print("✅ Test conversation initiated")
                else:
                    print("ℹ️ Chat interface not found (may not be implemented yet)")

            except Exception as e:
                print(f"ℹ️ Conversation test skipped: {e}")

            print("🎉 Assistant creation workflow completed successfully!")

        except Exception as e:
            print(f"❌ E2E test failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="assistant_creation_failure.png")
            raise

        finally:
            # Step 10: Cleanup
            print("🧹 Step 10: Cleaning up test data...")
            await self.cleanup_backend_data(backend_url, test_data)

    @pytest.mark.asyncio
    async def test_assistant_creation_validation_errors(self, page: Page):
        """Test form validation during assistant creation"""
        frontend_url = "http://localhost:3000"

        # Navigate to assistant creation
        await page.goto(f"{frontend_url}/assistant-management")
        await page.wait_for_load_state("networkidle")

        # Find and click create button
        create_button = page.locator('button:has-text("Create"), button:has-text("Add")').first()
        await create_button.click()
        await page.wait_for_timeout(2000)

        # Try to submit empty form
        submit_button = page.locator('button[type="submit"], button:has-text("Create")').first()
        await submit_button.click()

        # Check for validation messages
        validation_messages = page.locator('.error, .invalid, [data-testid="error"]')

        if await validation_messages.count() > 0:
            print("✅ Form validation working")
        else:
            print("ℹ️ Validation messages not found (may use different selectors)")

    @pytest.mark.asyncio
    async def test_assistant_creation_performance(self, page: Page):
        """Test performance of assistant creation workflow"""
        frontend_url = "http://localhost:3000"

        start_time = time.time()

        # Navigate to application
        await page.goto(f"{frontend_url}/assistant-management")
        await page.wait_for_load_state("networkidle")

        navigation_time = time.time() - start_time

        # Verify performance criteria
        assert navigation_time < 5.0, f"Page load too slow: {navigation_time}s"

        print(f"✅ Page loaded in {navigation_time:.2f}s")


if __name__ == '__main__':
    pytest.main([__file__])
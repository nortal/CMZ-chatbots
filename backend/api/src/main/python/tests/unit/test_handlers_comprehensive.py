"""
Comprehensive unit tests for handlers.py
Task T007: Add unit tests for uncovered handlers
Target: Achieve 85% test coverage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Tuple
import json

# Import the handlers module
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from openapi_server.impl import handlers
from openapi_server.models.error import Error
from openapi_server.models.user import User
from openapi_server.models.family import Family
from openapi_server.models.animal import Animal


class TestAuthHandlers:
    """Test authentication-related handlers"""

    @patch('openapi_server.impl.handlers.handle_login_post')
    def test_handle_auth_post(self, mock_login):
        """Test auth_post delegates to login_post"""
        mock_login.return_value = ({'token': 'test123'}, 200)
        body = {'email': 'test@example.com', 'password': 'test123'}

        result = handlers.handle_auth_post(body)

        assert result[1] == 200
        mock_login.assert_called_once_with(body)

    @patch('openapi_server.impl.auth_mock.handle_auth_logout_post')
    def test_handle_logout_post(self, mock_logout):
        """Test logout handler"""
        mock_logout.return_value = ({'message': 'Logged out'}, 200)

        result = handlers.handle_logout_post()

        assert result[1] == 200
        mock_logout.assert_called_once()

    @patch('openapi_server.impl.auth_mock.handle_auth_refresh_post')
    def test_handle_auth_refresh_post(self, mock_refresh):
        """Test token refresh handler"""
        mock_refresh.return_value = ({'token': 'new_token'}, 200)

        result = handlers.handle_auth_refresh_post()

        assert result[1] == 200
        mock_refresh.assert_called_once()

    @patch('openapi_server.impl.auth_mock.handle_auth_reset_password_post')
    def test_handle_auth_reset_password_post(self, mock_reset):
        """Test password reset handler"""
        mock_reset.return_value = ({'message': 'Reset email sent'}, 200)
        body = {'email': 'test@example.com'}

        result = handlers.handle_auth_reset_password_post(body)

        assert result[1] == 200
        mock_reset.assert_called_once()


class TestFamilyHandlers:
    """Test family-related handlers"""

    @patch('openapi_server.impl.handlers.create_flask_family_handler')
    def test_handle_family_list_get(self, mock_create_handler):
        """Test listing families"""
        mock_handler = Mock()
        mock_handler.list_families.return_value = ([{'familyId': '123'}], 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_family_list_get(user_id='user123')

        assert result[1] == 200
        mock_handler.list_families.assert_called_once_with(user_id='user123')

    @patch('openapi_server.impl.handlers.create_flask_family_handler')
    def test_handle_family_details_post(self, mock_create_handler):
        """Test creating a family"""
        mock_handler = Mock()
        mock_handler.create_family.return_value = ({'familyId': 'new123'}, 201)
        mock_create_handler.return_value = mock_handler

        body = {'familyName': 'Test Family', 'children': ['child1']}
        result = handlers.handle_family_details_post(body)

        assert result[1] == 201
        mock_handler.create_family.assert_called_once_with(body)

    @patch('openapi_server.impl.handlers.create_flask_family_handler')
    def test_handle_family_details_get(self, mock_create_handler):
        """Test getting a specific family"""
        mock_handler = Mock()
        mock_handler.get_family.return_value = ({'familyId': '123'}, 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_family_details_get('123')

        assert result[1] == 200
        mock_handler.get_family.assert_called_once_with('123')

    @patch('openapi_server.impl.handlers.create_flask_family_handler')
    def test_handle_family_details_delete(self, mock_create_handler):
        """Test deleting a family"""
        mock_handler = Mock()
        mock_handler.delete_family.return_value = (None, 204)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_family_details_delete('123')

        assert result[1] == 204
        mock_handler.delete_family.assert_called_once_with('123')

    def test_handle_create_family_alias(self):
        """Test that handle_create_family is an alias for handle_family_details_post"""
        # This should call the same function
        assert handlers.handle_create_family.__doc__ == "Alias for handle_family_details_post for forwarding compatibility"

    def test_handle_delete_family_alias(self):
        """Test that handle_delete_family is an alias for handle_family_details_delete"""
        # This should call the same function
        assert handlers.handle_delete_family.__doc__ == "Alias for handle_family_details_delete for forwarding compatibility"


class TestAnimalHandlers:
    """Test animal-related handlers"""

    @patch('openapi_server.impl.handlers.create_flask_animal_handler')
    def test_handle_animal_list_get(self, mock_create_handler):
        """Test listing animals"""
        mock_handler = Mock()
        mock_handler.list_animals.return_value = ([{'animalId': 'lion1'}], 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_animal_list_get()

        assert result[1] == 200
        mock_handler.list_animals.assert_called_once()

    @patch('openapi_server.impl.handlers.create_flask_animal_handler')
    def test_handle_animal_get(self, mock_create_handler):
        """Test getting a specific animal with multiple ID parameter names"""
        mock_handler = Mock()
        mock_handler.get_animal.return_value = ({'animalId': 'lion1'}, 200)
        mock_create_handler.return_value = mock_handler

        # Test with id parameter
        result = handlers.handle_animal_get(id='lion1')
        assert result[1] == 200

        # Test with id_ parameter (Connexion rename)
        result = handlers.handle_animal_get(id_='lion1')
        assert result[1] == 200

        # Test with animal_id parameter
        result = handlers.handle_animal_get(animal_id='lion1')
        assert result[1] == 200

    @patch('openapi_server.impl.handlers.create_flask_animal_handler')
    def test_handle_animal_post(self, mock_create_handler):
        """Test creating an animal"""
        mock_handler = Mock()
        mock_handler.create_animal.return_value = ({'animalId': 'new_lion'}, 201)
        mock_create_handler.return_value = mock_handler

        body = {'name': 'Leo', 'species': 'Lion'}
        result = handlers.handle_animal_post(body=body)

        assert result[1] == 201
        mock_handler.create_animal.assert_called_once_with(body)

    @patch('openapi_server.impl.handlers.create_flask_animal_handler')
    def test_handle_animal_delete(self, mock_create_handler):
        """Test deleting an animal (soft delete)"""
        mock_handler = Mock()
        mock_handler.delete_animal.return_value = (None, 204)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_animal_delete(animal_id='lion1')

        assert result[1] == 204
        mock_handler.delete_animal.assert_called_once_with('lion1')


class TestUserHandlers:
    """Test user-related handlers"""

    @patch('openapi_server.impl.handlers.create_flask_user_handler')
    def test_handle_user_list_get(self, mock_create_handler):
        """Test listing users"""
        mock_handler = Mock()
        mock_handler.list_users.return_value = ([{'userId': 'user1'}], 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_user_list_get()

        assert result[1] == 200
        mock_handler.list_users.assert_called_once()

    @patch('openapi_server.impl.handlers.create_flask_user_handler')
    def test_handle_user_details_get(self, mock_create_handler):
        """Test getting user details"""
        mock_handler = Mock()
        mock_handler.get_user.return_value = ({'userId': 'user1'}, 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_user_details_get('user1')

        assert result[1] == 200
        mock_handler.get_user.assert_called_once_with('user1')

    @patch('openapi_server.impl.handlers.create_flask_user_handler')
    def test_handle_user_details_post(self, mock_create_handler):
        """Test creating a user"""
        mock_handler = Mock()
        mock_handler.create_user.return_value = ({'userId': 'new_user'}, 201)
        mock_create_handler.return_value = mock_handler

        body = {'email': 'new@example.com', 'name': 'New User'}
        result = handlers.handle_user_details_post(body)

        assert result[1] == 201
        mock_handler.create_user.assert_called_once_with(body)

    @patch('openapi_server.impl.handlers.create_flask_user_handler')
    def test_handle_user_details_delete(self, mock_create_handler):
        """Test deleting a user (soft delete)"""
        mock_handler = Mock()
        mock_handler.delete_user.return_value = (None, 204)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_user_details_delete('user1')

        assert result[1] == 204
        mock_handler.delete_user.assert_called_once_with('user1')


class TestConversationHandlers:
    """Test conversation-related handlers"""

    @patch('openapi_server.impl.handlers.create_flask_conversation_handler')
    def test_handle_conversation_start_post(self, mock_create_handler):
        """Test starting a conversation"""
        mock_handler = Mock()
        mock_handler.start_conversation.return_value = ({'conversationId': 'conv123'}, 201)
        mock_create_handler.return_value = mock_handler

        body = {'animalId': 'lion1', 'userId': 'user1'}
        result = handlers.handle_conversation_start_post(body)

        assert result[1] == 201
        mock_handler.start_conversation.assert_called_once_with(body)

    @patch('openapi_server.impl.handlers.create_flask_conversation_handler')
    def test_handle_conversation_message_post(self, mock_create_handler):
        """Test sending a message in conversation"""
        mock_handler = Mock()
        mock_handler.send_message.return_value = ({'response': 'Hello!'}, 200)
        mock_create_handler.return_value = mock_handler

        body = {'message': 'Hi there!'}
        result = handlers.handle_conversation_message_post('conv123', body)

        assert result[1] == 200
        mock_handler.send_message.assert_called_once_with('conv123', body)


class TestErrorHandling:
    """Test error handling in handlers"""

    @patch('openapi_server.impl.handlers.create_flask_family_handler')
    def test_handle_exception_for_controllers(self, mock_create_handler):
        """Test exception handling"""
        mock_handler = Mock()
        mock_handler.list_families.side_effect = ValueError("Test error")
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_family_list_get()

        # Should return an error response
        assert result[1] >= 400  # Error status code
        assert 'error' in str(result[0]).lower() or 'Error' in str(result[0])


class TestDashboardHandlers:
    """Test dashboard and UI handlers"""

    @patch('openapi_server.impl.handlers.create_flask_ui_handler')
    def test_handle_admin_dashboard_get(self, mock_create_handler):
        """Test admin dashboard handler"""
        mock_handler = Mock()
        dashboard_data = {
            'totalUsers': 100,
            'totalAnimals': 24,
            'activeConversations': 5
        }
        mock_handler.get_admin_dashboard.return_value = (dashboard_data, 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_admin_dashboard_get()

        assert result[1] == 200
        assert result[0]['totalUsers'] == 100
        mock_handler.get_admin_dashboard.assert_called_once()

    @patch('openapi_server.impl.handlers.create_flask_ui_handler')
    def test_handle_index_get(self, mock_create_handler):
        """Test index page handler"""
        mock_handler = Mock()
        mock_handler.get_index.return_value = ({'message': 'Welcome'}, 200)
        mock_create_handler.return_value = mock_handler

        result = handlers.handle_index_get()

        assert result[1] == 200
        mock_handler.get_index.assert_called_once()


class TestSystemHandlers:
    """Test system and health check handlers"""

    def test_handle_health_get(self):
        """Test health check endpoint"""
        result = handlers.handle_health_get()

        assert result[1] == 200
        assert 'status' in result[0]

    def test_handle_system_info_get(self):
        """Test system info endpoint"""
        # This endpoint is not implemented yet
        result = handlers.handle_system_info_get()

        # Should return 501 Not Implemented
        assert result[1] == 501


class TestMediaHandlers:
    """Test media-related handlers"""

    @patch('openapi_server.impl.handlers.create_flask_media_handler')
    def test_handle_media_upload_post(self, mock_create_handler):
        """Test media upload handler"""
        mock_handler = Mock()
        mock_handler.upload_media.return_value = ({'mediaId': 'media123'}, 201)
        mock_create_handler.return_value = mock_handler

        file_data = {'file': 'test.jpg'}
        result = handlers.handle_media_upload_post(file_data)

        assert result[1] == 201
        mock_handler.upload_media.assert_called_once_with(file_data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
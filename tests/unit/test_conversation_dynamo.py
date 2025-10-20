"""
Unit tests for conversation_dynamo.py DynamoDB utilities
Tests infrastructure setup for PR003946-156
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime
import sys
import os

# Add the src path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/api/src/main/python')))


class TestConversationDynamo(unittest.TestCase):
    """Test DynamoDB conversation management utilities"""

    @patch('openapi_server.impl.utils.conversation_dynamo.dynamodb')
    def setUp(self, mock_dynamodb):
        """Set up test fixtures"""
        self.mock_table = Mock()
        mock_dynamodb.Table.return_value = self.mock_table

        # Import after patching
        from openapi_server.impl.utils import conversation_dynamo
        self.module = conversation_dynamo

    @patch('openapi_server.impl.utils.conversation_dynamo.uuid.uuid4')
    @patch('openapi_server.impl.utils.conversation_dynamo.datetime')
    def test_create_conversation_session(self, mock_datetime, mock_uuid):
        """Test creating a new conversation session"""
        # Setup
        mock_uuid.return_value = 'test-session-id'
        mock_datetime.utcnow.return_value.isoformat.return_value = '2025-09-18T12:00:00'

        # Execute
        session_id = self.module.create_conversation_session('user123', 'lion_001')

        # Assert
        self.assertEqual(session_id, 'test-session-id')
        self.mock_table.put_item.assert_called_once()

        # Verify item structure
        call_args = self.mock_table.put_item.call_args
        item = call_args[1]['Item']
        self.assertEqual(item['sessionId'], 'test-session-id')
        self.assertEqual(item['userId'], 'user123')
        self.assertEqual(item['animalId'], 'lion_001')
        self.assertEqual(item['status'], 'active')
        self.assertEqual(item['messageCount'], 0)

    @patch('openapi_server.impl.utils.conversation_dynamo.uuid.uuid4')
    @patch('openapi_server.impl.utils.conversation_dynamo.datetime')
    def test_store_conversation_turn(self, mock_datetime, mock_uuid):
        """Test storing a conversation turn"""
        # Setup
        mock_uuid.return_value = 'test-turn-id'
        mock_datetime.utcnow.return_value.isoformat.return_value = '2025-09-18T12:00:00'

        # Mock both tables
        conversations_table = Mock()
        sessions_table = Mock()

        with patch.object(self.module, 'get_conversations_table', return_value=conversations_table):
            with patch.object(self.module, 'get_sessions_table', return_value=sessions_table):
                # Execute
                turn_id = self.module.store_conversation_turn(
                    'session123',
                    'Hello!',
                    'Hi there!',
                    {'tokens': 10}
                )

        # Assert
        self.assertEqual(turn_id, 'test-turn-id')
        conversations_table.put_item.assert_called_once()
        sessions_table.update_item.assert_called_once()

        # Verify conversation item
        conv_item = conversations_table.put_item.call_args[1]['Item']
        self.assertEqual(conv_item['sessionId'], 'session123')
        self.assertEqual(conv_item['userMessage'], 'Hello!')
        self.assertEqual(conv_item['assistantReply'], 'Hi there!')
        self.assertEqual(conv_item['metadata'], {'tokens': 10})

    def test_get_conversation_history(self):
        """Test retrieving conversation history"""
        # Setup
        mock_response = {
            'Items': [
                {'turnId': '3', 'userMessage': 'Third', 'timestamp': '2025-09-18T12:03:00Z'},
                {'turnId': '2', 'userMessage': 'Second', 'timestamp': '2025-09-18T12:02:00Z'},
                {'turnId': '1', 'userMessage': 'First', 'timestamp': '2025-09-18T12:01:00Z'}
            ]
        }

        conversations_table = Mock()
        conversations_table.query.return_value = mock_response

        with patch.object(self.module, 'get_conversations_table', return_value=conversations_table):
            # Execute
            history = self.module.get_conversation_history('session123', limit=10)

        # Assert - should be reversed to chronological order
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['userMessage'], 'First')
        self.assertEqual(history[1]['userMessage'], 'Second')
        self.assertEqual(history[2]['userMessage'], 'Third')

    def test_check_user_access_admin(self):
        """Test admin access to any conversation"""
        # Admin should have access to any conversation
        has_access = self.module.check_user_access_to_session(
            'admin123',
            'any-session',
            'administrator'
        )
        self.assertTrue(has_access)

    def test_check_user_access_own_conversation(self):
        """Test user access to own conversation"""
        # Setup
        session_info = {'userId': 'user123'}

        with patch.object(self.module, 'get_session_info', return_value=session_info):
            # Execute
            has_access = self.module.check_user_access_to_session(
                'user123',
                'session123',
                'user'
            )

        # Assert
        self.assertTrue(has_access)

    def test_check_user_access_denied(self):
        """Test user denied access to other's conversation"""
        # Setup
        session_info = {'userId': 'other_user'}

        with patch.object(self.module, 'get_session_info', return_value=session_info):
            # Execute
            has_access = self.module.check_user_access_to_session(
                'user123',
                'session123',
                'user'
            )

        # Assert
        self.assertFalse(has_access)

    def test_get_conversation_analytics(self):
        """Test analytics generation for conversation"""
        # Setup
        session_info = {
            'startTime': '2025-09-18T12:00:00Z',
            'lastActivity': '2025-09-18T12:10:00Z'
        }

        history = [
            {'assistantReply': 'Hello there!'},
            {'assistantReply': 'How are you?'},
            {'assistantReply': 'Great!'}
        ]

        with patch.object(self.module, 'get_session_info', return_value=session_info):
            with patch.object(self.module, 'get_conversation_history', return_value=history):
                # Execute
                analytics = self.module.get_conversation_analytics('session123')

        # Assert
        self.assertEqual(analytics['sessionId'], 'session123')
        self.assertEqual(analytics['messageCount'], 3)
        self.assertEqual(analytics['userEngagement'], 'low')  # 3 messages = low
        self.assertGreater(analytics['averageResponseLength'], 0)


if __name__ == '__main__':
    unittest.main()
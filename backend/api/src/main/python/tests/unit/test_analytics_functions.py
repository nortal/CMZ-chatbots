"""
Unit tests for analytics.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests analytics functions including performance metrics, logging, billing,
time window validation, and business logic.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from openapi_server.impl.analytics import (
    handle_performance_metrics, handle_logs, handle_billing,
    _validate_time_window, _validate_billing_period,
    _get_mock_performance_metrics, _get_mock_logs, _get_mock_billing
)
from openapi_server.impl.error_handler import ValidationError


class TestHandlePerformanceMetrics:
    """Test handle_performance_metrics function with time window validation."""
    
    @patch('openapi_server.impl.analytics._get_mock_performance_metrics')
    @patch('openapi_server.impl.analytics._validate_time_window')
    def test_handle_performance_metrics_success(self, mock_validate, mock_get_metrics):
        """Test successful performance metrics retrieval."""
        start_dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_dt = datetime(2023, 1, 31, tzinfo=timezone.utc)
        mock_validate.return_value = (start_dt, end_dt)
        
        mock_metrics = {
            'timeWindow': {'start': '2023-01-01T00:00:00Z', 'end': '2023-01-31T00:00:00Z'},
            'totalRequests': 1000,
            'averageResponseTime': 250,
            'errorRate': 0.02
        }
        mock_get_metrics.return_value = mock_metrics
        
        result = handle_performance_metrics('2023-01-01T00:00:00Z', '2023-01-31T00:00:00Z')
        
        assert result[1] == 200
        assert result[0]['totalRequests'] == 1000
        assert result[0]['errorRate'] == 0.02
        mock_validate.assert_called_once_with('2023-01-01T00:00:00Z', '2023-01-31T00:00:00Z')
    
    @patch('openapi_server.impl.analytics._validate_time_window')
    def test_handle_performance_metrics_validation_error(self, mock_validate):
        """Test performance metrics fails with invalid time window."""
        mock_validate.side_effect = ValidationError(
            "Invalid time window",
            field_errors={'start': ['Invalid date format']}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            handle_performance_metrics('invalid_date', '2023-12-31T23:59:59Z')
        
        assert "Invalid time window" in str(exc_info.value)
        assert 'start' in exc_info.value.field_errors
    
    @patch('openapi_server.impl.analytics._get_mock_performance_metrics')
    @patch('openapi_server.impl.analytics._validate_time_window')
    def test_handle_performance_metrics_boundary_dates(self, mock_validate, mock_get_metrics):
        """Test performance metrics with boundary date values."""
        # Test same start and end date
        start_dt = datetime(2023, 6, 15, tzinfo=timezone.utc)
        end_dt = datetime(2023, 6, 15, tzinfo=timezone.utc)
        mock_validate.return_value = (start_dt, end_dt)
        mock_get_metrics.return_value = {'totalRequests': 0}
        
        result = handle_performance_metrics('2023-06-15T00:00:00Z', '2023-06-15T00:00:00Z')
        
        assert result[1] == 200
        mock_validate.assert_called_once()
        mock_get_metrics.assert_called_once_with(start_dt, end_dt)


class TestHandleLogs:
    """Test handle_logs function with log level and time filtering."""
    
    @patch('openapi_server.impl.analytics._get_mock_logs')
    @patch('openapi_server.impl.analytics._validate_time_window')
    def test_handle_logs_with_all_parameters(self, mock_validate, mock_get_logs):
        """Test logs retrieval with all parameters specified."""
        start_dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_dt = datetime(2023, 1, 31, tzinfo=timezone.utc)
        mock_validate.return_value = (start_dt, end_dt)
        
        mock_logs = {
            'logs': [
                {'timestamp': '2023-01-15T10:30:00Z', 'level': 'ERROR', 'message': 'Test error'},
                {'timestamp': '2023-01-16T11:45:00Z', 'level': 'ERROR', 'message': 'Another error'}
            ],
            'totalCount': 2
        }
        mock_get_logs.return_value = mock_logs
        
        result = handle_logs('ERROR', '2023-01-01T00:00:00Z', '2023-01-31T00:00:00Z')
        
        assert result[1] == 200
        assert result[0]['totalCount'] == 2
        assert len(result[0]['logs']) == 2
        assert all(log['level'] == 'ERROR' for log in result[0]['logs'])
        mock_validate.assert_called_once_with('2023-01-01T00:00:00Z', '2023-01-31T00:00:00Z', allow_none=True)
    
    @patch('openapi_server.impl.analytics._get_mock_logs')
    def test_handle_logs_level_only(self, mock_get_logs):
        """Test logs retrieval with only log level specified."""
        mock_logs = {'logs': [], 'totalCount': 0}
        mock_get_logs.return_value = mock_logs
        
        result = handle_logs('DEBUG')
        
        assert result[1] == 200
        mock_get_logs.assert_called_once()
    
    @patch('openapi_server.impl.analytics._get_mock_logs')
    def test_handle_logs_no_parameters(self, mock_get_logs):
        """Test logs retrieval with no parameters (defaults)."""
        mock_logs = {'logs': [], 'totalCount': 0}
        mock_get_logs.return_value = mock_logs
        
        result = handle_logs()
        
        assert result[1] == 200
        mock_get_logs.assert_called_once()
    
    @patch('openapi_server.impl.analytics._validate_time_window')
    def test_handle_logs_invalid_time_window(self, mock_validate):
        """Test logs fails with invalid time window."""
        mock_validate.side_effect = ValidationError(
            "Invalid time window",
            field_errors={'end': ['End date must be after start date']}
        )
        
        with pytest.raises(ValidationError):
            handle_logs('INFO', '2023-12-31T23:59:59Z', '2023-01-01T00:00:00Z')


class TestHandleBilling:
    """Test handle_billing function with period validation."""
    
    @patch('openapi_server.impl.analytics._get_mock_billing')
    @patch('openapi_server.impl.analytics._validate_billing_period')
    def test_handle_billing_with_valid_period(self, mock_validate, mock_get_billing):
        """Test billing retrieval with valid period."""
        mock_validate.return_value = None
        mock_billing = {
            'period': '2023-08',
            'totalCost': 125.50,
            'breakdown': {
                'compute': 75.25,
                'storage': 30.15,
                'networking': 20.10
            }
        }
        mock_get_billing.return_value = mock_billing
        
        result = handle_billing('2023-08')
        
        assert result[1] == 200
        assert result[0]['period'] == '2023-08'
        assert result[0]['totalCost'] == 125.50
        assert 'breakdown' in result[0]
        mock_validate.assert_called_once_with('2023-08')
    
    @patch('openapi_server.impl.analytics._get_mock_billing')
    def test_handle_billing_default_period(self, mock_get_billing):
        """Test billing retrieval with default (current) period."""
        current_month = datetime.now().strftime('%Y-%m')
        mock_billing = {'period': current_month, 'totalCost': 0}
        mock_get_billing.return_value = mock_billing
        
        result = handle_billing()  # No period specified
        
        assert result[1] == 200
        assert current_month in result[0]['period']
        mock_get_billing.assert_called_once_with(current_month)
    
    @patch('openapi_server.impl.analytics._validate_billing_period')
    def test_handle_billing_invalid_period(self, mock_validate):
        """Test billing fails with invalid period format."""
        mock_validate.side_effect = ValidationError(
            "Invalid period format",
            field_errors={'period': ['Period must be in YYYY-MM format']}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            handle_billing('invalid_format')
        
        assert "Invalid period format" in str(exc_info.value)
        assert 'period' in exc_info.value.field_errors


class TestValidateTimeWindow:
    """Test _validate_time_window function for date validation."""
    
    def test_validate_time_window_valid_range(self):
        """Test time window validation with valid date range."""
        start_str = '2023-01-01T00:00:00Z'
        end_str = '2023-01-31T23:59:59Z'
        
        start_dt, end_dt = _validate_time_window(start_str, end_str)
        
        assert isinstance(start_dt, datetime)
        assert isinstance(end_dt, datetime)
        assert start_dt < end_dt
        assert start_dt.tzinfo == timezone.utc
        assert end_dt.tzinfo == timezone.utc
    
    def test_validate_time_window_invalid_start_format(self):
        """Test time window validation fails with invalid start date format."""
        with pytest.raises(ValidationError) as exc_info:
            _validate_time_window('invalid_date', '2023-12-31T23:59:59Z')
        
        error = exc_info.value
        assert "Invalid date format" in error.message
        assert 'start' in error.field_errors
    
    def test_validate_time_window_invalid_end_format(self):
        """Test time window validation fails with invalid end date format."""
        with pytest.raises(ValidationError) as exc_info:
            _validate_time_window('2023-01-01T00:00:00Z', 'invalid_date')
        
        error = exc_info.value
        assert "Invalid date format" in error.message
        assert 'end' in error.field_errors
    
    def test_validate_time_window_end_before_start(self):
        """Test time window validation fails when end is before start."""
        with pytest.raises(ValidationError) as exc_info:
            _validate_time_window('2023-12-31T23:59:59Z', '2023-01-01T00:00:00Z')
        
        error = exc_info.value
        assert any('after' in str(errors).lower() for errors in error.field_errors.values())
    
    def test_validate_time_window_same_datetime(self):
        """Test time window validation with same start and end datetime."""
        same_time = '2023-06-15T12:00:00Z'
        
        start_dt, end_dt = _validate_time_window(same_time, same_time)
        
        assert start_dt == end_dt
        assert isinstance(start_dt, datetime)
    
    def test_validate_time_window_allow_none_true(self):
        """Test time window validation with allow_none=True."""
        # Should handle None values when allow_none=True
        start_dt, end_dt = _validate_time_window(None, None, allow_none=True)
        
        assert isinstance(start_dt, datetime)
        assert isinstance(end_dt, datetime)
        assert start_dt <= end_dt
    
    def test_validate_time_window_allow_none_false(self):
        """Test time window validation with allow_none=False (default)."""
        with pytest.raises(ValidationError):
            _validate_time_window(None, '2023-12-31T23:59:59Z', allow_none=False)


class TestValidateBillingPeriod:
    """Test _validate_billing_period function for period format validation."""
    
    def test_validate_billing_period_valid_format(self):
        """Test billing period validation with valid YYYY-MM format."""
        valid_periods = ['2023-01', '2023-12', '2024-06', '2022-11']
        
        for period in valid_periods:
            # Should not raise any exception
            _validate_billing_period(period)  # Returns None, just checking no exception
    
    def test_validate_billing_period_invalid_format(self):
        """Test billing period validation fails with invalid format."""
        invalid_formats = [
            'invalid_format',
            '2023/01',
            '2023',
            '23-01',
            '2023-1',
            '2023-001'
        ]
        
        for invalid_format in invalid_formats:
            with pytest.raises(ValidationError) as exc_info:
                _validate_billing_period(invalid_format)
            
            error = exc_info.value
            assert 'YYYY-MM' in str(error.field_errors.get('period', []))
    
    def test_validate_billing_period_invalid_month(self):
        """Test billing period validation fails with invalid month."""
        invalid_months = ['2023-00', '2023-13', '2023-99']
        
        for invalid_month in invalid_months:
            with pytest.raises(ValidationError) as exc_info:
                _validate_billing_period(invalid_month)
            
            error = exc_info.value
            assert any('month' in str(errors).lower() for errors in error.field_errors.values())
    
    def test_validate_billing_period_boundary_months(self):
        """Test billing period validation with boundary month values."""
        boundary_cases = ['2023-01', '2023-12']  # Valid boundaries
        
        for period in boundary_cases:
            # Should not raise any exception
            _validate_billing_period(period)  # Returns None, just checking no exception


class TestMockDataGenerators:
    """Test mock data generation functions."""
    
    def test_get_mock_performance_metrics(self):
        """Test performance metrics mock data generation."""
        start_dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_dt = datetime(2023, 1, 31, tzinfo=timezone.utc)
        
        result = _get_mock_performance_metrics(start_dt, end_dt)
        
        assert 'timeWindow' in result
        assert 'totalRequests' in result
        assert 'averageResponseTime' in result
        assert 'errorRate' in result
        assert isinstance(result['totalRequests'], int)
        assert isinstance(result['averageResponseTime'], (int, float))
        assert isinstance(result['errorRate'], (int, float))
        assert 0 <= result['errorRate'] <= 1  # Error rate should be a percentage
    
    def test_get_mock_logs(self):
        """Test logs mock data generation."""
        start_dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_dt = datetime(2023, 1, 31, tzinfo=timezone.utc)
        
        result = _get_mock_logs('ERROR', start_dt, end_dt, page=1, page_size=10)
        
        assert 'logs' in result
        assert 'totalCount' in result
        assert isinstance(result['logs'], list)
        assert isinstance(result['totalCount'], int)
        assert len(result['logs']) <= 10  # Respects limit
        
        for log_entry in result['logs']:
            assert 'timestamp' in log_entry
            assert 'level' in log_entry
            assert 'message' in log_entry
    
    def test_get_mock_billing(self):
        """Test billing mock data generation."""
        period = '2023-08'
        
        result = _get_mock_billing(period)
        
        assert 'period' in result
        assert 'totalCost' in result
        assert 'breakdown' in result
        assert result['period'] == period
        assert isinstance(result['totalCost'], (int, float))
        assert isinstance(result['breakdown'], dict)
        assert result['totalCost'] >= 0  # Cost should be non-negative


class TestAnalyticsFunctionIntegration:
    """Integration tests for analytics functions working together."""
    
    @patch('openapi_server.impl.analytics._get_mock_performance_metrics')
    @patch('openapi_server.impl.analytics._get_mock_logs')
    def test_performance_and_logs_same_time_window(self, mock_logs, mock_metrics):
        """Test performance metrics and logs for same time window."""
        time_window_start = '2023-06-01T00:00:00Z'
        time_window_end = '2023-06-30T23:59:59Z'
        
        mock_metrics.return_value = {'totalRequests': 5000, 'errorRate': 0.05}
        mock_logs.return_value = {'logs': [], 'totalCount': 250}  # 5% of 5000 requests
        
        # Get performance metrics
        perf_result = handle_performance_metrics(time_window_start, time_window_end)
        assert perf_result[1] == 200
        
        # Get error logs for same period
        logs_result = handle_logs('ERROR', time_window_start, time_window_end)
        assert logs_result[1] == 200
        
        # Error rate should correlate with error log count
        error_rate = perf_result[0]['errorRate']
        total_requests = perf_result[0]['totalRequests']
        expected_errors = int(total_requests * error_rate)
        actual_error_count = logs_result[0]['totalCount']
        
        # Allow for some variance in mock data
        assert abs(expected_errors - actual_error_count) <= expected_errors * 0.1
    
    def test_billing_period_consistency(self):
        """Test billing period consistency across calls."""
        period = '2023-11'
        
        # Call billing multiple times with same period
        result1 = handle_billing(period)
        result2 = handle_billing(period)
        
        assert result1[1] == result2[1] == 200
        assert result1[0]['period'] == result2[0]['period'] == period
        # Results should be consistent for same period
        assert result1[0]['totalCost'] == result2[0]['totalCost']
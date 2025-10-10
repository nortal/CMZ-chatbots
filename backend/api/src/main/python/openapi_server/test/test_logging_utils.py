"""
Unit tests for logging_utils security functions
"""
import pytest
from openapi_server.impl.utils.logging_utils import (
    sanitize_log_value,
    sanitize_log_extra
)


class TestSanitizeLogValue:
    """Tests for sanitize_log_value function"""

    def test_removes_newlines(self):
        """Test that newlines are removed"""
        malicious = "user123\nFAKE LOG: Admin access granted"
        result = sanitize_log_value(malicious)
        assert '\n' not in result
        assert '\r' not in result
        assert result == "user123 FAKE LOG: Admin access granted"

    def test_removes_carriage_returns(self):
        """Test that carriage returns are removed"""
        malicious = "user123\rFAKE LOG: Admin access granted"
        result = sanitize_log_value(malicious)
        assert '\r' not in result
        assert result == "user123 FAKE LOG: Admin access granted"

    def test_removes_null_bytes(self):
        """Test that null bytes are removed"""
        malicious = "user123\x00malicious"
        result = sanitize_log_value(malicious)
        assert '\x00' not in result
        assert result == "user123malicious"

    def test_removes_ansi_escape_sequences(self):
        """Test that ANSI color codes are removed"""
        malicious = "user123\x1b[31mRED TEXT\x1b[0m"
        result = sanitize_log_value(malicious)
        assert '\x1b' not in result
        assert result == "user123RED TEXT"

    def test_truncates_long_strings(self):
        """Test that very long strings are truncated"""
        long_string = "A" * 600
        result = sanitize_log_value(long_string)
        assert len(result) <= 520  # 500 + "...[truncated]"
        assert result.endswith("...[truncated]")

    def test_handles_none(self):
        """Test that None is handled safely"""
        result = sanitize_log_value(None)
        assert result == "None"

    def test_handles_integers(self):
        """Test that integers are converted properly"""
        result = sanitize_log_value(12345)
        assert result == "12345"

    def test_safe_string_unchanged(self):
        """Test that safe strings pass through"""
        safe_string = "user_12345_safe"
        result = sanitize_log_value(safe_string)
        assert result == safe_string


class TestSanitizeLogExtra:
    """Tests for sanitize_log_extra function"""

    def test_sanitizes_all_values(self):
        """Test that all dictionary values are sanitized"""
        malicious_dict = {
            "user_id": "user123\nFAKE LOG",
            "family_id": "family456\rANOTHER FAKE",
            "action": "safe_value"
        }
        result = sanitize_log_extra(malicious_dict)

        assert '\n' not in result["user_id"]
        assert '\r' not in result["family_id"]
        assert result["action"] == "safe_value"

    def test_preserves_keys(self):
        """Test that dictionary keys are preserved"""
        test_dict = {"user_id": "test", "family_id": "test2"}
        result = sanitize_log_extra(test_dict)

        assert set(result.keys()) == {"user_id", "family_id"}

    def test_empty_dict(self):
        """Test that empty dict is handled"""
        result = sanitize_log_extra({})
        assert result == {}


class TestLogInjectionPrevention:
    """Integration tests for log injection attack prevention"""

    def test_prevents_log_injection_attack(self):
        """
        Test that a real log injection attack is prevented
        """
        # Attacker tries to inject a fake admin login
        attack_payload = "user123\n[2024-01-01 10:00:00] INFO - Admin user admin@example.com logged in successfully"

        sanitized = sanitize_log_value(attack_payload)

        # The newline should be removed, preventing multi-line log injection
        assert '\n' not in sanitized
        # The attack payload is now on the same line and clearly part of the original value
        assert "INFO - Admin user" in sanitized

    def test_prevents_log_forgery(self):
        """
        Test that log forgery attempts are neutralized
        """
        attack = "innocentuser\n\n[ERROR] Database credentials leaked: password=secret123"

        sanitized = sanitize_log_value(attack)

        # Multiple newlines should be replaced
        assert '\n' not in sanitized
        # Content is preserved but can't create fake log entries
        assert "Database credentials leaked" in sanitized

    def test_defense_in_depth_pattern(self):
        """
        Test that the defense-in-depth pattern (replace + sanitize) works correctly
        """
        # Simulate the pattern used in production code
        user_id = "user123\n[FAKE LOG]\x1b[31mRED\x1b[0m\x00null"

        # Step 1: CodeQL-recognized sanitization (what CodeQL sees)
        step1 = str(user_id).replace("\n", " ").replace("\r", " ")
        assert '\n' not in step1
        assert '\r' not in step1

        # Step 2: Comprehensive sanitization (additional protection)
        step2 = sanitize_log_extra({"user_id": step1})

        # Verify all attack vectors are neutralized
        result = step2["user_id"]
        assert '\n' not in result  # Newlines removed by replace
        assert '\x1b' not in result  # ANSI codes removed by sanitize
        assert '\x00' not in result  # Null bytes removed by sanitize
        assert '[FAKE LOG]' in result  # Content preserved
        assert 'RED' in result  # Content preserved (without color codes)

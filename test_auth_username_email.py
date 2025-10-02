#!/usr/bin/env python3
"""
Simple contract test to verify auth endpoint accepts both username and email fields.
Run this to prevent auth regressions.
"""
import requests
import sys

BASE_URL = "http://localhost:8080"
TEST_USER = "test@cmz.org"
TEST_PASSWORD = "testpass123"

def test_auth_with_username():
    """Test auth with username field (backend expects this)"""
    print("Testing auth with 'username' field...", end=" ")
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": TEST_USER, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        print("✅ PASSED")
        return True
    else:
        print(f"❌ FAILED - Status: {response.status_code}, Response: {response.text}")
        return False

def test_auth_with_email():
    """Test auth with email field (frontend sends this)"""
    print("Testing auth with 'email' field...", end=" ")
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"email": TEST_USER, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        print("✅ PASSED")
        return True
    else:
        print(f"❌ FAILED - Status: {response.status_code}, Response: {response.text}")
        return False

def test_auth_with_both():
    """Test auth with both fields (email should take precedence)"""
    print("Testing auth with both fields...", end=" ")
    response = requests.post(
        f"{BASE_URL}/auth",
        json={
            "email": TEST_USER,
            "username": "wrong@example.com",
            "password": TEST_PASSWORD
        }
    )
    if response.status_code == 200:
        print("✅ PASSED")
        return True
    else:
        print(f"❌ FAILED - Status: {response.status_code}")
        return False

def test_jwt_format():
    """Test JWT is in correct 3-part format"""
    print("Testing JWT format...", end=" ")
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"email": TEST_USER, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        token = data.get("token", "")
        parts = token.split(".")
        if len(parts) == 3:
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED - JWT has {len(parts)} parts, expected 3")
            return False
    else:
        print(f"❌ FAILED - Auth failed")
        return False

def main():
    print("=" * 60)
    print("AUTH ENDPOINT CONTRACT TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print()

    tests = [
        test_auth_with_username,
        test_auth_with_email,
        test_auth_with_both,
        test_jwt_format
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED - Cannot connect to server at {BASE_URL}")
            failed += 1
        except Exception as e:
            print(f"❌ FAILED - {str(e)}")
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")

    if failed > 0:
        print("\n⚠️  AUTH CONTRACT VIOLATION!")
        print("The auth endpoint MUST accept both 'username' and 'email' fields.")
        print("This is critical to prevent frontend-backend mismatches.")
        return 1
    else:
        print("\n✅ All auth contract tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
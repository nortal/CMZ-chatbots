"""
Demonstration tests using cURL client for real API testing
Shows actual HTTP requests and responses with complete logging
"""

import pytest
import json


class TestCurlApiDemo:
    """Demo tests using real cURL commands against running API"""
    
    def test_api_root_endpoint(self, curl_client, api_logger):
        """Test the API root endpoint with cURL"""
        response = curl_client.get("/")
        api_logger.log_request(curl_client, "API Root Endpoint")
        
        assert response.status_code == 200
        data = response.json()
        # Check if we get some kind of API info response
        assert isinstance(data, (dict, list))
        
    def test_openapi_spec_endpoint(self, curl_client, api_logger):
        """Test OpenAPI spec endpoint availability"""
        response = curl_client.get("/ui")
        api_logger.log_request(curl_client, "OpenAPI UI Endpoint")
        
        # Should at least be accessible, might return HTML
        assert response.status_code in [200, 404, 501]
        
    def test_nonexistent_endpoint(self, curl_client, api_logger):
        """Test 404 error response format with cURL"""
        response = curl_client.get("/non_existent_endpoint")
        api_logger.log_request(curl_client, "Non-existent Endpoint (404 Test)")
        
        assert response.status_code == 404
        data = response.json()
        
        # Log what error format we actually get
        print(f"\n404 Error format received: {json.dumps(data, indent=2)}")
        
    def test_user_endpoint_structure(self, curl_client, api_logger):
        """Test user-related endpoints structure"""
        # Test GET /user (should exist based on OpenAPI spec)
        response = curl_client.get("/user")
        api_logger.log_request(curl_client, "GET /user endpoint")
        
        # Document what we get - could be 200, 401, 404, 501
        print(f"\nGET /user returned: {response.status_code}")
        if response.status_code != 500:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
    def test_animal_endpoints(self, curl_client, api_logger):
        """Test animal-related endpoints"""
        # Test animal list endpoint
        response = curl_client.get("/animal_list")
        api_logger.log_request(curl_client, "GET /animal_list endpoint")
        
        print(f"\nGET /animal_list returned: {response.status_code}")
        if response.status_code != 500:
            data = response.json()
            print(f"Response type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of animals: {len(data)}")
            elif isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                
    def test_auth_endpoint_structure(self, curl_client, api_logger):
        """Test authentication endpoint behavior"""
        # Test without credentials
        response = curl_client.post("/auth", json={"invalid": "data"})
        api_logger.log_request(curl_client, "POST /auth with invalid data")
        
        print(f"\nPOST /auth returned: {response.status_code}")
        data = response.json()
        print(f"Auth error response: {json.dumps(data, indent=2)}")
        
    def test_api_health_check(self, curl_client, api_logger):
        """Test if API has any health or status endpoints"""
        for endpoint in ["/health", "/status", "/ping", "/system_health"]:
            response = curl_client.get(endpoint)
            api_logger.log_request(curl_client, f"Health check: {endpoint}")
            
            if response.status_code == 200:
                print(f"\n✅ Health endpoint found: {endpoint}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                break
        else:
            print("\n❌ No standard health endpoints found")
            
    def test_error_response_consistency(self, curl_client, api_logger):
        """Test error response format consistency across different endpoints"""
        test_endpoints = [
            ("/invalid_endpoint", "GET"),
            ("/user/999999", "GET"),
            ("/auth", "POST"),  # No data
            ("/family", "DELETE")  # Wrong method
        ]
        
        error_formats = {}
        
        for endpoint, method in test_endpoints:
            if method == "GET":
                response = curl_client.get(endpoint)
            elif method == "POST":
                response = curl_client.post(endpoint)
            elif method == "DELETE":
                response = curl_client.delete(endpoint)
                
            api_logger.log_request(curl_client, f"{method} {endpoint} - Error Format Test")
            
            if 400 <= response.status_code < 600:
                error_formats[f"{method} {endpoint}"] = {
                    "status": response.status_code,
                    "format": response.json()
                }
                
        # Print summary of error formats
        print(f"\n📋 Error Response Format Analysis:")
        for endpoint, info in error_formats.items():
            print(f"\n{endpoint}: {info['status']}")
            print(f"  Format: {list(info['format'].keys())}")
            
    @pytest.fixture(autouse=True)  
    def save_logs_after_test(self, api_logger):
        """Save cURL logs after each test"""
        yield  # Test runs here
        # Save logs to file
        api_logger.save_logs("reports/curl_api_logs.json")
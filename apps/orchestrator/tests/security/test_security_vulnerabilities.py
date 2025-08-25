"""
Security Tests
Tests for vulnerabilities, dependency scanning, secret scanning, and signed URL scope.
"""
import pytest
import subprocess
import json
import re
import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import structlog
import aiohttp
import asyncio
from pathlib import Path

logger = structlog.get_logger()

class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    CSRF = "cross_site_request_forgery"
    AUTHENTICATION = "authentication_bypass"
    AUTHORIZATION = "authorization_bypass"
    DEPENDENCY = "dependency_vulnerability"
    SECRET_EXPOSURE = "secret_exposure"
    SIGNED_URL_SCOPE = "signed_url_scope"
    INPUT_VALIDATION = "input_validation"
    RATE_LIMITING = "rate_limiting"

@dataclass
class SecurityTestResult:
    """Result of a security test."""
    test_name: str
    vulnerability_type: VulnerabilityType
    severity: str  # low, medium, high, critical
    detected: bool
    description: str
    remediation: Optional[str] = None
    cve_id: Optional[str] = None
    affected_component: Optional[str] = None

class SecurityTestRunner:
    """Runner for security tests."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[SecurityTestResult] = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_all_security_tests(self) -> List[SecurityTestResult]:
        """Run all security tests."""
        logger.info("Starting security test suite")
        
        tests = [
            self.test_sql_injection,
            self.test_xss_vulnerabilities,
            self.test_csrf_protection,
            self.test_authentication_bypass,
            self.test_authorization_bypass,
            self.test_dependency_vulnerabilities,
            self.test_secret_scanning,
            self.test_signed_url_scope,
            self.test_input_validation,
            self.test_rate_limiting,
            self.test_jwt_security,
            self.test_api_security_headers,
        ]
        
        for test in tests:
            try:
                result = await test()
                self.test_results.append(result)
                logger.info(f"Security test {test.__name__} completed", 
                           detected=result.detected, 
                           severity=result.severity)
            except Exception as e:
                logger.error(f"Security test {test.__name__} failed", error=str(e))
                self.test_results.append(SecurityTestResult(
                    test_name=test.__name__,
                    vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
                    severity="unknown",
                    detected=True,
                    description=f"Test failed: {str(e)}"
                ))
        
        return self.test_results
    
    async def test_sql_injection(self) -> SecurityTestResult:
        """Test for SQL injection vulnerabilities."""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "1' OR '1' = '1' --",
        ]
        
        vulnerable_endpoints = []
        
        # Test login endpoint
        for payload in sql_payloads:
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"email": payload, "password": "test"}
                ) as response:
                    if response.status == 500:  # SQL error might indicate vulnerability
                        vulnerable_endpoints.append("login")
                        break
            except Exception:
                continue
        
        # Test search endpoints
        search_endpoints = [
            "/api/v1/nutrition/foods/search",
            "/api/v1/training/exercises/search",
        ]
        
        for endpoint in search_endpoints:
            for payload in sql_payloads:
                try:
                    async with self.session.get(
                        f"{self.base_url}{endpoint}?q={payload}"
                    ) as response:
                        if response.status == 500:
                            vulnerable_endpoints.append(endpoint)
                            break
                except Exception:
                    continue
        
        detected = len(vulnerable_endpoints) > 0
        
        return SecurityTestResult(
            test_name="sql_injection",
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            severity="critical" if detected else "low",
            detected=detected,
            description=f"SQL injection vulnerabilities detected in: {vulnerable_endpoints}" if detected else "No SQL injection vulnerabilities detected",
            remediation="Use parameterized queries and input validation" if detected else None,
            affected_component="API endpoints" if detected else None
        )
    
    async def test_xss_vulnerabilities(self) -> SecurityTestResult:
        """Test for XSS vulnerabilities."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
        ]
        
        vulnerable_endpoints = []
        
        # Test endpoints that might reflect user input
        test_endpoints = [
            ("/api/v1/check-ins", "POST", {"notes": ""}),
            ("/api/v1/habits/track", "POST", {"notes": ""}),
            ("/api/v1/nutrition/log", "POST", {"notes": ""}),
        ]
        
        for endpoint, method, base_data in test_endpoints:
            for payload in xss_payloads:
                try:
                    data = {**base_data, "notes": payload}
                    if method == "POST":
                        async with self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=data
                        ) as response:
                            if response.status == 201:
                                # Check if payload is reflected in response
                                response_text = await response.text()
                                if payload in response_text:
                                    vulnerable_endpoints.append(endpoint)
                                    break
                except Exception:
                    continue
        
        detected = len(vulnerable_endpoints) > 0
        
        return SecurityTestResult(
            test_name="xss_vulnerabilities",
            vulnerability_type=VulnerabilityType.XSS,
            severity="high" if detected else "low",
            detected=detected,
            description=f"XSS vulnerabilities detected in: {vulnerable_endpoints}" if detected else "No XSS vulnerabilities detected",
            remediation="Sanitize user input and use CSP headers" if detected else None,
            affected_component="API endpoints" if detected else None
        )
    
    async def test_csrf_protection(self) -> SecurityTestResult:
        """Test for CSRF protection."""
        # Test if endpoints require CSRF tokens
        csrf_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/check-ins",
            "/api/v1/programs/generate",
        ]
        
        vulnerable_endpoints = []
        
        for endpoint in csrf_endpoints:
            try:
                # Try to make request without CSRF token
                async with self.session.post(
                    f"{self.base_url}{endpoint}",
                    json={"test": "data"}
                ) as response:
                    # If request succeeds without CSRF token, it might be vulnerable
                    if response.status in [200, 201, 202]:
                        vulnerable_endpoints.append(endpoint)
            except Exception:
                continue
        
        detected = len(vulnerable_endpoints) > 0
        
        return SecurityTestResult(
            test_name="csrf_protection",
            vulnerability_type=VulnerabilityType.CSRF,
            severity="medium" if detected else "low",
            detected=detected,
            description=f"CSRF protection missing in: {vulnerable_endpoints}" if detected else "CSRF protection is in place",
            remediation="Implement CSRF tokens and validate origin headers" if detected else None,
            affected_component="API endpoints" if detected else None
        )
    
    async def test_authentication_bypass(self) -> SecurityTestResult:
        """Test for authentication bypass vulnerabilities."""
        protected_endpoints = [
            "/api/v1/users/profile",
            "/api/v1/programs",
            "/api/v1/check-ins",
            "/api/v1/nutrition",
            "/api/v1/training",
        ]
        
        bypassed_endpoints = []
        
        for endpoint in protected_endpoints:
            try:
                # Try to access without authentication
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:  # Should be 401
                        bypassed_endpoints.append(endpoint)
            except Exception:
                continue
        
        detected = len(bypassed_endpoints) > 0
        
        return SecurityTestResult(
            test_name="authentication_bypass",
            vulnerability_type=VulnerabilityType.AUTHENTICATION,
            severity="critical" if detected else "low",
            detected=detected,
            description=f"Authentication bypass in: {bypassed_endpoints}" if detected else "Authentication is properly enforced",
            remediation="Implement proper authentication middleware" if detected else None,
            affected_component="Protected endpoints" if detected else None
        )
    
    async def test_authorization_bypass(self) -> SecurityTestResult:
        """Test for authorization bypass vulnerabilities."""
        # Test if users can access other users' data
        test_user_id = "test_user_1"
        other_user_id = "test_user_2"
        
        bypassed_endpoints = []
        
        # Test endpoints that should be user-specific
        user_specific_endpoints = [
            f"/api/v1/users/{other_user_id}/profile",
            f"/api/v1/programs/{other_user_id}",
            f"/api/v1/check-ins/{other_user_id}",
        ]
        
        # Create a valid token for test_user_1
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": "test1@example.com", "password": "password123"}
            ) as response:
                if response.status == 200:
                    token = response.json().get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Try to access other user's data
                    for endpoint in user_specific_endpoints:
                        async with self.session.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers
                        ) as response:
                            if response.status == 200:  # Should be 403
                                bypassed_endpoints.append(endpoint)
        except Exception:
            pass
        
        detected = len(bypassed_endpoints) > 0
        
        return SecurityTestResult(
            test_name="authorization_bypass",
            vulnerability_type=VulnerabilityType.AUTHORIZATION,
            severity="critical" if detected else "low",
            detected=detected,
            description=f"Authorization bypass in: {bypassed_endpoints}" if detected else "Authorization is properly enforced",
            remediation="Implement proper authorization checks" if detected else None,
            affected_component="User-specific endpoints" if detected else None
        )
    
    async def test_dependency_vulnerabilities(self) -> SecurityTestResult:
        """Test for known vulnerabilities in dependencies."""
        try:
            # Run safety check (if available)
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                detected = len(vulnerabilities) > 0
                
                return SecurityTestResult(
                    test_name="dependency_vulnerabilities",
                    vulnerability_type=VulnerabilityType.DEPENDENCY,
                    severity="high" if detected else "low",
                    detected=detected,
                    description=f"Found {len(vulnerabilities)} dependency vulnerabilities" if detected else "No dependency vulnerabilities found",
                    remediation="Update vulnerable dependencies" if detected else None,
                    cve_id=", ".join([v.get("cve_id", "") for v in vulnerabilities]) if detected else None
                )
            else:
                # Fallback: check requirements files
                requirements_files = ["requirements.txt", "pyproject.toml"]
                vulnerable_deps = []
                
                for req_file in requirements_files:
                    if Path(req_file).exists():
                        # Simple check for known vulnerable packages
                        with open(req_file, 'r') as f:
                            content = f.read()
                            if any(dep in content for dep in ["django<2.2", "flask<1.1", "requests<2.25"]):
                                vulnerable_deps.append(req_file)
                
                detected = len(vulnerable_deps) > 0
                
                return SecurityTestResult(
                    test_name="dependency_vulnerabilities",
                    vulnerability_type=VulnerabilityType.DEPENDENCY,
                    severity="medium" if detected else "low",
                    detected=detected,
                    description=f"Potentially vulnerable dependencies in: {vulnerable_deps}" if detected else "No obvious dependency vulnerabilities",
                    remediation="Update to latest secure versions" if detected else None
                )
                
        except Exception as e:
            return SecurityTestResult(
                test_name="dependency_vulnerabilities",
                vulnerability_type=VulnerabilityType.DEPENDENCY,
                severity="unknown",
                detected=True,
                description=f"Could not check dependencies: {str(e)}",
                remediation="Install safety tool and run manual checks"
            )
    
    async def test_secret_scanning(self) -> SecurityTestResult:
        """Scan for exposed secrets in code."""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'][^"\']+["\']',
            r'aws_access_key_id\s*=\s*["\'][^"\']+["\']',
            r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']',
        ]
        
        exposed_secrets = []
        
        # Scan Python files
        for py_file in Path(".").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            exposed_secrets.append(f"{py_file}: {matches}")
            except Exception:
                continue
        
        # Scan configuration files
        config_files = [".env", ".env.example", "config.json", "settings.py"]
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in secret_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                exposed_secrets.append(f"{config_file}: {matches}")
                except Exception:
                    continue
        
        detected = len(exposed_secrets) > 0
        
        return SecurityTestResult(
            test_name="secret_scanning",
            vulnerability_type=VulnerabilityType.SECRET_EXPOSURE,
            severity="critical" if detected else "low",
            detected=detected,
            description=f"Exposed secrets found in: {exposed_secrets}" if detected else "No exposed secrets found",
            remediation="Remove secrets from code and use environment variables" if detected else None,
            affected_component="Source code and config files" if detected else None
        )
    
    async def test_signed_url_scope(self) -> SecurityTestResult:
        """Test signed URL scope and security."""
        # Test if signed URLs can be tampered with
        test_url = f"{self.base_url}/api/v1/reports/download/test_report.pdf"
        
        # Try to access without proper signature
        try:
            async with self.session.get(test_url) as response:
                if response.status == 200:  # Should be 403 or 401
                    detected = True
                else:
                    detected = False
        except Exception:
            detected = False
        
        # Test URL parameter tampering
        tampered_url = f"{test_url}?user_id=other_user&expires=9999999999"
        try:
            async with self.session.get(tampered_url) as response:
                if response.status == 200:  # Should be 403
                    detected = True
        except Exception:
            pass
        
        return SecurityTestResult(
            test_name="signed_url_scope",
            vulnerability_type=VulnerabilityType.SIGNED_URL_SCOPE,
            severity="high" if detected else "low",
            detected=detected,
            description="Signed URL scope bypass detected" if detected else "Signed URL scope is properly enforced",
            remediation="Implement proper URL signing and validation" if detected else None,
            affected_component="File download endpoints" if detected else None
        )
    
    async def test_input_validation(self) -> SecurityTestResult:
        """Test input validation and sanitization."""
        malicious_inputs = [
            {"email": "test@example.com<script>alert('XSS')</script>"},
            {"weight": "75'; DROP TABLE users; --"},
            {"age": "25 OR 1=1"},
            {"notes": "x" * 10000},  # Very long input
            {"file": "malicious.exe"},
        ]
        
        validation_failures = []
        
        # Test various endpoints
        test_endpoints = [
            ("/api/v1/auth/register", "POST"),
            ("/api/v1/check-ins", "POST"),
            ("/api/v1/nutrition/log", "POST"),
        ]
        
        for endpoint, method in test_endpoints:
            for malicious_input in malicious_inputs:
                try:
                    if method == "POST":
                        async with self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=malicious_input
                        ) as response:
                            if response.status in [200, 201]:  # Should be 422
                                validation_failures.append(f"{endpoint}: {malicious_input}")
                except Exception:
                    continue
        
        detected = len(validation_failures) > 0
        
        return SecurityTestResult(
            test_name="input_validation",
            vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
            severity="medium" if detected else "low",
            detected=detected,
            description=f"Input validation failures: {validation_failures}" if detected else "Input validation is working properly",
            remediation="Implement proper input validation and sanitization" if detected else None,
            affected_component="API endpoints" if detected else None
        )
    
    async def test_rate_limiting(self) -> SecurityTestResult:
        """Test rate limiting implementation."""
        # Try to make many requests quickly
        rapid_requests = []
        
        for i in range(100):
            try:
                async with self.session.get(f"{self.base_url}/api/v1/health") as response:
                    rapid_requests.append(response.status)
            except Exception:
                rapid_requests.append(0)
        
        # Check if rate limiting kicked in
        rate_limited = any(status == 429 for status in rapid_requests)
        
        return SecurityTestResult(
            test_name="rate_limiting",
            vulnerability_type=VulnerabilityType.RATE_LIMITING,
            severity="medium" if not rate_limited else "low",
            detected=not rate_limited,
            description="Rate limiting not properly implemented" if not rate_limited else "Rate limiting is working properly",
            remediation="Implement proper rate limiting" if not rate_limited else None,
            affected_component="API endpoints" if not rate_limited else None
        )
    
    async def test_jwt_security(self) -> SecurityTestResult:
        """Test JWT token security."""
        # Test for weak JWT algorithms
        weak_jwt_indicators = []
        
        try:
            # Try to decode JWT without verification
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": "test@example.com", "password": "password123"}
            ) as response:
                if response.status == 200:
                    token = response.json().get("access_token")
                    if token:
                        # Check if token uses weak algorithm
                        import jwt
                        try:
                            # Try to decode without verification
                            decoded = jwt.decode(token, options={"verify_signature": False})
                            if decoded.get("alg") == "HS256":
                                weak_jwt_indicators.append("Using HS256 algorithm")
                        except Exception:
                            pass
        except Exception:
            pass
        
        detected = len(weak_jwt_indicators) > 0
        
        return SecurityTestResult(
            test_name="jwt_security",
            vulnerability_type=VulnerabilityType.AUTHENTICATION,
            severity="medium" if detected else "low",
            detected=detected,
            description=f"JWT security issues: {weak_jwt_indicators}" if detected else "JWT security is properly configured",
            remediation="Use strong algorithms and proper key management" if detected else None,
            affected_component="Authentication system" if detected else None
        )
    
    async def test_api_security_headers(self) -> SecurityTestResult:
        """Test for security headers in API responses."""
        missing_headers = []
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/health") as response:
                headers = response.headers
                
                security_headers = {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                    "X-XSS-Protection": "1; mode=block",
                    "Strict-Transport-Security": None,  # Any value is good
                    "Content-Security-Policy": None,  # Any value is good
                }
                
                for header, expected_value in security_headers.items():
                    if header not in headers:
                        missing_headers.append(header)
                    elif expected_value and headers[header] not in expected_value:
                        missing_headers.append(f"{header}: {headers[header]}")
        except Exception:
            missing_headers.append("Could not test headers")
        
        detected = len(missing_headers) > 0
        
        return SecurityTestResult(
            test_name="api_security_headers",
            vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
            severity="medium" if detected else "low",
            detected=detected,
            description=f"Missing security headers: {missing_headers}" if detected else "Security headers are properly configured",
            remediation="Add missing security headers" if detected else None,
            affected_component="API responses" if detected else None
        )

@pytest.mark.asyncio
async def test_security_test_suite():
    """Run the complete security test suite."""
    async with SecurityTestRunner() as runner:
        results = await runner.run_all_security_tests()
        
        # Analyze results
        total_tests = len(results)
        critical_vulnerabilities = sum(1 for r in results if r.detected and r.severity == "critical")
        high_vulnerabilities = sum(1 for r in results if r.detected and r.severity == "high")
        medium_vulnerabilities = sum(1 for r in results if r.detected and r.severity == "medium")
        
        logger.info("Security test suite completed", 
                   total_tests=total_tests,
                   critical_vulnerabilities=critical_vulnerabilities,
                   high_vulnerabilities=high_vulnerabilities,
                   medium_vulnerabilities=medium_vulnerabilities)
        
        # Assert security requirements
        assert critical_vulnerabilities == 0, f"Found {critical_vulnerabilities} critical vulnerabilities"
        assert high_vulnerabilities == 0, f"Found {high_vulnerabilities} high severity vulnerabilities"
        
        # Log detailed results
        for result in results:
            if result.detected:
                logger.warning(f"Security vulnerability detected: {result.test_name}",
                             severity=result.severity,
                             description=result.description,
                             remediation=result.remediation)
            else:
                logger.info(f"Security test passed: {result.test_name}")

if __name__ == "__main__":
    asyncio.run(test_security_test_suite())

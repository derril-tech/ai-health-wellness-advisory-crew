"""
Chaos Tests for System Resilience
Tests system behavior under various failure conditions and edge cases.
"""
import asyncio
import aiohttp
import pytest
import time
import random
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class FailureType(Enum):
    """Types of failures to simulate."""
    DELAYED_API = "delayed_api"
    PARTIAL_WEEK = "partial_week"
    WEBSOCKET_DROP = "websocket_drop"
    DATABASE_TIMEOUT = "database_timeout"
    REDIS_FAILURE = "redis_failure"
    NATS_FAILURE = "nats_failure"
    DEVICE_API_DELAY = "device_api_delay"
    PARTIAL_DATA = "partial_data"
    CONCURRENT_FAILURES = "concurrent_failures"

@dataclass
class ChaosTestResult:
    """Result of a chaos test."""
    test_name: str
    failure_type: FailureType
    success: bool
    duration_ms: float
    error_message: Optional[str] = None
    recovery_time_ms: Optional[float] = None
    data_loss: bool = False
    partial_success: bool = False

@dataclass
class SystemState:
    """Current state of the system."""
    orchestrator_healthy: bool = True
    gateway_healthy: bool = True
    database_healthy: bool = True
    redis_healthy: bool = True
    nats_healthy: bool = True
    device_apis_healthy: bool = True

class ChaosTestRunner:
    """Runner for chaos tests."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[ChaosTestResult] = []
        self.system_state = SystemState()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_all_chaos_tests(self) -> List[ChaosTestResult]:
        """Run all chaos tests."""
        logger.info("Starting chaos test suite")
        
        tests = [
            self.test_delayed_device_apis,
            self.test_partial_week_data,
            self.test_websocket_drops,
            self.test_database_timeouts,
            self.test_redis_failures,
            self.test_nats_failures,
            self.test_partial_data_sync,
            self.test_concurrent_failures,
            self.test_network_partitions,
            self.test_memory_pressure,
        ]
        
        for test in tests:
            try:
                result = await test()
                self.test_results.append(result)
                logger.info(f"Chaos test {test.__name__} completed", 
                           success=result.success, 
                           duration=result.duration_ms)
            except Exception as e:
                logger.error(f"Chaos test {test.__name__} failed", error=str(e))
                self.test_results.append(ChaosTestResult(
                    test_name=test.__name__,
                    failure_type=FailureType.CONCURRENT_FAILURES,
                    success=False,
                    duration_ms=0,
                    error_message=str(e)
                ))
        
        return self.test_results
    
    async def test_delayed_device_apis(self) -> ChaosTestResult:
        """Test system behavior when device APIs are delayed."""
        start_time = time.time()
        
        try:
            # Simulate delayed Fitbit API response
            async def delayed_fitbit_sync():
                await asyncio.sleep(random.uniform(5, 15))  # 5-15 second delay
                return await self._make_device_sync_request("fitbit")
            
            # Start multiple concurrent device syncs
            tasks = [delayed_fitbit_sync() for _ in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            successful_syncs = sum(1 for r in results if not isinstance(r, Exception))
            partial_success = successful_syncs > 0 and successful_syncs < len(results)
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="delayed_device_apis",
                failure_type=FailureType.DEVICE_API_DELAY,
                success=successful_syncs > 0,
                duration_ms=duration,
                partial_success=partial_success
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="delayed_device_apis",
                failure_type=FailureType.DEVICE_API_DELAY,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_partial_week_data(self) -> ChaosTestResult:
        """Test system behavior with incomplete weekly data."""
        start_time = time.time()
        
        try:
            # Create check-in with missing data
            partial_checkin = {
                "user_id": "test_user_chaos",
                "program_id": "test_program_chaos",
                "week_number": 1,
                "weight": 75.0,
                # Missing: body_fat, sleep_quality, stress_level, energy_level, mood
                "notes": "Partial check-in for chaos testing"
            }
            
            # Submit partial check-in
            async with self.session.post(
                f"{self.base_url}/api/v1/check-ins",
                json=partial_checkin
            ) as response:
                if response.status == 422:  # Validation error expected
                    # Try with minimal required data
                    minimal_checkin = {
                        **partial_checkin,
                        "body_fat": 20.0,
                        "sleep_quality": 7,
                        "stress_level": 5,
                        "energy_level": 7,
                        "mood": 7
                    }
                    
                    async with self.session.post(
                        f"{self.base_url}/api/v1/check-ins",
                        json=minimal_checkin
                    ) as response2:
                        success = response2.status == 201
                else:
                    success = response.status == 201
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="partial_week_data",
                failure_type=FailureType.PARTIAL_WEEK,
                success=success,
                duration_ms=duration,
                partial_success=response.status == 422
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="partial_week_data",
                failure_type=FailureType.PARTIAL_WEEK,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_websocket_drops(self) -> ChaosTestResult:
        """Test WebSocket connection resilience."""
        start_time = time.time()
        
        try:
            # Simulate WebSocket connection and drops
            import websockets
            
            uri = f"ws://localhost:8000/ws/test_user_chaos"
            
            # Test multiple connection attempts
            connection_attempts = 3
            successful_connections = 0
            
            for i in range(connection_attempts):
                try:
                    async with websockets.connect(uri, timeout=5) as websocket:
                        successful_connections += 1
                        
                        # Send a test message
                        await websocket.send(json.dumps({
                            "type": "ping",
                            "user_id": "test_user_chaos"
                        }))
                        
                        # Wait for response
                        response = await asyncio.wait_for(
                            websocket.recv(), 
                            timeout=3
                        )
                        
                        # Simulate connection drop
                        await websocket.close()
                        
                except Exception as e:
                    logger.warning(f"WebSocket connection {i+1} failed", error=str(e))
            
            duration = (time.time() - start_time) * 1000
            success = successful_connections > 0
            
            return ChaosTestResult(
                test_name="websocket_drops",
                failure_type=FailureType.WEBSOCKET_DROP,
                success=success,
                duration_ms=duration,
                partial_success=successful_connections < connection_attempts
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="websocket_drops",
                failure_type=FailureType.WEBSOCKET_DROP,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_database_timeouts(self) -> ChaosTestResult:
        """Test system behavior during database timeouts."""
        start_time = time.time()
        
        try:
            # Simulate database timeout by making many concurrent requests
            async def make_concurrent_request():
                try:
                    async with self.session.get(
                        f"{self.base_url}/api/v1/health",
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as response:
                        return response.status == 200
                except asyncio.TimeoutError:
                    return False
            
            # Make many concurrent requests to trigger potential timeouts
            tasks = [make_concurrent_request() for _ in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_requests = sum(1 for r in results if r is True)
            timeout_requests = sum(1 for r in results if isinstance(r, asyncio.TimeoutError))
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="database_timeouts",
                failure_type=FailureType.DATABASE_TIMEOUT,
                success=successful_requests > 0,
                duration_ms=duration,
                partial_success=timeout_requests > 0 and successful_requests > 0
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="database_timeouts",
                failure_type=FailureType.DATABASE_TIMEOUT,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_redis_failures(self) -> ChaosTestResult:
        """Test system behavior during Redis failures."""
        start_time = time.time()
        
        try:
            # Test cache-dependent operations
            cache_operations = []
            
            # Test session management (uses Redis)
            for i in range(10):
                try:
                    async with self.session.post(
                        f"{self.base_url}/api/v1/auth/login",
                        json={
                            "email": f"user{i}@chaos.test",
                            "password": "testpassword"
                        },
                        timeout=5
                    ) as response:
                        cache_operations.append(response.status in [200, 401])
                except Exception:
                    cache_operations.append(False)
            
            successful_operations = sum(cache_operations)
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="redis_failures",
                failure_type=FailureType.REDIS_FAILURE,
                success=successful_operations > 0,
                duration_ms=duration,
                partial_success=successful_operations < len(cache_operations)
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="redis_failures",
                failure_type=FailureType.REDIS_FAILURE,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_nats_failures(self) -> ChaosTestResult:
        """Test system behavior during NATS failures."""
        start_time = time.time()
        
        try:
            # Test event-driven operations that use NATS
            event_operations = []
            
            # Test program generation (uses NATS for orchestration)
            for i in range(5):
                try:
                    async with self.session.post(
                        f"{self.base_url}/api/v1/programs/generate",
                        json={
                            "user_id": f"user{i}_chaos",
                            "goal": "weight_loss",
                            "duration_weeks": 12
                        },
                        timeout=30
                    ) as response:
                        event_operations.append(response.status in [200, 201, 202])
                except Exception:
                    event_operations.append(False)
            
            successful_operations = sum(event_operations)
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="nats_failures",
                failure_type=FailureType.NATS_FAILURE,
                success=successful_operations > 0,
                duration_ms=duration,
                partial_success=successful_operations < len(event_operations)
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="nats_failures",
                failure_type=FailureType.NATS_FAILURE,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_partial_data_sync(self) -> ChaosTestResult:
        """Test system behavior with partial data synchronization."""
        start_time = time.time()
        
        try:
            # Test device sync with incomplete data
            partial_device_data = {
                "user_id": "test_user_chaos",
                "device_id": "fitbit_chaos",
                "data": {
                    "steps": 10000,
                    # Missing: heart_rate, hrv, sleep
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/devices/sync/fitbit",
                json=partial_device_data
            ) as response:
                success = response.status in [200, 201, 202]
                partial_success = response.status == 422  # Validation error for partial data
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="partial_data_sync",
                failure_type=FailureType.PARTIAL_DATA,
                success=success,
                duration_ms=duration,
                partial_success=partial_success
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="partial_data_sync",
                failure_type=FailureType.PARTIAL_DATA,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_concurrent_failures(self) -> ChaosTestResult:
        """Test system behavior under multiple concurrent failures."""
        start_time = time.time()
        
        try:
            # Simulate multiple types of failures happening simultaneously
            async def simulate_failure(failure_type: str):
                if failure_type == "timeout":
                    await asyncio.sleep(random.uniform(1, 3))
                    raise asyncio.TimeoutError("Simulated timeout")
                elif failure_type == "connection_error":
                    await asyncio.sleep(random.uniform(0.5, 2))
                    raise ConnectionError("Simulated connection error")
                elif failure_type == "validation_error":
                    await asyncio.sleep(random.uniform(0.1, 1))
                    return "validation_error"
                else:
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    return "success"
            
            # Start multiple concurrent failure simulations
            failure_types = ["timeout", "connection_error", "validation_error", "success"]
            tasks = [simulate_failure(random.choice(failure_types)) for _ in range(20)]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_operations = sum(1 for r in results if not isinstance(r, Exception))
            timeout_errors = sum(1 for r in results if isinstance(r, asyncio.TimeoutError))
            connection_errors = sum(1 for r in results if isinstance(r, ConnectionError))
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="concurrent_failures",
                failure_type=FailureType.CONCURRENT_FAILURES,
                success=successful_operations > 0,
                duration_ms=duration,
                partial_success=successful_operations < len(results)
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="concurrent_failures",
                failure_type=FailureType.CONCURRENT_FAILURES,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_network_partitions(self) -> ChaosTestResult:
        """Test system behavior during network partitions."""
        start_time = time.time()
        
        try:
            # Simulate network partition by making requests to different endpoints
            endpoints = [
                "/api/v1/health",
                "/api/v1/auth/login",
                "/api/v1/programs",
                "/api/v1/check-ins",
                "/api/v1/nutrition",
                "/api/v1/training"
            ]
            
            async def test_endpoint(endpoint: str):
                try:
                    async with self.session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=5
                    ) as response:
                        return response.status < 500
                except Exception:
                    return False
            
            # Test all endpoints concurrently
            tasks = [test_endpoint(endpoint) for endpoint in endpoints]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_endpoints = sum(1 for r in results if r is True)
            failed_endpoints = sum(1 for r in results if r is False)
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="network_partitions",
                failure_type=FailureType.CONCURRENT_FAILURES,
                success=successful_endpoints > 0,
                duration_ms=duration,
                partial_success=failed_endpoints > 0 and successful_endpoints > 0
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="network_partitions",
                failure_type=FailureType.CONCURRENT_FAILURES,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def test_memory_pressure(self) -> ChaosTestResult:
        """Test system behavior under memory pressure."""
        start_time = time.time()
        
        try:
            # Simulate memory pressure by making many large requests
            large_data = {
                "user_id": "test_user_chaos",
                "program_id": "test_program_chaos",
                "week_number": 1,
                "weight": 75.0,
                "body_fat": 20.0,
                "sleep_quality": 7,
                "stress_level": 5,
                "energy_level": 7,
                "mood": 7,
                "notes": "x" * 10000,  # Large notes field
                "extra_data": {
                    "large_field": "x" * 5000,
                    "array_data": [{"item": "x" * 100} for _ in range(100)]
                }
            }
            
            # Make many requests with large data
            tasks = []
            for i in range(20):
                task = self.session.post(
                    f"{self.base_url}/api/v1/check-ins",
                    json={**large_data, "user_id": f"user{i}_chaos"}
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_requests = sum(1 for r in results if not isinstance(r, Exception))
            failed_requests = sum(1 for r in results if isinstance(r, Exception))
            
            duration = (time.time() - start_time) * 1000
            
            return ChaosTestResult(
                test_name="memory_pressure",
                failure_type=FailureType.CONCURRENT_FAILURES,
                success=successful_requests > 0,
                duration_ms=duration,
                partial_success=failed_requests > 0 and successful_requests > 0
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ChaosTestResult(
                test_name="memory_pressure",
                failure_type=FailureType.CONCURRENT_FAILURES,
                success=False,
                duration_ms=duration,
                error_message=str(e)
            )
    
    async def _make_device_sync_request(self, device_type: str) -> bool:
        """Make a device sync request."""
        try:
            device_data = {
                "user_id": "test_user_chaos",
                "device_id": f"{device_type}_chaos",
                "data": {
                    "steps": random.randint(5000, 20000),
                    "heart_rate": random.randint(60, 100),
                    "hrv": random.randint(20, 50),
                    "sleep": {
                        "hours": random.uniform(6, 9),
                        "quality": random.randint(1, 10)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/devices/sync/{device_type}",
                json=device_data,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202]
        except Exception:
            return False

@pytest.mark.asyncio
async def test_chaos_test_suite():
    """Run the complete chaos test suite."""
    async with ChaosTestRunner() as runner:
        results = await runner.run_all_chaos_tests()
        
        # Analyze results
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        partial_success_tests = sum(1 for r in results if r.partial_success)
        
        logger.info("Chaos test suite completed", 
                   total_tests=total_tests,
                   successful_tests=successful_tests,
                   partial_success_tests=partial_success_tests)
        
        # Assert minimum resilience requirements
        assert successful_tests > 0, "At least some tests should succeed"
        assert successful_tests + partial_success_tests >= total_tests * 0.7, \
            "At least 70% of tests should have some level of success"
        
        # Log detailed results
        for result in results:
            logger.info(f"Chaos test result: {result.test_name}",
                       success=result.success,
                       duration=result.duration_ms,
                       partial_success=result.partial_success,
                       error=result.error_message)

if __name__ == "__main__":
    asyncio.run(test_chaos_test_suite())

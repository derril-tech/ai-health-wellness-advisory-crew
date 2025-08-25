"""
Data Retention Service
Handles data lifecycle management, retention policies, and secure data deletion.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import hashlib
import os
from pathlib import Path
import aiofiles
import aiohttp
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()

class DataType(Enum):
    USER_PROFILE = "user_profile"
    HEALTH_DATA = "health_data"
    WORKOUT_LOGS = "workout_logs"
    NUTRITION_LOGS = "nutrition_logs"
    DEVICE_DATA = "device_data"
    PROGRESS_DATA = "progress_data"
    REPORTS = "reports"
    AUDIT_LOGS = "audit_logs"
    METRICS = "metrics"
    EXPORTS = "exports"

class RetentionPolicy(Enum):
    IMMEDIATE = "immediate"  # Delete immediately on request
    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 1 year
    LONG_TERM = "long_term"  # 7 years
    PERMANENT = "permanent"  # Never delete (legal/medical)

class DeletionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class RetentionRule:
    """Retention rule configuration."""
    data_type: DataType
    policy: RetentionPolicy
    retention_days: int
    auto_delete: bool
    legal_hold: bool
    description: str

@dataclass
class DeletionRequest:
    """Data deletion request."""
    request_id: str
    user_id: str
    data_types: List[DataType]
    reason: str
    requested_by: str
    requested_at: datetime
    status: DeletionStatus
    scheduled_for: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    audit_trail: List[Dict[str, Any]]

@dataclass
class DataInventory:
    """Data inventory for a user."""
    user_id: str
    data_type: DataType
    record_count: int
    total_size_bytes: int
    oldest_record: datetime
    newest_record: datetime
    last_accessed: datetime
    retention_policy: RetentionPolicy
    days_until_deletion: Optional[int]

class DataRetentionService:
    """Service for data retention and deletion management."""
    
    def __init__(self, db_session: AsyncSession):
        self.logger = structlog.get_logger()
        self.db_session = db_session
        self.deletion_requests: List[DeletionRequest] = []
        
        # Load retention policies
        self.retention_rules = self._load_retention_rules()
        
        # Initialize audit trail
        self.audit_trail = []
    
    def _load_retention_rules(self) -> Dict[DataType, RetentionRule]:
        """Load retention rules configuration."""
        return {
            DataType.USER_PROFILE: RetentionRule(
                data_type=DataType.USER_PROFILE,
                policy=RetentionPolicy.LONG_TERM,
                retention_days=2555,  # 7 years
                auto_delete=True,
                legal_hold=False,
                description="User profile data including health information"
            ),
            DataType.HEALTH_DATA: RetentionRule(
                data_type=DataType.HEALTH_DATA,
                policy=RetentionPolicy.LONG_TERM,
                retention_days=2555,  # 7 years
                auto_delete=True,
                legal_hold=True,
                description="Health screening and medical data"
            ),
            DataType.WORKOUT_LOGS: RetentionRule(
                data_type=DataType.WORKOUT_LOGS,
                policy=RetentionPolicy.MEDIUM_TERM,
                retention_days=365,  # 1 year
                auto_delete=True,
                legal_hold=False,
                description="Workout completion and performance logs"
            ),
            DataType.NUTRITION_LOGS: RetentionRule(
                data_type=DataType.NUTRITION_LOGS,
                policy=RetentionPolicy.MEDIUM_TERM,
                retention_days=365,  # 1 year
                auto_delete=True,
                legal_hold=False,
                description="Nutrition tracking and meal logs"
            ),
            DataType.DEVICE_DATA: RetentionRule(
                data_type=DataType.DEVICE_DATA,
                policy=RetentionPolicy.SHORT_TERM,
                retention_days=90,  # 3 months
                auto_delete=True,
                legal_hold=False,
                description="Fitness device and wearable data"
            ),
            DataType.PROGRESS_DATA: RetentionRule(
                data_type=DataType.PROGRESS_DATA,
                policy=RetentionPolicy.MEDIUM_TERM,
                retention_days=365,  # 1 year
                auto_delete=True,
                legal_hold=False,
                description="Progress tracking and analytics data"
            ),
            DataType.REPORTS: RetentionRule(
                data_type=DataType.REPORTS,
                policy=RetentionPolicy.MEDIUM_TERM,
                retention_days=365,  # 1 year
                auto_delete=True,
                legal_hold=False,
                description="Generated reports and exports"
            ),
            DataType.AUDIT_LOGS: RetentionRule(
                data_type=DataType.AUDIT_LOGS,
                policy=RetentionPolicy.LONG_TERM,
                retention_days=2555,  # 7 years
                auto_delete=True,
                legal_hold=True,
                description="Audit logs for compliance and security"
            ),
            DataType.METRICS: RetentionRule(
                data_type=DataType.METRICS,
                policy=RetentionPolicy.SHORT_TERM,
                retention_days=90,  # 3 months
                auto_delete=True,
                legal_hold=False,
                description="System metrics and performance data"
            ),
            DataType.EXPORTS: RetentionRule(
                data_type=DataType.EXPORTS,
                policy=RetentionPolicy.SHORT_TERM,
                retention_days=30,  # 30 days
                auto_delete=True,
                legal_hold=False,
                description="User-requested data exports"
            )
        }
    
    async def create_deletion_request(self, user_id: str, data_types: List[DataType], 
                                    reason: str, requested_by: str, 
                                    scheduled_for: Optional[datetime] = None) -> DeletionRequest:
        """Create a new data deletion request."""
        request_id = self._generate_request_id(user_id)
        
        deletion_request = DeletionRequest(
            request_id=request_id,
            user_id=user_id,
            data_types=data_types,
            reason=reason,
            requested_by=requested_by,
            requested_at=datetime.now(),
            status=DeletionStatus.PENDING,
            scheduled_for=scheduled_for,
            completed_at=None,
            error_message=None,
            audit_trail=[]
        )
        
        # Add to audit trail
        deletion_request.audit_trail.append({
            "action": "request_created",
            "timestamp": datetime.now().isoformat(),
            "actor": requested_by,
            "details": {
                "data_types": [dt.value for dt in data_types],
                "reason": reason,
                "scheduled_for": scheduled_for.isoformat() if scheduled_for else None
            }
        })
        
        self.deletion_requests.append(deletion_request)
        
        self.logger.info("Deletion request created", 
                        request_id=request_id, user_id=user_id, 
                        data_types=[dt.value for dt in data_types])
        
        return deletion_request
    
    async def get_deletion_request(self, request_id: str) -> Optional[DeletionRequest]:
        """Get a deletion request by ID."""
        for request in self.deletion_requests:
            if request.request_id == request_id:
                return request
        return None
    
    async def cancel_deletion_request(self, request_id: str, cancelled_by: str) -> bool:
        """Cancel a pending deletion request."""
        request = await self.get_deletion_request(request_id)
        if not request:
            return False
        
        if request.status != DeletionStatus.PENDING:
            return False
        
        request.status = DeletionStatus.CANCELLED
        
        # Add to audit trail
        request.audit_trail.append({
            "action": "request_cancelled",
            "timestamp": datetime.now().isoformat(),
            "actor": cancelled_by,
            "details": {"previous_status": DeletionStatus.PENDING.value}
        })
        
        self.logger.info("Deletion request cancelled", 
                        request_id=request_id, cancelled_by=cancelled_by)
        
        return True
    
    async def execute_deletion_request(self, request_id: str, executed_by: str) -> bool:
        """Execute a deletion request."""
        request = await self.get_deletion_request(request_id)
        if not request:
            return False
        
        if request.status != DeletionStatus.PENDING:
            return False
        
        request.status = DeletionStatus.IN_PROGRESS
        
        # Add to audit trail
        request.audit_trail.append({
            "action": "deletion_started",
            "timestamp": datetime.now().isoformat(),
            "actor": executed_by
        })
        
        try:
            # Execute deletion for each data type
            for data_type in request.data_types:
                await self._delete_user_data(request.user_id, data_type)
                
                # Add to audit trail
                request.audit_trail.append({
                    "action": "data_type_deleted",
                    "timestamp": datetime.now().isoformat(),
                    "actor": executed_by,
                    "details": {"data_type": data_type.value}
                })
            
            request.status = DeletionStatus.COMPLETED
            request.completed_at = datetime.now()
            
            # Add to audit trail
            request.audit_trail.append({
                "action": "deletion_completed",
                "timestamp": datetime.now().isoformat(),
                "actor": executed_by,
                "details": {"total_data_types": len(request.data_types)}
            })
            
            self.logger.info("Deletion request completed", 
                            request_id=request_id, user_id=request.user_id)
            
            return True
            
        except Exception as e:
            request.status = DeletionStatus.FAILED
            request.error_message = str(e)
            
            # Add to audit trail
            request.audit_trail.append({
                "action": "deletion_failed",
                "timestamp": datetime.now().isoformat(),
                "actor": executed_by,
                "details": {"error": str(e)}
            })
            
            self.logger.error("Deletion request failed", 
                             request_id=request_id, error=str(e))
            
            return False
    
    async def _delete_user_data(self, user_id: str, data_type: DataType):
        """Delete user data of a specific type."""
        self.logger.info("Deleting user data", user_id=user_id, data_type=data_type.value)
        
        # Check for legal hold
        rule = self.retention_rules[data_type]
        if rule.legal_hold:
            raise ValueError(f"Cannot delete {data_type.value} - legal hold in place")
        
        # Delete from database
        await self._delete_from_database(user_id, data_type)
        
        # Delete from file storage
        await self._delete_from_storage(user_id, data_type)
        
        # Delete from cache
        await self._delete_from_cache(user_id, data_type)
        
        self.logger.info("User data deleted successfully", 
                        user_id=user_id, data_type=data_type.value)
    
    async def _delete_from_database(self, user_id: str, data_type: DataType):
        """Delete data from database."""
        # This would contain actual SQL deletion logic
        # For now, we'll simulate the deletion
        
        deletion_queries = {
            DataType.USER_PROFILE: "DELETE FROM users WHERE id = :user_id",
            DataType.HEALTH_DATA: "DELETE FROM health_profiles WHERE user_id = :user_id",
            DataType.WORKOUT_LOGS: "DELETE FROM workout_logs WHERE user_id = :user_id",
            DataType.NUTRITION_LOGS: "DELETE FROM nutrition_logs WHERE user_id = :user_id",
            DataType.DEVICE_DATA: "DELETE FROM device_data WHERE user_id = :user_id",
            DataType.PROGRESS_DATA: "DELETE FROM progress_data WHERE user_id = :user_id",
            DataType.REPORTS: "DELETE FROM reports WHERE user_id = :user_id",
            DataType.AUDIT_LOGS: "DELETE FROM audit_logs WHERE user_id = :user_id",
            DataType.METRICS: "DELETE FROM metrics WHERE user_id = :user_id",
            DataType.EXPORTS: "DELETE FROM exports WHERE user_id = :user_id"
        }
        
        if data_type in deletion_queries:
            query = deletion_queries[data_type]
            # In production, this would execute the actual query
            # await self.db_session.execute(text(query), {"user_id": user_id})
            # await self.db_session.commit()
            
            self.logger.debug("Database deletion query prepared", 
                             query=query, user_id=user_id, data_type=data_type.value)
    
    async def _delete_from_storage(self, user_id: str, data_type: DataType):
        """Delete data from file storage."""
        # This would contain actual file deletion logic
        # For now, we'll simulate the deletion
        
        storage_paths = {
            DataType.REPORTS: f"/storage/reports/{user_id}",
            DataType.EXPORTS: f"/storage/exports/{user_id}",
            DataType.DEVICE_DATA: f"/storage/device_data/{user_id}"
        }
        
        if data_type in storage_paths:
            path = storage_paths[data_type]
            # In production, this would delete actual files
            # if os.path.exists(path):
            #     shutil.rmtree(path)
            
            self.logger.debug("Storage deletion prepared", 
                             path=path, user_id=user_id, data_type=data_type.value)
    
    async def _delete_from_cache(self, user_id: str, data_type: DataType):
        """Delete data from cache."""
        # This would contain actual cache deletion logic
        # For now, we'll simulate the deletion
        
        cache_keys = [
            f"user:{user_id}:profile",
            f"user:{user_id}:health",
            f"user:{user_id}:workouts",
            f"user:{user_id}:nutrition",
            f"user:{user_id}:progress"
        ]
        
        # In production, this would delete from Redis/Memcached
        # for key in cache_keys:
        #     await cache.delete(key)
        
        self.logger.debug("Cache deletion prepared", 
                         keys=cache_keys, user_id=user_id, data_type=data_type.value)
    
    async def get_data_inventory(self, user_id: str) -> List[DataInventory]:
        """Get data inventory for a user."""
        inventory = []
        
        for data_type, rule in self.retention_rules.items():
            # In production, this would query actual data
            # For now, we'll simulate the inventory
            
            inventory_item = DataInventory(
                user_id=user_id,
                data_type=data_type,
                record_count=self._simulate_record_count(data_type),
                total_size_bytes=self._simulate_data_size(data_type),
                oldest_record=datetime.now() - timedelta(days=30),
                newest_record=datetime.now(),
                last_accessed=datetime.now() - timedelta(hours=2),
                retention_policy=rule.policy,
                days_until_deletion=self._calculate_days_until_deletion(rule)
            )
            
            inventory.append(inventory_item)
        
        return inventory
    
    def _simulate_record_count(self, data_type: DataType) -> int:
        """Simulate record count for data type."""
        counts = {
            DataType.USER_PROFILE: 1,
            DataType.HEALTH_DATA: 5,
            DataType.WORKOUT_LOGS: 150,
            DataType.NUTRITION_LOGS: 300,
            DataType.DEVICE_DATA: 1000,
            DataType.PROGRESS_DATA: 90,
            DataType.REPORTS: 12,
            DataType.AUDIT_LOGS: 500,
            DataType.METRICS: 2000,
            DataType.EXPORTS: 3
        }
        return counts.get(data_type, 0)
    
    def _simulate_data_size(self, data_type: DataType) -> int:
        """Simulate data size in bytes for data type."""
        sizes = {
            DataType.USER_PROFILE: 2048,
            DataType.HEALTH_DATA: 10240,
            DataType.WORKOUT_LOGS: 512000,
            DataType.NUTRITION_LOGS: 1024000,
            DataType.DEVICE_DATA: 2048000,
            DataType.PROGRESS_DATA: 256000,
            DataType.REPORTS: 1024000,
            DataType.AUDIT_LOGS: 512000,
            DataType.METRICS: 4096000,
            DataType.EXPORTS: 2048000
        }
        return sizes.get(data_type, 0)
    
    def _calculate_days_until_deletion(self, rule: RetentionRule) -> Optional[int]:
        """Calculate days until automatic deletion."""
        if not rule.auto_delete or rule.policy == RetentionPolicy.PERMANENT:
            return None
        
        # In production, this would calculate based on actual data age
        # For now, return a simulated value
        return rule.retention_days - 30  # Assume data is 30 days old
    
    async def run_retention_cleanup(self) -> Dict[str, Any]:
        """Run automatic retention cleanup for expired data."""
        self.logger.info("Starting retention cleanup")
        
        cleanup_stats = {
            "processed_users": 0,
            "deleted_records": 0,
            "deleted_size_bytes": 0,
            "errors": 0
        }
        
        try:
            # In production, this would iterate through all users
            # For now, we'll simulate the cleanup
            
            for data_type, rule in self.retention_rules.items():
                if rule.auto_delete and rule.policy != RetentionPolicy.PERMANENT:
                    # Check for expired data
                    cutoff_date = datetime.now() - timedelta(days=rule.retention_days)
                    
                    # In production, this would query for expired records
                    # expired_records = await self._get_expired_records(data_type, cutoff_date)
                    
                    # Simulate expired records
                    expired_count = self._simulate_expired_records(data_type)
                    
                    if expired_count > 0:
                        # Delete expired records
                        await self._delete_expired_records(data_type, cutoff_date)
                        
                        cleanup_stats["deleted_records"] += expired_count
                        cleanup_stats["deleted_size_bytes"] += expired_count * 1024  # Simulate size
            
            cleanup_stats["processed_users"] = 1  # Simulate
            
            self.logger.info("Retention cleanup completed", stats=cleanup_stats)
            
        except Exception as e:
            cleanup_stats["errors"] += 1
            self.logger.error("Retention cleanup failed", error=str(e))
        
        return cleanup_stats
    
    def _simulate_expired_records(self, data_type: DataType) -> int:
        """Simulate number of expired records."""
        # In production, this would query actual expired records
        return 10  # Simulate 10 expired records
    
    async def _delete_expired_records(self, data_type: DataType, cutoff_date: datetime):
        """Delete expired records of a specific type."""
        # In production, this would delete actual expired records
        self.logger.debug("Deleting expired records", 
                         data_type=data_type.value, cutoff_date=cutoff_date.isoformat())
    
    def _generate_request_id(self, user_id: str) -> str:
        """Generate a unique request ID."""
        timestamp = datetime.now().isoformat()
        unique_string = f"{user_id}:{timestamp}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    async def export_deletion_audit_trail(self, request_id: str) -> str:
        """Export audit trail for a deletion request."""
        request = await self.get_deletion_request(request_id)
        if not request:
            return "Request not found"
        
        audit_data = {
            "request_id": request_id,
            "user_id": request.user_id,
            "data_types": [dt.value for dt in request.data_types],
            "reason": request.reason,
            "requested_by": request.requested_by,
            "requested_at": request.requested_at.isoformat(),
            "status": request.status.value,
            "scheduled_for": request.scheduled_for.isoformat() if request.scheduled_for else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "error_message": request.error_message,
            "audit_trail": request.audit_trail
        }
        
        return json.dumps(audit_data, indent=2)
    
    async def get_retention_policy_summary(self) -> Dict[str, Any]:
        """Get summary of retention policies."""
        summary = {
            "total_data_types": len(self.retention_rules),
            "policies": {},
            "legal_hold_count": 0,
            "auto_delete_count": 0
        }
        
        for data_type, rule in self.retention_rules.items():
            summary["policies"][data_type.value] = {
                "policy": rule.policy.value,
                "retention_days": rule.retention_days,
                "auto_delete": rule.auto_delete,
                "legal_hold": rule.legal_hold,
                "description": rule.description
            }
            
            if rule.legal_hold:
                summary["legal_hold_count"] += 1
            
            if rule.auto_delete:
                summary["auto_delete_count"] += 1
        
        return summary

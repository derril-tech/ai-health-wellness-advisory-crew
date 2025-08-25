"""
Device Connectors Service
Manages OAuth connections and data synchronization with fitness devices and wearables.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from abc import ABC, abstractmethod

logger = structlog.get_logger()

class DeviceType(Enum):
    """Supported device types."""
    FITBIT = "fitbit"
    OURA = "oura"
    GARMIN = "garmin"
    APPLE_WATCH = "apple_watch"
    GOOGLE_FIT = "google_fit"
    STRAVA = "strava"

class DataType(Enum):
    """Types of data that can be synced."""
    STEPS = "steps"
    HEART_RATE = "heart_rate"
    HEART_RATE_VARIABILITY = "hrv"
    SLEEP = "sleep"
    ACTIVITY = "activity"
    CALORIES = "calories"
    DISTANCE = "distance"
    ELEVATION = "elevation"

@dataclass
class DeviceConnection:
    """Represents a user's connection to a device."""
    id: str
    user_id: str
    device_type: DeviceType
    access_token: str
    refresh_token: str
    expires_at: datetime
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    is_active: bool = True
    last_sync: Optional[datetime] = None
    sync_frequency_hours: int = 24
    created_at: datetime = None

@dataclass
class DeviceData:
    """Represents normalized device data."""
    id: str
    user_id: str
    device_type: DeviceType
    data_type: DataType
    timestamp: datetime
    value: float
    unit: str
    metadata: Dict[str, Any] = None
    source_device_id: Optional[str] = None

@dataclass
class SleepData:
    """Normalized sleep data structure."""
    user_id: str
    device_type: DeviceType
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    sleep_score: Optional[float] = None
    deep_sleep_minutes: Optional[int] = None
    light_sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    awake_minutes: Optional[int] = None
    efficiency: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class HeartRateData:
    """Normalized heart rate data structure."""
    user_id: str
    device_type: DeviceType
    timestamp: datetime
    heart_rate: int
    heart_rate_variability: Optional[float] = None
    resting_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    metadata: Dict[str, Any] = None

class BaseDeviceConnector(ABC):
    """Abstract base class for device connectors."""
    
    def __init__(self, device_type: DeviceType):
        self.device_type = device_type
        self.logger = structlog.get_logger().bind(device_type=device_type.value)
    
    @abstractmethod
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate with the device API using OAuth code."""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token."""
        pass
    
    @abstractmethod
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information."""
        pass
    
    @abstractmethod
    async def sync_data(self, connection: DeviceConnection, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync data from the device."""
        pass
    
    @abstractmethod
    def normalize_data(self, raw_data: Dict[str, Any], data_type: DataType) -> List[DeviceData]:
        """Normalize raw device data to standard format."""
        pass

class FitbitConnector(BaseDeviceConnector):
    """Fitbit device connector."""
    
    def __init__(self):
        super().__init__(DeviceType.FITBIT)
        self.base_url = "https://api.fitbit.com"
        self.auth_url = "https://www.fitbit.com/oauth2/authorize"
        self.token_url = "https://api.fitbit.com/oauth2/token"
    
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate with Fitbit API."""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'client_id': 'YOUR_FITBIT_CLIENT_ID',
                'client_secret': 'YOUR_FITBIT_CLIENT_SECRET',
                'redirect_uri': 'YOUR_REDIRECT_URI'
            }
            
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data['refresh_token'],
                        'expires_in': token_data['expires_in']
                    }
                else:
                    raise Exception(f"Fitbit authentication failed: {response.status}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Fitbit access token."""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': 'YOUR_FITBIT_CLIENT_ID',
                'client_secret': 'YOUR_FITBIT_CLIENT_SECRET'
            }
            
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data['refresh_token'],
                        'expires_in': token_data['expires_in']
                    }
                else:
                    raise Exception(f"Fitbit token refresh failed: {response.status}")
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Fitbit user profile."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/1/user/-/profile.json"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get Fitbit profile: {response.status}")
    
    async def sync_data(self, connection: DeviceConnection, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync data from Fitbit."""
        # Check if token needs refresh
        if datetime.utcnow() >= connection.expires_at:
            token_data = await self.refresh_token(connection.refresh_token)
            # Update connection in database
            connection.access_token = token_data['access_token']
            connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        
        all_data = []
        
        # Sync steps
        steps_data = await self._sync_steps(connection.access_token, start_date, end_date)
        all_data.extend(steps_data)
        
        # Sync heart rate
        hr_data = await self._sync_heart_rate(connection.access_token, start_date, end_date)
        all_data.extend(hr_data)
        
        # Sync sleep
        sleep_data = await self._sync_sleep(connection.access_token, start_date, end_date)
        all_data.extend(sleep_data)
        
        return all_data
    
    async def _sync_steps(self, access_token: str, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync step data from Fitbit."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/1/user/-/activities/steps/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.normalize_data(data, DataType.STEPS)
                else:
                    self.logger.warning("Failed to sync Fitbit steps", status=response.status)
                    return []
    
    async def _sync_heart_rate(self, access_token: str, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync heart rate data from Fitbit."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/1/user/-/activities/heart/date/{start_date.strftime('%Y-%m-%d')}/1d.json"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.normalize_data(data, DataType.HEART_RATE)
                else:
                    self.logger.warning("Failed to sync Fitbit heart rate", status=response.status)
                    return []
    
    async def _sync_sleep(self, access_token: str, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync sleep data from Fitbit."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/1.2/user/-/sleep/date/{start_date.strftime('%Y-%m-%d')}.json"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.normalize_data(data, DataType.SLEEP)
                else:
                    self.logger.warning("Failed to sync Fitbit sleep", status=response.status)
                    return []
    
    def normalize_data(self, raw_data: Dict[str, Any], data_type: DataType) -> List[DeviceData]:
        """Normalize Fitbit data to standard format."""
        normalized_data = []
        
        if data_type == DataType.STEPS:
            for activity in raw_data.get('activities-steps', []):
                normalized_data.append(DeviceData(
                    id=f"fitbit_steps_{activity['dateTime']}",
                    user_id="user_id",  # Will be set by caller
                    device_type=DeviceType.FITBIT,
                    data_type=DataType.STEPS,
                    timestamp=datetime.strptime(activity['dateTime'], '%Y-%m-%d'),
                    value=float(activity['value']),
                    unit='steps',
                    metadata={'dateTime': activity['dateTime']}
                ))
        
        elif data_type == DataType.HEART_RATE:
            for hr_data in raw_data.get('activities-heart', []):
                for zone in hr_data.get('value', {}).get('heartRateZones', []):
                    normalized_data.append(DeviceData(
                        id=f"fitbit_hr_{hr_data['dateTime']}_{zone['name']}",
                        user_id="user_id",  # Will be set by caller
                        device_type=DeviceType.FITBIT,
                        data_type=DataType.HEART_RATE,
                        timestamp=datetime.strptime(hr_data['dateTime'], '%Y-%m-%d'),
                        value=float(zone['max']),
                        unit='bpm',
                        metadata={
                            'zone': zone['name'],
                            'min': zone['min'],
                            'max': zone['max'],
                            'minutes': zone['minutes']
                        }
                    ))
        
        elif data_type == DataType.SLEEP:
            for sleep in raw_data.get('sleep', []):
                normalized_data.append(DeviceData(
                    id=f"fitbit_sleep_{sleep['dateOfSleep']}",
                    user_id="user_id",  # Will be set by caller
                    device_type=DeviceType.FITBIT,
                    data_type=DataType.SLEEP,
                    timestamp=datetime.strptime(sleep['dateOfSleep'], '%Y-%m-%d'),
                    value=float(sleep['duration']),
                    unit='milliseconds',
                    metadata={
                        'efficiency': sleep.get('efficiency'),
                        'minutesAsleep': sleep.get('minutesAsleep'),
                        'minutesAwake': sleep.get('minutesAwake'),
                        'timeInBed': sleep.get('timeInBed')
                    }
                ))
        
        return normalized_data

class OuraConnector(BaseDeviceConnector):
    """Oura Ring device connector."""
    
    def __init__(self):
        super().__init__(DeviceType.OURA)
        self.base_url = "https://api.ouraring.com/v2"
    
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate with Oura API."""
        # Oura uses different OAuth flow
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'client_id': 'YOUR_OURA_CLIENT_ID',
                'client_secret': 'YOUR_OURA_CLIENT_SECRET',
                'redirect_uri': 'YOUR_REDIRECT_URI'
            }
            
            async with session.post('https://cloud.ouraring.com/oauth/token', data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data['refresh_token'],
                        'expires_in': token_data['expires_in']
                    }
                else:
                    raise Exception(f"Oura authentication failed: {response.status}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Oura access token."""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': 'YOUR_OURA_CLIENT_ID',
                'client_secret': 'YOUR_OURA_CLIENT_SECRET'
            }
            
            async with session.post('https://cloud.ouraring.com/oauth/token', data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data['refresh_token'],
                        'expires_in': token_data['expires_in']
                    }
                else:
                    raise Exception(f"Oura token refresh failed: {response.status}")
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Oura user profile."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/usercollection/personal_info"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get Oura profile: {response.status}")
    
    async def sync_data(self, connection: DeviceConnection, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync data from Oura."""
        # Check if token needs refresh
        if datetime.utcnow() >= connection.expires_at:
            token_data = await self.refresh_token(connection.refresh_token)
            connection.access_token = token_data['access_token']
            connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        
        all_data = []
        
        # Sync sleep data
        sleep_data = await self._sync_sleep(connection.access_token, start_date, end_date)
        all_data.extend(sleep_data)
        
        # Sync activity data
        activity_data = await self._sync_activity(connection.access_token, start_date, end_date)
        all_data.extend(activity_data)
        
        # Sync heart rate data
        hr_data = await self._sync_heart_rate(connection.access_token, start_date, end_date)
        all_data.extend(hr_data)
        
        return all_data
    
    async def _sync_sleep(self, access_token: str, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync sleep data from Oura."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/usercollection/daily_sleep"
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.normalize_data(data, DataType.SLEEP)
                else:
                    self.logger.warning("Failed to sync Oura sleep", status=response.status)
                    return []
    
    async def _sync_activity(self, access_token: str, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync activity data from Oura."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/usercollection/daily_activity"
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.normalize_data(data, DataType.STEPS)
                else:
                    self.logger.warning("Failed to sync Oura activity", status=response.status)
                    return []
    
    async def _sync_heart_rate(self, access_token: str, start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Sync heart rate data from Oura."""
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {access_token}'}
            url = f"{self.base_url}/usercollection/heartrate"
            params = {
                'start_datetime': start_date.isoformat(),
                'end_datetime': end_date.isoformat()
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.normalize_data(data, DataType.HEART_RATE)
                else:
                    self.logger.warning("Failed to sync Oura heart rate", status=response.status)
                    return []
    
    def normalize_data(self, raw_data: Dict[str, Any], data_type: DataType) -> List[DeviceData]:
        """Normalize Oura data to standard format."""
        normalized_data = []
        
        if data_type == DataType.SLEEP:
            for sleep in raw_data.get('data', []):
                normalized_data.append(DeviceData(
                    id=f"oura_sleep_{sleep['day']}",
                    user_id="user_id",  # Will be set by caller
                    device_type=DeviceType.OURA,
                    data_type=DataType.SLEEP,
                    timestamp=datetime.strptime(sleep['day'], '%Y-%m-%d'),
                    value=float(sleep.get('sleep', 0)),
                    unit='seconds',
                    metadata={
                        'deep_sleep': sleep.get('deep_sleep_duration'),
                        'rem_sleep': sleep.get('rem_sleep_duration'),
                        'light_sleep': sleep.get('light_sleep_duration'),
                        'awake': sleep.get('awake'),
                        'sleep_score': sleep.get('sleep_score'),
                        'efficiency': sleep.get('sleep_efficiency')
                    }
                ))
        
        elif data_type == DataType.STEPS:
            for activity in raw_data.get('data', []):
                normalized_data.append(DeviceData(
                    id=f"oura_steps_{activity['day']}",
                    user_id="user_id",  # Will be set by caller
                    device_type=DeviceType.OURA,
                    data_type=DataType.STEPS,
                    timestamp=datetime.strptime(activity['day'], '%Y-%m-%d'),
                    value=float(activity.get('steps', 0)),
                    unit='steps',
                    metadata={
                        'calories': activity.get('calories_total'),
                        'active_calories': activity.get('calories_active'),
                        'distance': activity.get('distance'),
                        'activity_score': activity.get('activity_score')
                    }
                ))
        
        elif data_type == DataType.HEART_RATE:
            for hr_data in raw_data.get('data', []):
                normalized_data.append(DeviceData(
                    id=f"oura_hr_{hr_data['timestamp']}",
                    user_id="user_id",  # Will be set by caller
                    device_type=DeviceType.OURA,
                    data_type=DataType.HEART_RATE,
                    timestamp=datetime.fromisoformat(hr_data['timestamp'].replace('Z', '+00:00')),
                    value=float(hr_data.get('heart_rate', 0)),
                    unit='bpm',
                    metadata={
                        'hrv': hr_data.get('hrv'),
                        'resting_heart_rate': hr_data.get('resting_heart_rate')
                    }
                ))
        
        return normalized_data

class DeviceConnectorsService:
    """Service for managing device connections and data synchronization."""
    
    def __init__(self):
        self.connectors = {
            DeviceType.FITBIT: FitbitConnector(),
            DeviceType.OURA: OuraConnector(),
            # Add other connectors as needed
        }
        self.logger = structlog.get_logger()
    
    async def connect_device(self, user_id: str, device_type: DeviceType, auth_code: str) -> DeviceConnection:
        """Connect a new device for a user."""
        if device_type not in self.connectors:
            raise ValueError(f"Unsupported device type: {device_type}")
        
        connector = self.connectors[device_type]
        token_data = await connector.authenticate(auth_code)
        
        # Get user profile
        profile = await connector.get_user_profile(token_data['access_token'])
        
        connection = DeviceConnection(
            id=f"{user_id}_{device_type.value}",
            user_id=user_id,
            device_type=device_type,
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            expires_at=datetime.utcnow() + timedelta(seconds=token_data['expires_in']),
            device_name=profile.get('displayName', device_type.value),
            created_at=datetime.utcnow()
        )
        
        self.logger.info("Device connected", user_id=user_id, device_type=device_type.value)
        return connection
    
    async def sync_user_devices(self, user_id: str, days_back: int = 7) -> List[DeviceData]:
        """Sync data from all connected devices for a user."""
        # In production, this would fetch connections from database
        connections = []  # Get from database
        
        all_data = []
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        for connection in connections:
            if connection.user_id == user_id and connection.is_active:
                try:
                    connector = self.connectors[connection.device_type]
                    device_data = await connector.sync_data(connection, start_date, end_date)
                    
                    # Set user_id for all data
                    for data in device_data:
                        data.user_id = user_id
                    
                    all_data.extend(device_data)
                    
                    # Update last sync time
                    connection.last_sync = datetime.utcnow()
                    
                    self.logger.info("Device sync completed", 
                                   user_id=user_id, 
                                   device_type=connection.device_type.value,
                                   data_count=len(device_data))
                
                except Exception as e:
                    self.logger.error("Device sync failed", 
                                    user_id=user_id, 
                                    device_type=connection.device_type.value,
                                    error=str(e))
        
        return all_data
    
    async def get_user_device_data(self, user_id: str, data_type: DataType, 
                                  start_date: datetime, end_date: datetime) -> List[DeviceData]:
        """Get normalized device data for a user within a date range."""
        # In production, this would query the database
        # For now, return empty list
        return []
    
    def get_supported_devices(self) -> List[DeviceType]:
        """Get list of supported device types."""
        return list(self.connectors.keys())
    
    async def disconnect_device(self, user_id: str, device_type: DeviceType) -> bool:
        """Disconnect a device for a user."""
        # In production, this would update the database
        self.logger.info("Device disconnected", user_id=user_id, device_type=device_type.value)
        return True

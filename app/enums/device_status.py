from enum import Enum


class DeviceStatus(str, Enum):
    """
    Device status enumeration for IoT device lifecycle management.
    
    Values:
    - ACTIVE: Device is operational and communicating
    - INACTIVE: Device exists but is not actively in use
    - MAINTENANCE: Device is under maintenance and temporarily unavailable
    - OFFLINE: Device is disconnected from the network
    """
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"

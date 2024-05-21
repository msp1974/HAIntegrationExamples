"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from dataclasses import dataclass
from enum import StrEnum
from random import choice, randrange


class DeviceType(StrEnum):
    """Device types."""

    TEMP_SENSOR = "temp_sensor"
    DOOR_SENSOR = "door_sensor"


@dataclass
class Device:
    """API device."""

    device_id: int
    device_type: DeviceType
    name: str
    state: int | bool


class API:
    """Class for example API."""

    def __init__(self, host: str, user: str, pwd: str) -> None:
        """Initialise."""
        self.host = host
        self.user = user
        self.pwd = pwd
        self.connected: bool = False

    def connect(self) -> bool:
        """Connect to api."""
        if self.user == "test" and self.pwd == "1234":
            self.connected = True
            return True
        raise APIAuthError("Error connecting to api. Invalid username or password.")

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True

    def get_devices(self) -> list[Device]:
        """Get devices on api."""
        return [
            Device(1, DeviceType.TEMP_SENSOR, "TempSensor1", randrange(18, 23)),
            Device(2, DeviceType.TEMP_SENSOR, "TempSensor2", randrange(10, 15)),
            Device(3, DeviceType.TEMP_SENSOR, "TempSensor3", randrange(12, 18)),
            Device(4, DeviceType.TEMP_SENSOR, "TempSensor4", randrange(32, 45)),
            Device(1, DeviceType.DOOR_SENSOR, "Door1", choice([True, False])),
            Device(2, DeviceType.DOOR_SENSOR, "Door2", choice([True, False])),
            Device(3, DeviceType.DOOR_SENSOR, "Door3", choice([True, False])),
            Device(4, DeviceType.DOOR_SENSOR, "Door4", choice([True, False])),
        ]


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""

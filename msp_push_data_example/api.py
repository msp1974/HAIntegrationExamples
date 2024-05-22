"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
import logging
from random import choice, randrange

_LOGGER = logging.getLogger(__name__)


class DeviceType(StrEnum):
    """Device types."""

    TEMP_SENSOR = "temp_sensor"
    DOOR_SENSOR = "door_sensor"
    OTHER = "other"


DEVICES = [
    {"id": 1, "type": DeviceType.TEMP_SENSOR},
    {"id": 2, "type": DeviceType.TEMP_SENSOR},
    {"id": 3, "type": DeviceType.TEMP_SENSOR},
    {"id": 4, "type": DeviceType.TEMP_SENSOR},
    {"id": 1, "type": DeviceType.DOOR_SENSOR},
    {"id": 2, "type": DeviceType.DOOR_SENSOR},
    {"id": 3, "type": DeviceType.DOOR_SENSOR},
    {"id": 4, "type": DeviceType.DOOR_SENSOR},
]


@dataclass
class Device:
    """API device."""

    device_id: int
    device_unique_id: str
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

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.host.replace(".", "_")

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
            Device(
                device_id=device.get("id"),
                device_unique_id=self.get_device_unique_id(
                    device.get("id"), device.get("type")
                ),
                device_type=device.get("type"),
                name=self.get_device_name(device.get("id"), device.get("type")),
                state=self.get_device_value(device.get("id"), device.get("type")),
            )
            for device in DEVICES
        ]

    def get_device_unique_id(self, device_id: str, device_type: DeviceType) -> str:
        """Return a unique device id."""
        if device_type == DeviceType.DOOR_SENSOR:
            return f"{self.controller_name}_D{device_id}"
        if device_type == DeviceType.TEMP_SENSOR:
            return f"{self.controller_name}_T{device_id}"
        return f"{self.controller_name}_Z{device_id}"

    def get_device_name(self, device_id: str, device_type: DeviceType) -> str:
        """Return the device name."""
        if device_type == DeviceType.DOOR_SENSOR:
            return f"DoorSensor{device_id}"
        if device_type == DeviceType.TEMP_SENSOR:
            return f"TempSensor{device_id}"
        return f"OtherSensor{device_id}"

    def get_device_value(self, device_id: str, device_type: DeviceType) -> int | bool:
        """Get device random value."""
        if device_type == DeviceType.DOOR_SENSOR:
            return choice([True, False])
        if device_type == DeviceType.TEMP_SENSOR:
            return randrange(15, 28)
        return randrange(1, 10)


class PushAPI(API):
    """Mimic for a push api."""

    def __init__(
        self, host: str, user: str, pwd: str, message_callback: Callable | None = None
    ) -> None:
        """Initialise."""
        super().__init__(host, user, pwd)
        self.message_callback = message_callback
        self._task: asyncio.Task = None

    async def async_connect(self) -> bool:
        """Connect tothe api.

        In this case we will create a task to add the device update function call
        to the event loop and return.
        """
        if super().connect():
            if self.message_callback:
                loop = asyncio.get_running_loop()
                self._task = loop.create_task(self.async_update_devices())
        return True

    async def async_disconnect(self) -> bool:
        """Disconnect from api."""
        if self._task:
            self._task.cancel()
        super().disconnect()
        return True

    async def async_get_devices(self) -> list[Device]:
        """Async version of get_devices."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.get_devices)

    async def async_update_devices(self) -> None:
        """Loop to send updated device data every 15s."""
        while self.connected:
            delay = randrange(10, 30)
            _LOGGER.debug("Next update for devices in %is", delay)
            await asyncio.sleep(delay)
            devices = await self.get_devices()
            if asyncio.iscoroutinefunction(self.message_callback):
                await self.message_callback(devices)
            else:
                self.message_callback(devices)


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""

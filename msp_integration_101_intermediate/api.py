"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from copy import deepcopy
import logging
from typing import Any

import requests

_LOGGER = logging.getLogger(__name__)

MOCK_DATA = [
    {
        "device_id": 1,
        "device_type": "SOCKET",
        "device_name": "Lounge Socket 1",
        "device_uid": "0123-4567-8910-1112",
        "software_version": "2.13",
        "state": "ON",
        "voltage": 239,
        "current": 1.2,
        "energy_delivered": 3247,
        "last_reboot": "2024-01-01T10:04:23Z",
    },
    {
        "device_id": 2,
        "device_type": "SOCKET",
        "device_name": "Lounge Socket 2",
        "device_uid": "0123-4567-8910-3723",
        "software_version": "2.13",
        "state": "ON",
        "voltage": 237,
        "current": 0.1,
        "energy_delivered": 634,
        "last_reboot": "2024-03-12T17:33:01Z",
    },
    {
        "device_id": 3,
        "device_type": "ON_OFF_LIGHT",
        "device_name": "Lounge Light",
        "device_uid": "0123-4567-8910-4621",
        "software_version": "1.30",
        "state": "ON",
        "voltage": 237,
        "current": 0.2,
        "off_timer": "00:00",
        "last_reboot": "2023-11-11T09:03:01Z",
    },
    {
        "device_id": 4,
        "device_type": "DIMMABLE_LIGHT",
        "device_name": "Kitchen Light",
        "device_uid": "0123-4967-8940-4691",
        "software_version": "1.35",
        "state": "ON",
        "brightness": 85,
        "voltage": 237,
        "current": 1.275,
        "off_timer": "00:00",
        "last_reboot": "2023-11-11T09:03:01Z",
    },
    {
        "device_id": 5,
        "device_type": "TEMP_SENSOR",
        "device_name": "Kitchen Temp Sensor",
        "device_uid": "0123-4567-8910-9254",
        "software_version": "3.00",
        "temperature": 18.3,
        "last_reboot": "2024-05-02T19:46:00Z",
    },
    {
        "device_id": 6,
        "device_type": "TEMP_SENSOR",
        "device_name": "Lounge Temp Sensor",
        "device_uid": "0123-4567-8910-9255",
        "software_version": "1.30",
        "temperature": 19.2,
        "last_reboot": "2024-03-12T17:33:01Z",
    },
    {
        "device_id": 7,
        "device_type": "CONTACT_SENSOR",
        "device_name": "Kitchen Door Sensor",
        "device_uid": "0123-4567-8911-6295",
        "software_version": "1.41",
        "state": "OPEN",
    },
    {
        "device_id": 8,
        "device_type": "CONTACT_SENSOR",
        "device_name": "Lounge Door Sensor",
        "device_uid": "0123-4567-8911-1753",
        "software_version": "1.41",
        "state": "CLOSED",
    },
    {
        "device_id": 9,
        "device_type": "FAN",
        "device_name": "Lounge Fan",
        "device_uid": "0123-4599-1541-1793",
        "software_version": "2.11",
        "state": "ON",
        "oscillating": "OFF",
        "speed": 2,
    },
]


class API:
    """Class for example API."""

    def __init__(self, host: str, user: str, pwd: str, mock: bool = False) -> None:
        """Initialise."""
        self.host = host
        self.user = user
        self.pwd = pwd

        # For getting and setting the mock data
        self.mock = mock
        self.mock_data = deepcopy(MOCK_DATA)

        # Mock auth error if user != test and pwd != 1234
        if mock and (self.user != "test" or self.pwd != "1234"):
            raise APIAuthError("Invalid credentials!")

    def get_data(self) -> list[dict[str, Any]]:
        """Get api data."""
        if self.mock:
            return self.get_mock_data()
        try:
            r = requests.get(f"http://{self.host}/api", timeout=10)
            return r.json()
        except requests.exceptions.ConnectTimeout as err:
            raise APIConnectionError("Timeout connecting to api") from err

    def set_data(self, device_id: int, parameter: str, value: Any) -> bool:
        """Set api data."""
        if self.mock:
            return self.set_mock_data(device_id, parameter, value)
        try:
            data = {parameter, value}
            r = requests.post(
                f"http://{self.host}/api/{device_id}", json=data, timeout=10
            )
        except requests.exceptions.ConnectTimeout as err:
            raise APIConnectionError("Timeout connecting to api") from err
        else:
            return r.status_code == 200

    # ----------------------------------------------------------------------------
    # The below methods are used to mimic a real api for the example that changes
    # its values based on commands from the switches and lights and obvioulsy will
    # not be needed wiht your real api.
    # ----------------------------------------------------------------------------
    def get_mock_data(self) -> dict[str, Any]:
        """Get mock api data."""
        return self.mock_data

    def set_mock_data(self, device_id: int, parameter: str, value: Any) -> bool:
        """Update mock data."""
        try:
            device = [
                devices
                for devices in self.mock_data
                if devices.get("device_id") == device_id
            ][0]
        except IndexError:
            # Device id does not exist
            return False

        other_devices = [
            devices
            for devices in self.mock_data
            if devices.get("device_id") != device_id
        ]

        # Modify device parameter
        if device.get(parameter):
            device[parameter] = value
        else:
            # Parameter does not exist on device
            return False

        # For sockets and lights, modify current values when off/on to mimic
        # real api and show changing sensors from your actions.
        if device["device_type"] in ["SOCKET", "ON_OFF_LIGHT", "DIMMABLE_LIGHT"]:
            if value == "OFF":
                device["current"] = 0
            else:
                original_device = [
                    devices
                    for devices in MOCK_DATA
                    if devices.get("device_id") == device_id
                ][0]
                device["current"] = original_device.get("current")

        # For dimmable lights if brightness is set to > 0, set to on
        if device["device_type"] == "DIMMABLE_LIGHT":
            if parameter == "brightness":
                if value > 0:
                    device["state"] = "ON"
                    device["current"] = value * 0.015
                else:
                    device["state"] = "OFF"

            if parameter == "state":
                if value == "ON":
                    device["brightness"] = 100
                else:
                    device["brightness"] = 0

        _LOGGER.debug("Device Updated: %s", device)

        # Update mock data
        self.mock_data = other_devices
        self.mock_data.append(device)
        return True


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""

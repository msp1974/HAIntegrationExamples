"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import logging
from typing import Any

import requests

_LOGGER = logging.getLogger(__name__)


MOCK_DATA = {
    "device": "Product1",
    "role": "Master",
    "bms_num": 0,
    "can_protocol": "",
    "type": "type1",
    "code_version": "3.01",
    "esp-idf_version": "v5.1.2",
    "cores": 2,
    "chip_id": 123456789012345,
    "uptime": "0d 16h 21m 4s",
    "charge_status": "Bulk",
    "charge_enabled": "ON",
    "charge_current": 50,
    "absorption_voltage": 56,
    "absorption_time": 30,
    "rebulk_offset": 2.5,
    "float_mode": "OFF",
    "float_time": 6,
    "manual_charge": "OFF",
    "battery_soh": 100,
    "slaves_total": 0,
    "force_chg_v": 44,
    "discharge_enabled": "ON",
    "discharge_current": 100,
    "min_discharge_v": 48,
    "max_cycles": 6000,
    "cycles_offset": 0,
    "logs": "OFF",
    "min_voltage_cell": 11,
    "max_voltage_cell": 13,
    "min_cell_voltage": 3.388,
    "max_cell_voltage": 3.398,
    "delta_cell_voltage": 0.01,
    "average_cell_voltage": 3.393,
    "cell_voltage_1": 3.394,
    "cell_voltage_2": 3.394,
    "cell_voltage_3": 3.393,
    "cell_voltage_4": 3.394,
}


class API:
    """Class for example API."""

    def __init__(self, host: str, user: str, pwd: str) -> None:
        """Initialise."""
        self.host = host
        self.user = user
        self.pwd = pwd

    def get_data(self, path: str) -> dict[str, Any]:
        """Get api data."""
        try:
            r = requests.get(f"{self.host}/{path}", timeout=10)
            return r.json()
        except requests.exceptions.ConnectTimeout as err:
            raise APIConnectionError("Timeout connecting to api") from err

    def get_mock_data(self, path: str) -> dict[str, Any]:
        """Get mock data."""
        return MOCK_DATA


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""

"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BINARY_SENSORS, DOMAIN
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: ExampleCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    # Enumerate all the binary sensors in your data value from your DataUpdateCoordinator and add an instance of your binary sensor class
    # to a list for each one.
    # THis example uses the parameter names listed in constants from const.py
    # This maybe different in your specific case, depending on how your data is structured
    binary_sensors = [
        ExampleBinarySensor(coordinator, parameter)
        for parameter in BINARY_SENSORS
        if coordinator.get_api_data_value(parameter)
    ]

    # Create the binary sensors.
    async_add_entities(binary_sensors)


class ExampleBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Implementation of a sensor."""

    def __init__(self, coordinator: ExampleCoordinator, parameter_name: str) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.parameter = parameter_name
        self.parameter_value = coordinator.get_api_data_value(self.parameter)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.parameter_value = self.coordinator.get_api_data_value(self.parameter)
        _LOGGER.debug("Parameter: %s, Value: %s", self.parameter, self.parameter_value)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # Set to none for our base class and adjust in classes that inherit this.
        # https://developers.home-assistant.io/docs/core/entity/binary-sensor#available-device-classes
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        device_name = self.coordinator.get_api_data_value("device")
        return DeviceInfo(
            name=device_name,
            manufacturer="ACME Manufacturer",
            model="MyAPI v1",
            sw_version="1.0",
            identifiers={(DOMAIN, f"{device_name}")},
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        # Make nive name format by replacing parameter name _'s and title case
        return self.parameter.replace("_", " ").title()

    @property
    def is_on(self) -> bool | None:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return self.parameter_value == "ON"

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return (
            f"{DOMAIN}-{self.coordinator.get_api_data_value("device")}-{self.parameter}"
        )

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return None

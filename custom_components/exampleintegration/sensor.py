"""Interfaces with the Example api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Device, DeviceType
from .const import DOMAIN
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    coordinator: ExampleCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator  # config_entry.runtime_data.coordinator
    sensors = [
        ExampleSensor(coordinator, device)
        for device in coordinator.data
        if device.device_type == DeviceType.TEMP_SENSOR
    ]

    async_add_entities(sensors)


class ExampleSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(self, coordinator: ExampleCoordinator, device: Device) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        self.device = self.coordinator.get_device_by_id(self.device_id)
        _LOGGER.debug("Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            name=f"ExampleDevice{self.device.device_id}",
            manufacturer="ACME Manufacturer",
            model="Door&Temp v1",
            sw_version="1.0",
            identifiers={(DOMAIN, f"exampledevice-sensor-{self.device.device_id}")},
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return f"{DOMAIN}-{self.device.device_id}-{self.device.name}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return {}

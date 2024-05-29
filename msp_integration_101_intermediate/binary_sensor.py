"""Binary sensor setup for our Integration."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import ExampleBaseEntity
from .const import DOMAIN
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

    # ----------------------------------------------------------------------------
    # Here we are going to add some binary sensors for the contact sensors in our
    # mock data. So we add an instance of our ExampleBinarySensor class for each
    # contact sensor we have in our data.
    # ----------------------------------------------------------------------------
    binary_sensors = [
        ExampleBinarySensor(coordinator, device, "state")
        for device in coordinator.data
        if device.get("device_type") == "CONTACT_SENSOR"
    ]

    # Create the binary sensors.
    async_add_entities(binary_sensors)


class ExampleBinarySensor(ExampleBaseEntity, BinarySensorEntity):
    """Implementation of a sensor.

    This inherits our ExampleBaseEntity to set common properties.
    See base.py for this class.

    https://developers.home-assistant.io/docs/core/entity/binary-sensor
    """

    # https://developers.home-assistant.io/docs/core/entity/binary-sensor#available-device-classes
    _attr_device_class = BinarySensorDeviceClass.DOOR

    @property
    def is_on(self) -> bool | None:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return (
            self.coordinator.get_device_parameter(self.device_id, self.parameter)
            == "OPEN"
        )

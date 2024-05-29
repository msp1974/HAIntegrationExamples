"""Switch setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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
    # Here we enumerate the switches in your data value from your
    # DataUpdateCoordinator and add an instance of your switch class to a list
    # for each one.
    # This maybe different in your specific case, depending on how your data is
    # structured
    # ----------------------------------------------------------------------------

    switches = [
        ExampleSwitch(coordinator, device, "state")
        for device in coordinator.data
        if device.get("device_type") == "SOCKET"
    ]

    # Create the binary sensors.
    async_add_entities(switches)


class ExampleSwitch(ExampleBaseEntity, SwitchEntity):
    """Implementation of a switch.

    This inherits our ExampleBaseEntity to set common properties.
    See base.py for this class.

    https://developers.home-assistant.io/docs/core/entity/switch
    """

    _attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool | None:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return (
            self.coordinator.get_device_parameter(self.device_id, self.parameter)
            == "ON"
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data, self.device_id, self.parameter, "ON"
        )
        # ----------------------------------------------------------------------------
        # Use async_refresh on the DataUpdateCoordinator to perform immediate update.
        # Using self.async_update or self.coordinator.async_request_refresh may delay update due
        # to trying to batch requests.
        # ----------------------------------------------------------------------------
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data, self.device_id, self.parameter, "OFF"
        )
        # ----------------------------------------------------------------------------
        # Use async_refresh on the DataUpdateCoordinator to perform immediate update.
        # Using self.async_update or self.coordinator.async_request_refresh may delay update due
        # to trying to batch requests.
        # ----------------------------------------------------------------------------
        await self.coordinator.async_refresh()

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["last_rebooted"] = self.coordinator.get_device_parameter(
            self.device_id, "last_reboot"
        )
        return attrs

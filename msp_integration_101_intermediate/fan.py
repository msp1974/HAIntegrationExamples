"""Fan setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
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
    """Set up the Fans."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: ExampleCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    # ----------------------------------------------------------------------------
    # Here we are going to add some lights entities for the lights in our mock data.
    # We have an on/off light and a dimmable light in our mock data, so add each
    # specific class based on the light type.
    # ----------------------------------------------------------------------------

    # On/Off lights
    fans = [
        ExampleFan(coordinator, device, "state")
        for device in coordinator.data
        if device.get("device_type") == "FAN"
    ]

    # Create the fans.
    async_add_entities(fans)


class ExampleFan(ExampleBaseEntity, FanEntity):
    """Implementation of a fan.

    This inherits our ExampleBaseEntity to set common properties.
    See base.py for this class.

    https://developers.home-assistant.io/docs/core/entity/fan/
    """

    _attr_speed_count = 3
    _attr_supported_features = FanEntityFeature.OSCILLATE | FanEntityFeature.SET_SPEED

    _speed_parameter = "speed"
    _oscillating_parameter = "oscillating"

    @property
    def is_on(self) -> bool | None:
        """Return if the fan is on."""
        # This needs to enumerate to true or false
        return (
            self.coordinator.get_device_parameter(self.device_id, self.parameter)
            == "ON"
        )

    @property
    def oscillating(self) -> bool | None:
        """Return whether or not the fan is currently oscillating."""
        return (
            self.coordinator.get_device_parameter(
                self.device_id, self._oscillating_parameter
            )
            == "ON"
        )

    @property
    def percentage(self) -> int | None:
        """Return the current speed as a percentage."""
        speed = self.coordinator.get_device_parameter(
            self.device_id, self._speed_parameter
        )
        # Need to return a percentage but our fan has speeds 0,1,2,3
        return int(self.percentage_step * speed)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""

        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data, self.device_id, self.parameter, "ON"
        )

        if percentage:
            self.set_our_fan_speed(percentage)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""

        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data, self.device_id, self.parameter, "OFF"
        )
        await self.coordinator.async_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""

        if percentage == 0:
            await self.async_turn_off()
        elif not self.is_on:
            await self.async_turn_on(percentage)
        else:
            await self.set_our_fan_speed(percentage)
            await self.coordinator.async_refresh()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Oscillate the fan."""

        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data,
            self.device_id,
            self._oscillating_parameter,
            "ON" if oscillating else "OFF",
        )
        await self.coordinator.async_refresh()

    # ----------------------------------------------------------------------------
    # Added a couple of custom methods to make our code simpler
    # ----------------------------------------------------------------------------

    def speed_from_percentage(self, percentage) -> int:
        """Get fan speed from percentage."""
        return int(round(percentage / self.percentage_step, 0))

    async def set_our_fan_speed(self, percentage: int) -> None:
        """Set fan speed."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data,
            self.device_id,
            self._speed_parameter,
            self.speed_from_percentage(percentage),
        )

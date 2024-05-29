"""Light setup for our Integration."""

from datetime import timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import ExampleBaseEntity
from .const import CONF_OFF_TIME, DOMAIN, SET_OFF_TIMER_ENTITY_SERVICE_NAME
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
    # Here we are going to add some lights entities for the lights in our mock data.
    # We have an on/off light and a dimmable light in our mock data, so add each
    # specific class based on the light type.
    # ----------------------------------------------------------------------------
    lights = []

    # On/Off lights
    lights.extend(
        [
            ExampleOnOffLight(coordinator, device, "state")
            for device in coordinator.data
            if device.get("device_type") == "ON_OFF_LIGHT"
        ]
    )

    # Dimmable lights
    lights.extend(
        [
            ExampleDimmableLight(coordinator, device, "state")
            for device in coordinator.data
            if device.get("device_type") == "DIMMABLE_LIGHT"
        ]
    )

    # Create the lights.
    async_add_entities(lights)

    # ----------------------------------------------------------------------------
    # Add an Entity Service
    #
    # This example creates a service to set an off timer for our mock device.
    # You can have your schema as anything you need and must relate to the entry
    # in services.yaml.  Best to set your target filters in serivces.yaml to match
    # what this can be called on, so your users cannot pick inappropriate entities.
    # If an entity is supplied that does not support this service, nothing will
    # happen.
    #
    # The function async_set_off_timer has to be part of your entity class and
    # is shown below.
    #
    # You will see the off timer sensor on a light update to reflect the time you
    # set.
    # ----------------------------------------------------------------------------
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SET_OFF_TIMER_ENTITY_SERVICE_NAME,
        {
            vol.Required(CONF_OFF_TIME): cv.time_period,
        },
        "async_set_off_timer",
    )


class ExampleOnOffLight(ExampleBaseEntity, LightEntity):
    """Implementation of an on/off light.

    This inherits our ExampleBaseEntity to set common properties.
    See base.py for this class.

    https://developers.home-assistant.io/docs/core/entity/light/
    """

    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

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

    async def async_set_off_timer(self, off_time: timedelta) -> None:
        """Handle the set off timer service call.

        Important here to have your service parameters included in your
        function as they are passed as named parameters.
        """
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data,
            self.device_id,
            "off_timer",
            ":".join(str(off_time).split(":")[:2]),
        )
        # We have made a change to our device, so call a refresh to get updated data.
        # We use async_request_refresh here to batch the updates in case you select
        # multiple entities.
        await self.coordinator.async_request_refresh()


class ExampleDimmableLight(ExampleOnOffLight):
    """Implementation of a dimmable light."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        # Our light is in range 0..100, so convert
        return int(
            self.coordinator.get_device_parameter(self.device_id, "brightness")
            * (255 / 100)
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] * (100 / 255))
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_data, self.device_id, "brightness", brightness
            )
        else:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_data, self.device_id, self.parameter, "ON"
            )
        # ----------------------------------------------------------------------------
        # Use async_refresh on the DataUpdateCoordinator to perform immediate update.
        # Using self.async_update or self.coordinator.async_request_refresh may delay update due
        # to trying to batch requests and cause wierd UI behaviour.
        # ----------------------------------------------------------------------------
        await self.coordinator.async_refresh()

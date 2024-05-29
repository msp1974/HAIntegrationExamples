"""Config flows for our integration.

This config flow demonstrates many aspects of possible config flows.

Multi step flows
Menus
Using your api data in your flow
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_CHOOSE,
    CONF_DESCRIPTION,
    CONF_HOST,
    CONF_MINIMUM,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector

from .api import API, APIAuthError, APIConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Adjust the data schema to the data that you need
# ----------------------------------------------------------------------------
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, description={"suggested_value": "10.10.10.1"}): str,
        vol.Required(CONF_USERNAME, description={"suggested_value": "test"}): str,
        vol.Required(CONF_PASSWORD, description={"suggested_value": "1234"}): str,
    }
)

# ----------------------------------------------------------------------------
# Example selectors
# There are lots of selectors available for you to use, described at
# https://www.home-assistant.io/docs/blueprint/selectors/
# ----------------------------------------------------------------------------
STEP_SETTINGS_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSORS): selector(
            {"entity": {"filter": {"integration": "sun"}}}
        ),
        # Take note of translation key and entry in strings.json and translation files.
        vol.Required(CONF_CHOOSE): selector(
            {
                "select": {
                    "options": ["all", "light", "switch"],
                    "mode": "dropdown",
                    "translation_key": "example_selector",
                }
            }
        ),
        vol.Required(CONF_MINIMUM): selector({"number": {"min": 0, "max": 100}}),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        # ----------------------------------------------------------------------------
        # If your api is not async, use the executor to access it
        # If you cannot connect, raise CannotConnect
        # If the authentication is wrong, raise InvalidAuth
        # ----------------------------------------------------------------------------
        api = API(data[CONF_HOST], data[CONF_USERNAME], data[CONF_PASSWORD], mock=True)
        await hass.async_add_executor_job(api.get_data)
    except APIAuthError as err:
        raise InvalidAuth from err
    except APIConnectionError as err:
        raise CannotConnect from err
    return {"title": f"Example Integration - {data[CONF_HOST]}"}


async def validate_settings(hass: HomeAssistant, data: dict[str, Any]) -> bool:
    """Another validation method for our config steps."""
    return True


class ExampleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Example Integration."""

    VERSION = 1
    _input_data: dict[str, Any]
    _title: str

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler.

        Remove this method and the ExampleOptionsFlowHandler class
        if you do not want any options for your integration.
        """
        return ExampleOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step.

        Called when you initiate adding an integration via the UI
        """

        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            try:
                # ----------------------------------------------------------------------------
                # Validate that the setup data is valid and if not handle errors.
                # You can do any validation you want or no validation on each step.
                # The errors["base"] values match the values in your strings.json and translation files.
                # ----------------------------------------------------------------------------
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Validation was successful, so proceed to the next step.

                # ----------------------------------------------------------------------------
                # Setting our unique id here just because we have the info at this stage to do that
                # and it will abort early on in the process if alreay setup.
                # You can put this in any step however.
                # ----------------------------------------------------------------------------
                await self.async_set_unique_id(info.get("title"))
                self._abort_if_unique_id_configured()

                # Set our title variable here for use later
                self._title = info["title"]

                # ----------------------------------------------------------------------------
                # You need to save the input data to a class variable as you go through each step
                # to ensure it is accessible across all steps.
                # ----------------------------------------------------------------------------
                self._input_data = user_input

                # Call the next step
                return await self.async_step_settings()

        # Show initial form.
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            last_step=False,  # Adding last_step True/False decides whether form shows Next or Submit buttons
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the second step.

        Our second config flow step.
        Works just the same way as the first step.
        Except as it is our last step, we create the config entry after any validation.
        """

        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            if not await validate_settings(self.hass, user_input):
                errors["base"] = "invalid_settings"

            if "base" not in errors:
                # ----------------------------------------------------------------------------
                # Validation was successful, so create the config entry.
                # ----------------------------------------------------------------------------
                self._input_data.update(user_input)
                return self.async_create_entry(title=self._title, data=self._input_data)

        # ----------------------------------------------------------------------------
        # Show settings form.  The step id always needs to match the bit after async_step_ in your method.
        # Set last_step to True here if it is last step.
        # ----------------------------------------------------------------------------
        return self.async_show_form(
            step_id="settings",
            data_schema=STEP_SETTINGS_DATA_SCHEMA,
            errors=errors,
            last_step=True,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add reconfigure step to allow to reconfigure a config entry.

        This methid displays a reconfigure option in the integration and is
        different to options.
        It can be used to reconfigure any of the data submitted when first installed.
        This is optional and can be removed if you do not want to allow reconfiguration.
        """
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            try:
                user_input[CONF_HOST] = config_entry.data[CONF_HOST]
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    unique_id=config_entry.unique_id,
                    data={**config_entry.data, **user_input},
                    reason="reconfigure_successful",
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=config_entry.data[CONF_USERNAME]
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class ExampleOptionsFlowHandler(OptionsFlow):
    """Handles the options flow.

    Here we use an initial menu to select different options forms,
    and show how to use api data to populate a selector.
    """

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Handle options flow.

        Display an options menu
        option ids relate to step function name
        Also need to be in strings.json and translation files.
        """

        return self.async_show_menu(
            step_id="init",
            menu_options=["option1", "option2"],
        )

    async def async_step_option1(self, user_input=None):
        """Handle menu option 1 flow."""
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(title="", data=options)

        # ----------------------------------------------------------------------------
        # It is recommended to prepopulate options fields with default values if
        # available.
        # These will be the same default values you use on your coordinator for
        # setting variable values if the option has not been set.
        # ----------------------------------------------------------------------------
        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): (vol.All(vol.Coerce(int), vol.Clamp(min=MIN_SCAN_INTERVAL))),
                vol.Optional(
                    CONF_DESCRIPTION,
                    default=self.options.get(CONF_DESCRIPTION),
                ): str,
            }
        )

        return self.async_show_form(step_id="option1", data_schema=data_schema)

    async def async_step_option2(self, user_input=None):
        """Handle menu option 2 flow.

        In this option, we show how to use dynamic data in a selector.
        """
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(title="", data=options)

        coordinator: ExampleCoordinator = self.hass.data[DOMAIN][
            self.config_entry.entry_id
        ].coordinator
        devices = coordinator.data
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_CHOOSE, default=devices[0]["device_name"]): selector(
                    {
                        "select": {
                            "options": [device["device_name"] for device in devices],
                            "mode": "dropdown",
                            "sort": True,
                        }
                    }
                ),
            }
        )

        return self.async_show_form(step_id="option2", data_schema=data_schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

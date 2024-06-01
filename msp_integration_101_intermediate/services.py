"""Global services file.

This needs to be viewed with the services.yaml file
to demonstrate the different setup for using these services in the UI

IMPORTANT NOTES:
To ensure your service runs on the event loop, either make service function async
or decorate with @callback.  However, ensure that your function is non blocking or,
if it is, run in the executor.
Both examples are shown here.  Running services on different threads can cause issues.

https://developers.home-assistant.io/docs/dev_101_services/
"""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID, ATTR_NAME
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import async_get as async_get_dr

from .const import DOMAIN, RENAME_DEVICE_SERVICE_NAME, RESPONSE_SERVICE_NAME
from .coordinator import ExampleCoordinator

ATTR_TEXT = "text"

# Services schemas
RENAME_DEVICE_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): int,
        vol.Required(ATTR_NAME): str,
    }
)

RESPONSE_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): int,
    }
)


class ExampleServicesSetup:
    """Class to handle Integration Services."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialise services."""
        self.hass = hass
        self.config_entry = config_entry
        self.coordinator: ExampleCoordinator = hass.data[DOMAIN][
            config_entry.entry_id
        ].coordinator

        self.setup_services()

    def setup_services(self):
        """Initialise the services in Hass."""
        # ----------------------------------------------------------------------------
        # A simple definition of a service with 2 parameters, as denoted by the
        # RENAME_DEVICE_SERVICE_SCHEMA
        # ----------------------------------------------------------------------------
        self.hass.services.async_register(
            DOMAIN,
            RENAME_DEVICE_SERVICE_NAME,
            self.rename_device,
            schema=RENAME_DEVICE_SERVICE_SCHEMA,
        )

        # ----------------------------------------------------------------------------
        # The definition here for a response service is the same as before but you
        # must include supports_response = only/optional
        # https://developers.home-assistant.io/docs/dev_101_services/#supporting-response-data
        # ----------------------------------------------------------------------------
        self.hass.services.async_register(
            DOMAIN,
            RESPONSE_SERVICE_NAME,
            self.async_response_service,
            schema=RESPONSE_SERVICE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    async def rename_device(self, service_call: ServiceCall) -> None:
        """Execute rename device service call function.

        This will send a command to the api which will rename the
        device and then update the device registry to match.

        Data from the service call will be in service_call.data
        as seen below.
        """
        device_id = service_call.data[ATTR_DEVICE_ID]
        device_name = service_call.data[ATTR_NAME]

        # check for valid device id
        try:
            assert self.coordinator.get_device(device_id) is not None
        except AssertionError as ex:
            raise HomeAssistantError(
                "Error calling service: The device ID does not exist"
            ) from ex
        else:
            result = await self.hass.async_add_executor_job(
                self.coordinator.api.set_data, device_id, "device_name", device_name
            )

            if result:
                # ----------------------------------------------------------------------------
                # In this scenario, we would need to update the device registry name here
                # as it will not automatically update.
                # ----------------------------------------------------------------------------

                # Get our device from coordinator data to retrieve its devie_uid as that is
                # what we used in the devices identifiers.
                device = self.coordinator.get_device(device_id)

                # Get the device registry
                dr = async_get_dr(self.hass)

                # Get the device entry in the registry by its identifiers.  This is the same as
                # we used to set them in base.py
                device_entry = dr.async_get_device([(DOMAIN, device["device_uid"])])

                # Update our device entry with the new name.  You will see this change in the UI
                dr.async_update_device(device_entry.id, name=device_name)

            await self.coordinator.async_request_refresh()

    @callback
    def async_response_service(self, service_call: ServiceCall) -> None:
        """Execute response service call function.

        This will take a device id and return json data for the
        devices info on the api.

        If the device does not exist, it will raise an error.
        """
        device_id = service_call.data[ATTR_DEVICE_ID]
        response = self.coordinator.get_device(device_id)

        try:
            assert response is not None
        except AssertionError as ex:
            raise HomeAssistantError(
                "Error calling service: The device ID does not exist"
            ) from ex
        else:
            return response

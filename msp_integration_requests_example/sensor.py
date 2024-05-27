"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BATTERY_SENSORS,
    CURRENT_SENSORS,
    DOMAIN,
    OTHER_SENSORS,
    VOLTAGE_SENSORS,
)
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: ExampleCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    sensors = []

    # Add voltage sensors - ExampleVoltageSensor inherits the ExampleBaseSensor class
    # and sets the devide type and unit of measure.
    sensors.extend(
        [
            ExampleVoltageSensor(coordinator, parameter)
            for parameter in VOLTAGE_SENSORS
            if coordinator.get_api_data_value(parameter)
        ]
    )

    # Same as above but different device class and unit of measure
    sensors.extend(
        [
            ExampleCurrentSensor(coordinator, parameter)
            for parameter in CURRENT_SENSORS
            if coordinator.get_api_data_value(parameter)
        ]
    )

    # Same as above but different device class and unit of measure
    sensors.extend(
        [
            ExampleBatterySensor(coordinator, parameter)
            for parameter in BATTERY_SENSORS
            if coordinator.get_api_data_value(parameter)
        ]
    )

    # Our generic sensors
    sensors.extend(
        [
            ExampleBaseSensor(coordinator, parameter)
            for parameter in OTHER_SENSORS
            if coordinator.get_api_data_value(parameter)
        ]
    )

    # Now add the sensors.
    async_add_entities(sensors)


class ExampleBaseSensor(CoordinatorEntity, SensorEntity):
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
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
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
            model=self.coordinator.get_api_data_value("role"),
            sw_version=self.coordinator.get_api_data_value("code_version"),
            identifiers={(DOMAIN, f"{device_name}")},
        )

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        # Make nive name format by replacing parameter name _'s and title case
        return self.parameter.replace("_", " ").title()

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return self.parameter_value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return None

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return None

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


class ExampleVoltageSensor(ExampleBaseSensor):
    """Class to handle voltage sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides device_class and unit_of_measure properties
    """

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.VOLTAGE

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfElectricPotential.VOLT


class ExampleCurrentSensor(ExampleBaseSensor):
    """Class to handle current sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides device_class and unit_of_measure properties
    """

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.CURRENT

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfElectricCurrent.AMPERE


class ExampleBatterySensor(ExampleBaseSensor):
    """Class to handle battery sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides device_class and unit_of_measure properties
    """

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.BATTERY

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return PERCENTAGE

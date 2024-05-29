"""Sensor setup for our Integration.

Here we use a different method to define some of our entity classes.
As, in our example, so much is common, we use our base entity class to define
many properties, then our base sensor class to define the property to get the
value of the sensor.

As such, for all our other sensor types, we can just set the _attr_ value to
keep our code small and easily readable.  You can do this for all entity properties(attributes)
if you so wish, or mix and match to suit.
"""

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import ExampleBaseEntity
from .const import DOMAIN
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class SensorTypeClass:
    """Class for holding sensor type to sensor class."""

    type: str
    sensor_class: object


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

    # ----------------------------------------------------------------------------
    # Here we enumerate the sensors in your data value from your
    # DataUpdateCoordinator and add an instance of your sensor class to a list
    # for each one.
    # This maybe different in your specific case, depending on how your data is
    # structured
    # ----------------------------------------------------------------------------

    sensor_types = [
        SensorTypeClass("current", ExampleCurrentSensor),
        SensorTypeClass("energy_delivered", ExampleEnergySensor),
        SensorTypeClass("off_timer", ExampleOffTimerSensor),
        SensorTypeClass("temperature", ExampleTemperatureSensor),
        SensorTypeClass("voltage", ExampleVoltageSensor),
    ]

    sensors = []

    for sensor_type in sensor_types:
        sensors.extend(
            [
                sensor_type.sensor_class(coordinator, device, sensor_type.type)
                for device in coordinator.data
                if device.get(sensor_type.type)
            ]
        )

    # Now create the sensors.
    async_add_entities(sensors)


class ExampleBaseSensor(ExampleBaseEntity, SensorEntity):
    """Implementation of a sensor.

    This inherits our ExampleBaseEntity to set common properties.
    See base.py for this class.

    https://developers.home-assistant.io/docs/core/entity/sensor
    """

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return self.coordinator.get_device_parameter(self.device_id, self.parameter)


class ExampleCurrentSensor(ExampleBaseSensor):
    """Class to handle current sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_suggested_display_precision = 2


class ExampleEnergySensor(ExampleBaseSensor):
    """Class to handle energy sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR


class ExampleOffTimerSensor(ExampleBaseSensor):
    """Class to handle off timer sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """


class ExampleTemperatureSensor(ExampleBaseSensor):
    """Class to handle temperature sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1


class ExampleVoltageSensor(ExampleBaseSensor):
    """Class to handle voltage sensors.

    This inherits the ExampleBaseSensor and so uses all the properties and methods
    from that class and then overrides specific attributes relevant to this sensor type.
    """

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_suggested_display_precision = 0

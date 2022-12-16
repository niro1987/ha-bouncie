"""Sensors for Bouncie devices."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import LENGTH_MILES, PERCENTAGE, SPEED_MILES_PER_HOUR
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from .common import BouncieVehiclesDataUpdateCoordinator
from .const import (
    ATTR_DATA,
    ATTR_EVENT,
    ATTR_NICKNAME,
    ATTR_STATS,
    ATTR_VIN,
    DOMAIN,
    EVENT_TRIPDATA,
    EVENT_TRIPEND,
    VEHICLES_COORDINATOR,
)
from .entity import BouncieEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: BouncieVehiclesDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][VEHICLES_COORDINATOR]

    entities: list[SensorEntity] = []

    # Odometer
    entities.extend(
        BouncieOdometer(coordinator, vin)
        for vin, vehicle in coordinator.data.items()
        if vehicle[ATTR_STATS].get("odometer") is not None
    )

    # Fuellevel
    entities.extend(
        BouncieFuelLevelSensor(coordinator, vin)
        for vin, vehicle in coordinator.data.items()
        if vehicle[ATTR_STATS].get("fuelLevel") is not None
    )

    # Speed
    entities.extend(
        BouncieSpeedSensor(coordinator, vin)
        for vin, vehicle in coordinator.data.items()
        if vehicle[ATTR_STATS].get("speed") is not None
    )

    async_add_entities(entities)


class BouncieOdometer(BouncieEntity, SensorEntity):
    """Representation of a Bouncie Odometer Sensor."""

    def __init__(self, coordinator: BouncieVehiclesDataUpdateCoordinator, vin: str):
        """Initialize the sensor."""
        super().__init__(coordinator, vin)

        vehicle = coordinator.data[vin]
        self._attr_unique_id = f"{vin}_odometer"
        self._attr_name = f"{vehicle[ATTR_NICKNAME]} Odometer"
        self._attr_device_class = "distance"
        self._attr_state_class = STATE_CLASS_TOTAL
        self._attr_last_reset = dt.parse_datetime(
            f"{vehicle[ATTR_STATS]['lastUpdated']}"
        )

        self._odometer: float = vehicle[ATTR_STATS]["odometer"]

    @property
    def native_value(self) -> float:
        """Return the value reported by the sensor."""
        return round(self._odometer, 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return LENGTH_MILES

    async def async_event_received(self, event: Event) -> None:
        """Update status if event received for this entity."""
        status = event.data
        if status[ATTR_VIN] == self.vin:
            if status[ATTR_EVENT] == EVENT_TRIPEND:
                self._odometer = status["end"]["odometer"]
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        vehicle = self.coordinator.data[self.vin]
        self._odometer = vehicle[ATTR_STATS]["odometer"]
        self.async_write_ha_state()


class BouncieFuelLevelSensor(BouncieEntity, SensorEntity):
    """Representation of a Bouncie FuelLevel Sensor."""

    def __init__(self, coordinator: BouncieVehiclesDataUpdateCoordinator, vin: str):
        """Initialize the sensor."""
        super().__init__(coordinator, vin)

        vehicle = coordinator.data[vin]
        self._attr_unique_id = f"{vin}_fuelLevel"
        self._attr_name = f"{vehicle[ATTR_NICKNAME]} Fuel Level"
        self._attr_state_class = STATE_CLASS_MEASUREMENT

        self._fuellevel: float = vehicle[ATTR_STATS]["fuelLevel"]

    @property
    def native_value(self) -> float:
        """Return the value reported by the sensor."""
        return round(self._fuellevel, 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return PERCENTAGE

    async def async_event_received(self, event: Event) -> None:
        """Update status if event received for this entity."""
        status = event.data
        if status[ATTR_VIN] == self.vin and status[ATTR_EVENT] == EVENT_TRIPDATA:
            for entry in reversed(status["data"]):
                if (fuellevel := entry.get("fuelLevelInput")) is not None:
                    self._fuellevel = fuellevel
                    break
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        vehicle = self.coordinator.data[self.vin]
        self._fuellevel = vehicle[ATTR_STATS]["fuelLevel"]
        self.async_write_ha_state()


class BouncieSpeedSensor(BouncieEntity, SensorEntity):
    """Representation of a Bouncie Speed Sensor."""

    def __init__(self, coordinator: BouncieVehiclesDataUpdateCoordinator, vin: str):
        """Initialize the sensor."""
        super().__init__(coordinator, vin)

        vehicle = coordinator.data[vin]
        self._attr_unique_id = f"{vin}_speed"
        self._attr_name = f"{vehicle[ATTR_NICKNAME]} Speed"
        self._attr_state_class = STATE_CLASS_MEASUREMENT
        self._attr_device_class = "speed"

        self._speed: float = vehicle[ATTR_STATS]["speed"]

    @property
    def native_value(self) -> float:
        """Return the value reported by the sensor."""
        return round(self._speed, 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return SPEED_MILES_PER_HOUR

    async def async_event_received(self, event: Event) -> None:
        """Update status if event received for this entity."""
        status = event.data
        if status[ATTR_VIN] == self.vin:
            if status[ATTR_EVENT] == EVENT_TRIPDATA:
                self._speed = status[ATTR_DATA][-1]["speed"]
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        vehicle = self.coordinator.data[self.vin]
        self._speed: float = vehicle[ATTR_STATS]["speed"]
        self.async_write_ha_state()

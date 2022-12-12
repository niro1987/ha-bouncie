from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import LENGTH_MILES, PERCENTAGE, SPEED_MILES_PER_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import dt

from .common import BouncieVehiclesDataUpdateCoordinator
from .const import (
    ATTR_MAKE,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_NICKNAME,
    ATTR_STATS,
    BOUNCIE_PORTAL,
    DOMAIN,
    VEHICLES_COORDINATOR,
)

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
        if vehicle["stats"].get("odometer") is not None
    )

    # Fuellevel
    entities.extend(
        BouncieFuelLevelSensor(coordinator, vin)
        for vin, vehicle in coordinator.data.items()
        if vehicle["stats"].get("fuelLevel") is not None
    )

    # Speed
    entities.extend(
        BouncieSpeedSensor(coordinator, vin)
        for vin, vehicle in coordinator.data.items()
        if vehicle["stats"].get("speed") is not None
    )

    async_add_entities(entities)


class BouncieOdometer(CoordinatorEntity, SensorEntity):
    """Representation of a Bouncie Odometer Sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, vin: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.vin: str = vin

        vehicle = coordinator.data[vin]
        self._attr_unique_id = f"{vin}_odometer"
        self._attr_name = f"{vehicle[ATTR_NICKNAME]} Odometer"
        self._attr_device_class = "distance"
        self._attr_state_class = STATE_CLASS_TOTAL
        self._attr_last_reset = dt.parse_datetime(
            f"{vehicle[ATTR_STATS]['lastUpdated']}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        vehicle = self.coordinator.data[self.vin]
        return DeviceInfo(
            name=vehicle[ATTR_NICKNAME],
            manufacturer=vehicle[ATTR_MODEL][ATTR_MAKE],
            model=vehicle[ATTR_MODEL][ATTR_NAME],
            identifiers={(DOMAIN, self.vin)},
            configuration_url=BOUNCIE_PORTAL,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.vin in self.coordinator.data

    @property
    def native_value(self) -> float:
        """Return the value reported by the sensor."""
        vehicle = self.coordinator.data[self.vin]
        return round(float(vehicle[ATTR_STATS]["odometer"]), 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return LENGTH_MILES


class BouncieFuelLevelSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Bouncie FuelLevel Sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, vin: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.vin: str = vin

        vehicle = coordinator.data[vin]
        self._attr_unique_id = f"{vin}_fuelLevel"
        self._attr_name = f"{vehicle[ATTR_NICKNAME]} Fuel Level"
        self._attr_state_class = STATE_CLASS_MEASUREMENT

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        vehicle = self.coordinator.data[self.vin]
        return DeviceInfo(
            name=vehicle[ATTR_NICKNAME],
            manufacturer=vehicle[ATTR_MODEL][ATTR_MAKE],
            model=vehicle[ATTR_MODEL][ATTR_NAME],
            identifiers={(DOMAIN, self.vin)},
            configuration_url=BOUNCIE_PORTAL,
        )

    @property
    def native_value(self) -> float:
        """Return the value reported by the sensor."""
        vehicle = self.coordinator.data[self.vin]
        return round(float(vehicle[ATTR_STATS]["fuelLevel"]), 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return PERCENTAGE


class BouncieSpeedSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Bouncie Speed Sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, vin: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.vin: str = vin

        vehicle = coordinator.data[vin]
        self._attr_unique_id = f"{vin}_speed"
        self._attr_name = f"{vehicle[ATTR_NICKNAME]} Speed"
        self._attr_state_class = STATE_CLASS_MEASUREMENT
        self._attr_device_class = "speed"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        vehicle = self.coordinator.data[self.vin]
        return DeviceInfo(
            name=vehicle[ATTR_NICKNAME],
            manufacturer=vehicle[ATTR_MODEL][ATTR_MAKE],
            model=vehicle[ATTR_MODEL][ATTR_NAME],
            identifiers={(DOMAIN, self.vin)},
            configuration_url=BOUNCIE_PORTAL,
        )

    @property
    def native_value(self) -> float:
        """Return the value reported by the sensor."""
        vehicle = self.coordinator.data[self.vin]
        return round(float(vehicle[ATTR_STATS]["speed"]), 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return SPEED_MILES_PER_HOUR

"""Device Tracker for Bouncie devices."""
from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import BouncieVehiclesDataUpdateCoordinator
from .const import (
    ATTR_DATA,
    ATTR_EVENT,
    ATTR_GPS,
    ATTR_LAT,
    ATTR_LOCATION,
    ATTR_LON,
    ATTR_NICKNAME,
    ATTR_STATS,
    ATTR_VIN,
    DOMAIN,
    EVENT_TRIPDATA,
    UPDATE_INTERVAL,
    VEHICLES_COORDINATOR,
)
from .entity import BouncieEntity

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = UPDATE_INTERVAL
PARALLEL_UPDATES = 5


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bouncie tracker from config entry."""
    coordinator: BouncieVehiclesDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][VEHICLES_COORDINATOR]
    entities: list[BouncieDeviceTracker] = []

    for vin in coordinator.data:
        entities.append(BouncieDeviceTracker(coordinator, vin))
    async_add_entities(entities)


class BouncieDeviceTracker(BouncieEntity, TrackerEntity):
    """Bouncie device tracker."""

    _attr_icon: str = "mdi:car"

    def __init__(
        self,
        coordinator: BouncieVehiclesDataUpdateCoordinator,
        vin: str,
    ):
        """Initialize the tracker."""
        super().__init__(coordinator, vin)

        vehicle = coordinator.data[vin]
        self._attr_unique_id = vin
        self._attr_name = vehicle[ATTR_NICKNAME]

        self._lat: float = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LAT]
        self._lon: float = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LON]

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self._lat

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self._lon

    @property
    def source_type(self) -> str:
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    async def async_event_received(self, event: Event) -> None:
        """Update status if event received for this entity."""
        status = event.data
        if status[ATTR_VIN] == self.vin and status[ATTR_EVENT] == EVENT_TRIPDATA:
            self._lat = status[ATTR_DATA][-1][ATTR_GPS][ATTR_LAT]
            self._lon = status[ATTR_DATA][-1][ATTR_GPS][ATTR_LON]
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        vehicle = self.coordinator.data[self.vin]
        self._lat = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LAT]
        self._lon = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LON]
        self.async_write_ha_state()

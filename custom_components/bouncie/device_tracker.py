"""Device Tracker for Bouncie devices."""
from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .common import BouncieVehiclesDataUpdateCoordinator
from .const import (
    ATTR_DATA,
    ATTR_EVENT,
    ATTR_GPS,
    ATTR_LAT,
    ATTR_LOCATION,
    ATTR_LON,
    ATTR_MAKE,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_NICKNAME,
    ATTR_STATS,
    ATTR_VIN,
    BOUNCIE_EVENT,
    BOUNCIE_PORTAL,
    DOMAIN,
    EVENT_TRIPDATA,
    ICON,
    UPDATE_INTERVAL,
    VEHICLES_COORDINATOR,
)

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


class BouncieDeviceTracker(CoordinatorEntity, TrackerEntity):
    """Bouncie device tracker."""

    _attr_icon: str = ICON

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[BouncieVehiclesDataUpdateCoordinator],
        vin: str,
    ):
        """Initialize the tracker."""
        super().__init__(coordinator)
        self.vin: str = vin

        vehicle = coordinator.data[vin]
        self._attr_unique_id = vin
        self._attr_name = vehicle[ATTR_NICKNAME]
        self._lat: float = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LAT]
        self._lon: float = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LON]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        vehicle = self.coordinator.data[self.vin]
        return DeviceInfo(
            name=vehicle[ATTR_NICKNAME],
            manufacturer=vehicle[ATTR_MODEL][ATTR_MAKE],
            model=vehicle[ATTR_MODEL][ATTR_NAME],
            identifiers={(DOMAIN, self._attr_unique_id)},
            configuration_url=BOUNCIE_PORTAL,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.vin in self.coordinator.data

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
        if status[ATTR_VIN] == self.vin:
            if status[ATTR_EVENT] == EVENT_TRIPDATA:
                self._lat = status[ATTR_DATA][-1][ATTR_GPS][ATTR_LAT]
                self._lon = status[ATTR_DATA][-1][ATTR_GPS][ATTR_LON]
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        await super().async_added_to_hass()
        # Register callback for webhook event
        self.async_on_remove(
            self.hass.bus.async_listen(BOUNCIE_EVENT, self.async_event_received)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        vehicle = self.coordinator.data[self.vin]
        self._lat = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LAT]
        self._lon = vehicle[ATTR_STATS][ATTR_LOCATION][ATTR_LON]
        self.async_write_ha_state()

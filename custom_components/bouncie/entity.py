"""BlueprintEntity class"""
from abc import ABC, abstractmethod

from homeassistant.core import Event, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common import BouncieVehiclesDataUpdateCoordinator
from .const import (
    ATTR_MAKE,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_NICKNAME,
    BOUNCIE_EVENT,
    BOUNCIE_PORTAL,
    DOMAIN,
)


class BouncieEntity(CoordinatorEntity, ABC):
    """Bouncie Entity Base."""

    def __init__(self, coordinator: BouncieVehiclesDataUpdateCoordinator, vin: str):
        super().__init__(coordinator)
        self.vin: str = vin

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

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        await super().async_added_to_hass()
        # Register callback for webhook event
        self.async_on_remove(
            self.hass.bus.async_listen(BOUNCIE_EVENT, self.async_event_received)
        )

    @abstractmethod
    async def async_event_received(self, event: Event) -> None:
        """Handle updates from webhooks."""

    @callback
    @abstractmethod
    def _handle_coordinator_update(self) -> None:
        """Handle updates from the coordinator."""

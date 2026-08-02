"""Sensor platform for PIRA.AT."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PiraAtConfigEntry
from .const import DOMAIN, NAME
from .coordinator import PiraAtDataUpdateCoordinator


async def async_setup_entry(
    hass, entry: PiraAtConfigEntry, async_add_entities
) -> None:
    """Set up the PIRA.AT catalog sensor."""
    async_add_entities([PiraAtStationsSensor(entry.runtime_data.coordinator)])


class PiraAtStationsSensor(CoordinatorEntity[PiraAtDataUpdateCoordinator], SensorEntity):
    """Expose the number of currently playable PIRA.AT stations."""

    _attr_has_entity_name = True
    _attr_name = "Stations"
    _attr_icon = "mdi:radio"

    def __init__(self, coordinator: PiraAtDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = "pira_at_stations"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "catalog")},
            "name": NAME,
            "manufacturer": "PIRA.AT",
            "model": "Public station catalog",
            "configuration_url": "https://pira.at/",
        }

    @property
    def native_value(self) -> int:
        """Return the number of playable stations."""
        return len(self.coordinator.data.stations)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful, compact catalog metadata."""
        updated = self.coordinator.data.updated_at
        return {
            "updated_at": datetime.fromtimestamp(updated, UTC).isoformat() if updated else None,
            "sources": dict(self.coordinator.data.source_counts),
            "regions": len(self.coordinator.data.regions()),
        }


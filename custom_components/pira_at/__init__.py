"""Home Assistant integration for PIRA.AT."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PiraAtApiClient
from .const import DOMAIN, PLATFORMS
from .coordinator import PiraAtDataUpdateCoordinator


@dataclass(slots=True)
class PiraAtRuntimeData:
    """Runtime objects shared by PIRA.AT platforms and actions."""

    coordinator: PiraAtDataUpdateCoordinator


type PiraAtConfigEntry = ConfigEntry[PiraAtRuntimeData]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration-wide actions."""
    from .services import async_register_services

    async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PiraAtConfigEntry) -> bool:
    """Set up PIRA.AT from a config entry."""
    client = PiraAtApiClient(async_get_clientsession(hass))
    coordinator = PiraAtDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = PiraAtRuntimeData(coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PiraAtConfigEntry) -> bool:
    """Unload a PIRA.AT config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


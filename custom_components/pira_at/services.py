"""Automation actions for PIRA.AT."""

from __future__ import annotations

import random

import voluptuous as vol

from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN, MediaType
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.config_validation as cv

from . import PiraAtConfigEntry
from .api import PiraAtCatalog, PiraAtStation
from .const import (
    ATTR_ENTITY_ID,
    ATTR_REGION,
    ATTR_STATION_ID,
    DOMAIN,
    SERVICE_PLAY_RANDOM,
    SERVICE_PLAY_STATION,
)

_PLAY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_STATION_ID): cv.string,
        vol.Optional(ATTR_REGION): cv.string,
    }
)


def _catalog(hass: HomeAssistant) -> PiraAtCatalog:
    """Return the loaded catalog for a service action."""
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]
    if not entries:
        raise ServiceValidationError("PIRA.AT is not configured")

    entry: PiraAtConfigEntry = entries[0]
    catalog = entry.runtime_data.coordinator.data
    if catalog is None:
        raise ServiceValidationError("PIRA.AT catalog is not available")
    return catalog


async def _async_play_station(
    hass: HomeAssistant, entity_id: str, station: PiraAtStation, context
) -> None:
    """Send a resolved station URL to an existing Home Assistant media player."""
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        "play_media",
        {
            ATTR_ENTITY_ID: entity_id,
            "media_content_id": station.stream_url,
            "media_content_type": MediaType.MUSIC,
        },
        blocking=True,
        context=context,
    )


async def async_handle_play_station(hass: HomeAssistant, call: ServiceCall) -> None:
    """Play one predictable station by its ``source:id`` key."""
    catalog = _catalog(hass)
    station_id = call.data[ATTR_STATION_ID]
    station = catalog.station(station_id)
    if station is None:
        raise ServiceValidationError(f"Unknown PIRA.AT station: {station_id}")
    await _async_play_station(hass, call.data[ATTR_ENTITY_ID], station, call.context)


async def async_handle_play_random(hass: HomeAssistant, call: ServiceCall) -> None:
    """Play a random current station, optionally constrained to one region."""
    catalog = _catalog(hass)
    region = call.data.get(ATTR_REGION, "")
    candidates = catalog.stations_in_region(region)
    if not candidates:
        raise ServiceValidationError(f"No playable PIRA.AT stations found for region: {region}")
    popular_candidates = [station for station in candidates if station.listeners > 0]
    station = random.choice(popular_candidates or candidates)
    await _async_play_station(hass, call.data[ATTR_ENTITY_ID], station, call.context)


def async_register_services(hass: HomeAssistant) -> None:
    """Register integration actions once for Home Assistant."""
    if hass.services.has_service(DOMAIN, SERVICE_PLAY_STATION):
        return

    async def _handle_play_station(call: ServiceCall) -> None:
        await async_handle_play_station(hass, call)

    async def _handle_play_random(call: ServiceCall) -> None:
        await async_handle_play_random(hass, call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_STATION,
        _handle_play_station,
        schema=_PLAY_SCHEMA.extend({vol.Required(ATTR_STATION_ID): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_RANDOM,
        _handle_play_random,
        schema=_PLAY_SCHEMA,
    )

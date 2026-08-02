"""Coordinator for the PIRA.AT station catalog."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PiraAtApiClient, PiraAtApiError, PiraAtCatalog
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PiraAtDataUpdateCoordinator(DataUpdateCoordinator[PiraAtCatalog]):
    """Fetch the public station catalog once for all PIRA.AT consumers."""

    def __init__(self, hass: HomeAssistant, client: PiraAtApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> PiraAtCatalog:
        """Fetch fresh station information."""
        try:
            return await self.client.async_fetch_catalog()
        except PiraAtApiError as err:
            raise UpdateFailed(f"Error communicating with PIRA.AT: {err}") from err


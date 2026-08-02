"""Config flow for PIRA.AT."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PiraAtApiClient, PiraAtApiError
from .const import DOMAIN, NAME


class PiraAtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the no-auth configuration flow for PIRA.AT."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Validate that the public API can be reached before creating the entry."""
        if user_input is None:
            return self.async_show_form(step_id="user")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        try:
            await PiraAtApiClient(async_get_clientsession(self.hass)).async_fetch_catalog()
        except PiraAtApiError:
            return self.async_show_form(step_id="user", errors={"base": "cannot_connect"})

        return self.async_create_entry(title=NAME, data={})


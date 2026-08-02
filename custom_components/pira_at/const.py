"""Constants for the PIRA.AT integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "pira_at"
NAME: Final = "PIRA.AT"
API_URL: Final = "https://pira.at/api/"
SCAN_INTERVAL: Final = timedelta(seconds=120)

PLATFORMS: Final = [Platform.SENSOR]

SERVICE_PLAY_STATION: Final = "play_station"
SERVICE_PLAY_RANDOM: Final = "play_random"

ATTR_ENTITY_ID: Final = "entity_id"
ATTR_STATION_ID: Final = "station_id"
ATTR_REGION: Final = "region"

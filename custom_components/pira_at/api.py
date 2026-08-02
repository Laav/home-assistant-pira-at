"""Client and data model for the public PIRA.AT station API."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import re
from typing import Any
from urllib.parse import urlparse

import aiohttp

from .const import API_URL


class PiraAtApiError(Exception):
    """Raised when the PIRA.AT API cannot be read safely."""


def _text(value: Any) -> str:
    """Return a compact, display-safe text value."""
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _positive_int(value: Any) -> int:
    """Coerce an untrusted listener count to a non-negative integer."""
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _is_stream_url(value: str) -> bool:
    """Only allow absolute HTTP(S) stream URLs from the public API."""
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@dataclass(frozen=True, slots=True)
class PiraAtStation:
    """A normalized PIRA.AT station."""

    key: str
    source: str
    source_id: str
    name: str
    stream_url: str
    frequency: str
    region: str
    phone: str
    listeners: int
    now_playing: str
    timestamp: int

    @classmethod
    def from_api(cls, source: str, source_id: str, item: Mapping[str, Any]) -> "PiraAtStation | None":
        """Create a station from one untrusted API record."""
        stream_url = _text(item.get("mp3link"))
        if not _is_stream_url(stream_url):
            return None

        clean_source = _text(item.get("bron")) or source
        clean_id = _text(item.get("id")) or source_id
        if not clean_source or not clean_id:
            return None

        return cls(
            key=f"{clean_source}:{clean_id}",
            source=clean_source,
            source_id=clean_id,
            name=_text(item.get("station")) or "Onbekend station",
            stream_url=stream_url,
            frequency=_text(item.get("freq")),
            region=_text(item.get("locatie")) or "Onbekend",
            phone=_text(item.get("telefoon")),
            listeners=_positive_int(item.get("luisteraars")),
            now_playing=_text(item.get("nowPlaying")),
            timestamp=_positive_int(item.get("timestamp")),
        )


@dataclass(frozen=True, slots=True)
class PiraAtCatalog:
    """The current station catalog, prepared for Home Assistant consumers."""

    stations: tuple[PiraAtStation, ...]
    source_counts: tuple[tuple[str, int], ...]
    updated_at: int

    def station(self, key: str) -> PiraAtStation | None:
        """Return a station by its stable ``source:id`` key."""
        return next((station for station in self.stations if station.key == key), None)

    def regions(self) -> tuple[str, ...]:
        """Return regions ordered for easy browsing."""
        return tuple(sorted({station.region for station in self.stations}, key=str.casefold))

    def stations_in_region(self, region: str | None = None) -> tuple[PiraAtStation, ...]:
        """Return stations ordered by listeners and then name."""
        stations = self.stations
        if region:
            region_key = region.casefold()
            stations = tuple(station for station in stations if station.region.casefold() == region_key)

        return tuple(sorted(stations, key=lambda station: (-station.listeners, station.name.casefold(), station.key)))


def parse_catalog(payload: Any) -> PiraAtCatalog:
    """Normalize the source-grouped public API response into a catalog."""
    if not isinstance(payload, Mapping):
        raise PiraAtApiError("API response is not a JSON object")

    stations: list[PiraAtStation] = []
    source_counts: list[tuple[str, int]] = []
    seen_keys: set[str] = set()

    for source, source_payload in payload.items():
        if not isinstance(source_payload, Mapping):
            continue

        valid_count = 0
        for source_id, raw_station in source_payload.items():
            if not isinstance(raw_station, Mapping):
                continue
            station = PiraAtStation.from_api(_text(source), _text(source_id), raw_station)
            if station is None or station.key in seen_keys:
                continue
            seen_keys.add(station.key)
            stations.append(station)
            valid_count += 1

        source_counts.append((_text(source), valid_count))

    if not stations:
        raise PiraAtApiError("API response contained no playable stations")

    stations.sort(key=lambda station: (station.region.casefold(), station.name.casefold(), station.key))
    return PiraAtCatalog(
        stations=tuple(stations),
        source_counts=tuple(sorted(source_counts, key=lambda item: item[0].casefold())),
        updated_at=max(station.timestamp for station in stations),
    )


class PiraAtApiClient:
    """Fetch the PIRA.AT public station catalog."""

    def __init__(self, session: aiohttp.ClientSession, url: str = API_URL) -> None:
        self._session = session
        self._url = url

    async def async_fetch_catalog(self) -> PiraAtCatalog:
        """Fetch and validate the current catalog."""
        try:
            async with asyncio.timeout(15):
                async with self._session.get(self._url, headers={"Accept": "application/json"}) as response:
                    response.raise_for_status()
                    payload = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise PiraAtApiError("Could not fetch the PIRA.AT API") from err

        return parse_catalog(payload)

"""Media Browser support for PIRA.AT stations."""

from __future__ import annotations

from urllib.parse import quote, unquote

from homeassistant.components.media_player import BrowseError, MediaClass, MediaType
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from . import PiraAtConfigEntry
from .api import PiraAtCatalog, PiraAtStation
from .const import DOMAIN, NAME


async def async_get_media_source(hass: HomeAssistant) -> "PiraAtMediaSource":
    """Return the PIRA.AT media source."""
    return PiraAtMediaSource(hass)


class PiraAtMediaSource(MediaSource):
    """Expose PIRA.AT's public station catalog in the Media Browser."""

    name = NAME

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(DOMAIN)
        self.hass = hass

    def _catalog(self) -> PiraAtCatalog:
        """Return the loaded catalog or a meaningful media-browser error."""
        entries = [
            entry
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            if entry.state is ConfigEntryState.LOADED
        ]
        if not entries:
            raise BrowseError("Set up PIRA.AT first")

        entry: PiraAtConfigEntry = entries[0]
        catalog = entry.runtime_data.coordinator.data
        if catalog is None:
            raise BrowseError("PIRA.AT catalog is not available")
        return catalog

    @staticmethod
    def _station_item(station: PiraAtStation) -> BrowseMediaSource:
        """Turn a station into a playable Media Browser item."""
        details = [detail for detail in (station.frequency, station.region, f"{station.listeners} luisteraars") if detail]
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=f"station/{quote(station.key, safe='')}",
            media_class=MediaClass.MUSIC,
            media_content_type=MediaType.MUSIC,
            title=f"{station.name} — {' · '.join(details)}",
            can_play=True,
            can_expand=False,
        )

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve a Media Browser item to its current stream URL."""
        category, _, encoded_key = (item.identifier or "").partition("/")
        station = self._catalog().station(unquote(encoded_key)) if category == "station" else None
        if station is None:
            raise Unresolvable("Unknown PIRA.AT station")
        return PlayMedia(station.stream_url, "audio/mpeg")

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        """Browse stations per region, plus an all-stations directory."""
        catalog = self._catalog()
        identifier = item.identifier or ""
        category, _, value = identifier.partition("/")

        if not identifier:
            children = [
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier="all",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type=MediaType.MUSIC,
                    title="Alle stations",
                    can_play=False,
                    can_expand=True,
                )
            ]
            children.extend(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"region/{quote(region, safe='')}",
                    media_class=MediaClass.DIRECTORY,
                    media_content_type=MediaType.MUSIC,
                    title=region,
                    can_play=False,
                    can_expand=True,
                )
                for region in catalog.regions()
            )
            return BrowseMediaSource(
                domain=DOMAIN,
                identifier=None,
                media_class=MediaClass.APP,
                media_content_type="",
                title=NAME,
                can_play=False,
                can_expand=True,
                children=children,
                children_media_class=MediaClass.DIRECTORY,
            )

        if category == "all" and not value:
            title = "Alle stations"
            stations = catalog.stations_in_region()
        elif category == "region" and value:
            title = unquote(value)
            stations = catalog.stations_in_region(title)
            if not stations:
                raise BrowseError("Unknown PIRA.AT region")
        else:
            raise BrowseError("Unknown PIRA.AT media item")

        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=identifier,
            media_class=MediaClass.DIRECTORY,
            media_content_type=MediaType.MUSIC,
            title=title,
            can_play=False,
            can_expand=True,
            children=[self._station_item(station) for station in stations],
            children_media_class=MediaClass.MUSIC,
        )

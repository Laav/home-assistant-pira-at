"""Tests for public API parsing that do not need Home Assistant installed."""

from custom_components.pira_at.api import parse_catalog


def test_parse_catalog_keeps_only_playable_stations() -> None:
    """Invalid streams and duplicate source IDs never reach Home Assistant."""
    catalog = parse_catalog(
        {
            "gzc": {
                "9016": {
                    "id": "9016",
                    "station": "Radio Noaberkracht",
                    "freq": "95.10MHz",
                    "locatie": "Twente",
                    "luisteraars": "531",
                    "mp3link": "https://piratenopname.nl/9016.stream",
                    "bron": "gzc",
                    "timestamp": 1780053001,
                },
                "invalid": {"station": "Broken", "mp3link": "file:///not-allowed"},
            },
            "epc": {
                "37": {
                    "id": "37",
                    "station": "Drommelse Jongens",
                    "locatie": "Opname",
                    "luisteraars": 3,
                    "mp3link": "https://etherpiraten.com/stream/8084",
                    "bron": "epc",
                    "timestamp": 1780053002,
                }
            },
        }
    )

    assert len(catalog.stations) == 2
    assert catalog.station("gzc:9016").listeners == 531
    assert catalog.updated_at == 1780053002
    assert catalog.stations_in_region("twente")[0].name == "Radio Noaberkracht"


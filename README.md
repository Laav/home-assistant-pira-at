# PIRA.AT voor Home Assistant

Brengt de actuele stations van [pira.at](https://pira.at/) naar Home Assistant. Deze integratie leest uitsluitend de publieke, bestaande API op `https://pira.at/api/`; er zijn geen inloggegevens nodig.

## Wat deze eerste versie doet

- Toont één diagnostische sensor met het aantal speelbare stations, regio's en bronstatus.
- Voegt **PIRA.AT** toe aan de Home Assistant Media Browser, met `Alle stations` en een indeling per regio.
- Een gekozen station resolveert altijd opnieuw naar de actuele stream-URL uit de API.
- Werkt met bestaande Home Assistant-mediaspelers. Chromecast is de primaire route; AirPlay werkt wanneer het AirPlay-apparaat in Home Assistant als een mediaspeler beschikbaar is, bijvoorbeeld via Apple TV of een bridge.
- Leest de catalogus elke 120 seconden, gelijk aan de refresh op de pira.at-site.
- Biedt automatiseringsacties voor een specifiek station of een willekeurig station (optioneel per regio).

Dit is bewust een **custom integration**, geen Home Assistant add-on. De integratie levert de catalogus en streams; Home Assistant en de al geïnstalleerde media-playerintegraties zorgen voor het afspelen op Chromecast, Apple TV, AirPlay-bridges, Sonos enzovoort.

## Installatie via HACS

1. Open in HACS `Integrations` en kies in het menu `Custom repositories`.
2. Voeg [`https://github.com/Laav/home-assistant-pira-at`](https://github.com/Laav/home-assistant-pira-at) toe met categorie **Integration**.
3. Installeer **PIRA.AT** en herstart Home Assistant.
4. Ga naar `Instellingen` → `Apparaten & diensten` → `Integratie toevoegen` → **PIRA.AT**.
5. Open daarna de Media Browser, kies **PIRA.AT**, selecteer een station en kies de gewenste mediaspeler.

## Automatiseringen

In de Media Browser is geen station-ID nodig. Voor automations kan een stabiele sleutel `bron:id` worden gebruikt, zoals `gzc:9016`.

```yaml
action:
  - action: pira_at.play_random
    data:
      entity_id: media_player.woonkamer
      region: Twente
```

```yaml
action:
  - action: pira_at.play_station
    data:
      entity_id: media_player.woonkamer
      station_id: gzc:9016
```

Station-ID's zijn alleen stabiel binnen de actuele catalogus. Voor een dashboard of dagelijks gebruik is de Media Browser daarom de prettigste ingang.

## Ontwikkeling en publicatie

De repository volgt de standaard HACS-layout: precies één directory onder `custom_components/`. De GitHub Action valideert die structuur bij een push of pull request.

De actuele installeerbare release is [v0.1.1](https://github.com/Laav/home-assistant-pira-at/releases/tag/v0.1.1). HACS toont deze release na installatie als beschikbare versie.

De integratie heeft geen directe AirPlay-implementatie. Dat is bewust: AirPlay is afhankelijk van de Home Assistant-integratie die jouw ontvangende hardware aanbiedt. Waar die hardware als `media_player` beschikbaar is en directe audio-URL's accepteert, kan PIRA.AT er via Home Assistant naartoe afspelen. De actie `play_random` geeft net als Ether Roulette voorrang aan stations met minstens één luisteraar.

## Licentie

Deze integratie wordt gepubliceerd onder de MIT-licentie. Zie [LICENSE](LICENSE).

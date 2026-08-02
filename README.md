# PIRA.AT voor Home Assistant

Luister naar actuele PIRA.AT-stations vanuit Home Assistant. Kies een station in de Media Browser en speel het af op een beschikbare mediaspeler, zoals Chromecast, Sonos of Apple TV.

Er is geen account, sleutel of aparte server nodig.

## Snel aan de slag

1. Open **HACS** in Home Assistant en ga naar **Integrations**.
2. Kies in het menu **Custom repositories**.
3. Voeg [`https://github.com/Laav/home-assistant-pira-at`](https://github.com/Laav/home-assistant-pira-at) toe met categorie **Integration**.
4. Installeer **PIRA.AT** en herstart Home Assistant.
5. Ga naar **Instellingen** → **Apparaten & diensten** → **Integratie toevoegen** en kies **PIRA.AT**.
6. Open de **Media Browser**, kies **PIRA.AT**, selecteer een station en vervolgens de gewenste mediaspeler.

Gebruik altijd de [laatste release](https://github.com/Laav/home-assistant-pira-at/releases); HACS toont deze als beschikbare update.

## Wat kun je ermee?

- Stations bekijken als één overzicht of gegroepeerd per regio.
- Een station afspelen op bestaande Home Assistant-mediaspelers.
- Het aantal beschikbare stations en regio's terugzien in een diagnostische sensor.
- Een specifiek of willekeurig station in een automatisering starten.

Chromecast is de meest directe route. Apple TV, Sonos en andere apparatuur werken wanneer zij in Home Assistant als `media_player` beschikbaar zijn. AirPlay zelf wordt niet door deze integratie geleverd; de koppeling van jouw AirPlay-apparaat met Home Assistant verzorgt dat.

## Automatiseringen

Voor dagelijks luisteren is de Media Browser het prettigst. Voor dashboards en automatiseringen zijn er twee acties beschikbaar.

Een willekeurig station uit Twente starten:

```yaml
action:
  - action: pira_at.play_random
    data:
      entity_id: media_player.woonkamer
      region: Twente
```

Een bekend station starten:

```yaml
action:
  - action: pira_at.play_station
    data:
      entity_id: media_player.woonkamer
      station_id: gzc:9016
```

Een station-ID heeft de vorm `bron:id`. Gebruik voor een vast dashboard bij voorkeur de Media Browser of controleer de actuele station-ID: stations kunnen tijdelijk verdwijnen of van bron wisselen.

## Handig om te weten

- De stationslijst wordt maximaal eens per twee minuten vernieuwd.
- De integratie is een **custom integration** voor Home Assistant, geen Home Assistant add-on.
- De integratie levert stations en streamlinks. Het afspelen en casten gebeurt door Home Assistant en de mediaspelerintegraties die je al gebruikt.
- Voor Music Assistant is er een aparte, native provider. Zie de [PIRA.AT Music Assistant-provider](https://github.com/Laav/music-assistant-pira-at-provider).

## Voor technische gebruikers

De standaard HACS-structuur wordt gebruikt: één integratiedirectory onder `custom_components/`. De GitHub Action valideert de repository bij elke wijziging. De integratie heeft geen configuratievelden en geen afhankelijkheden buiten Home Assistant zelf.

## Licentie

Deze integratie wordt gepubliceerd onder de MIT-licentie. Zie [LICENSE](LICENSE).

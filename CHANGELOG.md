# Release notes

This is the development copy of the [official Cozify HAN integration](https://github.com/cozify/han-home-assistant). It is based on the official code at commit `0d27a23` (version 1.0.14).

## 1.0.14-dev.2 (2026-11-06)

### Changed

- Version bumped to `1.0.14-dev.2` in `manifest.json` (it previously said `1.0.14-dev` while the release notes said `1.0.14-dev.1`). No functional changes to the sensors compared to `1.0.14-dev.1`.

### Documentation

- README rewritten for the dev copy: HACS custom repository and manual installation instructions, setup as "Cozify HAN (dev)", entity ids with the `dev` prefix, and updated badges (no more links to the official project's release and HACS Default badges).
- README notes that the blueprints are copies from the official repository and only list entities of the official integration (`cozify_han`).
- Release notes added as `CHANGELOG.md`.
- README shows the current dev version.

## 1.0.14-dev.1 (2026-11-06)

### New

- **Current electricity price sensor**: `sensor.cozify_han_dev_current_electricity_price` shows the price currently active on the HAN, read from the HAN `/prices` endpoint. With spot pricing enabled on the HAN this is the current spot price, otherwise the fixed price.
  - The unit follows the currency reported by the HAN (c/kWh for EUR, öre/kWh for SEK, and so on).
  - Attribute `prices`: all price slots known to the HAN as `[[start_timestamp_ms, price], ...]`. The list is excluded from the recorder.
  - Attribute `currency`: the currency reported by the HAN.
  - Attribute `spot_pricing`: whether spot pricing is enabled on the HAN. Only present if the HAN reports it in `/configuration` (key `s`).
  - The price is read from the HAN at most once per minute.
  - The sensor is `unknown` when the HAN has no current price, or when the firmware does not provide `/prices`. All other sensors keep working in that case.

### Changed

- **Separate integration**: the integration now uses its own domain and directory, `cozify_han_dev`, so it can be installed next to the official `cozify_han` (HACS does not allow installing into a directory owned by another repository).
  - Integration name: "Cozify HAN (dev)". The device name gets the suffix "(dev)".
  - Entity names are prefixed `Cozify HAN Dev` and entity ids are `sensor.cozify_han_dev_*`, so they do not collide with the official integration's entities.
  - Add it from Settings -> Devices & services -> Add integration -> "Cozify HAN (dev)".

### Notes

- The official and the dev integration both poll the HAN. Remove one of them when you are done testing.
- The blueprints are unchanged copies from the official repository and refer to the official integration.
- Tests (pytest-homeassistant-custom-component) cover the price sensor: current price, null price, currency units, missing `/prices` endpoint and request throttling.

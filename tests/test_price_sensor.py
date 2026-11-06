"""Tests for the Cozify HAN current electricity price sensor."""
from datetime import timedelta
from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.cozify_han.const import DOMAIN
from custom_components.cozify_han.sensor import CozifyPriceSensor

from .conftest import HOST, PRICES

ENTITY_ID = "sensor.cozify_han_current_electricity_price"


async def _setup(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: HOST}, entry_id="test_entry")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _price_calls(aioclient_mock):
    return [c for c in aioclient_mock.mock_calls if str(c[1]).endswith("/prices")]


async def test_current_price(hass, mock_han):
    mock_han()
    await _setup(hass)

    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert float(state.state) == 8.123456
    assert state.attributes["unit_of_measurement"] == "c/kWh"
    assert state.attributes["currency"] == "EUR"
    assert state.attributes["prices"] == PRICES["prices"]
    assert state.attributes["spot_pricing"] is True

    entry = er.async_get(hass).async_get(ENTITY_ID)
    assert entry.unique_id == "test_entry_price_current"


def test_price_attribute_not_recorded():
    assert "prices" in CozifyPriceSensor._unrecorded_attributes


async def test_null_price_is_unknown(hass, mock_han):
    mock_han({**PRICES, "price": None})
    await _setup(hass)

    assert hass.states.get(ENTITY_ID).state == "unknown"


async def test_swedish_currency_unit(hass, mock_han):
    mock_han({**PRICES, "currency": "SEK"})
    await _setup(hass)

    assert hass.states.get(ENTITY_ID).attributes["unit_of_measurement"] == "öre/kWh"


async def test_missing_prices_endpoint_keeps_other_sensors_working(hass, mock_han):
    """Older firmware without /prices must not break the integration."""
    mock_han({}, prices_status=404)
    await _setup(hass)

    assert hass.states.get(ENTITY_ID).state == "unknown"
    assert hass.states.get("sensor.cozify_han_total_power_imported").state == "1000.5"


async def test_prices_fetch_is_throttled(hass, mock_han):
    aioclient_mock = mock_han()
    await _setup(hass)
    assert len(_price_calls(aioclient_mock)) == 1

    # Several meter refreshes within the throttle window do not re-fetch prices
    for i in range(3):
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=6 * (i + 1)))
        await hass.async_block_till_done()
    assert len(_price_calls(aioclient_mock)) == 1

    # After the window a new price is picked up
    mock_han({**PRICES, "price": 12.5})
    with patch("custom_components.cozify_han.sensor.monotonic", return_value=10**9):
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=120))
        await hass.async_block_till_done()
    assert float(hass.states.get(ENTITY_ID).state) == 12.5

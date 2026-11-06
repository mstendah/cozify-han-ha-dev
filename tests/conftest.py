"""Fixtures for the Cozify HAN tests."""
import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

HOST = "192.0.2.10"

HAN_INFO = {"name": "Cozify HAN", "version": "1.0.1.17", "serial": "SN-TEST", "mac": "aa:bb:cc:dd:ee:ff"}
METER = {"ic": 1000.5, "ec": 0.0, "p": [600, 200, 200, 200], "pi": [600, 200, 200, 200],
         "pe": [0, 0, 0, 0], "u": [230, 231, 232], "i": [1.0, 1.1, 1.2], "r": [0, 0, 0, 0], "ts": 1735682400}
CONFIG = {"p": 10.0, "t": "Europe/Helsinki", "v": "1.0.1.17", "s": True, "m": {"f": 25}}
PRICES = {
    "type": "HAN_PRICES_MESSAGE",
    "price": 8.123456,
    "currency": "EUR",
    "prices": [[1735682400000, 8.123456], [1735683300000, 9.234567]],
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow loading custom_components in every test."""
    yield


@pytest.fixture
def mock_han(aioclient_mock):
    """Return a function that mocks all HAN endpoints.

    Call it with a /prices JSON body, or with a status code (e.g. 404) to
    simulate firmware without the /prices endpoint.
    """

    def _mock(prices=PRICES, prices_status=200):
        aioclient_mock.clear_requests()
        aioclient_mock.get(f"http://{HOST}/han", json=HAN_INFO)
        aioclient_mock.get(f"http://{HOST}/meter", json=METER)
        aioclient_mock.get(f"http://{HOST}/configuration", json=CONFIG)
        aioclient_mock.get(f"http://{HOST}/meter/id", json={})
        aioclient_mock.get(f"http://{HOST}/prices", json=prices, status=prices_status)
        return aioclient_mock

    return _mock

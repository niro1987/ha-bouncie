"""Constants for integration_blueprint tests."""
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bouncie.const import (
    CONF_API_KEY,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DOMAIN,
)

MOCK_TOKEN = ""
MOCK_CONFIG = {
    CONF_CLIENT_ID: "spam-eggs",
    CONF_CLIENT_SECRET: "bacon",
    CONF_API_KEY: "sausages",
}
MOCK_ENTRY = MockConfigEntry(
    domain=DOMAIN,
    data={
        "auth_implementation": "bouncie-home-assistant",
        "token": {
            "access_token": "spam.eggs.bacon",
            "expires_in": 3600,
            "token_type": "Bearer",
            "code": "sausages",
            "expires_at": 1671439550.287522,
        },
        **MOCK_CONFIG,
    },
    entry_id="test",
    unique_id="bouncie_test",
)
MOCK_VEHICLE = {
    "model": {"make": "SPAM", "name": "Eggs"},
    "nickName": "SPAM Eggs",
    "vin": "ABCDEFG123456NOP7",
    "imei": "000000000000000",
    "stats": {
        "localTimeZone": "-0500",
        "lastUpdated": "2022-01-01T12:00:00.000Z",
        "odometer": 123456.789,
        "location": {
            "lat": 1.2345,
            "lon": 6.7890,
        },
        "fuelLevel": 98.76,
        "speed": 12.34,
    },
}

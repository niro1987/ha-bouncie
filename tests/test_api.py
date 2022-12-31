"""Test bouncie API."""
from http import HTTPStatus
from unittest.mock import patch

from homeassistant.helpers import config_entry_oauth2_flow
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMockResponse,
)

from custom_components.bouncie.api import BouncieAPI
from custom_components.bouncie.common import BouncieOAuth2Implementation
from custom_components.bouncie.const import (
    CONF_API_KEY,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DOMAIN,
    OAUTH2_AUTHORIZE,
    OAUTH2_TOKEN,
    VEHICLES_URL,
)

from .const import MOCK_ENTRY, MOCK_VEHICLE


async def test_api(hass):
    """Test API."""
    MOCK_ENTRY.add_to_hass(hass)
    implementation = BouncieOAuth2Implementation(
        hass,
        DOMAIN,
        MOCK_ENTRY.data[CONF_CLIENT_ID],
        MOCK_ENTRY.data[CONF_CLIENT_SECRET],
        MOCK_ENTRY.data[CONF_API_KEY],
        OAUTH2_AUTHORIZE,
        OAUTH2_TOKEN,
    )
    api = BouncieAPI(
        config_entry_oauth2_flow.OAuth2Session(hass, MOCK_ENTRY, implementation)
    )

    with patch(
        # "custom_components.bouncie.BouncieSession.async_request",
        "homeassistant.helpers.config_entry_oauth2_flow.OAuth2Session.async_request",
        return_value=AiohttpClientMockResponse(
            "get",
            VEHICLES_URL,
            status=HTTPStatus.OK,
            json=[MOCK_VEHICLE],
        ),
    ):
        await api.async_get_vehicles()

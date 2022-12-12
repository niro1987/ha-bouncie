"""API for Bouncie API bound to Home Assistant OAuth."""
import logging
from typing import Any, Dict, List

from aiohttp import client
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import USER_URL, VEHICLES_URL

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def async_oauth2_request(
    hass: HomeAssistant, token: dict, method: str, url: str, **kwargs: Any
) -> client.ClientResponse:
    """Make an OAuth2 authenticated request."""
    session = async_get_clientsession(hass)

    return await session.request(
        method,
        url,
        **kwargs,
        headers={
            **(kwargs.get("headers") or {}),
            "authorization": f"{token['access_token']}",
        },
    )


class BouncieAPI:
    """Provide Bouncie authentication tied to an OAuth2 based config entry."""

    def __init__(self, oauth_session: OAuth2Session) -> None:
        """Bouncie API Client."""
        self._oauth_session: OAuth2Session = oauth_session

    async def async_get_access_token(self) -> dict:
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()

        return self._oauth_session.token

    async def async_get_user(self) -> Dict[str, Any]:
        """Get associated user information."""
        resp = await self._oauth_session.async_request(
            "get", USER_URL, raise_for_status=True
        )
        return await resp.json()

    async def async_get_vehicles(self) -> List[Dict[str, Any]]:
        """Get associated vehicles."""
        resp = await self._oauth_session.async_request(
            "get",
            VEHICLES_URL,
            raise_for_status=True,
        )
        return await resp.json()

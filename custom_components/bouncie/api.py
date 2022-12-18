"""API for Bouncie API bound to Home Assistant OAuth."""
import logging
from typing import Any, Dict, List

from aiohttp import client
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import USER_URL, VEHICLES_URL

_LOGGER: logging.Logger = logging.getLogger(__name__)


class BouncieSession(OAuth2Session):
    """Bouncie specific session to make requests authenticated with OAuth2."""

    async def async_request(
        self, method: str, url: str, **kwargs: Any
    ) -> client.ClientResponse:
        """Make an authorized request."""
        await self.async_ensure_token_valid()
        session = async_get_clientsession(self.hass)
        token = self.config_entry.data["token"]
        return await session.request(
            method,
            url,
            **{k: v for k, v in kwargs.items() if k != "headers"},
            headers={
                **(kwargs.get("headers") or {}),
                "authorization": f"{token['access_token']}",
            },
        )


class BouncieAPI:
    """Provide Bouncie authentication tied to an OAuth2 based config entry."""

    def __init__(self, oauth_session: BouncieSession) -> None:
        """Bouncie API Client."""
        self._oauth_session: BouncieSession = oauth_session

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

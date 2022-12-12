"""Common classes and functions for Bouncie."""
from http import HTTPStatus
from logging import getLogger
from typing import Any

from aiohttp.web import Request, Response
from homeassistant.components.http.view import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BouncieAPI
from .const import (
    ATTR_VIN,
    BOUNCIE_EVENT,
    CONF_CLIENT_ID,
    DOMAIN,
    HA_URL,
    UPDATE_INTERVAL,
    WEBHOOK_RESPONSE_SCHEMA,
)

_LOGGER = getLogger(__name__)


def valid_external_url(hass: HomeAssistant) -> bool:
    """Return whether a valid external URL for HA is available."""
    try:
        get_url(hass, allow_internal=False, prefer_cloud=True)
        return True
    except NoURLAvailableError:
        _LOGGER.error(
            "You do not have an external URL for your Home Assistant instance "
            "configured which is needed to set up the Bouncie integration. "
            "You need to set the `external_url` property in the "
            "`homeassistant` section of your `configuration.yaml`, or set the "
            "`External URL` property in the Home Assistant `General "
            "Configuration` UI, before trying to setup the Bouncie integration "
            "again. You can learn more about configuring this parameter at "
            "https://www.home-assistant.io/docs/configuration/basic"
        )
        return False


class BouncieOAuth2Implementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    """Oauth2 implementation that only uses the external url."""

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
        api_key: str,
        authorize_url: str,
        token_url: str,
    ) -> None:
        """Initialize local auth implementation."""
        super().__init__(
            hass,
            domain,
            client_id,
            client_secret,
            authorize_url,
            token_url,
        )
        self.api_key: str = api_key

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return self.client_id

    @property
    def domain(self) -> str:
        """Domain providing the implementation."""
        return self.client_id

    @property
    def redirect_uri(self) -> str:
        """Return the redirect uri."""
        url = get_url(self.hass, allow_internal=False, prefer_cloud=True)
        return f"{url}{config_entry_oauth2_flow.AUTH_CALLBACK_PATH}"

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """Resolve the authorization code to tokens."""
        return {
            **await self._token_request(
                {
                    "grant_type": "authorization_code",
                    "code": external_data["code"],
                    "redirect_uri": external_data["state"]["redirect_uri"],
                }
            ),
            "code": external_data["code"],
        }

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh tokens."""
        new_token = await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": token["code"],
                "redirect_uri": self.redirect_uri,
            }
        )
        return {**token, **new_token}


class BouncieWebhookRequestView(HomeAssistantView):
    """Provide a page for the device to call."""

    requires_auth = False
    cors_allowed = True
    url = HA_URL
    name = HA_URL[1:].replace("/", ":")

    async def post(self, request: Request) -> Response:
        """Respond to requests from the device."""
        hass: HomeAssistant = request.app["hass"]
        implementations: dict[
            str, Any
        ] = await config_entry_oauth2_flow.async_get_implementations(hass, DOMAIN)
        client_id: str = request.headers.get("Authorization")

        if client_id and client_id in implementations.keys():
            try:
                data = await request.json()
                status = WEBHOOK_RESPONSE_SCHEMA(data)
                # _LOGGER.info("Received event: %s", status)
                hass.bus.async_fire(
                    f"{BOUNCIE_EVENT}", {**status, CONF_CLIENT_ID: client_id}
                )
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Received authorized event but unable to parse: %s (%s)",
                    await request.text(),
                    err,
                )
            return Response(status=HTTPStatus.OK)

        _LOGGER.warning(
            "Received unauthorized request: %s (Headers: %s)",
            await request.text(),
            request.headers,
        )
        return Response(status=HTTPStatus.OK)


class BouncieVehiclesDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to hold Bouncie user profile data."""

    def __init__(self, hass: HomeAssistant, api: BouncieAPI) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            update_method=self._async_update_data,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Update data via library."""
        _LOGGER.info("Refresh data")
        try:
            data = await self.api.async_get_vehicles()
            return {vehicle[ATTR_VIN]: vehicle for vehicle in data}
        except Exception as err:
            raise UpdateFailed from err

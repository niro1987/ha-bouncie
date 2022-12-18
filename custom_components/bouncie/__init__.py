"""The Bouncie integration."""
from logging import getLogger

from aiohttp.client_exceptions import ClientResponseError
from aiohttp.web_exceptions import HTTPUnauthorized
from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import BouncieAPI, BouncieSession
from .common import (
    BouncieOAuth2Implementation,
    BouncieVehiclesDataUpdateCoordinator,
    BouncieWebhookRequestView,
    valid_external_url,
)
from .config_flow import BouncieOAuth2FlowHandler
from .const import (
    API,
    CONF_API_KEY,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DOMAIN,
    OAUTH2_AUTHORIZE,
    OAUTH2_TOKEN,
    PLATFORMS,
    VEHICLES_COORDINATOR,
)

_LOGGER = getLogger(__name__)


async def async_setup(hass: HomeAssistant, _: ConfigType):
    """Set up the Bouncie component."""
    if not valid_external_url(hass):
        return False

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Bouncie from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN].setdefault(CONF_CLIENT_ID, set())

    implementation = BouncieOAuth2Implementation(
        hass,
        DOMAIN,
        entry.data[CONF_CLIENT_ID],
        entry.data[CONF_CLIENT_SECRET],
        entry.data[CONF_API_KEY],
        OAUTH2_AUTHORIZE,
        OAUTH2_TOKEN,
    )
    BouncieOAuth2FlowHandler.async_register_implementation(hass, implementation)
    api = BouncieAPI(BouncieSession(hass, entry, implementation))
    vehicles_coordinator = BouncieVehiclesDataUpdateCoordinator(hass, api)
    await vehicles_coordinator.async_refresh()
    hass.data[DOMAIN][entry.entry_id][API] = api
    hass.data[DOMAIN][entry.entry_id][VEHICLES_COORDINATOR] = vehicles_coordinator
    hass.data[DOMAIN][CONF_CLIENT_ID].add(entry.data[CONF_CLIENT_ID])

    # Register view
    hass.http.register_view(BouncieWebhookRequestView())

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(config_entry.entry_id)

    return True

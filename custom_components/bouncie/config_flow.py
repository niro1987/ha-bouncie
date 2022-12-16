"""Config flow for Bouncie Automation."""
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.util import slugify
import voluptuous as vol

from .common import BouncieOAuth2Implementation, valid_external_url
from .const import (
    BOUNCIE_SCHEMA,
    CONF_API_KEY,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DOMAIN,
    OAUTH2_AUTHORIZE,
    OAUTH2_TOKEN,
)

_LOGGER = logging.getLogger(__name__)


class BouncieOAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Bouncie Automation OAuth2 authentication."""

    DOMAIN = DOMAIN
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    def __init__(self) -> None:
        """Instantiate config flow."""
        self._stored_data = {}
        super().__init__()

    async def async_step_user(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle a flow start."""
        if not valid_external_url(self.hass):
            return self.async_abort(reason="no_external_url")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=BOUNCIE_SCHEMA)

        if user_input:
            await self.async_set_unique_id(
                f"{DOMAIN}_{slugify(user_input[CONF_CLIENT_ID])}",
                raise_on_progress=True,
            )
            self.hass.data.setdefault(DOMAIN, {})
            self.async_register_implementation(
                self.hass,
                BouncieOAuth2Implementation(
                    self.hass,
                    DOMAIN,
                    user_input[CONF_CLIENT_ID],
                    user_input[CONF_CLIENT_SECRET],
                    user_input[CONF_API_KEY],
                    OAUTH2_AUTHORIZE,
                    OAUTH2_TOKEN,
                ),
            )

        return await self.async_step_pick_implementation()

    async def async_step_reauth(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform reauth when OAuth token is invalid."""
        self._stored_data = {
            CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
            CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
            CONF_API_KEY: user_input[CONF_API_KEY],
        }
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Confirm reauth."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm", data_schema=vol.Schema({})
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(
        self, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create an entry for the flow."""
        # Update existing entry if performing reauth
        if self.source == config_entries.SOURCE_REAUTH:
            data.update(self._stored_data)
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if entry.unique_id == self.unique_id:
                    self.hass.config_entries.async_update_entry(entry, data=data)
                    self.hass.async_create_task(
                        self.hass.config_entries.async_reload(entry.entry_id)
                    )
                    return self.async_abort(reason="reauth_successful")

        data.update(
            {
                CONF_CLIENT_ID: self.flow_impl.client_id,
                CONF_CLIENT_SECRET: self.flow_impl.client_secret,
                CONF_API_KEY: self.flow_impl.api_key,
            }
        )
        if not self.unique_id:
            await self.async_set_unique_id(
                f"{DOMAIN}_{slugify(self.flow_impl.client_id)}", raise_on_progress=True
            )
            self._abort_if_unique_id_configured()
        return self.async_create_entry(title=DOMAIN, data=data)

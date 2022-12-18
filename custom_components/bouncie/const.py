"""Constants for integration_blueprint."""
from datetime import timedelta

# pylint: disable=unused-import
from homeassistant.const import (  # noqa: F401
    ATTR_LOCATION,
    ATTR_MODEL,
    ATTR_NAME,
    CONF_API_KEY,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
)
import voluptuous as vol

# Basics
NAME = "Bouncie"
VERSION = "0.0.1"
ISSUE_URL = "https://github.com/niro1987/ha-bouncie/issues"
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# API
BOUNCIE_PORTAL = "https://www.bouncie.dev/"
OAUTH2_AUTHORIZE = "https://auth.bouncie.com/dialog/authorize"
OAUTH2_TOKEN = "https://auth.bouncie.com/oauth/token"
USER_URL = "https://api.bouncie.dev/v1/user"
VEHICLES_URL = "https://api.bouncie.dev/v1/vehicles"
TRIPS_URL = "https://api.bouncie.dev/v1/trips"
BOUNCIE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): vol.Coerce(str),
        vol.Required(CONF_CLIENT_SECRET): vol.Coerce(str),
        vol.Required(CONF_API_KEY): vol.Coerce(str),
    }
)

# Component
DOMAIN = "bouncie"
BOUNCIE_EVENT = f"{DOMAIN}_webhook"
UPDATE_INTERVAL = timedelta(hours=1)
HA_URL = f"/api/{DOMAIN}"
API = "api"
USER_COORDINATOR = "user_coordinator"
VEHICLES_COORDINATOR = "vehicles_coordinator"
VERIFICATION_TOKENS = "verification_tokens"

# Bouncie Webhooks
ATTR_EVENT = "eventType"
ATTR_IMEI = "imei"
ATTR_VIN = "vin"
ATTR_NICKNAME = "nickName"
ATTR_MAKE = "make"
ATTR_DATA = "data"
ATTR_GPS = "gps"
ATTR_STATS = "stats"
ATTR_LAT = "lat"
ATTR_LON = "lon"

WEBHOOK_RESPONSE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_EVENT): vol.Coerce(str),
        vol.Required(ATTR_IMEI): vol.Coerce(str),
        vol.Required(ATTR_VIN): vol.Coerce(str),
    },
    extra=vol.ALLOW_EXTRA,
)
EVENT_CONNECT = "connect"
EVENT_DISCONNECT = "disconnect"
EVENT_BATTERY = "battery"
EVENT_MIL = "mil"
EVENT_TRIPSTART = "tripStart"
EVENT_TRIPEND = "tripEnd"
EVENT_TRIPMETRICS = "tripMetrics"
EVENT_TRIPDATA = "tripData"

# Platforms
DEVICE_TRACKER = "device_tracker"
SENSOR = "sensor"
PLATFORMS = [DEVICE_TRACKER, SENSOR]

"""Global fixtures for bouncie integration."""
from unittest.mock import patch

import pytest

from .const import MOCK_VEHICLE

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(name="external_url", autouse=True)
def external_url_fixture(hass):
    """Set external URL."""
    hass.config.external_url = "https://example.com"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture(name="bypass_get_vehicles")
def bypass_get_vehicles_fixture():
    """Mock calls to api.async_get_vehicles."""
    with patch(
        "custom_components.bouncie.BouncieAPI.async_get_vehicles",
        return_value=[MOCK_VEHICLE],
    ):
        yield

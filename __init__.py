import logging
import requests
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .olarm_api import OlarmApi
import voluptuous as vol
from .const import DOMAIN
from homeassistant.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """
    DOCSTRING: This function handles the setup of the Olarm integration.
    """

    # Creating an instance of the Olarm API class to call the requests to arm, disarm, sleep, or stay the zones.
    OLARM_API = OlarmApi(
        device_id=config_entry.data[CONF_DEVICE_ID],
        api_key=config_entry.data[CONF_API_KEY],
    )
    HTTP_POST_SERVICE_SCHEMA = vol.Schema({})

    # Forwarding the setup for the binary sensors.
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Registering Services
    # Zone 1 Arming
    hass.services.async_register(
        DOMAIN, "area_1_arm", OLARM_API.arm_zone_1, schema=HTTP_POST_SERVICE_SCHEMA
    )
    # Zone 1 Sleeping
    hass.services.async_register(
        DOMAIN,
        "area_1_sleep",
        OLARM_API.sleep_zone_1,
        schema=HTTP_POST_SERVICE_SCHEMA,
    )
    # Zone 1 Staying
    hass.services.async_register(
        DOMAIN,
        "area_1_stay",
        OLARM_API.stay_zone_1,
        schema=HTTP_POST_SERVICE_SCHEMA,
    )
    # Zone 1 Disarming
    hass.services.async_register(
        DOMAIN,
        "area_1_disarm",
        OLARM_API.disarm_zone_1,
        schema=HTTP_POST_SERVICE_SCHEMA,
    )
    # Zone 2 Arming
    hass.services.async_register(
        DOMAIN, "area_2_arm", OLARM_API.arm_zone_2, schema=HTTP_POST_SERVICE_SCHEMA
    )
    # Zone 2 Sleeping
    hass.services.async_register(
        DOMAIN,
        "area_2_sleep",
        OLARM_API.sleep_zone_2,
        schema=HTTP_POST_SERVICE_SCHEMA,
    )
    # Zone 2 Staying
    hass.services.async_register(
        DOMAIN,
        "area_2_stay",
        OLARM_API.stay_zone_2,
        schema=HTTP_POST_SERVICE_SCHEMA,
    )
    # Zone 2 Disarming
    hass.services.async_register(
        DOMAIN,
        "area_2_disarm",
        OLARM_API.disarm_zone_2,
        schema=HTTP_POST_SERVICE_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    return True

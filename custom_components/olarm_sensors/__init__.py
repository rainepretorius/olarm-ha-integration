import logging
import requests

from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_CONTROL_PANEL_DOMAIN,
)

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
)

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import config_validation as cv

from .coordinator import OlarmCoordinator
from .olarm_api import OlarmApi
import voluptuous as vol
from .const import DOMAIN, ZONE
from homeassistant.helpers import service
from homeassistant.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [
    ALARM_CONTROL_PANEL_DOMAIN,
    BINARY_SENSOR_DOMAIN,
]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """
    This function handles the setup of the Olarm integration. It creates a coordinator instance, registers services for each zone, and forwards the setup for binary sensors.
    """
    coordinator = OlarmCoordinator(hass, entry=config_entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # Creating an instance of the Olarm API class to call the requests to arm, disarm, sleep, or stay the zones.
    OLARM_API = OlarmApi(
        device_id=config_entry.data[CONF_DEVICE_ID],
        api_key=config_entry.data[CONF_API_KEY],
    )
    HTTP_POST_SERVICE_SCHEMA = vol.Schema({})

    # Forwarding the setup for the binary sensors.
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    max_zones = await OLARM_API.get_devices_json()

    max_areas = max_zones["deviceProfile"]["areasLimit"]

    # Registering Services
    # Zone 1 Arming
    hass.services.async_register(
        DOMAIN,
        "area_1_arm",
        OLARM_API.arm_area,
        schema=vol.Schema({vol.Optional("area", default=1): int}),
    )
    # Zone 1 Sleeping
    hass.services.async_register(
        DOMAIN,
        "area_1_sleep",
        OLARM_API.sleep_area,
        schema=vol.Schema({vol.Optional("area", default=1): int}),
    )
    # Zone 1 Staying
    hass.services.async_register(
        DOMAIN,
        "area_1_stay",
        OLARM_API.stay_area,
        schema=vol.Schema({vol.Optional("area", default=1): int}),
    )
    # Zone 1 Disarming
    hass.services.async_register(
        DOMAIN,
        "area_1_disarm",
        OLARM_API.disarm_area,
        schema=vol.Schema({vol.Optional("area", default=1): int}),
    )

    # Checking if the panel has an area 2
    if int(max_areas) >= 2:
        # Zone 2 Arming
        hass.services.async_register(
            DOMAIN,
            "area_2_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=2): int}),
        )
        # Zone 2 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_2_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=2): int}),
        )
        # Zone 2 Staying
        hass.services.async_register(
            DOMAIN,
            "area_2_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=2): int}),
        )
        # Zone 2 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_2_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=2): int}),
        )

    # Checking if the panel has an area 3
    if int(max_areas) >= 3:
        # Zone 3 Arming
        hass.services.async_register(
            DOMAIN,
            "area_3_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=3): int}),
        )
        # Zone 3 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_3_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=3): int}),
        )
        # Zone 3 Staying
        hass.services.async_register(
            DOMAIN,
            "area_3_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=3): int}),
        )
        # Zone 3 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_3_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=3): int}),
        )

    # Checking if the panel has an area 4
    if int(max_areas) >= 4:
        # Zone 4 Arming
        hass.services.async_register(
            DOMAIN,
            "area_4_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=4): int}),
        )
        # Zone 4 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_4_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=4): int}),
        )
        # Zone 4 Staying
        hass.services.async_register(
            DOMAIN,
            "area_4_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=4): int}),
        )
        # Zone 4 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_4_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=4): int}),
        )

    # Checking if the panel has an area 5
    if int(max_areas) >= 5:
        # Zone 5 Arming
        hass.services.async_register(
            DOMAIN,
            "area_5_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=5): int}),
        )
        # Zone 5 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_5_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=5): int}),
        )
        # Zone 5 Staying
        hass.services.async_register(
            DOMAIN,
            "area_5_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=5): int}),
        )
        # Zone 2 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_5_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=5): int}),
        )

    # Checking if the panel has an area 6
    if int(max_areas) >= 6:
        # Zone 6 Arming
        hass.services.async_register(
            DOMAIN,
            "area_6_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=6): int}),
        )
        # Zone 6 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_6_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=6): int}),
        )
        # Zone 6 Staying
        hass.services.async_register(
            DOMAIN,
            "area_6_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=6): int}),
        )
        # Zone 6 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_6_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=6): int}),
        )

    # Checking if the panel has an area 7
    if int(max_areas) >= 7:
        # Zone 7 Arming
        hass.services.async_register(
            DOMAIN,
            "area_7_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=7): int}),
        )
        # Zone 7 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_7_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=7): int}),
        )
        # Zone 7 Staying
        hass.services.async_register(
            DOMAIN,
            "area_7_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=7): int}),
        )
        # Zone 7 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_7_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=7): int}),
        )

    # Checking if the panel has an area 8
    if int(max_areas) >= 8:
        # Zone 8 Arming
        hass.services.async_register(
            DOMAIN,
            "area_8_arm",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=8): int}),
        )
        # Zone 8 Sleeping
        hass.services.async_register(
            DOMAIN,
            "area_8_sleep",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=8): int}),
        )
        # Zone 8 Staying
        hass.services.async_register(
            DOMAIN,
            "area_8_stay",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=8): int}),
        )
        # Zone 8 Disarming
        hass.services.async_register(
            DOMAIN,
            "area_8_disarm",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=8): int}),
        )

    # Register the bypass service
    hass.services.async_register(
        DOMAIN,
        "bypass_zone",
        OLARM_API.bypass_zone,
        vol.Schema(
            {
                vol.Required("zone_num"): vol.Coerce(int),
            }
        ),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    return True

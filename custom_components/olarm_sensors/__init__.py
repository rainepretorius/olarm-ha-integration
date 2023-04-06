"""Integration for Olarm Devices for Home Assistant"""
import logging
import requests
from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_CONTROL_PANEL_DOMAIN,
)
from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import config_validation as cv
from .coordinator import OlarmCoordinator
from .olarm_api import OlarmApi, OlarmSetupApi
import asyncio
import voluptuous as vol
from .const import DOMAIN, SERVICES_TO_YAML, LOGGER
from homeassistant.helpers import service
from homeassistant.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
)
from .exceptions import ListIndexError
import os


path = os.path.abspath(__file__).replace("__init__.py", "")
PLATFORMS = [ALARM_CONTROL_PANEL_DOMAIN, BINARY_SENSOR_DOMAIN, BUTTON_DOMAIN]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """
    This function handles the setup of the Olarm integration. It creates a coordinator instance, registers services for each zone, and forwards the setup for binary sensors.
    """
    setup_api = OlarmSetupApi(api_key=config_entry.data[CONF_API_KEY])
    devices = await setup_api.get_olarm_devices()

    # Generating services file
    filedata = []
    for device in devices:
        LOGGER.debug("Setting up device %s with device id: %s", device["deviceName"], device["deviceId"])
        
        coordinator = OlarmCoordinator(
            hass,
            entry=config_entry,
            device_id=device["deviceId"],
            device_name=device["deviceName"],
            device_make=device["deviceAlarmType"],
        )

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][config_entry.entry_id] = coordinator
        hass.data[DOMAIN][device["deviceId"]] = coordinator
        hass.data[DOMAIN]["devices"] = devices

        # Creating an instance of the Olarm API class to call the requests to arm, disarm, sleep, or stay the zones.
        OLARM_API = OlarmApi(
            device_id=device["deviceId"],
            api_key=config_entry.data[CONF_API_KEY],
        )

        # Forwarding the setup for the binary sensors.
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

        device1 = await OLARM_API.get_devices_json()

        max_areas = device1["deviceProfile"]["areasLimit"]
        areas = device1["deviceProfile"]["areasLabels"]

        filedata = []
        filedata.append(
            f"{str(device['deviceName']).lower()}_bypass_zone:\n  description: Send a request to Olarm to bypass the zone on {device['deviceName']}.\n  fields:\n    zone_num:\n      description: 'Zone Number'\n      example: '1'\n      required: true\n"
        )
        # Registering Services

        # Bypass service
        # Register the bypass service
        hass.services.async_register(
            DOMAIN,
            f"{str(device['deviceName']).lower()}_bypass_zone",
            OLARM_API.bypass_zone,
            vol.Schema(
                {
                    vol.Required("zone_num"): vol.Coerce(int),
                }
            ),
        )
        for area in range(0, max_areas):
            try:
                name = areas[area]
                if name == "":
                    name = f"area_{area+1}"

            except ListIndexError:
                name = f"area_{area+1}"

            name = "".join(name.lower().split(" "))

            # Area Arming
            filedata.append(
                f"{str(device['deviceName']).lower()}_{name}_arm:\n  description: {SERVICES_TO_YAML['arm']['description']}\n".replace(
                    "areanumber", name
                ).replace(
                    "alarm", device["deviceName"]
                )
            )
            hass.services.async_register(
                DOMAIN,
                f"{str(device['deviceName']).lower()}_{name}_arm",
                OLARM_API.arm_area,
                schema=vol.Schema({vol.Optional("area", default=area + 1): int}),
            )
            # Area Sleeping
            filedata.append(
                f"{str(device['deviceName']).lower()}_{name}_sleep:\n  description: {SERVICES_TO_YAML['sleep']['description']}\n".replace(
                    "areanumber", name
                ).replace(
                    "alarm", device["deviceName"]
                )
            )
            hass.services.async_register(
                DOMAIN,
                f"{str(device['deviceName']).lower()}_{name}_sleep",
                OLARM_API.sleep_area,
                schema=vol.Schema({vol.Optional("area", default=area + 1): int}),
            )
            # Area Staying
            filedata.append(
                f"{str(device['deviceName']).lower()}_{name}_stay:\n  description: {SERVICES_TO_YAML['stay']['description']}\n".replace(
                    "areanumber", name
                ).replace(
                    "alarm", device["deviceName"]
                )
            )
            hass.services.async_register(
                DOMAIN,
                f"{str(device['deviceName']).lower()}_{name}_stay",
                OLARM_API.stay_area,
                schema=vol.Schema({vol.Optional("area", default=area + 1): int}),
            )
            # Area Disarming
            filedata.append(
                f"{str(device['deviceName']).lower()}_{name}_disarm:\n  description: {SERVICES_TO_YAML['disarm']['description']}\n".replace(
                    "areanumber", name
                ).replace(
                    "alarm", device["deviceName"]
                )
            )
            hass.services.async_register(
                DOMAIN,
                f"{str(device['deviceName']).lower()}_{name}_disarm",
                OLARM_API.disarm_area,
                schema=vol.Schema({vol.Optional("area", default=area + 1): int}),
            )
        
        LOGGER.debug("Sett up device %s with device id: %s", device["deviceName"], device["deviceId"])
        

    with open(
        file=os.path.join(path, "services.yaml"), mode="w+", encoding="utf8"
    ) as service_file:
        for line in filedata:
            service_file.write(line)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await async_setup_entry(hass, config_entry)
    await hass.config_entries.async_reload(entry.entry_id)

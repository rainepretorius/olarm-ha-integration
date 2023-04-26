"""Module that stores the Coordinator class to update the data from the api."""
from __future__ import annotations
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.util import aiohttp
from .const import LOGGER, OLARM_CHANGE_TO_HA, DOMAIN
from .olarm_api import OlarmApi
from homeassistant.config_entries import ConfigEntry
import time
from datetime import datetime, timedelta
from .exceptions import ListIndexError


class OlarmCoordinator(DataUpdateCoordinator):
    """
    This class handles the coordination of the Olarm integration. It fetches data for the coordinator from the Olarm API, and provides it to the binary sensors and alarm control panel.
    """

    data = []
    changed_by: dict = {1: None, 2: None}
    last_changed: dict = {1: time.ctime(), 2: time.ctime()}
    last_action: dict = {1: None, 2: None}

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        device_id: str,
        device_name: str,
        device_make: str,
    ) -> None:
        """
        This class handles the coordination of the Olarm integration. It fetches data for the coordinator from the Olarm API, and provides it to the binary sensors and alarm control panel.
        """
        self.entry = entry

        super().__init__(
            hass,
            LOGGER,
            name=f"Olarm Coordinator ({device_id})",
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
        )

        # Instansiating a local instance of the Olarm API
        self.api = OlarmApi(device_id=device_id, api_key=entry.data[CONF_API_KEY])

        # Setting the nessecary class variables and lists.
        self.sensor_data = []
        self.panel_data = {}
        self.panel_state = []
        self.bypass_data = {}
        self.bypass_state = []
        self.ukey_data = []
        self.pgm_data = []
        self.area_triggers = [None, None, None, None, None, None, None, None]

        # Setting the device info.
        self.olarm_device_name = device_name
        self.olarm_device_make = str(device_make).capitalize()
        self.olarm_device_id = device_id
        self.last_changed: dict = {1: time.ctime(), 2: time.ctime()}

        return None

    async def get_panel_states(self) -> bool:
        """
        DOCSTRING: Get the state of each area for the alarm panel.
        return: Boolean
        """
        try:
            devices_json = await self.api.get_devices_json()
            if bool(devices_json):
                return await self.api.get_panel_states(devices_json)

            else:
                LOGGER.warning("Olarm error:\tdevices_json is empty, skipping update")

        except aiohttp.web.HTTPForbidden as ex:
            LOGGER.error("Could not log in to Olarm, %s", ex)
            return False

    async def update_data(self):
        """
        DOCSTRING: Called to update the data for the integration from Olarm's API.
        """
        devices = await self.api.get_all_devices()
        for device in devices:
            coordinator = OlarmCoordinator(
                self.hass,
                entry=self.entry,
                device_id=device["deviceId"],
                device_name=device["deviceName"],
                device_make=device["deviceAlarmType"],
            )

            self.hass.data.setdefault(DOMAIN, {})
            self.hass.data[DOMAIN][device["deviceId"]] = coordinator
            self.hass.data[DOMAIN]["devices"] = devices

        devices_json = await self.api.get_devices_json()
        if bool(devices_json):
            # Getting the sesor states for each zone.
            self.data = await self.api.get_sensor_states(devices_json)
            self.sensor_data = self.data

            # Getting the Area Information
            self.panel_data = await self.api.get_panel_states(devices_json)
            self.panel_state = self.panel_data

            # Getting the Bypass Information
            self.bypass_data = await self.api.get_sensor_bypass_states(devices_json)
            self.bypass_state = self.bypass_data

            try:
                # Getting the device profile
                for i in range(devices_json["deviceProfile"]["areasLimit"]):
                    change_json = await self.api.get_changed_by_json(i + 1)
                    self.changed_by[i + 1] = change_json["userFullname"]
                    # Wed Apr  5 01:19:56 2023
                    self.last_changed[i + 1] = datetime.strptime(
                        time.ctime(
                            int(devices_json["deviceState"]["areasStamp"][i - 1] / 1000)
                        ),
                        "%a %b  %d %X %Y",
                    ) + timedelta(hours=2)
                    self.last_changed[i + 1] = self.last_changed[i + 1].strftime(
                        "%a %d %b %Y %X"
                    )
                    self.last_action[i + 1] = OLARM_CHANGE_TO_HA[change_json["actionCmd"]]
            
            except ListIndexError:
                LOGGER.warning("The area settings in the Olarm App is incorrect. It is currently set to %s and needs to be set to %s for device: (%s)", devices_json["deviceProfile"]["areasLimit"], len(devices_json["deviceState"]["areasStamp"]), self.olarm_device_name)

            # Getting PGM Data
            self.pgm_data = await self.api.get_pgm_zones(devices_json)
            # Getting Ukey Data
            self.ukey_data = await self.api.get_ukey_zones(devices_json)
            # Getting alarm trigger
            self.area_triggers = await self.api.get_alarm_trigger(devices_json)

            # Setting the last update success to true to show device as available.
            self.last_update_success = True

        else:
            LOGGER.warning("Olarm Sensors:\ndevices_json is empty, skipping update")
            self.last_update_success = False

        return self.last_update_success

    async def _async_update_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_get_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID, CONF_SCAN_INTERVAL
from homeassistant.util import aiohttp
from .const import LOGGER
from .olarm_api import OlarmApi
from homeassistant.config_entries import ConfigEntry
import time

_LOGGER = logging.getLogger(__name__)


class OlarmCoordinator(DataUpdateCoordinator):
    """
    This class handles the coordination of the Olarm integration. It fetches data for the coordinator from the Olarm API, and provides it to the binary sensors and alarm control panel.
    """

    data = []
    changed_by: dict = {1: None, 2: None}
    last_changed: dict = {1: time.ctime(), 2: time.ctime()}
    last_action: dict = {1: None, 2: None}

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """
        This class handles the coordination of the Olarm integration. It fetches data for the coordinator from the Olarm API, and provides it to the binary sensors and alarm control panel.
        """
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name="Olarm Coordinator",
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
        )
        self.api = OlarmApi(
            device_id=entry.data[CONF_DEVICE_ID], api_key=entry.data[CONF_API_KEY]
        )
        self.sensor_data = []
        self.panel_data = {}
        self.panel_state = []
        self.bypass_data = {}
        self.bypass_state = []
        self.ukey_data = []
        self.pgm_data = []
        self.area_triggers = [None, None, None, None, None, None, None, None]
        self.last_changed: dict = {1: time.ctime(), 2: time.ctime()}

        return None

    async def get_panel_states(self):
        try:
            """
            DOCSTRING: Get the state of each area for the alarm panel.
            return: None
            """
            devices_json = await self.api.get_devices_json()
            if bool(devices_json):
                return await self.api.get_panel_states(devices_json)
            else:
                LOGGER.warning("devices_json is empty, skipping update")

        except aiohttp.web.HTTPForbidden as ex:
            LOGGER.error("Could not log in to Olarm, %s", ex)
            return False

    async def update_data(self):
        devices_json = await self.api.get_devices_json()
        if bool(devices_json):
            self.data = await self.api.get_sensor_states(devices_json)
            self.sensor_data = self.data
            # Getting the Area Information
            self.panel_data = await self.api.get_panel_states(devices_json)
            self.panel_state = self.panel_data
            # Getting the Bypass Information
            self.bypass_data = await self.api.get_sensor_bypass_states(devices_json)
            self.bypass_state = self.bypass_data
            # Getting the device profile

            for i in range(devices_json["deviceProfile"]["areasLimit"]):
                change_json = await self.api.get_changed_by_json(i + 1)
                self.changed_by[i + 1] = change_json["userFullname"]
                self.last_changed[i + 1] = change_json["actionCreated"]
                self.last_action[i + 1] = change_json["actionCmd"]

            # Getting PGM Data
            self.pgm_data = await self.api.get_pgm_zones(devices_json)
            # Getting Ukey Data
            self.ukey_data = await self.api.get_ukey_zones(devices_json)
            # Getting alarm trigger
            self.area_triggers = await self.api.get_alarm_trigger(devices_json)

            self.last_update_success = True

        else:
            LOGGER.warning("Olarm Sensors:\ndevices_json is empty, skipping update")
            self.last_update_success = False

        return self.last_update_success

    async def _async_update_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_update_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_get_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

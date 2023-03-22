from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID, CONF_SCAN_INTERVAL
from homeassistant.util import aiohttp
from .const import CONF_DEVICE_DEVICE_NAME
from .const import CONF_DEVICE_MAKE
from .const import CONF_DEVICE_MODEL
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
    changed_by = None
    last_changed = None

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

        self.device_name = entry.data[CONF_DEVICE_DEVICE_NAME]
        self.device_make = entry.data[CONF_DEVICE_MAKE]
        self.device_model = entry.data[CONF_DEVICE_MODEL]

        return None

    async def get_panel_states(self):
        try:
            """Update data via Olarm's API"""
            devices_json = await self.api.get_devices_json()
            if bool(devices_json):
                return await self.api.get_panel_states(devices_json)
            else:
                LOGGER.warning("devices_json is empty, skipping update")

        except aiohttp.web.HTTPForbidden as ex:
            LOGGER.error("Could not log in to Olarm Alarm, %s", ex)
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
            # Getting Device_Info
            self.device_make = devices_json["deviceAlarmType"]
            self.device_model = devices_json["deviceSerial"]
            self.device_name = devices_json["deviceName"]
            change_json = await self.api.get_changed_by_json()
            self.changed_by = change_json["userFullname"]
            self.last_changed = time.ctime(int(change_json["actionCreated"]) / 1000)

        else:
            LOGGER.warning("devices_json is empty, skipping update")
        return {sensor["name"]: sensor["state"] for sensor in self.data}

    async def _async_update_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_update_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_get_data(self):
        """Update data via Olarm's API"""
        return await self.update_data()

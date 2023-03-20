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

_LOGGER = logging.getLogger(__name__)


class OlarmCoordinator(DataUpdateCoordinator):
    """Manage fetching events state from NVR or camera"""

    data = []

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data Coordinator"""
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
            LOGGER.error("Could not log in to IMA Protect Alarm, %s", ex)
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

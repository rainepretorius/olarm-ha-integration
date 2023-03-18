from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID, CONF_SCAN_INTERVAL
from .olarm_api import OlarmApi
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)


class OlarmCoordinator(DataUpdateCoordinator):
    """Manage fetching events state from NVR or camera"""

    data = []

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data Coordinator"""

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

    async def _async_update_data(self):
        """Update data via Olarm's API"""
        # Geting the Zone Information
        self.data = await self.api.get_sensor_states()
        self.sensor_data = self.data
        # Getting the Area Information
        self.panel_data = await self.api.get_panel_states()
        self.panel_state = self.panel_data
        # Getting the Bypass Information
        self.bypass_data = await self.api.get_sensor_bypass_states()
        self.bypass_state = self.bypass_data
        return {sensor["name"]: sensor["state"] for sensor in self.data}

    async def async_update_data(self):
        """Update data via Olarm's API"""
        # Geting the Zone Information
        self.data = await self.api.get_sensor_states()
        self.sensor_data = self.data
        # Getting the Area Information
        self.panel_data = await self.api.get_panel_states()
        self.panel_state = self.panel_data
        # Getting the Bypass Information
        self.bypass_data = await self.api.get_sensor_bypass_states()
        self.bypass_state = self.bypass_data
        return {sensor["name"]: sensor["state"] for sensor in self.data}

    async def async_get_data(self):
        """Update data via Olarm's API"""
        # Geting the Zone Information
        self.data = await self.api.get_sensor_states()
        self.sensor_data = self.data
        # Getting the Area Information
        self.panel_data = await self.api.get_panel_states()
        self.panel_state = self.panel_data
        # Getting the Bypass Information
        self.bypass_data = await self.api.get_sensor_bypass_states()
        self.bypass_state = self.bypass_data
        return {sensor["name"]: sensor["state"] for sensor in self.data}

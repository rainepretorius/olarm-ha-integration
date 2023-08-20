"""Module that stores the Coordinator class to update the data from the api."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from .const import LOGGER, DOMAIN
from .olarm_api import OlarmApi
from homeassistant.config_entries import ConfigEntry
from datetime import datetime, timedelta
from .exceptions import ClientConnectorError, APIContentTypeError
from .dataclasses import OlarmDevice
from .dataclasses.api_classes import (
    APIAreaResponse,
    APIBypassResponse,
    APIPGMResponse,
    APISensorResponse,
    APIUkeyResponse,
)


class OlarmCoordinator(DataUpdateCoordinator):
    """
    This class handles the coordination of the Olarm integration. It fetches data for the coordinator from the Olarm API, and provides it to the binary sensors and alarm control panel.
    """

    sensor_data: list[APISensorResponse] = []
    panel_data: list[APIAreaResponse] = []
    bypass_state: list[APIBypassResponse] = []
    ukey_data: list[APIUkeyResponse] = []
    pgm_data: list[APIPGMResponse] = []
    device: OlarmDevice
    api: OlarmApi
    _hass: HomeAssistant

    def __init__(
        self,
        entry: ConfigEntry,
        device: OlarmDevice,
        hass: HomeAssistant,
    ) -> None:
        """
        This class handles the coordination of the Olarm integration. It fetches data for the coordinator from the Olarm API, and provides it to the binary sensors and alarm control panel.
        """
        self.entry = entry
        self.device = device
        self._hass = hass

        super().__init__(
            logger=LOGGER,
            name=f"Olarm Coordinator ({self.device.device_name})",
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
            hass=self._hass,
        )

        # Instansiating a local instance of the Olarm API
        self.api = OlarmApi(
            api_key=entry.data[CONF_API_KEY], device=self.device, hass=self._hass
        )
        self.last_update = datetime.now() - timedelta(minutes=30)

        # Setting the nessecary class variables and lists.
        self.sensor_data = []
        self.panel_data = []
        self.bypass_state = []
        self.ukey_data = []
        self.pgm_data = []
        self.area_triggers = []

        return None

    async def update_data(self):
        """
        Called to update the data for the integration from Olarm's API.
        """
        try:
            # Getting all the devices for your Olarm Account.
            devices = await self.api.get_all_devices()
            self._hass.data[DOMAIN]["devices"] = devices

        except ClientConnectorError as ex:
            self.device.add_error_to_device(
                "Could not check for new Olarm devices connected to your account.\nError:%s",
                ex,
            )
            LOGGER.error(
                "Could not check for new Olarm devices connected to your account.\nError:%s",
                ex,
            )

        except APIContentTypeError as ex:
            self.device.add_error_to_device(
                "Could not retrieve devices connected to your account. The Invalid response is:\n%s",
                ex,
            )
            LOGGER.error(
                "Could not retrieve devices connected to your account. The Invalid response is:\n%s",
                ex,
            )

        if datetime.now() - self.last_update > timedelta(
            seconds=(0.5 * self.entry.data[CONF_SCAN_INTERVAL])
        ):
            self.device = await self.api.get_device_json()

        if bool(self.device) and not self.device.is_errored:
            # Checking if the device is online.
            if self.device.device_status:
                self.device.set_as_enabled()

            else:
                self.device.set_as_disabled()

            # Getting the sensor states for each zone.
            self.sensor_data = await self.api.get_sensor_states(self.device)

            # Getting the Area Information
            self.panel_data = await self.api.get_panel_states(self.device)

            # Getting the Bypass Information
            self.bypass_state = await self.api.get_sensor_bypass_states(self.device)

            # Getting PGM Data
            self.pgm_data = await self.api.get_pgm_zones(self.device)

            # Getting Ukey Data
            self.ukey_data = await self.api.get_ukey_zones(self.device)

            # Getting alarm trigger
            self.area_triggers = await self.api.get_alarm_trigger(self.device)

            for area in self.panel_data:
                self.panel_data[area.index].set_triggers(self.area_triggers[area.index])
                # self.panel_data[area.index].set_last_changed(self.api.get_changed_by_json(area.area_number))

            # Setting the last update success to true to show device as available.
            self.last_update_success = True
            self.last_update = datetime.now()

        else:
            self.device.add_error_to_device(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update",
                self.device.device_name,
            )
            LOGGER.warning(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update",
                self.device.device_name,
            )
            self.last_update_success = False

        return self.last_update_success

    async def _async_update_data(self) -> bool:
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_get_data(self) -> bool:
        """Update data via Olarm's API"""
        return await self.update_data()

    async def async_update_sensor_data(self) -> bool:
        """
        Called to update the data for the integration from Olarm's API.
        """
        self.device = await self.api.get_device_json()

        if bool(self.device) and not self.device.is_errored:
            # Checking if the device is online.
            if self.device["deviceStatus"].lower() == "online":
                self.device.set_as_enabled()

            else:
                self.device.set_as_disabled()

            # Getting the sensor states for each zone.
            self.sensor_data = await self.api.get_sensor_states(self.device)

            # Getting the Bypass Information
            self.bypass_state = await self.api.get_sensor_bypass_states(self.device)

        else:
            self.device.add_error_to_device(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of sensors",
                self.device.device_name,
            )
            LOGGER.warning(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of sensors",
                self.device.device_name,
            )

        return self.last_update_success

    async def async_update_bypass_data(self) -> bool:
        """
        Called to update the data for the integration from Olarm's API.
        """
        self.device = await self.api.get_device_json()

        if bool(self.device) and not self.device.is_errored:
            # Checking if the device is online.
            if self.device["deviceStatus"].lower() == "online":
                self.device.set_as_enabled()

            else:
                self.device.set_as_disabled()

            # Getting the sensor states for each zone.
            self.sensor_data = await self.api.get_sensor_states(self.device)

            # Getting the Bypass Information
            self.bypass_state = await self.api.get_sensor_bypass_states(self.device)

        else:
            self.device.add_error_to_device(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of bypass sensors",
                self.device.device_name,
            )
            LOGGER.warning(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of bypass senosrs",
                self.device.device_name,
            )
            self.last_update_success = False

        return self.last_update_success

    async def async_update_panel_data(self) -> bool:
        """
        Called to update the data for the integration from Olarm's API.
        """
        self.device = await self.api.get_device_json()

        if bool(self.device) and not self.device.is_errored:
            # Checking if the device is online.
            if self.device["deviceStatus"].lower() == "online":
                self.device.set_as_enabled()

            else:
                self.device.set_as_disabled()

            # Getting the Area Information
            self.panel_data = await self.api.get_panel_states(self.device)

            # Getting alarm trigger
            self.area_triggers = await self.api.get_alarm_trigger(self.device)

            for area in self.panel_data:
                self.panel_data[area.index].set_triggers(self.area_triggers[area.index])
                # self.panel_data[area.index].set_last_changed(self.api.get_changed_by_json(area.area_number))

        else:
            self.device.add_error_to_device(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of area panels",
                self.device.device_name,
            )
            LOGGER.warning(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update area panels",
                self.device.device_name,
            )
            self.last_update_success = False

        return self.last_update_success

    async def async_update_pgm_ukey_data(self) -> bool:
        """
        Called to update the data for the integration from Olarm's API.
        """
        self.device = await self.api.get_device_json()

        if bool(self.device) and not self.device.is_errored:
            # Checking if the device is online.
            if self.device["deviceStatus"].lower() == "online":
                self.device.set_as_enabled()

            else:
                self.device.set_as_disabled()

            # Getting PGM Data
            self.pgm_data = await self.api.get_pgm_zones(self.device)

            # Getting Ukey Data
            self.ukey_data = await self.api.get_ukey_zones(self.device)

        else:
            self.device.add_error_to_device(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of utility keys and pgm's",
                self.device.device_name,
            )
            LOGGER.warning(
                "Olarm Sensors:\nself.devices_json for Olarm device (%s) is empty, skipping update of utility keys and pgm's",
                self.device.device_name,
            )
            self.last_update_success = False

        return self.last_update_success

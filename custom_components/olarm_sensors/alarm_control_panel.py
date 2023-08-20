# pylint: disable=hass-component-root-import
from __future__ import annotations
from collections.abc import Iterable, Callable
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel import CodeFormat
from homeassistant.components.alarm_control_panel import const
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import DOMAIN
from .const import LOGGER
from .const import VERSION
from .const import CONF_ALARM_CODE
from .const import CONF_OLARM_DEVICES
from .coordinator import OlarmCoordinator
from .exceptions import CodeTypeError
from datetime import datetime, timedelta
from .dataclasses.api_classes import APIAreaResponse, APIPGMResponse
import asyncio


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Olarm alarm control panel from a config entry."""

    entities = []

    for device in hass.data[DOMAIN]["devices"]:
        if device.device_name not in entry.data[CONF_OLARM_DEVICES]:
            continue

        LOGGER.info("Setting up Alarm Panels for device (%s)", device.device_name)

        # Getting the instance of the DataCoordinator to update the data from Olarm.
        coordinator: OlarmCoordinator = hass.data[DOMAIN][device.device_id]

        for sensor in coordinator.panel_data:
            LOGGER.info(
                "Setting up area (%s) for device (%s)",
                sensor.name,
                coordinator.device.device_name,
            )

            entities.append(OlarmAlarm(coordinator=coordinator, data=sensor))

            LOGGER.info(
                "Set up area (%s) for device (%s)",
                sensor.name,
                coordinator.device.device_name,
            )

    async_add_entities(entities)

    LOGGER.info("Added Olarm Alarm Control Panels for all devices")
    return True


class OlarmAlarm(AlarmControlPanelEntity):
    """
    This class represents an alarm control panel entity in Home Assistant for an Olarm security zone. It defines the panel's state and attributes, and provides methods for updating them.
    """

    _coordinator: OlarmCoordinator
    _data: APIAreaResponse
    _format: str | None
    _trigger_pgm: APIPGMResponse | None = None
    _post_data: dict | None = None

    def __init__(self, coordinator, data: APIAreaResponse) -> None:
        """Initialize the Olarm Alarm Control Panel."""
        self._data = data
        self._coordinator = coordinator

        LOGGER.info(
            "Initializing Olarm Alarm Control Panel for area (%s) device (%s)",
            self._data.name,
            self._coordinator.device.device_name,
        )

        self._format = None

        if not self._coordinator.entry.data[CONF_ALARM_CODE] is None:
            try:
                int(self._coordinator.entry.data[CONF_ALARM_CODE])
                self._format = CodeFormat.NUMBER

            except CodeTypeError:
                self._format = CodeFormat.TEXT

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._data.name + " (" + self._coordinator.device.device_name + ")"

    @property
    def code_format(self):
        """The format of the code used to authenticate alarm actions."""
        if self._format is None:
            return None

        else:
            return self._format

    @property
    def code_arm_required(self):
        """whether a code is needed to authenticate alarm actions."""
        if self._format is None:
            return False

        else:
            return True

    @property
    def unique_id(self):
        """
        The unique id for this entity sothat it can be managed from the ui.
        """
        return f"{self._coordinator.device.device_id}_alarm_contol_panel_{self._data.area_number}"

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        return {
            "name": f"Olarm Sensors ({self._coordinator.device.device_name})",
            "manufacturer": "Raine Pretorius",
            "model": f"{self._coordinator.device.device_make}",
            "identifiers": {(DOMAIN, self._coordinator.device.device_id)},
            "sw_version": VERSION,
            "hw_version": f"{self._coordinator.device.firmware}",
        }

    @property
    def state(self) -> str | None:
        """Return the state of the entity."""
        return self._data.state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        if self._coordinator.device.device_name == "nemtek":
            return const.AlarmControlPanelEntityFeature.ARM_AWAY

        else:
            return (
                const.AlarmControlPanelEntityFeature.ARM_AWAY
                | const.AlarmControlPanelEntityFeature.ARM_HOME
                | const.AlarmControlPanelEntityFeature.ARM_NIGHT
            )

    @property
    def available(self):
        """
        Whether the entity is available. IE the coordinator updatees successfully.
        """
        return (
            self._coordinator.last_update > datetime.now() - timedelta(minutes=2)
            and not self._coordinator.device.is_errored
            and self._coordinator.device.is_online
        )

    @property
    def last_changed(self) -> str | None:
        """Return the last change triggered by."""
        return self._data.last_changed

    @property
    def should_poll(self):
        """Disable polling. Integration will notify Home Assistant on sensor value update."""
        return False

    @property
    def extra_state_attributes(self) -> dict | None:
        """
        Return the state attributes.
        """
        return {
            "last_changed": self._data.last_changed,
            "changed_by": self._data.changed_by,
            "area_trigger": self._data.triggers,
            "last_action": self._data.last_action,
            "code_format": self.code_format,
            "area_name": self._data.name,
            "area_number": self._data.area_number,
        }

    async def async_alarm_disarm(self, code=None) -> None:
        """
        Send the disarm command to the api.
        """
        if self.check_code(code):
            LOGGER.info(
                "Area '%s' on Olarm device (%s) has been disarmed",
                self._data.name,
                self._coordinator.device.device_name,
            )
            resp = await self._coordinator.api.disarm_area(self._data.area_number)
            await self._coordinator.async_update_panel_data()
            return resp

        else:
            self._coordinator.device.add_error_to_device(
                "Invalid code given to disarm area '%s' for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            LOGGER.error(
                "Invalid code given to disarm area '%s' for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            return False

    async def async_alarm_arm_home(self, code=None) -> None:
        """
        Send the stay command to the api.
        """
        if self.check_code(code):
            LOGGER.info(
                "Area '%s' on Olarm device (%s) has been set to armed_home (stay)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            resp = await self._coordinator.api.stay_area(self._data.area_number)
            await self._coordinator.async_update_panel_data()
            return resp

        else:
            self._coordinator.device.add_error_to_device(
                "Invalid code given to set area '%s' to armed home (stay) for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            LOGGER.error(
                "Invalid code given to set area '%s' to armed home (stay) for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            return False

    async def async_alarm_arm_away(self, code=None) -> None:
        """
        Send the arm command to the api.
        """
        if self.check_code(code):
            LOGGER.info(
                "Area '%s' on Olarm device (%s) has been set to armed_away (armed)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            resp = await self._coordinator.api.arm_area(self._data.area_number)
            await self._coordinator.async_update_panel_data()
            return resp

        else:
            self._coordinator.device.add_error_to_device(
                "Invalid code given to set area '%s' to armed_away (Arm) for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            LOGGER.error(
                "Invalid code given to set area '%s' to armed_away (Arm) for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            return False

    async def async_alarm_arm_night(self, code=None) -> None:
        """
        Send the sleep command to the api.
        """
        if self.check_code(code):
            LOGGER.info(
                "Area '%s' on Olarm device (%s) has been set to armed_night (sleep)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            resp = await self._coordinator.api.sleep_area(self._data.area_number)
            await self._coordinator.async_update_panel_data()
            return resp

        else:
            self._coordinator.device.add_error_to_device(
                "Invalid code given to set area '%s' to armed_night (sleep) for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            LOGGER.error(
                "Invalid code given to set area '%s' to armed_night (sleep) for Olarm device (%s)",
                self._data.name,
                self._coordinator.device.device_name,
            )
            return False

    async def async_added_to_hass(self) -> None:
        """
        When entity is added to hass.
        """
        await super().async_added_to_hass()

    async def async_update(self) -> bool:
        """
        Updates the state of the zone sensor from the coordinator.

        Returns:
            boolean: Whether the update worked.
        """
        if datetime.now() - self._coordinator.last_update > timedelta(
            seconds=(0.9 * self._coordinator.entry.data[CONF_SCAN_INTERVAL])
        ):
            # Only update the state from the api if it has been more than 0.9 times the scan interval since the last update.
            await self._coordinator.async_update_panel_data()

        self._data = self._coordinator.panel_data[self._data.index]
        return self._coordinator.last_update_success

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Send alarm trigger command."""
        if not self._coordinator.device.device_name == "FSrl":
            raise NotImplementedError()

        for sensor in self._coordinator.pgm_data:
            # Creating a sensor for each zone on the alarm panel.
            if "Radio Alarm" in sensor["name"]:
                self._trigger_pgm = sensor
                break

        if not self._trigger_pgm.pulse:
            self._post_data = {
                "actionCmd": "pgm-close",
                "actionNum": self._trigger_pgm.pgm_number,
            }

        LOGGER.info("Triggering alarm for %s", self._coordinator.device.device_name)
        self._coordinator.api.send_action(self._post_data)

        await asyncio.sleep(45)
        LOGGER.info("Triggered alarm for %s", self._coordinator.device.device_name)

        self._post_data = {
            "actionCmd": "pgm-open",
            "actionNum": self._trigger_pgm.pgm_number,
        }

        self._coordinator.api.send_action(self._post_data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """
        Updates the state of the zone sensor from the coordinator.

        Returns:
            boolean: Whether the update worked.
        """
        # Setting the state.
        self._data = self._coordinator.panel_data[self._data.index]
        self.async_write_ha_state()

    def check_code(self, entered_code=None) -> bool:
        """
        Checks the code that was enetered against the code in setup.
        """
        try:
            if (
                entered_code is None
                and self._coordinator.entry.data[CONF_ALARM_CODE] is None
            ):
                return True

            elif self.code_format == "number":
                try:
                    checkcode = int(entered_code)
                    return checkcode == int(
                        self._coordinator.entry.data[CONF_ALARM_CODE]
                    )

                except CodeTypeError:
                    return False

            elif self.code_format == "text":
                return entered_code == str(
                    self._coordinator.entry.data[CONF_ALARM_CODE]
                )

            else:
                return False

        except CodeTypeError:
            return False

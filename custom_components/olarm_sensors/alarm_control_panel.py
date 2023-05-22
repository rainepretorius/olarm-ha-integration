# pylint: disable=hass-component-root-import
from __future__ import annotations
from collections.abc import Iterable, Callable
from typing import Any
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel import CodeFormat
from homeassistant.components.alarm_control_panel import const
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import OLARM_STATE_TO_HA
from .const import DOMAIN
from .const import LOGGER
from .const import VERSION
from .const import CONF_DEVICE_FIRMWARE
from .const import CONF_ALARM_CODE
from .coordinator import OlarmCoordinator
from .exceptions import ListIndexError, CodeTypeError
from datetime import datetime, timedelta


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Olarm alarm control panel from a config entry."""

    entities = []

    for device in hass.data[DOMAIN]["devices"]:
        LOGGER.info("Setting up Alarm Panels for device (%s)", device["deviceName"])
        coordinator = hass.data[DOMAIN][device["deviceId"]]

        await coordinator.async_get_data()

        for sensor in coordinator.panel_state:
            LOGGER.info(
                "Setting up area (%s) for device (%s)",
                sensor["name"],
                device["deviceName"],
            )
            alarm_panel = OlarmAlarm(
                coordinator=coordinator,
                sensor_name=sensor["name"],
                state=sensor["state"],
                area=sensor["area_number"],
            )

            entities.append(alarm_panel)

            LOGGER.info(
                "Set up area (%s) for device (%s)",
                sensor["name"],
                device["deviceName"],
            )

    """
    if "alarm_control_panel.olarm_sensors" in hass.config.components:
        LOGGER.info("Added Olarm Alarm Control Panels for all devices")
        return True
    """

    async_add_entities(entities)
    LOGGER.info("Added Olarm Alarm Control Panels for all devices")
    return True


class OlarmAlarm(CoordinatorEntity, AlarmControlPanelEntity):
    """
    This class represents an alarm control panel entity in Home Assistant for an Olarm security zone. It defines the panel's state and attributes, and provides methods for updating them.
    """

    coordinator: OlarmCoordinator

    _changed_by: str | None = None
    _last_changed: Any | None = None
    _state: str | None = None
    area: int = 1
    _area_trigger: str | None = None
    _last_action: str | None = None

    def __init__(self, coordinator, sensor_name, state, area) -> None:
        """Initialize the Olarm Alarm Control Panel."""
        LOGGER.info(
            "Initiating Olarm Alarm Control Panel for area (%s) device (%s)",
            sensor_name,
            coordinator.olarm_device_name,
        )
        super().__init__(coordinator)
        self._state = OLARM_STATE_TO_HA.get(state)
        self.sensor_name = sensor_name
        self.area = area
        self.format = None

        if not self.coordinator.entry.data[CONF_ALARM_CODE] is None:
            try:
                int(self.coordinator.entry.data[CONF_ALARM_CODE])
                self.format = CodeFormat.NUMBER

            except CodeTypeError:
                self.format = CodeFormat.TEXT

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.sensor_name + " (" + self.coordinator.olarm_device_name + ")"

    @property
    def code_format(self):
        """The format of the code used to authenticate alarm actions."""
        if self.format is None:
            return None

        else:
            return self.format

    @property
    def code_arm_required(self):
        """whether a code is needed to authenticate alarm actions."""
        if self.format is None:
            return False

        else:
            return True

    @property
    def unique_id(self):
        """
        The unique id for this entity sothat it can be managed from the ui.
        """
        return f"{self.coordinator.olarm_device_id}_" + "_".join(
            self.sensor_name.lower().split(" ")
        )

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        return {
            "name": f"Olarm Sensors ({self.coordinator.olarm_device_name})",
            "manufacturer": "Raine Pretorius",
            "model": f"{self.coordinator.olarm_device_make}",
            "identifiers": {(DOMAIN, self.coordinator.olarm_device_id)},
            "sw_version": VERSION,
            "hw_version": f"{self.coordinator.entry.data[CONF_DEVICE_FIRMWARE]}",
        }

    @property
    def state(self) -> str | None:
        """Return the state of the entity."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        if self.coordinator.olarm_device_make.lower() == "nemtek":
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
        return self.coordinator.last_update > datetime.now() - timedelta(minutes=2)

    @property
    def last_changed(self) -> str | None:
        """Return the last change triggered by."""
        return self._last_changed

    @property
    def extra_state_attributes(self) -> dict | None:
        """
        Return the state attributes.
        """
        return {
            "last_changed": self._last_changed,
            "area_trigger": self._area_trigger,
            "last_action": self._last_action,
            "code_required": self.code_arm_required,
            "code_format": self.code_format,
            "area_name": self.sensor_name,
            "area_number": self.area,
        }

    async def async_alarm_disarm(self, code=None) -> None:
        """
        Send the disarm command to the api.
        """
        LOGGER.info(
            "Olarm device (%s) has been disarmed", self.coordinator.olarm_device_name
        )
        if self.check_code(code):
            return await self.coordinator.api.disarm_area(self.area)

        else:
            LOGGER.error(
                "Invalid code given to disarm alarm for Olarm device (%s)",
                self.coordinator.olarm_device_name,
            )
            return False

    async def async_alarm_arm_home(self, code=None) -> None:
        """
        Send the stay command to the api.
        """
        LOGGER.info(
            "Olarm device (%s) has been set to armed_home (stay)",
            self.coordinator.olarm_device_name,
        )
        if self.check_code(code):
            return await self.coordinator.api.stay_area(self.area)

        else:
            LOGGER.error(
                "Invalid code given to set alarm to armed home (stay) for Olarm device (%s)",
                self.coordinator.olarm_device_name,
            )
            return False

    async def async_alarm_arm_away(self, code=None) -> None:
        """
        Send the arm command to the api.
        """
        LOGGER.info(
            "Olarm device (%s) has been set to armed_away (armed)",
            self.coordinator.olarm_device_name,
        )
        if self.check_code(code):
            return await self.coordinator.api.arm_area(self.area)

        else:
            LOGGER.error(
                "Invalid code given to set alarm to armed_away (Arm) for Olarm device (%s)",
                self.coordinator.olarm_device_name,
            )
            return False

    async def async_alarm_arm_night(self, code=None) -> None:
        """
        Send the sleep command to the api.
        """
        LOGGER.info(
            "Olarm device (%s) has been set to armed_night (sleep)",
            self.coordinator.olarm_device_name,
        )
        if self.check_code(code):
            return await self.coordinator.api.sleep_area(self.area)

        else:
            LOGGER.error(
                "Invalid code given to set alarm to armed_night (sleep) for Olarm device (%s)",
                self.coordinator.olarm_device_name,
            )
            return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            self._state = OLARM_STATE_TO_HA.get(
                self.coordinator.panel_state[self.area - 1]["state"]
            )

        except ListIndexError:
            LOGGER.error("Could not set alarm panel state for %s", self.sensor_name)

        try:
            self._changed_by = self.coordinator.changed_by[self.area]

        except ListIndexError:
            LOGGER.debug("Could not set alarm panel changed by")

        try:
            self._last_changed = self.coordinator.last_changed[self.area]

        except ListIndexError:
            LOGGER.debug("Could not set alarm panel last changed")

        try:
            self._last_action = self.coordinator.last_action[self.area]

        except ListIndexError:
            LOGGER.debug("Could not set alarm panel last action")

        try:
            self._area_trigger = self.coordinator.area_triggers[self.area - 1]

        except ListIndexError:
            LOGGER.debug("Could not set alarm panel trigger")

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """
        When entity is added to hass.
        """
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    def check_code(self, entered_code=None) -> bool:
        """
        Checks the code that was enetered against the code in setup.
        """
        try:
            if (
                entered_code is None
                and self.coordinator.entry.data[CONF_ALARM_CODE] is None
            ):
                return True

            elif self.code_format == "number":
                try:
                    checkcode = int(entered_code)
                    return checkcode == int(
                        self.coordinator.entry.data[CONF_ALARM_CODE]
                    )

                except CodeTypeError:
                    return False

            elif self.code_format == "text":
                return entered_code == str(self.coordinator.entry.data[CONF_ALARM_CODE])

            else:
                return False

        except CodeTypeError:
            return False

"""Support for Olarm alarm control panels."""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Callable, Any
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel import CodeFormat
from homeassistant.components.alarm_control_panel.const import SUPPORT_ALARM_ARM_AWAY
from homeassistant.components.alarm_control_panel.const import SUPPORT_ALARM_ARM_HOME
from homeassistant.components.alarm_control_panel.const import SUPPORT_ALARM_ARM_NIGHT
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import ALARM_STATE_TO_HA
from .const import CONF_ALARM_CODE
from .const import DOMAIN
from .const import LOGGER
from .const import AlarmPanelArea
from .const import VERSION
from .const import CONF_DEVICE_NAME
from .const import CONF_DEVICE_MAKE
from .coordinator import OlarmCoordinator
from .exceptions import ListIndexError


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Olarm alarm control panel from a config entry."""
    LOGGER.debug("olarm_panel -> async_setup_entry")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    panel_states = await coordinator.get_panel_states()

    area = 1
    for sensor in panel_states:
        sensor = OlarmAlarm(
            coordinator=hass.data[DOMAIN][entry.entry_id],
            sensor_name=sensor["name"],
            state=sensor["state"],
            area=area,
        )
        entities.append(sensor)
        area = area + 1

    async_add_entities(entities)
    # async_add_entities([OlarmAlarm(coordinator=hass.data[DOMAIN][entry.entry_id])])


class OlarmAlarm(CoordinatorEntity, AlarmControlPanelEntity):
    """
    This class represents an alarm control panel entity in Home Assistant for an Olarm security zone. It defines the panel's state and attributes, and provides methods for updating them.
    """

    LOGGER.debug("OlarmAlarm")

    coordinator: OlarmCoordinator

    _changed_by: str | None = None
    _last_changed: Any | None = None
    _state: str | None = None
    area: int = 1
    _area_trigger: str | None = None
    _last_action: str | None = None

    def __init__(self, coordinator, sensor_name, state, area) -> None:
        """Initialize the Olarm Alarm Control Panel."""
        LOGGER.debug("OlarmAlarm.init")
        super().__init__(coordinator)
        self._state = ALARM_STATE_TO_HA.get(state)
        self.sensor_name = sensor_name
        self.area = area

    @property
    def code(self):
        return self.coordinator.entry.options.get(CONF_ALARM_CODE)

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.sensor_name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.entry.data[CONF_DEVICE_ID] + "_" + self.sensor_name

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        return {
            "name": f"Olarm Sensors ({self.coordinator.entry.data[CONF_DEVICE_NAME]})",
            "manufacturer": "Olarm Integration",
            "model": f"{self.coordinator.entry.data[CONF_DEVICE_MAKE]}",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
            "sw_version": VERSION,
            "hw_version": "Not Implemented",
        }

    @property
    def state(self) -> str | None:
        """Return the state of the entity."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_NIGHT

    @property
    def code_format(self):
        code = self.code
        if code is None or code == "":
            return None
        if isinstance(code, str) and re.search("^\\d+$", code):
            return CodeFormat
        return CodeFormat

    @property
    def changed_by(self) -> str | None:
        """Return the last change triggered by."""
        return self._changed_by

    @property
    def last_changed(self) -> str | None:
        """Return the last change triggered by."""
        return self._last_changed

    @property
    def state_attributes(self) -> dict | None:
        """
        DOCSTRING: Return the state attributes.
        """
        return {
            "last_changed": self._last_changed,
            "changed_by": self._changed_by,
            "area_trigger": self._area_trigger,
            "last_action": self._last_action,
        }

    def _validate_code(self, code_test) -> bool:
        """
        Should valaidate the alarm code someday.
        """
        LOGGER.debug("OlarmAlarm._validate_code")
        code = self.code
        if code is None or code == "":
            return True

        if isinstance(code, str):
            alarm_code = code

        else:
            alarm_code = code.render(parse_result=False)

        check = not alarm_code or code_test == alarm_code

        if not check:
            LOGGER.warning("Invalid code given")

        return check

    async def async_alarm_disarm(self, code=None) -> None:
        """
        DOCSTRING: Send the disarm command to the api.
        """
        if not self._validate_code(code):
            return
        LOGGER.info("OlarmAlarm.async_alarm_disarm")
        return await self.coordinator.api.disarm_area(AlarmPanelArea(self.area))

    async def async_alarm_arm_home(self, code=None) -> None:
        """
        DOCSTRING: Send the stay command to the api.
        """
        if not self._validate_code(code):
            return
        LOGGER.info("OlarmAlarm.async_alarm_arm_home")
        return await self.coordinator.api.stay_area(AlarmPanelArea(self.area))

    async def async_alarm_arm_away(self, code=None) -> None:
        """
        DOCSTRING: Send the arm command to the api.
        """
        if not self._validate_code(code):
            return
        LOGGER.info("OlarmAlarm.async_alarm_arm_away")
        return await self.coordinator.api.arm_area(AlarmPanelArea(self.area))

    async def async_alarm_arm_night(self, code=None) -> None:
        """
        DOCSTRING: Send the sleep command to the api.
        """
        if not self._validate_code(code):
            return
        LOGGER.info("OlarmAlarm.async_alarm_arm_night")
        return await self.coordinator.api.sleep_area(AlarmPanelArea(self.area))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.panel_state
        if len(state) > 0:
            for area_state in state:
                if area_state["name"] == self.sensor_name:
                    self._state = ALARM_STATE_TO_HA.get(area_state["state"])
                    break

        try:
            self._changed_by = self.coordinator.changed_by[self.area]
        except ListIndexError:
            LOGGER.error("Could not set alarm panel changed by")

        try:
            self._last_changed = self.coordinator.last_changed[self.area]
        except ListIndexError:
            LOGGER.error("Could not set alarm panel last changed")

        try:
            self._last_action = self.coordinator.last_action[self.area]
        except ListIndexError:
            LOGGER.error("Could not set alarm panel last action")

        try:
            self._area_trigger = self.coordinator.area_triggers[self.area - 1]
        except ListIndexError:
            LOGGER.error("Could not set alarm panel trigger")

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """
        DOCSTRING: When entity is added to hass.
        """
        LOGGER.debug("OlarmAlarm.async_added_to_hass")
        await super().async_added_to_hass()
        self._handle_coordinator_update()

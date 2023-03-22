"""Support for Olarm alarm control panels."""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Callable

from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel import FORMAT_NUMBER
from homeassistant.components.alarm_control_panel import FORMAT_TEXT
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
from .coordinator import OlarmCoordinator


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
    """Representation of an Olarm alarm status."""

    coordinator: OlarmCoordinator

    _changed_by: str | None = None
    _state: str | None = None
    area = None

    def __init__(self, coordinator, sensor_name, state, area) -> None:
        """Initialize the Olarm Alarm Control Panel."""
        LOGGER.debug("OlarmAlarm.init")
        super().__init__(coordinator)
        self._changed_by = None
        self._last_changed = None
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
    def device_info(self):
        """Return device information about this entity."""
        LOGGER.debug("OlarmAlarm.device_info")
        return {
            "name": "Olarm Sensors",
            "manufacturer": "Raine Pretorius",
            "model": "Olarm Device",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
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
            return FORMAT_NUMBER
        return FORMAT_TEXT

    @property
    def changed_by(self) -> str | None:
        """Return the last change triggered by."""
        return self._changed_by

    @property
    def last_changed(self) -> str | None:
        """Return the last change triggered by."""
        return self._last_changed

    def _validate_code(self, code_test) -> bool:
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

    async def _async_set_arm_state(self, state: int, code=None) -> None:
        LOGGER.debug("OlarmAlarm._async_set_arm_state")
        """Send set arm state command."""
        if not self._validate_code(code):
            return

        if state == 0:
            if self.area == 1:
                await self.coordinator.api.disarm_zone_1(None)

            elif self.area == 2:
                await self.coordinator.api.disarm_zone_2(None)

        elif state == 1:
            if self.area == 1:
                await self.coordinator.api.stay_zone_1(None)

            elif self.area == 2:
                await self.coordinator.api.stay_zone_2(None)

        elif state == 2:
            if self.area == 1:
                await self.coordinator.api.arm_zone_1(None)

            elif self.area == 2:
                await self.coordinator.api.arm_zone_2(None)

            else:
                return

        elif state == 3:
            if self.area == 1:
                self.coordinator.api.sleep_zone_1(None)

            elif self.area == 2:
                self.coordinator.api.sleep_zone_2(None)

            else:
                return

        await self.hass.async_add_executor_job(
            self.coordinator.__setattr__, "status", state
        )
        # LOGGER.debug("Olarm set arm state %s", state)
        await self.coordinator.async_refresh()

    async def async_alarm_disarm(self, code=None) -> None:
        LOGGER.info("OlarmAlarm.async_alarm_disarm")
        """Send disarm command."""
        await self._async_set_arm_state(0, code)

    async def async_alarm_arm_home(self, code=None) -> None:
        LOGGER.info("OlarmAlarm.async_alarm_arm_home")
        """Send arm home command."""
        await self._async_set_arm_state(1, code)

    async def async_alarm_arm_away(self, code=None) -> None:
        LOGGER.info("OlarmAlarm.async_alarm_arm_away")
        """Send arm away command."""
        await self._async_set_arm_state(2, code)

    async def async_alarm_arm_night(self, code=None) -> None:
        LOGGER.info("OlarmAlarm.async_alarm_arm_night")
        """Send arm away command."""
        await self._async_set_arm_state(3, code)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.panel_state
        if len(state) > 0:
            for obj in state:
                if obj["name"] == self.sensor_name:
                    self._state = ALARM_STATE_TO_HA.get(obj["state"])
                    break

        self._changed_by = self.coordinator.changed_by
        self._last_changed = self.coordinator.last_changed
        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        LOGGER.debug("OlarmAlarm.async_added_to_hass")
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @property
    def state_attributes(self) -> dict | None:
        """Return the state attributes."""
        return {"last_changed": self._last_changed, "changed_by": self._changed_by}

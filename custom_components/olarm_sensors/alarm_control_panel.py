"""Support for Olarm alarm control panels."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Callable, Any
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel import CodeFormat
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import OLARM_STATE_TO_HA
from .const import DOMAIN
from .const import LOGGER
from .const import AlarmPanelArea
from .const import VERSION
from .const import CONF_DEVICE_FIRMWARE
from .const import CONF_ALARM_CODE
from .coordinator import OlarmCoordinator
from .exceptions import ListIndexError, DictionaryKeyError, CodeTypeError


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Olarm alarm control panel from a config entry."""
    LOGGER.debug("olarm_panel -> async_setup_entry")

    entities = []
    for device in hass.data[DOMAIN]["devices"]:
        coordinator = hass.data[DOMAIN][device["deviceId"]]

        panel_states = await coordinator.get_panel_states()

        area = 1
        for sensor in panel_states:
            sensor = OlarmAlarm(
                coordinator=coordinator,
                sensor_name=sensor["name"],
                state=sensor["state"],
                area=area,
            )
            entities.append(sensor)
            area = area + 1

    async_add_entities(entities)


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
        LOGGER.debug(
            "Initiating Olarm Alarm Panel for %s",
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
        if self.format is None:
            return None

        else:
            return self.format

    @property
    def code_arm_required(self):
        if self.format is None:
            return False

        else:
            return True

    @property
    def unique_id(self):
        """
        DOCSTRING: The unique id for this entity sothat it can be managed from the ui.
        """
        return f"{self.coordinator.olarm_device_id}_{self.sensor_name}".replace(
            " ", "_"
        ).lower()

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        try:
            return {
                "name": f"Olarm Sensors ({self.coordinator.olarm_device_name})",
                "manufacturer": "Raine Pretorius",
                "model": f"{self.coordinator.olarm_device_make}",
                "identifiers": {(DOMAIN, self.coordinator.olarm_device_id)},
                "sw_version": VERSION,
                "hw_version": f"{self.coordinator.entry.data[CONF_DEVICE_FIRMWARE]}",
            }

        except DictionaryKeyError:
            return {
                "name": f"Olarm Sensors ({self.coordinator.olarm_device_name})",
                "manufacturer": "Raine Pretorius",
                "model": f"{self.coordinator.olarm_device_make}",
                "identifiers": {(DOMAIN, self.coordinator.olarm_device_id)},
                "sw_version": VERSION,
                "hw_version": "Redo setup for integration",
            }

    @property
    def state(self) -> str | None:
        """Return the state of the entity."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        if self.coordinator.olarm_device_make.lower() == "nemtek":
            return AlarmControlPanelEntityFeature.ARM_AWAY

        else:
            return (
                AlarmControlPanelEntityFeature.ARM_AWAY
                | AlarmControlPanelEntityFeature.ARM_HOME
                | AlarmControlPanelEntityFeature.ARM_NIGHT
            )

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
            "code_required": self.code_arm_required,
            "code_format": self.code_format,
        }

    async def async_alarm_disarm(self, code=None) -> None:
        """
        DOCSTRING: Send the disarm command to the api.
        """
        LOGGER.info("OlarmAlarm.async_alarm_disarm")
        if self.check_code(code):
            return await self.coordinator.api.disarm_area(AlarmPanelArea(self.area))

        else:
            LOGGER.error(
                "Invalid code given for alarm disarm for device: %s",
                self.coordinator.olarm_device_name,
            )
            return False

    async def async_alarm_arm_home(self, code=None) -> None:
        """
        DOCSTRING: Send the stay command to the api.
        """
        LOGGER.info("OlarmAlarm.async_alarm_arm_home")
        if self.check_code(code):
            return await self.coordinator.api.stay_area(AlarmPanelArea(self.area))
        else:
            LOGGER.error(
                "Invalid code given for alarm arm home for device: %s",
                self.coordinator.olarm_device_name,
            )
            return False

    async def async_alarm_arm_away(self, code=None) -> None:
        """
        DOCSTRING: Send the arm command to the api.
        """
        LOGGER.info("OlarmAlarm.async_alarm_arm_away")
        if self.check_code(code):
            return await self.coordinator.api.arm_area(AlarmPanelArea(self.area))
        else:
            LOGGER.error(
                "Invalid code given for alarm arm away for device: %s",
                self.coordinator.olarm_device_name,
            )
            return False

    async def async_alarm_arm_night(self, code=None) -> None:
        """
        DOCSTRING: Send the sleep command to the api.
        """
        LOGGER.info("OlarmAlarm.async_alarm_arm_night")
        if self.check_code(code):
            return await self.coordinator.api.sleep_area(AlarmPanelArea(self.area))
        else:
            LOGGER.error(
                "Invalid code given for alarm arm night for device: %s",
                self.coordinator.olarm_device_name,
            )
            return False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.panel_state
        if len(state) > 0:
            for area_state in state:
                if area_state["name"] == self.sensor_name:
                    self._state = OLARM_STATE_TO_HA.get(area_state["state"])
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
                except Exception:
                    return False

            elif self.code_format == "text":
                return entered_code == str(self.coordinator.entry.data[CONF_ALARM_CODE])

            else:
                return False

        except CodeTypeError:
            return False

        except Exception:
            return False

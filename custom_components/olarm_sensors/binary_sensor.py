"""Platform for binary sensor integration."""
from __future__ import annotations
from .coordinator import OlarmCoordinator
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging
import datetime
from .const import CONF_DEVICE_NAME, CONF_DEVICE_MODEL, CONF_DEVICE_MAKE, LOGGER, DOMAIN
from homeassistant.const import CONF_DEVICE_ID

# from homeassistant.exceptions import *

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add binary sensors for Olarm alarm sensor and panel states."""

    # Defining the list to store the instances of each alarm zone.
    entities = []

    # Creating an instance of the DataCoordinator to update the data from Olarm.
    coordinator = OlarmCoordinator(hass, entry)

    # Getting the first setup data from Olarm. eg: Panelstates, and all zones.
    await coordinator.async_get_data()

    LOGGER.info("Setting up Olarm Sensors")

    # Looping through the sensors/zones for the panel.
    index = 0
    for sensor in coordinator.sensor_data:
        # Creating a sensor for each zone on the alarm panel.
        sensor = OlarmSensor(
            coordinator=coordinator,
            sensor_name=sensor["name"],
            state=sensor["state"],
            index=index,
            last_changed=sensor["last_changed"],
        )
        index = index + 1
        entities.append(sensor)

    index = 0
    for sensor1 in coordinator.bypass_state:
        # Creating a bypass sensor for each zone on the alarm panel.
        sensor = OlarmBypassSensor(
            coordinator=coordinator,
            sensor_name=sensor1["name"],
            state=sensor1["state"],
            index=index,
            last_changed=sensor1["last_changed"],
        )
        index = index + 1
        entities.append(sensor)

    LOGGER.info("Adding Olarm Sensors")

    # Adding Olarm Sensors to Home Assistant
    async_add_entities(entities)

    LOGGER.info("Added Olarm Sensors")


class OlarmSensor(BinarySensorEntity):
    """
    This class represents a binary sensor entity in Home Assistant for an Olarm security zone. It defines the sensor's state and attributes, and provides methods for updating them.
    """

    index = 0

    def __init__(
        self,
        coordinator: OlarmCoordinator,
        sensor_name: str,
        state: str,
        index: int,
        last_changed,
    ) -> None:
        """
        DOCSTRING: Creates a sensor for each zone on the alarm panel.

        (params):
            coordinator(OlarmCoordinator): The Data Update Coordinator.
            sensor_name(str): The name of the Sensor on the alarm panel.
            state(str): The state of the sensor. (on or off)
            index(int): The index in the coordinator's data list of the sensor's state.
        """
        self.coordinator = coordinator
        self.sensor_name = str(sensor_name)
        self.set_state = state
        self._attr_is_on = self.set_state == "on"
        self.index = index
        self.last_changed = last_changed

        # Setting the type of Binarysensor
        # Motion Sensor
        if "pir" in self.sensor_name.lower():
            self._attr_device_class = BinarySensorDeviceClass.MOTION

        # Window
        elif (
            "windows" in self.sensor_name.lower() or "wind" in self.sensor_name.lower()
        ):
            self._attr_device_class = BinarySensorDeviceClass.WINDOW

        # Door
        elif "door" in self.sensor_name.lower():
            self._attr_device_class = BinarySensorDeviceClass.DOOR

        # Powered by AC
        elif "ac" in self.sensor_name.lower():
            self._attr_device_class = BinarySensorDeviceClass.PLUG

        # Powered By Battery
        elif "batt" in self.sensor_name.lower():
            self._attr_device_class = BinarySensorDeviceClass.POWER

        # Motion Sensor if no match.
        else:
            self._attr_device_class = BinarySensorDeviceClass.MOTION

    @property
    def unique_id(self):
        """
        DOCSTRING: The unique id for this entity sothat it can be managed from the ui.
        """
        return f"olarm_sensor_{self.sensor_name}".replace(" ", "").lower()

    @property
    def name(self):
        """
        DOCSTRING: The name of the zone from the ALarm Panel
        """
        name = []
        for item in str(self.sensor_name).lower().split(" "):
            name.append(str(item).capitalize())
        return " ".join(name)

    @property
    def is_on(self):
        """
        DOCSTRING: Whether the sensor/zone is active or not.
        """
        if self.coordinator.sensor_data[self.index]["state"] == "on":
            # Zone Active
            self._attr_is_on = True
            return True

        else:
            # Zone not active
            self._attr_is_on = False
            return False

    @property
    def icon(self):
        """
        DOCSTRING: Setting the icon of the entity depending on the state of the zone.
        """
        # Motion Sensor
        if "pir" in self.sensor_name.lower():
            if self.is_on:
                return "mdi:motion-sensor"

            else:
                return "mdi:motion-sensor-off"

        # Window
        elif (
            "windows" in self.sensor_name.lower() or "wind" in self.sensor_name.lower()
        ):
            if self.is_on:
                return "mdi:window-open"

            else:
                return "mdi:window-closed"

        # Door
        elif "door" in self.sensor_name.lower():
            if self.is_on:
                return "mdi:door-open"

            else:
                return "mdi:door-closed"

        # Powered by AC
        elif "ac" in self.sensor_name.lower():
            if self.is_on:
                return "mdi:power-plug"

            else:
                return "mdi:power-plug-off"

        # Powered By Battery
        elif "batt" in self.sensor_name.lower():
            return "mdi:battery"

        # Motion Sensor if no match
        else:
            if self.is_on:
                return "mdi:motion-sensor"

            else:
                return "mdi:motion-sensor-off"

    @property
    def available(self):
        """
        DOCSTRING: Whether the entity is available. IE the coordinator updates successfully.
        """
        return self.coordinator.last_update_success

    @property
    def state_attributes(self) -> dict | None:
        """Return the state attributes."""
        self.last_changed = self.coordinator.sensor_data[self.index]["last_changed"]
        return {"last_tripped_time": self.last_changed}

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        LOGGER.debug("OlarmAlarm.device_info")
        return {
            "name": f"Olarm Sensors ({self.coordinator.entry.data[CONF_DEVICE_NAME]})",
            "manufacturer": f"Olarm Integration",
            "model": f"{self.coordinator.entry.data[CONF_DEVICE_MAKE]}",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
        }

    async def async_update(self):
        if self.coordinator.sensor_data[self.index][
            "state"
        ] == "on" and self._attr_is_on != (
            self.coordinator.sensor_data[self.index]["state"] == "on"
        ):
            # Zone Active
            self._attr_is_on = True
            self.last_changed = self.coordinator.sensor_data[self.index]["last_changed"]
            self.async_write_ha_state()
            return True

        else:
            # Zone not active
            self._attr_is_on = False
            self.last_changed = self.coordinator.sensor_data[self.index]["last_changed"]
            self.async_write_ha_state()
            return False

    async def async_added_to_hass(self):
        """
        DOCSTRING: Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class OlarmPanelState(BinarySensorEntity):
    index = 0

    def __init__(self, coordinator, sensor_name, state, index) -> None:
        """
        DOCSTRING: Creates a sensor for each zone from Olarm.

        (params):
            coordinator(OlarmCoordinator): The Data Update Coordinator.
            sensor_name(str): The name of the zone from Olarm.
            state(str): The state of the zone. (on or off)
            index(int): The index in the coordinator's data list of the sensor's state.
        """
        self.coordinator = coordinator
        self.sensor_name = str(sensor_name)
        self.set_state = state
        self._attr_is_on = self.set_state == "on"
        self.index = index
        self.last_changed = datetime.datetime.now()
        self._old_state = self.set_state == "on"

    @property
    def unique_id(self):
        """
        DOCSTRING: The unique id for this entity sothat it can be managed from the ui.
        """
        return f"olarm_panel_{self.sensor_name}".replace(" ", "").lower()

    @property
    def name(self):
        """
        DOCSTRING: The name of the zone from Olarm
        """
        name = []
        for item in str(self.sensor_name).lower().split(" "):
            name.append(str(item).capitalize())
        return " ".join(name)

    @property
    def is_on(self):
        """
        DOCSTRING: Whether the sensor/zone is active or not.
        """

        if self.coordinator.panel_state[self.index]["state"] == "on":
            self._attr_is_on = True
            return True

        else:
            self._attr_is_on = False
            return False

    @property
    def icon(self):
        """
        DOCSTRING: Setting the icon of the entity depending on the state of the zone.
        """
        if self.is_on:
            return "mdi:alarm-panel"

        else:
            return "mdi:alarm-panel-outline"

    @property
    def available(self):
        """
        DOCSTRING: Whether the entity is available. IE the coordinator updatees successfully.
        """
        return self.coordinator.last_update_success

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        LOGGER.debug("OlarmAlarm.device_info")
        return {
            "name": f"Olarm Sensors ({self.coordinator.entry.data[CONF_DEVICE_NAME]})",
            "manufacturer": f"Olarm Integration",
            "model": f"{self.coordinator.entry.data[CONF_DEVICE_MAKE]}",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
        }

    async def async_added_to_hass(self):
        """
        DOCSTRING: Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class OlarmBypassSensor(BinarySensorEntity):
    """
    This class represents a binary sensor entity in Home Assistant for an Olarm security zone's bypass state. It defines the sensor's state and attributes, and provides methods for updating them.
    """

    index = 0

    def __init__(
        self,
        coordinator: OlarmCoordinator,
        sensor_name: str,
        state: str,
        index: int,
        last_changed,
    ) -> None:
        """
        DOCSTRING: Creates a sensor for each zone on the alarm panel.

        (params):
            coordinator(OlarmCoordinator): The Data Update Coordinator.
            sensor_name(str): The name of the Sensor on the alarm panel.
            state(str): The state of the sensor. (on or off)
            index(int): The index in the coordinator's data list of the sensor's state.
        """
        self.coordinator = coordinator
        self.sensor_name = str(sensor_name) + " Bypass"
        self.set_state = state
        self._attr_is_on = self.set_state == "on"
        self.index = index
        self.last_changed = last_changed

    @property
    def unique_id(self):
        """
        DOCSTRING: The unique id for this entity sothat it can be managed from the ui.
        """
        return f"olarm_sensor_{self.sensor_name}".replace(" ", "").lower()

    @property
    def name(self):
        """
        DOCSTRING: The name of the zone from the ALarm Panel
        """
        name = []
        for item in str(self.sensor_name).lower().split(" "):
            name.append(str(item).capitalize())
        return " ".join(name)

    @property
    def is_on(self):
        """
        DOCSTRING: Whether the sensor/zone is bypassed or not.
        """
        if self.coordinator.bypass_state[self.index]["state"] == "on":
            # Zone Bypassed
            self._attr_is_on = True
            return True

        else:
            # Zone not bypassed
            self._attr_is_on = False
            return False

    @property
    def icon(self):
        """
        DOCSTRING: Setting the icon of the entity depending on the state of the zone.
        """
        # Zone Bypass
        if self.is_on:
            return "mdi:shield-home-outline"

        else:
            return "mdi:shield-home"

    @property
    def available(self):
        """
        DOCSTRING: Whether the entity is available. IE the coordinator updatees successfully.
        """
        return self.coordinator.last_update_success

    @property
    def device_state_attributes(self):
        """
        DOCSTRING: The last time the state of the zone/ sensor changed on Olarm's side.
        """
        self.last_changed = self.coordinator.bypass_state[self.index]["last_changed"]
        return {"last_tripped_time": self.last_changed}

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        LOGGER.debug("OlarmAlarm.device_info")
        return {
            "name": f"Olarm Sensors ({self.coordinator.entry.data[CONF_DEVICE_NAME]})",
            "manufacturer": f"Olarm Integration",
            "model": f"{self.coordinator.entry.data[CONF_DEVICE_MAKE]}",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
        }

    async def async_added_to_hass(self):
        """
        DOCSTRING: Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

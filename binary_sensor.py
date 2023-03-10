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

_LOGGER = logging.getLogger(__name__)


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

    _LOGGER.info("Setting up Olarm Sensors")

    # Looping through the sensors/zones for the panel. 
    index = 0
    for sensor in coordinator.sensor_data:
        # Creating a sensor for each zone on the alarm panel.
        sensor = OlarmSensor(
            coordinator=coordinator,
            sensor_name=sensor["name"],
            state=sensor["state"],
            index=index,
        )
        index = index + 1
        entities.append(sensor)

    index = 0
    # Looping through the panelstates for each of the panel. 
    for sensor in coordinator.panel_state:
        # Creating a sensor for each zone on the alarm panel.
        sensor = OlarmPanelState(
            coordinator=coordinator,
            sensor_name=sensor["name"],
            state=sensor["state"],
            index=index,
        )
        index = index + 1
        entities.append(sensor)

    _LOGGER.info("Adding Olarm Sensors")

    # Adding Olarm Sensors to Home Assistant
    async_add_entities(entities)

    _LOGGER.info("Added Olarm Sensors")


class OlarmSensor(BinarySensorEntity):
    index = 0

    def __init__(self, coordinator: OlarmCoordinator, sensor_name: str, state:str, index:int) -> None:
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

        # Motion Sensor if no match
        else:
            if self.is_on:
                return "mdi:motion-sensor"

            else:
                return "mdi:motion-sensor-off"

    @property
    def available(self):
        """
        DOCSTRING: Whether the entity is available. IE the coordinator updatees successfully.
        """
        return self.coordinator.last_update_success

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

    async def async_added_to_hass(self):
        """
        DOCSTRING: Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

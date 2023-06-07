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
from homeassistant.core import callback
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import LOGGER
from .const import CONF_DEVICE_FIRMWARE
from .const import DOMAIN
from .const import VERSION
from .const import OLARM_ZONE_TYPE_TO_HA
from .const import CONF_OLARM_DEVICES
from .exceptions import DictionaryKeyError
from datetime import datetime, timedelta


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add binary sensors for Olarm alarm sensor and panel states."""

    # Defining the list to store the instances of each alarm zone.
    entities = []
    for device in hass.data[DOMAIN]["devices"]:
        if not device["deviceName"] in entry.data[CONF_OLARM_DEVICES]:
            continue

        # Getting the instance of the DataCoordinator to update the data from Olarm.
        coordinator = hass.data[DOMAIN][device["deviceId"]]

        LOGGER.info(
            "Adding Olarm Zone Sensors for device (%s)", coordinator.olarm_device_name
        )

        # Looping through the sensors/zones for the panel.
        for sensor in coordinator.sensor_data:
            # Creating a sensor for each zone on the alarm panel.
            zone_sensor = OlarmSensor(
                coordinator=coordinator,
                sensor_name=sensor["name"],
                state=sensor["state"],
                index=sensor["zone_number"],
                last_changed=sensor["last_changed"],
                sensortype=sensor["type"],
            )

            entities.append(zone_sensor)

        LOGGER.info(
            "Added Olarm Zones Sensors for device (%s)", coordinator.olarm_device_name
        )

    async_add_entities(entities)
    LOGGER.info("Added Olarm Zone Sensors")
    return True


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
        sensortype: int,
    ) -> None:
        """
        Creates a sensor for each zone on the alarm panel.

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
        self.type = sensortype
        self.sensortypestring = "N/A"

        # Setting the type of Binarysensor
        # Motion Sensor
        if self.type == 0 or self.type == "":
            if "pir" in self.sensor_name.lower():
                self._attr_device_class = BinarySensorDeviceClass.MOTION

            # Window
            elif (
                "windows" in self.sensor_name.lower()
                or "wind" in self.sensor_name.lower()
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

        else:
            # Setting the deviceclass from the Olarm App config.
            try:
                self._attr_device_class = OLARM_ZONE_TYPE_TO_HA[self.type]

            except (DictionaryKeyError, KeyError):
                # Cannot find a type and thus reverting to motion sensor.
                self._attr_device_class = BinarySensorDeviceClass.MOTION

        if self._attr_device_class == BinarySensorDeviceClass.MOTION:
            self.sensortypestring = "Motion Sensor"

        elif self._attr_device_class == BinarySensorDeviceClass.POWER:
            self.sensortypestring = "Battery Powered"

        elif self._attr_device_class == BinarySensorDeviceClass.PROBLEM:
            self.sensortypestring = "Sensor Disabled"

        elif self._attr_device_class == BinarySensorDeviceClass.DOOR:
            self.sensortypestring = "Door Sensor"

        elif self._attr_device_class == BinarySensorDeviceClass.WINDOW:
            self.sensortypestring = "Window Sensor"

        elif self._attr_device_class == BinarySensorDeviceClass.SAFETY:
            self.sensortypestring = "Panic Button"

        elif self._attr_device_class == BinarySensorDeviceClass.PLUG:
            self.sensortypestring = "Device Power Plug Status"

    async def async_update(self) -> bool:
        """
        Updates the state of the zone sensor from the coordinator.

        Returns:
            boolean: Whether tthe update worked.
        """
        self._attr_is_on = self.coordinator.sensor_data[self.index]["state"] == "on"
        self.last_changed = self.coordinator.sensor_data[self.index]["last_changed"]
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """
        Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def unique_id(self):
        """
        The unique id for this entity sothat it can be managed from the ui.
        """
        return f"{self.coordinator.olarm_device_id}_{self.sensor_name}".replace(
            " ", "_"
        ).lower()

    @property
    def name(self):
        """
        The name of the zone from the Alarm Panel
        """
        name = []
        name1 = self.sensor_name.replace("_", " ")
        for item in str(name1).lower().split(" "):
            name.append(str(item).capitalize())
        return " ".join(name) + " (" + self.coordinator.olarm_device_name + ")"

    @property
    def is_on(self):
        """
        Whether the sensor/zone is active or not.
        """
        self._attr_is_on = self.coordinator.sensor_data[self.index]["state"] == "on"
        return self.coordinator.sensor_data[self.index]["state"] == "on"

    @property
    def icon(self):
        """
        Setting the icon of the entity depending on the state of the zone.
        """
        # Motion Sensor
        if "pir" in self.sensor_name.lower():
            if self.is_on:
                return "mdi:motion-sensor"

            else:
                return "mdi:motion-sensor-off"

        # Window Sensor
        elif (
            "windows" in self.sensor_name.lower() or "wind" in self.sensor_name.lower()
        ):
            if self.is_on:
                return "mdi:window-open"

            else:
                return "mdi:window-closed"

        # Door Sensor
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
        Whether the entity is available. IE the coordinator updatees successfully.
        """
        return (
            self.coordinator.last_update > datetime.now() - timedelta(minutes=2)
            and self.coordinator.device_online
        )

    @property
    def state_attributes(self) -> dict | None:
        """Return the state attributes."""
        self.last_changed = self.coordinator.sensor_data[self.index]["last_changed"]
        return {
            "last_tripped_time": self.last_changed,
            "zone_number": self.index + 1,
            "sensor_type": self.sensortypestring,
        }

    @property
    def should_poll(self):
        """Disable polling. Integration will notify Home Assistant on sensor value update."""
        return False

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.sensor_data[self.index]["state"] == "on"
        self.last_changed = self.coordinator.sensor_data[self.index]["last_changed"]
        self.async_write_ha_state()

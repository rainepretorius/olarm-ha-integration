"""Platform for binary sensor integration."""
from __future__ import annotations
from .coordinator import OlarmCoordinator
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import callback
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import LOGGER
from .const import DOMAIN
from .const import VERSION
from .const import CONF_OLARM_DEVICES
from datetime import datetime, timedelta
from .dataclasses.api_classes import APISensorResponse


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add binary sensors for Olarm alarm sensor and panel states."""

    # Defining the list to store the instances of each alarm zone.
    entities = []
    for device in hass.data[DOMAIN]["devices"]:
        if device.device_name not in entry.data[CONF_OLARM_DEVICES]:
            continue

        # Getting the instance of the DataCoordinator to update the data from Olarm.
        coordinator: OlarmCoordinator = hass.data[DOMAIN][device.device_id]

        LOGGER.info(
            "Adding Olarm Zone Sensors for device (%s)", coordinator.device.device_name
        )

        # Looping through the sensors/zones for the panel.
        for sensor in coordinator.sensor_data:
            # Creating a sensor for each zone on the alarm panel.
            zone_sensor = OlarmSensorEntity(coordinator=coordinator, data=sensor)

            entities.append(zone_sensor)

        LOGGER.info(
            "Added Olarm Zones Sensors for device (%s)", coordinator.device.device_name
        )

    async_add_entities(entities)
    LOGGER.info("Added Olarm Zone Sensors")
    return True


class OlarmSensorEntity(BinarySensorEntity):
    """
    This class represents a binary sensor entity in Home Assistant for an Olarm security zone. It defines the sensor's state and attributes, and provides methods for updating them.
    """

    index = 0
    _data: APISensorResponse
    _coordinator: OlarmCoordinator

    def __init__(self, coordinator: OlarmCoordinator, data: APISensorResponse) -> None:
        """
        Creates a sensor for each zone on the alarm panel.

        (params):
            coordinator(OlarmCoordinator): The Data Update Coordinator.
            sensor_name(str): The name of the Sensor on the alarm panel.
            state(str): The state of the sensor. (on or off)
            index(int): The index in the coordinator's data list of the sensor's state.
        """
        self._coordinator = coordinator
        self._data = data
        self._attr_device_class = self._data.zone_type

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
            await self._coordinator.async_update_sensor_data()

        self._data = self._coordinator.sensor_data[self.index]
        return self._coordinator.last_update_success

    async def async_added_to_hass(self):
        """
        Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def unique_id(self):
        """
        The unique id for this entity sothat it can be managed from the ui.
        """
        return f"{self._coordinator.device.device_id}_zone_{self._data.zone_number}".replace(
            " ", "_"
        ).lower()

    @property
    def name(self):
        """
        The name of the zone from the Alarm Panel
        """
        return self._data.name + " (" + self._coordinator.device.device_name + ")"

    @property
    def is_on(self):
        """
        Whether the sensor/zone is active or not.
        """
        self._attr_is_on = self._data.state == "on"
        return self._data.state == "on"

    @property
    def icon(self):
        """
        Setting the icon of the entity depending on the state of the zone.
        """
        return self._data.icon

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
    def extra_state_attributes(self) -> dict | None:
        """
        Return the state attributes of the zone sensor.
        """
        return {
            "last_tripped_time": self._data.last_changed,
            "zone_number": self._data.zone_number,
            "sensor_type": self._data.sensor_type,
        }

    @property
    def should_poll(self):
        """Disable polling. Integration will notify Home Assistant on sensor value update."""
        return False

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._data = self._coordinator.sensor_data[self.index]
        self.async_write_ha_state()

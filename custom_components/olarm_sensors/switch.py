from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime, timedelta
from .coordinator import OlarmCoordinator
from .const import LOGGER
from .const import CONF_DEVICE_FIRMWARE
from .const import DOMAIN
from .const import VERSION
from .const import CONF_OLARM_DEVICES
from .const import BypassZone


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add switches for Olarm alarm sensor zone bypassing."""

    # Defining the list to store the instances of each alarm zone bypass switch.
    entities = []

    for device in hass.data[DOMAIN]["devices"]:
        if not device['deviceName'] in entry.data[CONF_OLARM_DEVICES]:
            continue
        
        # Creating an instance of the DataCoordinator to update the data from Olarm.
        coordinator = hass.data[DOMAIN][device["deviceId"]]

        # Getting the first setup data from Olarm. eg: Panelstates, and all zones.
        if datetime.now() - coordinator.last_update > timedelta(seconds=60):
            await coordinator.async_get_data()

        LOGGER.info(
            "Setting up Olarm switches for device (%s)", coordinator.olarm_device_name
        )

        LOGGER.info(
            "Adding Olarm PGM switches for device (%s)", coordinator.olarm_device_name
        )
        # Looping through the pgm's for the panel.
        for sensor in coordinator.pgm_data:
            # Creating a sensor for each zone on the alarm panel.
            if sensor["pulse"]:
                continue

            pgm_switch = PGMSwitchEntity(
                coordinator=coordinator,
                name=sensor["name"],
                state=sensor["state"],
                enabled=sensor["enabled"],
                pgm_number=sensor["pgm_number"],
            )

            entities.append(pgm_switch)

        LOGGER.info(
            "Added Olarm PGM switches for device (%s)", coordinator.olarm_device_name
        )

        # Looping through the zoness for the panel.
        LOGGER.info(
            "Adding Olarm Bypass switches for device (%s)",
            coordinator.olarm_device_name,
        )
        for sensordata in coordinator.bypass_state:
            # Creating a bypass button for each zone on the alarm panel.
            bypass_switch = BypassSwitchEntity(
                coordinator=coordinator,
                sensor_name=sensordata["name"],
                state=sensordata["state"],
                index=sensordata["zone_number"],
                last_changed=sensordata["last_changed"],
            )

            entities.append(bypass_switch)

        LOGGER.info(
            "Added Olarm Bypass switches for device (%s)", coordinator.olarm_device_name
        )

    # Adding Olarm Switches to Home Assistant
    async_add_entities(entities)
    LOGGER.info("Added Olarm PGM and Bypass switches for all devices")
    return True


class BypassSwitchEntity(SwitchEntity):
    """Representation of a switch for bypassing a zone."""

    def __init__(
        self,
        coordinator: OlarmCoordinator,
        sensor_name,
        state,
        index=None,
        last_changed=None,
    ) -> None:
        """Initialize the bypass switch entity."""
        self.coordinator = coordinator
        self.sensor_name = sensor_name
        self._state = state
        self.index = index
        self.last_changed = last_changed

    async def async_turn_on(self, **kwargs):
        """Turn on the zone bypass."""
        ret = await self.coordinator.api.bypass_zone(BypassZone(self.index + 1))
        await self.coordinator.async_update_bypass_data()
        await self.async_write_ha_state()
        return ret

    async def async_turn_off(self, **kwargs):
        """Turn off the zone bypass."""
        ret = await self.coordinator.api.bypass_zone(BypassZone(self.index + 1))
        await self.coordinator.async_update_bypass_data()
        await self.async_write_ha_state()
        return ret

    async def async_added_to_hass(self):
        """
        Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Handle the update of the new/updated data."""
        if datetime.now() - self.coordinator.last_update > timedelta(seconds=60):
            # Only update the state from the api if it has been more than 60s since the last update.
            await self.coordinator.async_update_bypass_data()
        self._state = self.coordinator.bypass_state[self.index]["state"]

    @property
    def available(self):
        """
        Whether the entity is available. IE the coordinator updates successfully.
        """
        return (
            self.coordinator.last_update > datetime.now() - timedelta(minutes=2)
            and self.coordinator.device_online
        )

    @property
    def name(self):
        """
        The name of the zone from the Alarm Panel
        """
        name = []
        name1 = self.sensor_name.replace("_", " ")
        for item in str(name1).lower().split(" "):
            if item == "bypass":
                continue

            name.append(str(item).capitalize())

        return " ".join(name) + " Bypass (" + self.coordinator.olarm_device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.olarm_device_id + "_bypass_switch_" + self.sensor_name

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def icon(self):
        """
        Setting the icon of the entity depending on the state of the zone.
        """
        # Zone Bypass
        if self.is_on:
            return "mdi:shield-home-outline"

        else:
            return "mdi:shield-home"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.bypass_state[self.index]["state"] == "on"

    @property
    def device_state_attributes(self):
        """
        The last time the state of the zone/ sensor changed on Olarm's side.
        """
        self.last_changed = self.coordinator.bypass_state[self.index]["last_changed"]
        return {"last_tripped_time": self.last_changed, "zone_number": self.index + 1}

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
        self._state = self.coordinator.bypass_state[self.index]["state"]
        self.async_write_ha_state()


class PGMSwitchEntity(SwitchEntity):
    """Representation of a custom switch entity."""

    def __init__(
        self,
        coordinator: OlarmCoordinator,
        name,
        state,
        enabled=True,
        pgm_number=None,
        pulse=False,
    ) -> None:
        """Initialize the custom switch entity."""
        self.coordinator = coordinator
        self.sensor_name = name
        self._state = state
        self.button_enabled = enabled
        self._pgm_number = pgm_number
        self.post_data = {}

    async def async_turn_on(self, **kwargs):
        """Turn the custom switch entity off."""
        self.post_data = {"actionCmd": "pgm-close", "actionNum": self._pgm_number}

        ret = await self.coordinator.api.update_pgm(self.post_data)
        await self.coordinator.async_update_pgm_ukey_data()

        self._state = self.coordinator.pgm_data[self._pgm_number - 1]
        self.async_write_ha_state()

        return ret

    async def async_turn_off(self, **kwargs):
        """Turn the custom switch entity off."""
        self.post_data = {"actionCmd": "pgm-open", "actionNum": self._pgm_number}

        ret = await self.coordinator.api.update_pgm(self.post_data)
        await self.coordinator.async_update_pgm_ukey_data()

        self._state = self.coordinator.pgm_data[self._pgm_number - 1]
        self.async_write_ha_state()

        return ret

    async def async_added_to_hass(self):
        """Run when the entity is added to Home Assistant."""
        await super().async_added_to_hass()

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
    def name(self):
        """Return the name of the custom switch entity."""
        return self.sensor_name + " (" + self.coordinator.olarm_device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.olarm_device_id + "_pgm_switch_" + self.sensor_name

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the custom switch entity."""
        return "mdi:toggle-switch"

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

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_SCAN_INTERVAL
from datetime import datetime, timedelta
from .coordinator import OlarmCoordinator
from .const import LOGGER
from .const import DOMAIN
from .const import VERSION
from .const import CONF_OLARM_DEVICES
from .dataclasses.api_classes import APIBypassResponse, APIPGMResponse
import random
import asyncio


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add switches for Olarm alarm sensor zone bypassing."""

    # Defining the list to store the instances of each alarm zone bypass switch.
    entities = []

    for device in hass.data[DOMAIN]["devices"]:
        if device.device_name not in entry.data[CONF_OLARM_DEVICES]:
            continue

        # Getting the instance of the DataCoordinator to update the data from Olarm.
        coordinator: OlarmCoordinator = hass.data[DOMAIN][device.device_id]

        # Getting the first setup data from Olarm. eg: Panelstates, and all zones.

        LOGGER.info("Setting up Olarm switches for device (%s)", device.device_name)

        LOGGER.info("Adding Olarm PGM switches for device (%s)", device.device_name)
        # Looping through the pgm's for the panel.
        for sensor in coordinator.pgm_data:
            # Creating a sensor for each zone on the alarm panel.
            if sensor.pulse:
                continue

            entities.append(PGMSwitchEntity(coordinator=coordinator, data=sensor))

        LOGGER.info(
            "Added Olarm PGM switches for device (%s)", coordinator.device.device_name
        )

        # Looping through the zones for the panel.
        LOGGER.info(
            "Adding Olarm Bypass switches for device (%s)",
            coordinator.device.device_name,
        )

        for sensordata in coordinator.bypass_state:
            # Creating a bypass button for each zone on the alarm panel.
            entities.append(
                BypassSwitchEntity(coordinator=coordinator, data=sensordata)
            )

        LOGGER.info(
            "Added Olarm Bypass switches for device (%s)",
            coordinator.device.device_name,
        )

    # Adding Olarm Switches to Home Assistant
    async_add_entities(entities)
    LOGGER.info("Added Olarm PGM and Bypass switches for all devices")
    return True


class BypassSwitchEntity(SwitchEntity):
    """Representation of a switch for bypassing a zone."""

    _data: APIBypassResponse
    _coordinator: OlarmCoordinator

    def __init__(self, coordinator: OlarmCoordinator, data: APIBypassResponse) -> None:
        """Initialize the bypass switch entity."""
        self._coordinator = coordinator
        self._data = data

    async def async_turn_on(self, **kwargs):
        """Turn on the zone bypass."""
        await asyncio.sleep(random.uniform(1.5, 3))
        ret = await self._coordinator.api.bypass_zone(self._data.bypass_zone)
        await asyncio.sleep(random.uniform(1.5, 3))
        await self._coordinator.async_update_bypass_data()
        self.async_write_ha_state()
        return ret

    async def async_turn_off(self, **kwargs):
        """Turn off the zone bypass."""
        await asyncio.sleep(random.uniform(1.5, 3))
        ret = await self._coordinator.api.bypass_zone(self._data.bypass_zone)
        await asyncio.sleep(random.uniform(1.5, 3))
        await self._coordinator.async_update_bypass_data()
        self.async_write_ha_state()
        return ret

    async def async_added_to_hass(self):
        """
        Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Handle the update of the new/updated data."""
        if datetime.now() - self._coordinator.last_update > timedelta(
            seconds=(1.5 * self._coordinator.entry.data[CONF_SCAN_INTERVAL])
        ):
            # Only update the state from the api if it has been more than 1.5 times the scan interval since the last update.
            await self._coordinator.async_update_bypass_data()

        self._data = self._coordinator.bypass_state[self._data.index]

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
    def name(self):
        """
        The name of the zone from the Alarm Panel
        """
        return (
            self._data.name + " Bypass (" + self._coordinator.device.device_name + ")"
        )

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return (
            self._coordinator.device.device_id
            + "_bypass_switch_"
            + str(self._data.zone_number)
        )

    @property
    def should_poll(self):
        """Disable polling. Integration will notify Home Assistant on sensor value update."""
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
        return self._coordinator.bypass_state[self._data.index].state == "on"

    @property
    def device_state_attributes(self):
        """
        The last time the state of the zone/ sensor changed on Olarm's side.
        """
        return {
            "last_tripped_time": self._data.last_changed,
            "zone_number": self._data.zone_number,
        }

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
        self._data = self._coordinator.bypass_state[self._data.index]
        self.async_write_ha_state()


class PGMSwitchEntity(SwitchEntity):
    """Representation of a custom switch entity."""

    _data: APIPGMResponse
    _post_data: dict

    def __init__(self, coordinator: OlarmCoordinator, data: APIPGMResponse) -> None:
        """Initialize the custom switch entity."""
        self._coordinator = coordinator
        self._data = data
        self._post_data = {}

    async def async_turn_on(self, **kwargs):
        """Turn the custom switch entity off."""
        self._post_data = {"actionCmd": "pgm-close", "actionNum": self._data.pgm_number}

        ret = await self._coordinator.api.update_pgm(self._post_data)
        await self._coordinator.async_update_pgm_ukey_data()

        self._data = self._coordinator.pgm_data[self._data.index]
        self.async_write_ha_state()

        return ret

    async def async_turn_off(self, **kwargs):
        """Turn the custom switch entity off."""
        self._post_data = {"actionCmd": "pgm-open", "actionNum": self._data.pgm_number}

        ret = await self._coordinator.api.update_pgm(self._post_data)
        await self._coordinator.async_update_pgm_ukey_data()

        self._data = self._coordinator.pgm_data[self._data.index]
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
            self._coordinator.last_update > datetime.now() - timedelta(minutes=2)
            and not self._coordinator.device.is_errored
            and self._coordinator.device.is_online
        )

    @property
    def name(self):
        """Return the name of the custom switch entity."""
        return self._data.name + " (" + self._coordinator.device.device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return (
            self._coordinator.device.device_id
            + "_pgm_switch_"
            + str(self._data.pgm_number)
        )

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._data.state

    @property
    def icon(self):
        """Return the icon of the custom switch entity."""
        return "mdi:toggle-switch"

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
        self._data = self._coordinator.pgm_data[self._data.index]
        self.async_write_ha_state()

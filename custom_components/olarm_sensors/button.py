"""Module to create and maintain binary / zone sensors for the alarm panel."""
from homeassistant.helpers.entity import Entity
from .coordinator import OlarmCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import callback
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import CONF_DEVICE_FIRMWARE
from .const import LOGGER
from .const import DOMAIN
from .const import VERSION
from .const import CONF_OLARM_DEVICES
from datetime import datetime, timedelta


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add Buttons for Olarm alarm sensor and panel states."""

    # Defining the list to store the instances of each alarm zone.
    entities = []

    for device in hass.data[DOMAIN]["devices"]:
        if not device["deviceName"] in entry.data[CONF_OLARM_DEVICES]:
            continue
        # Creating an instance of the DataCoordinator to update the data from Olarm.
        coordinator = hass.data[DOMAIN][device["deviceId"]]

        # Getting the first setup data from Olarm. eg: Panelstates, and all zones.
        if datetime.now() - coordinator.last_update > timedelta(
            seconds=(1.5 * entry.data[CONF_SCAN_INTERVAL])
        ):
            LOGGER.warning("Updating data Button")
            LOGGER.warning(datetime.now() - coordinator.last_update)
            LOGGER.warning("Button Done")
            await coordinator.async_get_data()

        LOGGER.info(
            "Setting up Olarm buttons for device (%s)", coordinator.olarm_device_name
        )

        LOGGER.info(
            "Adding Olarm PGM buttons for device (%s)", coordinator.olarm_device_name
        )
        # Looping through the pgm's for the panel.
        for sensor in coordinator.pgm_data:
            # Creating a sensor for each zone on the alarm panel.
            if not sensor["pulse"]:
                continue

            pgm_button = PGMButtonEntity(
                coordinator=coordinator,
                name=sensor["name"],
                state=sensor["state"],
                enabled=sensor["enabled"],
                pgm_number=sensor["pgm_number"],
            )

            entities.append(pgm_button)

        LOGGER.info(
            "Added Olarm PGM buttons for device (%s)", coordinator.olarm_device_name
        )

        LOGGER.info(
            "Adding Olarm Utility key buttons for device (%s)",
            coordinator.olarm_device_name,
        )
        # Looping through the ukeys's for the panel.
        for sensor1 in coordinator.ukey_data:
            # Creating a sensor for each zone on the alarm panel.
            ukey_button = UKeyButtonEntity(
                coordinator=coordinator,
                name=sensor1["name"],
                state=sensor1["state"],
                ukey_number=sensor1["ukey_number"],
            )

            entities.append(ukey_button)

        LOGGER.info(
            "Added Olarm Utility key buttons for device (%s)",
            coordinator.olarm_device_name,
        )

        LOGGER.info(
            "Adding Olarm data refresh button for device (%s)",
            coordinator.olarm_device_name,
        )

        entities.append(RefreshButtonEntity(coordinator))

        LOGGER.info(
            "Added Olarm data refresh button for device (%s)",
            coordinator.olarm_device_name,
        )

    async_add_entities(entities)
    LOGGER.info("Added Olarm pgm and utility key buttons")
    return True


class PGMButtonEntity(Entity):
    """Representation of a custom button entity."""

    def __init__(
        self,
        coordinator: OlarmCoordinator,
        name,
        state,
        enabled=True,
        pgm_number=None,
    ) -> None:
        """Initialize the custom button entity."""
        self.coordinator = coordinator
        self.sensor_name = name
        self._state = state
        self.button_enabled = enabled
        self._pgm_number = pgm_number
        self.post_data = {}

        return None

    async def async_added_to_hass(self):
        """Run when the entity is added to Home Assistant."""
        await super().async_added_to_hass()

    async def async_press(self):
        """
        Handle the button press event.
        """
        self.post_data = {"actionCmd": "pgm-pulse", "actionNum": self._pgm_number}
        self._state = await self.coordinator.api.update_pgm(self.post_data)
        self.async_write_ha_state()
        return self._state

    async def _async_press_action(self):
        """
        Handle the button press event.
        """
        self.post_data = {"actionCmd": "pgm-pulse", "actionNum": self._pgm_number}
        self._state = await self.coordinator.api.update_pgm(self.post_data)
        self.async_write_ha_state()
        return self._state

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
        """Return the name of the custom button entity."""
        return self.sensor_name + " (" + self.coordinator.olarm_device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.olarm_device_id + "_pgm_" + self.sensor_name

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:gesture-tap-button"

    @property
    def state(self):
        """Returns the state of the PGM"""
        if self.button_enabled and self._state:
            return "on"

        elif self._state:
            return "on"

        elif not self.button_enabled:
            return "disabled"

        else:
            return "off"

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


class UKeyButtonEntity(Entity):
    """Representation of a custom button entity."""

    def __init__(
        self, coordinator: OlarmCoordinator, name, state, ukey_number=None
    ) -> None:
        """Initialize the Utility key button entity."""
        self.coordinator = coordinator
        self.sensor_name = name
        self._state = state
        self._ukey_number = ukey_number
        self.post_data = {}

        return None

    async def async_update(self):
        if datetime.now() - self.coordinator.last_update > timedelta(
            seconds=(1.5 * self.coordinator.entry.data[CONF_SCAN_INTERVAL])
        ):
            # Only update the state from the api if it has been more than 60s since the last update.
            await self.coordinator.async_update_data()
        self._state = self.coordinator.ukey_data[self._ukey_number - 1]

    async def async_press(self):
        """Turn the custom button entity on."""
        self.post_data = {"actionCmd": "ukey-activate", "actionNum": self._ukey_number}

        ret = await self.coordinator.api.update_ukey(self.post_data)
        await self.async_update()
        return ret

    async def _async_press_action(self):
        """Turn the custom button entity on."""
        self.post_data = {"actionCmd": "ukey-activate", "actionNum": self._ukey_number}

        ret = await self.coordinator.api.update_ukey(self.post_data)

        await self.async_update()

        return ret

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
        """Return the name of the custom button entity."""
        return self.sensor_name + " (" + self.coordinator.olarm_device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.olarm_device_id + "_ukey_" + self.sensor_name

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:gesture-tap-button"

    @property
    def state(self):
        """Return the state of the Utility key"""
        if self._state:
            return "on"

        else:
            return "off"

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
        self._state = self.coordinator.ukey_data[self._ukey_number - 1]
        self.async_write_ha_state()


class RefreshButtonEntity(Entity):
    """Representation of a button to press for refreshing the data."""

    def __init__(
        self,
        coordinator: OlarmCoordinator,
    ) -> None:
        """Initialize the bypass button entity."""
        self.coordinator = coordinator

        return None

    async def async_press(self):
        """Frefresh the data."""
        return await self._async_press_action()

    async def _async_press_action(self):
        """Handle the button press event for refreshing the data."""
        ret = await self.coordinator.update_data()
        return ret

    async def async_added_to_hass(self):
        """
        Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self):
        """
        Whether the entity is available. IE the coordinator updatees successfully.
        """
        return True

    @property
    def name(self):
        """
        The name of the zone from the Alarm Panel
        """
        return f"({self.coordinator.olarm_device_name}) Refresh"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.olarm_device_id + "_refresh_button"

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:shield-refresh"

    @property
    def device_state_attributes(self):
        """
        The last time the state of the zone/ sensor changed on Olarm's side.
        """
        return {"last_update_time": self.coordinator.last_update}

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

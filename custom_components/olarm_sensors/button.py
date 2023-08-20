"""Module to create and maintain binary / zone sensors for the alarm panel."""
from homeassistant.helpers.entity import Entity
from .coordinator import OlarmCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import callback
from .dataclasses.api_classes import APIPGMResponse, APIUkeyResponse
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
        if device.device_name not in entry.data[CONF_OLARM_DEVICES]:
            continue

        # Getting the instance of the DataCoordinator to update the data from Olarm.
        coordinator: OlarmCoordinator = hass.data[DOMAIN][device.device_id]

        LOGGER.info(
            "Setting up Olarm buttons for device (%s)", coordinator.device.device_name
        )

        LOGGER.info(
            "Adding Olarm PGM buttons for device (%s)", coordinator.device.device_name
        )
        # Looping through the pgm's for the panel.
        for sensor in coordinator.pgm_data:
            # Creating a button for each pulse PGM on the alarm panel.
            if not sensor.pulse:
                continue

            pgm_button = PGMButtonEntity(coordinator=coordinator, data=sensor)

            entities.append(pgm_button)

        LOGGER.info(
            "Added Olarm PGM buttons for device (%s)", coordinator.device.device_name
        )

        LOGGER.info(
            "Adding Olarm Utility key buttons for device (%s)",
            coordinator.device.device_name,
        )
        # Looping through the ukeys's for the panel.
        for sensor1 in coordinator.ukey_data:
            # Creating a button for each Utility Key on the alarm panel.
            ukey_button = UKeyButtonEntity(coordinator=coordinator, data=sensor1)

            entities.append(ukey_button)

        LOGGER.info(
            "Added Olarm Utility key buttons for device (%s)",
            coordinator.device.device_name,
        )

        LOGGER.info(
            "Adding Olarm data refresh button for device (%s)",
            coordinator.device.device_name,
        )

        entities.append(RefreshButtonEntity(coordinator))

        LOGGER.info(
            "Added Olarm data refresh button for device (%s)",
            coordinator.device.device_name,
        )

        coordinator.device.set_ukey_buttons(entities)

    async_add_entities(entities)
    LOGGER.info("Added Olarm pgm and utility key buttons")
    return True


class PGMButtonEntity(Entity):
    """Representation of a custom button entity."""

    _data: APIPGMResponse
    _post_data: dict
    _state: bool = False
    _coordinator: OlarmCoordinator

    def __init__(self, coordinator: OlarmCoordinator, data: APIPGMResponse) -> None:
        """Initialize the custom button entity."""
        self._coordinator = coordinator
        self._data = data
        self._post_data = {"actionCmd": "pgm-pulse", "actionNum": self._data.pgm_number}
        return None

    async def async_added_to_hass(self):
        """Run when the entity is added to Home Assistant."""
        await super().async_added_to_hass()

    async def async_press(self):
        """
        Handle the button press event.
        """
        self._state = await self._coordinator.api.update_pgm(self._post_data)
        self.async_write_ha_state()
        return self._state

    async def _async_press_action(self):
        """
        Handle the button press event.
        """
        self._state = await self._coordinator.api.update_pgm(self._post_data)
        self.async_write_ha_state()
        return self._state

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
        """Return the name of the custom button entity."""
        return self._data.name + " (" + self._coordinator.device.device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self._coordinator.device.device_id + "_pgm_" + str(self._data.pgm_number)

    @property
    def should_poll(self):
        """Disable polling. Integration will notify Home Assistant on sensor value update."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:gesture-tap-button"

    @property
    def state(self):
        """Returns the state of the PGM"""
        if self._data.enabled:
            return "enabled"

        else:
            return "off"

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


class UKeyButtonEntity(Entity):
    """Representation of a custom button entity."""

    _coordinator: OlarmCoordinator
    _data: APIUkeyResponse
    _state: bool
    _post_data: dict

    def __init__(self, coordinator: OlarmCoordinator, data: APIUkeyResponse) -> None:
        """Initialize the Utility key button entity."""
        self._coordinator = coordinator
        self._data = data
        self._post_data = {"actionCmd": "ukey-activate", "actionNum": self._data.index}
        return None

    async def async_update(self):
        """
        Updates the state of the zone sensor from the coordinator.

        Returns:
            boolean: Whether the update worked.
        """
        self._state = self._coordinator.ukey_data[self._data.index]

    async def async_press(self):
        """Turn the custom button entity on."""

        ret = await self._coordinator.api.update_ukey(self._post_data)
        await self.async_update()
        return ret

    async def _async_press_action(self):
        """Turn the custom button entity on."""
        ret = await self._coordinator.api.update_ukey(self._post_data)

        await self.async_update()

        return ret

    @property
    def available(self):
        """
        Whether the entity is available. IE the coordinator updatees successfully.
        """
        return (
            self._coordinator.last_update > datetime.now() - timedelta(minutes=2)
            and self._coordinator.device.is_online
        )

    @property
    def name(self):
        """Return the name of the custom button entity."""
        return self._data.name + " (" + self._coordinator.device.device_name + ")"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return (
            self._coordinator.device.device_id + "_ukey_" + str(self._data.ukey_number)
        )

    @property
    def should_poll(self):
        """Disable polling. Integration will notify Home Assistant on sensor value update."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:gesture-tap-button"

    @property
    def state(self):
        """Return the state of the Utility key"""
        if self._data.state:
            return "on"

        else:
            return "off"

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
        self._state = self._coordinator.ukey_data[self._data.index]
        self.async_write_ha_state()


class RefreshButtonEntity(Entity):
    """Representation of a button to press for refreshing the data."""

    _coordinator: OlarmCoordinator

    def __init__(
        self,
        coordinator: OlarmCoordinator,
    ) -> None:
        """Initialize the bypass button entity."""
        self._coordinator = coordinator
        return None

    async def async_press(self):
        """Frefresh the data."""
        return await self._async_press_action()

    async def _async_press_action(self):
        """Handle the button press event for refreshing the data."""
        ret = await self._coordinator.update_data()
        return ret

    async def async_added_to_hass(self):
        """
        Writing the state of the sensor to Home Assistant
        """
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
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
        return f"({self._coordinator.device.device_name}) Refresh"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self._coordinator.device.device_id + "_refresh_button"

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
        return {"last_update_time": self._coordinator.last_update}

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

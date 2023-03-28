from homeassistant.helpers.entity import Entity
from .coordinator import OlarmCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_DEVICE_ID
from .const import CONF_DEVICE_NAME
from .const import CONF_DEVICE_MAKE
from .const import LOGGER
from .const import DOMAIN
from .const import VERSION


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

    # Looping through the pgm's for the panel.
    for sensor in coordinator.pgm_data:
        if not sensor["enabled"]:
            continue
        # Creating a sensor for each zone on the alarm panel.
        sensor = PGMButtonEntity(
            coordinator=coordinator,
            name=sensor["name"],
            state=sensor["state"],
            enabled=sensor["enabled"],
            pgm_number=sensor["pgm_number"],
            pulse=sensor["pulse"],
        )
        entities.append(sensor)

    # Looping through the ukeys's for the panel.
    for sensor in coordinator.ukey_data:
        # Creating a sensor for each zone on the alarm panel.
        sensor = UKeyButtonEntity(
            coordinator=coordinator,
            name=sensor["name"],
            state=sensor["state"],
            ukey_number=sensor["ukey_number"],
        )
        entities.append(sensor)

    LOGGER.info("Adding Olarm PGM's and Ukeys")

    # Adding Olarm Sensors to Home Assistant
    async_add_entities(entities)

    LOGGER.info("Added Olarm PGM's and Ukeys")


class PGMButtonEntity(Entity):
    """Representation of a custom button entity."""

    def __init__(
        self,
        coordinator: OlarmCoordinator,
        name,
        state,
        enabled=False,
        pgm_number=None,
        pulse=False,
    ) -> None:
        """Initialize the custom button entity."""
        self.coordinator = coordinator
        self.sensor_name = name
        self._state = state
        self._enabled = True  # enabled
        self._pgm_number = (pgm_number,)
        self._pulse = pulse
        self.post_data = {}

        return None

    @property
    def name(self):
        """Return the name of the custom button entity."""
        return self.sensor_name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.entry.data[CONF_DEVICE_ID] + "_pgm_" + self.sensor_name

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:gesture-tap-button"

    async def async_turn_on(self, **kwargs):
        """Turn the custom button entity on."""
        if self._enabled and self._pulse:
            self.post_data = {"actionCmd": "pgm-pulse", "actionNum": self._pgm_number}

        elif self._enabled:
            self.post_data = {"actionCmd": "pgm-close", "actionNum": self._pgm_number}

        else:
            return False

        ret = await self.coordinator.api.update_pgm(self.post_data)
        await self.coordinator.async_update_data()

        self._state = self.coordinator.pgm_data[self._pgm_number - 1]
        self.async_schedule_update_ha_state()

        return ret

    async def async_turn_off(self, **kwargs):
        """Turn the custom button entity on."""
        if self._enabled and self._pulse:
            self.post_data = {"actionCmd": "pgm-pulse", "actionNum": self._pgm_number}

        elif self._enabled:
            self.post_data = {"actionCmd": "pgm-open", "actionNum": self._pgm_number}

        else:
            return False

        ret = await self.coordinator.api.update_pgm(self.post_data)
        await self.coordinator.async_update_data()

        self._state = self.coordinator.pgm_data[self._pgm_number - 1]
        self.async_schedule_update_ha_state()

        return ret

    async def async_added_to_hass(self):
        """Run when the entity is added to Home Assistant."""
        await super().async_added_to_hass()

    async def async_press(self):
        if self._state:
            return await self.async_turn_off()

        else:
            return await self.async_turn_on()

    @property
    def state(self):
        if self._enabled and self._state:
            return "on"

        elif self._state:
            return "on"

        elif not self._enabled:
            return "disabled"

        else:
            return "off"

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        return {
            "name": f"Olarm Sensors ({self.coordinator.entry.data[CONF_DEVICE_NAME]})",
            "manufacturer": "Olarm Integration",
            "model": f"{self.coordinator.entry.data[CONF_DEVICE_MAKE]}",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
            "sw_version": VERSION,
            "hw_version": "Not Implemented",
        }


class UKeyButtonEntity(Entity):
    """Representation of a custom button entity."""

    def __init__(
        self, coordinator: OlarmCoordinator, name, state, ukey_number=None
    ) -> None:
        """Initialize the custom button entity."""
        self.coordinator = coordinator
        self.sensor_name = name
        self._state = state
        self._ukey_number = ukey_number
        self.post_data = {}

        return None

    @property
    def name(self):
        """Return the name of the custom button entity."""
        return self.sensor_name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.entry.data[CONF_DEVICE_ID] + "_ukey_" + self.sensor_name

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def icon(self):
        """Return the icon of the custom button entity."""
        return "mdi:gesture-tap-button"

    async def async_press(self):
        """Turn the custom button entity on."""
        self.post_data = {"actionCmd": "ukey-activate", "actionNum": self._ukey_number}

        ret = await self.coordinator.api.update_ukey(self.post_data)
        await self.coordinator.async_update_data()

        self._state = self.coordinator.ukey_data[self._ukey_number - 1]
        self.async_schedule_update_ha_state()

        return ret

    @property
    def state(self):
        if self._state:
            return "on"

        else:
            return "off"

    @property
    def device_info(self) -> dict:
        """Return device information about this entity."""
        return {
            "name": f"Olarm Sensors ({self.coordinator.entry.data[CONF_DEVICE_NAME]})",
            "manufacturer": "Olarm Integration",
            "model": f"{self.coordinator.entry.data[CONF_DEVICE_MAKE]}",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_DEVICE_ID])},
            "sw_version": VERSION,
            "hw_version": "Not Implemented",
        }

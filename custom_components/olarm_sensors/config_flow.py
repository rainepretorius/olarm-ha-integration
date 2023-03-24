import logging
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID, CONF_SCAN_INTERVAL
from .olarm_api import OlarmApi
from .const import (
    CONF_DEVICE_NAME,
    CONF_DEVICE_MAKE,
    CONF_DEVICE_MODEL,
    AuthenticationError,
    DOMAIN,
    DeviceIDError,
)
from .exceptions import APIForbiddenError, APINotFoundError

_LOGGER = logging.getLogger(__name__)


class OlarmSensorsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Olarm Sensors."""

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
            errors=errors or {},
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is None:
            return await self._show_setup_form()

        # If user_input is not None, the user has submitted the form
        if user_input is not None:
            # Validate the user input
            errors = {}
            if not user_input[CONF_API_KEY]:
                errors[CONF_API_KEY] = "API key is required."
            if not user_input[CONF_DEVICE_ID]:
                errors[CONF_DEVICE_ID] = "Device ID is required."
            if not user_input[CONF_SCAN_INTERVAL]:
                errors[CONF_SCAN_INTERVAL] = "Scan interval is required."
            elif user_input[CONF_SCAN_INTERVAL] < 5:
                errors[CONF_SCAN_INTERVAL] = "Scan interval must be at least 5 seconds."

            api_key = user_input[CONF_API_KEY]
            device_id = user_input[CONF_DEVICE_ID]
            scan_interval = user_input[CONF_SCAN_INTERVAL]

            try:
                api = OlarmApi(device_id, api_key)
                json = await api.check_credentials()

            except APIForbiddenError:
                _LOGGER.warning(
                    "User entered invalid credentials or API access is not enabled."
                )
                errors[AuthenticationError] = "Invalid credentials!"

            except APINotFoundError:
                _LOGGER.warning("User entered invalid device_id.")
                errors[DeviceIDError] = "Invalid credentials!"

            # If there are errors, show the setup form with error messages
            if errors:
                return await self._show_setup_form(errors=errors)

            # If there are no errors, create a config entry and return
            device_name = json["deviceName"]
            device_make = str(json["deviceAlarmType"]).capitalize()
            device_model = json["deviceSerial"]

            # Saving the device
            return self.async_create_entry(
                title=f"Olarm Sensors ({device_name})",
                data={
                    CONF_API_KEY: api_key,
                    CONF_DEVICE_ID: device_id,
                    CONF_SCAN_INTERVAL: scan_interval,
                    CONF_DEVICE_NAME: device_name,
                    CONF_DEVICE_MAKE: device_make,
                    CONF_DEVICE_MODEL: device_model,
                },
            )

        # If user_input is None, this is the first step
        return self.async_show_form(step_id="user", data_schema=self._get_schema())

    def _get_schema(self):
        """Return the data schema for the user form."""
        return vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY,
                    description={
                        "suggested_value": "Your Olarm API key",
                        "description": "API key for accessing the Olarm API. You can find your API key here: https://user.olarm.co/#/api",
                    },
                ): cv.string,
                vol.Required(
                    CONF_DEVICE_ID,
                    description={
                        "suggested_value": "Your Olarm device ID",
                        "description": "ID of the Olarm device to be monitored. You can find your device ID here: https://apiv4.olarm.co/api/v4/devices/?accessToken=Your_API_KEY",
                    },
                ): cv.string,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    description={
                        "suggested_value": 5,
                        "description": "Interval, in seconds, at which to scan the Olarm device for sensor data. Minimum value is 1 second.",
                    },
                ): vol.All(vol.Coerce(int), vol.Range(min=5)),
            }
        )

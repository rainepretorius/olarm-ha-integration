"""Module used for a GUI to configure the device"""
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from .olarm_api import OlarmSetupApi
from .const import (
    AuthenticationError,
    DOMAIN,
    DeviceIDError,
    CONF_DEVICE_FIRMWARE,
    CONF_ALARM_CODE,
    LOGGER,
    OLARM_DEVICES,
    CONF_OLARM_DEVICES,
    OLARM_DEVICE_AMOUNT,
    OLARM_DEVICE_NAMES,
)
from .exceptions import APIForbiddenError, APINotFoundError
from typing import Any


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

            if not user_input[CONF_SCAN_INTERVAL]:
                errors[CONF_SCAN_INTERVAL] = "Scan interval is required."

            elif user_input[CONF_SCAN_INTERVAL] < 1:
                errors[CONF_SCAN_INTERVAL] = "Scan interval must be at least 1 second."

            api_key = user_input[CONF_API_KEY]
            scan_interval = user_input[CONF_SCAN_INTERVAL]

            if user_input[CONF_ALARM_CODE] == "1234567890":
                alarm_code = None

            else:
                alarm_code = user_input[CONF_ALARM_CODE]

            try:
                api = OlarmSetupApi(api_key)
                json = await api.get_olarm_devices()

            except APIForbiddenError:
                LOGGER.warning(
                    "User entered invalid credentials or API access is not enabled!"
                )
                errors[AuthenticationError] = "Invalid credentials!"

            # If there are errors, show the setup form with error messages
            if errors:
                return await self._show_setup_form(errors=errors)

            # If there are no errors, create a config entry and return
            firmware = json[0]["deviceFirmware"]

            setup_devices = [dev["deviceName"] for dev in json]

            # Saving the device
            return self.async_create_entry(
                title="Olarm Sensors",
                data={
                    CONF_API_KEY: api_key,
                    CONF_SCAN_INTERVAL: scan_interval,
                    CONF_DEVICE_FIRMWARE: firmware,
                    CONF_ALARM_CODE: alarm_code,
                    CONF_OLARM_DEVICES: setup_devices,
                    OLARM_DEVICES: json,
                    OLARM_DEVICE_AMOUNT: len(json),
                    OLARM_DEVICE_NAMES: setup_devices,
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
                    msg="The api key for your account.",
                    description={
                        "suggested_value": "Your Olarm API key",
                        "description": "API key for accessing the Olarm API. You can find your API key here: https://user.olarm.co/#/api",
                    },
                ): cv.string,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    msg="The update interval in seconds.",
                    description={
                        "suggested_value": 5,
                        "description": "Interval, in seconds, at which to scan the Olarm device for sensor data. Minimum value is 1 second.",
                    },
                ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Optional(
                    CONF_ALARM_CODE,
                    msg="The code for alarm actions. Leave default for no code.",
                    description={
                        "suggested_value": "1234567890",
                        "description": "Alarm Panel Code",
                    },
                ): cv.string,
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OlarmOptionsFlow(config_entry)


class OlarmOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    def _get_schema(self):
        """Return the data schema for the user form."""
        if self.config_entry.data[CONF_ALARM_CODE] is None:
            alarm_code = "1234567890"

        else:
            alarm_code = self.config_entry.data[CONF_ALARM_CODE]

        return vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY,
                    msg="The api key for your account.",
                    description={
                        "suggested_value": self.config_entry.data[CONF_API_KEY],
                        "description": "API key for accessing the Olarm API. You can find your API key here: https://user.olarm.co/#/api",
                    },
                ): cv.string,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    msg="The update interval in seconds.",
                    description={
                        "suggested_value": self.config_entry.data[CONF_SCAN_INTERVAL],
                        "description": "Interval, in seconds, at which to scan the Olarm device for sensor data. Minimum value is 1 second.",
                    },
                ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Optional(
                    CONF_ALARM_CODE,
                    msg="The code for alarm actions. Leave default for no code.",
                    description={
                        "suggested_value": alarm_code,
                        "description": "Alarm Panel Code",
                    },
                ): cv.string,
                vol.Optional(
                    CONF_OLARM_DEVICES,
                    msg="The Olarm devices to load into this Home Assistant instance.",
                    description={
                        "description": "The Olarm devices to load into this Home Assistant instance.",
                    },
                ): cv.multi_select(self.config_entry.data[OLARM_DEVICE_NAMES]),
            }
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            if user_input[CONF_ALARM_CODE] == "1234567890":
                alarm_code = None

            else:
                alarm_code = user_input[CONF_ALARM_CODE]

            new = {**self.config_entry.data}

            new[CONF_ALARM_CODE] = alarm_code
            new[OLARM_DEVICE_AMOUNT] = len(self.config_entry.data[OLARM_DEVICE_NAMES])

            return self.async_create_entry(title="Olarm Sensors", data=new)

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_schema(),
        )

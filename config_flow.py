import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_DEVICE_ID, CONF_SCAN_INTERVAL
from . import const

_LOGGER = logging.getLogger(__name__)


class OlarmSensorsConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
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
            if len(user_input[CONF_API_KEY]) < 1:
                errors[CONF_API_KEY] = "api_key is required."

            if len(user_input[CONF_DEVICE_ID]) < 1:
                errors[CONF_DEVICE_ID] = "device_id is required."

            if errors:
                # If there are errors, return the form with error messages
                return self.async_show_form(
                    step_id="user", data_schema=self._get_schema(), errors=errors
                )

            api_key = user_input[CONF_API_KEY]
            device_id = user_input[CONF_DEVICE_ID]
            scan_interval = user_input[CONF_SCAN_INTERVAL]

            # If there are no errors, create a config entry and return
            return self.async_create_entry(
                title="Olarm Sensors",
                data={
                    CONF_API_KEY: api_key,
                    CONF_DEVICE_ID: device_id,
                    CONF_SCAN_INTERVAL: scan_interval,
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
                    description="Olarm API Key",
                    msg="Olarm API Key",
                    default="Olarm API Key",
                ): str,
                vol.Required(
                    CONF_DEVICE_ID,
                    description="Olarm Device ID",
                    msg="Olarm Device ID",
                    default="Olarm Device ID",
                ): str,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    description="Scan Interval",
                    msg="Scan Interval",
                    default=1,
                ): int,
            }
        )

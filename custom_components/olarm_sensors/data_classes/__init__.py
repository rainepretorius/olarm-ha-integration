"""
Module containing the classes for storing data between the API JSON and the Home Assistant classes.
Module containing the classes for storing data between Home Assistant and the API.
Also mimics service schemas.
"""
from homeassistant.core import HomeAssistant
from ..const import DOMAIN


class OlarmDevice:
    """
    This class represents an Olarm device.
    """

    _data: dict
    _alarm_panels: list
    _sensors: list
    _pgm_buttons: list
    _ukey_buttons: list
    _refresh_button: None
    _bypass_switches: list
    _pgm_switches: list
    _setup_complete: bool = False
    _enabled: bool = True
    _error: bool = False
    _errors: list = []
    _online: bool = True
    _hass: HomeAssistant

    def __init__(self, data: dict, hass: HomeAssistant = None) -> None:
        """
        This class represents an Olarm device.
        """
        self._data = data
        self._error = False
        self._online = True
        self._hass = hass
        try:
            self._hass.data.setdefault(DOMAIN, {})
        except Exception:
            pass
        return None

    def set_panels(self, panels) -> None:
        """
        Sets the alarm panels for each Olarm device
        """
        self._alarm_panels = panels
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_panels(self):
        """
        Returns all the sensors for the spesified device.
        """
        return self._alarm_panels

    def set_sensors(self, sensors: list) -> None:
        """
        Sets the sensors for each Olarm device
        """
        self._sensors = sensors
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_sensors(self) -> list:
        """
        Returns all the sensors for the spesified device.
        """
        return self._sensors

    def set_pgm_buttons(self, pgm_buttons: list) -> None:
        """
        Sets the PGM buttons for the spesified device
        """
        self._pgm_buttons = pgm_buttons
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_pgm_buttons(self) -> list:
        """
        Gets all the PGM buttons for the spesified device.
        """
        return self._pgm_buttons

    def set_ukey_buttons(self, ukey_buttons: list) -> None:
        """
        Sets the Utility key buttons for the spesified device.
        """
        self._ukey_buttons = ukey_buttons
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_ukey_buttons(self) -> list:
        """
        Gets all the Utility key buttons for the spesified device.
        """
        return self._ukey_buttons

    def set_refresh_button(self, refresh_button) -> None:
        """
        Sets the refresh button for the spesified device.
        """
        self._refresh_button = refresh_button
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_refresh_button(self):
        """
        Gets the refresh button for the spresified device.
        """
        return self._refresh_button

    def set_bypass_switches(self, bypass_switches: list) -> None:
        """
        Sets the bypass buttons for the device.
        """
        self._bypass_switches = bypass_switches
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_bypass_switches(self) -> list:
        """
        Returns the bypass switches for the spesified device.
        """
        return self._bypass_switches

    def set_pgm_switches(self, pgm_switches: list) -> None:
        """
        Sets the pgm switches for the spesified device.
        """
        self._pgm_switches = pgm_switches
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def get_pgm_switches(self) -> list:
        """
        Gets the PGM switches for the spesified device.
        """
        return self._pgm_switches

    def set_as_enabled(self) -> None:
        """
        Sets the device as active and in use.
        """
        self._enabled = True
        return None

    def set_as_disabled(self) -> None:
        """
        Sets the device as inactive or not in use.
        """
        self._enabled = False
        return None

    def set_as_errored(self) -> None:
        """
        Sets the device as errored.
        """
        self._error = True
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def clear_errored_state(self) -> None:
        """
        Clears the errored state of the device.
        """
        self._error = False
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def set_device_online(self) -> None:
        """
        Sets the Olarm device as online.
        """
        self._online = True
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def set_device_offline(self) -> None:
        """
        Sets the Olarm device as offline.
        """
        self._online = False
        self._hass.data[DOMAIN][self.device_id].device = self
        return None

    def add_error_to_device(self, error) -> None:
        """
        Adds the error that occured to the device.
        """
        self._errors.append(error)
        try:
            self._hass.data[DOMAIN][self.device_id].device = self
        except Exception:
            pass
        return None

    def get_errors(self) -> list:
        """
        Returns all the errors for the device.
        """
        return self._errors

    def initial_setup_complete(self, hass: HomeAssistant) -> None:
        """
        All sensors for the device has been added and setup is complete
        """
        self._hass = hass
        self._hass.data.setdefault(DOMAIN, {})
        self._setup_complete = True
        try:
            self._hass.data[DOMAIN][self.device_id].device = self
        except Exception:
            pass
        return None

    @property
    def firmware(self) -> str:
        """
        Returns the firmware version of the Olarm Device.
        """
        return self._data["deviceFirmware"]

    @property
    def is_setup(self) -> bool:
        """
        Returns whether the initial setup of the device is done.
        """
        return self._setup_complete

    @property
    def is_enabled(self):
        """
        Returns if the device is enabled.
        """
        return self._enabled

    @property
    def device_name(self) -> str:
        """
        Returns the name of the device
        """
        return str(self._data["deviceName"])

    @property
    def device_id(self) -> str:
        """
        Returns the device id (unique identifier) for the device.
        """
        return str(self._data["deviceId"])

    @property
    def device_firmware(self) -> str:
        """
        Returns the device id (unique identifier) for the device.
        """
        return str(self._data["deviceFirmware"])

    @property
    def device_make(self) -> str:
        """
        Returns the make of the alarm panel for the device.
        """
        return str(self._data["deviceAlarmType"]).capitalize()

    @property
    def is_online(self) -> bool:
        """
        Returns the online state of the device.
        """
        return self._online

    @property
    def is_errored(self) -> bool:
        """
        Returns whether the device is errored.
        """
        return self._error

    @property
    def device_status(self) -> bool:
        """
        Returns the status of the device.
        """
        return str(self._data["deviceStatus"]).lower() == "online"

    @property
    def device_state(self):
        """
        Returns the device state.
        """
        return self._data["deviceState"]

    @property
    def device_profile(self):
        """
        Return the device profile
        """
        return self._data["deviceProfile"]

    def __dict__(self):
        """
        Returns the data in a dictionary format.
        """
        return self._data

    def __str__(self):
        return str(self._data)

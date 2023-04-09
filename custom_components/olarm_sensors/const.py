"""Module that stores all the constants for the integration"""
import logging
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMING,
    STATE_ALARM_TRIGGERED,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
)
from homeassistant.components.binary_sensor import BinarySensorDeviceClass


VERSION = "2.0.3"

DOMAIN = "olarm_sensors"
AuthenticationError = "invalid_credentials"
DeviceIDError = "invalid_device_id"
LOGGER = logging.getLogger(__package__)
CONF_DEVICE_NAME = "olarm_device_name"
CONF_DEVICE_MAKE = "olarm_device_make"
CONF_DEVICE_MODEL = "olarm_device_model"
CONF_DEVICE_FIRMWARE = "olarm_device_firmware"
CONF_ALARM_CODE = "olarm_arm_code"

OLARM_STATE_TO_HA = {
    "disarm": STATE_ALARM_DISARMED,
    "notready": STATE_ALARM_DISARMED,
    "countdown": STATE_ALARM_ARMING,
    "sleep": STATE_ALARM_ARMED_NIGHT,
    "stay": STATE_ALARM_ARMED_HOME,
    "arm": STATE_ALARM_ARMED_AWAY,
    "alarm": STATE_ALARM_TRIGGERED,
    "fire": STATE_ALARM_TRIGGERED,
    "emergency": STATE_ALARM_TRIGGERED,
}

OLARM_CHANGE_TO_HA = {
    "area-disarm": STATE_ALARM_DISARMED,
    "area-stay": STATE_ALARM_ARMED_HOME,
    "area-sleep": STATE_ALARM_ARMED_NIGHT,
    "area-arm": STATE_ALARM_ARMED_AWAY,
    None: None,
}

OLARM_ZONE_TYPE_TO_HA = {
    "": BinarySensorDeviceClass.MOTION,
    0: BinarySensorDeviceClass.MOTION,
    10: BinarySensorDeviceClass.DOOR,
    11: BinarySensorDeviceClass.WINDOW,
    20: BinarySensorDeviceClass.MOTION,
    21: BinarySensorDeviceClass.MOTION,
    90: BinarySensorDeviceClass.PROBLEM,
    50: BinarySensorDeviceClass.SAFETY,
    51: BinarySensorDeviceClass.SAFETY,
    1000: BinarySensorDeviceClass.PLUG,
    1001: BinarySensorDeviceClass.POWER,
}

SERVICES_TO_YAML = {
    "arm": {
        "description": "Send a request to Olarm to set areanumber area to armed on alarm."
    },
    "sleep": {
        "description": "Send a request to Olarm to set areanumber area to sleep on alarm."
    },
    "stay": {
        "description": "Send a request to Olarm to set areanumber area to stay on alarm."
    },
    "disarm": {
        "description": "Send a request to Olarm to set areanumber area to disarmed on alarm."
    },
}


class AlarmPanelArea:
    """
    DOCSTRING: Representation of the area number
    """

    area: int = 0

    def __init__(self, area: int) -> None:
        self.area = area
        return None

    @property
    def data(self):
        """
        DOCSTRING: Returns the area number for the api.
        """
        return {"area": self.area}

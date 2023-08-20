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


VERSION = "2.2.3"
DOMAIN = "olarm_sensors"
AUTHENTICATION_ERROR = "invalid_credentials"
LOGGER = logging.getLogger(__package__)
CONF_DEVICE_NAME = "olarm_device_name"
CONF_DEVICE_MAKE = "olarm_device_make"
CONF_DEVICE_MODEL = "olarm_device_model"
CONF_DEVICE_FIRMWARE = "olarm_device_firmware"
CONF_ALARM_CODE = "olarm_arm_code"
CONF_OLARM_DEVICES = "selected_olarm_devices"
OLARM_DEVICE_NAMES = "olarm_device_names"
OLARM_DEVICES = "olarm_devices"
OLARM_DEVICE_AMOUNT = "olarm_device_amount"
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
    "null": None,
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

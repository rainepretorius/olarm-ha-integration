import logging

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMING,
    STATE_ALARM_TRIGGERED,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
)

DOMAIN = "olarm_sensors"
CONF_UPDATE_INTERVAL = 5
DEFAULT_UPDATE_INTERVAL = 5
MIN_UPDATE_INTERVAL = 5
AuthenticationError = "invalid_credentials"
DeviceIDError = "invalid_device_id"
ZONE = 0
LOGGER = logging.getLogger(__package__)
CONF_ALARM_CODE = "alarm_code"
CONF_DEVICE_NAME = "olarm_device_name"
CONF_DEVICE_MAKE = "olarm_device_make"
CONF_DEVICE_MODEL = "olarm_device_model"

ALARM_STATE_TO_HA = {
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


class AlarmPanelArea:
    area: int = 0

    def __init__(self, area: int):
        self.area = area

    @property
    def data(self):
        return {"area": self.area}

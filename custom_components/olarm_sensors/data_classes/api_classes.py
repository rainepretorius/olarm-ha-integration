"""
Module containing the classes for storing data between the API JSON and the Home Assistant classes.
"""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from ..const import OLARM_CHANGE_TO_HA, OLARM_STATE_TO_HA, OLARM_ZONE_TYPE_TO_HA
from datetime import datetime
from .ha_classes import BypassZone
import time


class APISensorResponse:
    """
    The class used to link the json data from the Olarm API to the Home Assistant instances of the sensors.
    """

    _index: int
    _zone_number: int
    _api_zone_type: BinarySensorDeviceClass
    _state_data: dict
    _zone_data: dict

    def __init__(self, state_data: dict, zone_data: dict, index: int) -> None:
        """
        The initiator of the class that is used to link the json data from the Olarm API to the Home Assistant instances of the sensors.
        params:
            data (dict): The data returned from the Olarm API.
            index (int): The index position of the data in the coordinator alarm panel list for the data of this sensor.
        """
        self._index = index
        self._state_data = state_data
        self._zone_data = zone_data
        self._zone_number = index + 1
        self._apizonetype = self._zone_data["zonesTypes"][self._index]
        return None

    @property
    def sensor_type(self) -> str:
        """
        Returns the type of sensor.
        """
        if self.zone_type == BinarySensorDeviceClass.MOTION:
            return "Motion Sensor"

        elif self.zone_type == BinarySensorDeviceClass.POWER:
            return "Battery Powered"

        elif self.zone_type == BinarySensorDeviceClass.PROBLEM:
            return "Sensor Disabled"

        elif self.zone_type == BinarySensorDeviceClass.DOOR:
            return "Door Sensor"

        elif self.zone_type == BinarySensorDeviceClass.WINDOW:
            return "Window Sensor"

        elif self.zone_type == BinarySensorDeviceClass.SAFETY:
            return "Panic Button"

        elif self.zone_type == BinarySensorDeviceClass.PLUG:
            return "Device Power Plug Status"

    @property
    def zone_number(self):
        """
        Returns the zone number of the sensors.
        """
        return self._zone_number

    @property
    def icon(self) -> str:
        """
        Returns the icon for the sensor.
        """
        if self.zone_type == BinarySensorDeviceClass.MOTION:
            if self.state == "on":
                return "mdi:motion-sensor"

            else:
                return "mdi:motion-sensor-off"

        # Window Sensor
        elif self.zone_type == BinarySensorDeviceClass.WINDOW:
            if self.state == "on":
                return "mdi:window-open"

            else:
                return "mdi:window-closed"

        # Door Sensor
        elif self.zone_type == BinarySensorDeviceClass.DOOR:
            if self.state == "on":
                return "mdi:door-open"

            else:
                return "mdi:door-closed"

        # Powered by AC
        elif self.zone_type == BinarySensorDeviceClass.PLUG:
            if self.state == "on":
                return "mdi:power-plug"

            else:
                return "mdi:power-plug-off"

        # Powered By Battery
        elif self.zone_type == BinarySensorDeviceClass.POWER:
            return "mdi:battery"

        # Motion Sensor if no match
        else:
            if self.state == "on":
                return "mdi:motion-sensor"

            else:
                return "mdi:motion-sensor-off"

    @property
    def state(self) -> str:
        """
        Returns the state of the sensor.
        """
        if str(self._state_data["zones"][self._index]).lower() == "a":
            return "on"

        else:
            return "off"

    @property
    def last_changed(self) -> str:
        """
        Returns the last time the state of the sensor changed.
        """
        return datetime.strptime(
            time.ctime(int(self._state_data["zonesStamp"][self._index]) / 1000),
            "%a %b  %d %X %Y",
        ).strftime("%a %d %b %Y %X")

    @property
    def name(self) -> str:
        """
        Returns the name of the zone sensor.
        """
        try:
            if self._zone_data["zonesLabels"][self._index] != "":
                return str(self._zone_data["zonesLabels"][self._index])

            else:
                return "Zone %s", self._zone_number

        except KeyError:
            return "Zone %s", self._zone_number

    @property
    def zone_type(self) -> BinarySensorDeviceClass:
        """
        Returns the Home Assistant Binary Sesor type for the type of sensor on the alarm panel.
        """
        try:
            return OLARM_ZONE_TYPE_TO_HA[self._apizonetype]

        except KeyError:
            if "pir" in self.name.lower():
                return BinarySensorDeviceClass.MOTION

            elif "windows" in self.name.lower() or "wind" in self.name.lower():
                return BinarySensorDeviceClass.WINDOW

            elif "door" in self.name.lower():
                return BinarySensorDeviceClass.DOOR

            elif "ac" in self.name.lower():
                return BinarySensorDeviceClass.PLUG

            elif "batt" in self.name.lower():
                return BinarySensorDeviceClass.POWER

            else:
                return BinarySensorDeviceClass.MOTION

    def __dict__(self):
        """
        Returns the data in a dictionary format.
        """
        return {"zone_data": self._zone_data, "state_data": self._state_data}


class APIPowerResponse:
    """
    The class used to link the json data from the Olarm API to the Home Assistant instances of the sensors.
    """

    _name: str
    _state: int

    def __init__(self, name: str, state: int) -> None:
        """
        The initiator of the class that is used to link the json data from the Olarm API to the Home Assistant instances of the sensors.
        params:
            data (dict): The data returned from the Olarm API.
            index (int): The index position of the data in the coordinator alarm panel list for the data of this sensor.
        """
        if name == "Batt":
            name = "Battery"
        self._name = name
        self._state = state

        return None

    @property
    def sensor_type(self):
        """
        Returns the type of sensor.
        """
        if "ac" in self._name.lower():
            return "Powered by AC"

        elif "batt" in self._name.lower():
            return "Powered by Battery"

    @property
    def last_changed(self) -> None:
        """
        Returns the last time a sensor changed.
        """
        return None

    @property
    def state(self) -> str:
        """
        Returns the state of the sensor.
        """
        if int(self._state) == 1:
            return "on"

        else:
            return "off"

    @property
    def name(self) -> str:
        """
        Returns the name of the zone sensor.
        """
        return self._name

    @property
    def zone_type(self) -> BinarySensorDeviceClass:
        """
        Returns the Home Assistant Binary Sesor type for the type of sensor on the alarm panel.
        """
        if "ac" in self._name.lower():
            return BinarySensorDeviceClass.PLUG

        elif "batt" in self._name.lower():
            return BinarySensorDeviceClass.POWER

    @property
    def icon(self):
        """
        Returns the icon.
        """
        if "ac" in self._name.lower():
            if self.state == "on":
                return "mdi:power-plug"

            else:
                return "mdi:power-plug-off"

        elif "batt" in self._name.lower():
            return "mdi:battery"

    @property
    def zone_number(self) -> int:
        """
        Return the zone number
        """
        if "ac" in self._name.lower():
            return 90009990909

        elif "batt" in self._name.lower():
            return 900090099909909

    def __dict__(self):
        """
        Returns the data in a dictionary format.
        """
        return {"name": self.name, "state": self.state}


class APIBypassResponse:
    """
    The class used to link the json data from the Olarm API to the Home Assistant instances of the sensors.
    """

    _index: int
    _zone_number: int
    _api_zone_type: BinarySensorDeviceClass
    _state_data: dict
    _zone_data: dict

    def __init__(self, state_data: dict, zone_data: dict, index: int) -> None:
        """
        The initiator of the class that is used to link the json data from the Olarm API to the Home Assistant instances of the sensors.
        params:
            data (dict): The data returned from the Olarm API.
            index (int): The index position of the data in the coordinator alarm panel list for the data of this sensor.
        """
        self._index = index
        self._state_data = state_data
        self._zone_data = zone_data
        self._zone_number = index + 1
        self._apizonetype = self._zone_data["zonesTypes"][self._index]
        return None

    @property
    def index(self) -> int:
        """
        The index of the data
        """
        return self._index

    @property
    def zone_number(self):
        """
        Returns the zone number of the sensors.
        """
        return self._zone_number

    @property
    def state(self) -> str:
        """
        Returns the state of the sensor.
        """
        if str(self._state_data["zones"][self._index]).lower() == "b":
            return "on"

        else:
            return "off"

    @property
    def last_changed(self) -> str:
        """
        Returns the last time the state of the sensor changed.
        """
        return datetime.strptime(
            time.ctime(int(self._state_data["zonesStamp"][self._index]) / 1000),
            "%a %b  %d %X %Y",
        ).strftime("%a %d %b %Y %X")

    @property
    def name(self) -> str:
        """
        Returns the name of the zone sensor.
        """
        try:
            if self._zone_data["zonesLabels"][self._index] != "":
                return self._zone_data["zonesLabels"][self._index]

            else:
                return "Zone %s", self._zone_number

        except KeyError:
            return "Zone %s", self._zone_number

    @property
    def zone_type(self) -> BinarySensorDeviceClass:
        """
        Returns the Home Assistant Binary Sesor type for the type of sensor on the alarm panel.
        """
        try:
            return OLARM_ZONE_TYPE_TO_HA[self._apizonetype]

        except KeyError:
            if "pir" in self.name.lower():
                return BinarySensorDeviceClass.MOTION

            elif "windows" in self.name.lower() or "wind" in self.name.lower():
                return BinarySensorDeviceClass.WINDOW

            elif "door" in self.name.lower():
                return BinarySensorDeviceClass.DOOR

            elif "ac" in self.name.lower():
                return BinarySensorDeviceClass.PLUG

            elif "batt" in self.name.lower():
                return BinarySensorDeviceClass.POWER

            else:
                return BinarySensorDeviceClass.MOTION

    @property
    def bypass_zone(self) -> BypassZone:
        """
        Returns the BypassZone representation of the zone.
        """
        return BypassZone(self.zone_number)

    def __dict__(self):
        """
        Returns the data in a dictionary format.
        """
        return {"zone_data": self._zone_data, "state_data": self._state_data}


class APIAreaResponse:
    """
    The class used to link the json data from the Olarm API to the Home Assistant instances of the alarm panels.
    """

    _area_data: dict
    _state_data: dict
    _area_number: int
    _index: int
    _triggers: list = []
    _changes: dict = {"userFullname": "No User", "actionCreated": 0, "actionCmd": None}

    def __init__(self, area_data: dict, state_data: dict, index: int) -> None:
        """
        The initiator of the class that is used to link the json data drom the Olarm API to the Home Assistant instances of the sensors.
        params:
            area_data (dict): The data returned from the Olarm API for the area data.
            state_data (dict): The data returned for the data of this area.
            index (int): The index position of the data in the coordinator panel list for the data of this sensor.
        """
        self._area_data = area_data
        self._state_data = state_data
        self._area_number = index + 1
        self._index = index
        return None

    @property
    def name(self) -> str:
        """
        Returns the name of the area.
        """
        if self._area_data[self._index] == "":
            self._area_data[self._index] = f"Area {self._area_number}"

        return self._area_data[self._index]

    @property
    def index(self) -> int:
        """
        Returns the index of this item.
        """
        return self._index

    @property
    def state(self):
        """
        Returns the state of the panel
        """
        print(self._state_data["areas"][self._index])
        return OLARM_STATE_TO_HA.get(self._state_data["areas"][self._index])

    @property
    def triggers(self) -> str:
        """
        Returns the name of the zones that triggered the alarm.
        """
        return ", ".join(self._triggers)

    @property
    def area_number(self):
        """ "
        Returns the area number of the panel on the alarm.
        """
        return self._area_number

    @property
    def last_changed(self) -> datetime:
        """
        Returns the last time the area / panel changed.
        """
        return datetime.strptime(
            time.ctime(int(self._changes["actionCreated"])), "%a %b  %d %X %Y"
        ).strftime("%a %d %b %Y %X")

    @property
    def changed_by(self) -> str:
        """
        Returns the user that last changed the alarm panel/ area
        """
        return " ".join(
            word.capitalize() for word in str(self._changes["userFullname"]).split()
        )

    @property
    def last_action(self) -> str:
        """
        Returns the last action to the panel/area
        """
        return OLARM_CHANGE_TO_HA.get(self._changes["actionCmd"])

    def set_changes(self, changes: dict) -> None:
        """
        Sets the changes of the alarm panel/area.
        """
        self._changes = changes
        return None

    def set_triggers(self, triggers: list) -> None:
        """
        Sets the triggers of each area/panel.
        """
        self._triggers = triggers
        return None

    def set_last_changed(self, in_time: int) -> None:
        """
        Set the last time the area was changed.
        """
        self._changes["actionCreated"] = in_time
        return None

    def __str__(self):
        return f"Area Data:\n{self._area_data}\n\nState Data:\n{self._state_data}"


class APIPGMResponse:
    """
    The class used to link the json data from the Olarm API to the Home Assistant instances of the pgms.
    """

    _pgm_state: dict
    _pgm_setup: dict
    _pgm_labels: dict
    _pgm_number: int
    _index: int

    def __init__(
        self, pgm_state: dict, pgm_labels: dict, pgm_setup: str, index: int
    ) -> None:
        """
        Initiator for the representation of a pgm on the alarm panel.

        params:
        pgm_state (dict): The state of the pgm's.
        pgm_labels (dict): The name labels of the pgm's.
        pgm_setup (dict): The setup of the pgm's.
        index (int): The index in the api respose of this pgm.
        """
        self._pgm_state = pgm_state
        self._pgm_labels = pgm_labels
        self._pgm_setup = pgm_setup
        self._index = index
        self._pgm_number = index + 1
        return None

    @property
    def index(self) -> int:
        """
        Returns the intdex of the data.
        """
        return self._index

    @property
    def enabled(self) -> bool:
        """
        Returns wheter the PGM is enabled.
        """
        return self._pgm_setup[self._index][0] == "1"

    @property
    def pulse(self) -> bool:
        """
        Returns if the pgm is set up to pulse.
        """
        return self._pgm_setup[self._index][2] == "1"

    @property
    def name(self) -> str:
        """
        Returns the name of the PGM.
        """
        if self._pgm_labels[self._index] == "":
            self._pgm_labels[self._index] = f"PGM {self._pgm_number}"

        return self._pgm_labels[self._index]

    @property
    def state(self) -> bool:
        """
        Returns the state of the pgm.
        """
        return str(self._pgm_state[self._index]).lower() == "a"

    @property
    def pgm_number(self) -> int:
        """
        Returns the pgm number.
        """
        return self._pgm_number


class APIUkeyResponse:
    """
    The class used to link the json data from the Olarm API to the Home Assistant instances of the utility keys.
    """

    _ukey_state: dict
    _ukey_labels: dict
    _ukey_number: int
    _index: int

    def __init__(self, ukey_state: dict, ukey_labels: dict, index: int) -> None:
        """
        Initiator for the representation of a pgm on the alarm panel.

        params:
        pgm_state (dict): The state of the pgm's.
        pgm_labels (dict): The name labels of the pgm's.
        pgm_setup (dict): The setup of the pgm's.
        index (int): The index in the api respose of this pgm.
        """
        self._ukey_labels = ukey_labels
        self._ukey_state = ukey_state
        self._index = index
        self._ukey_number = index + 1
        return None

    @property
    def index(self) -> int:
        """
        Returns the intdex of the data.
        """
        return self._index

    @property
    def ukey_number(self) -> int:
        """
        Return the number of the utility key.
        """
        return self._ukey_number

    @property
    def name(self) -> str:
        """
        Returns the name of the PGM.
        """
        if self._ukey_labels[self._index] == "":
            self._ukey_labels[self._index] = f"Utility Key {self._ukey_number}"

        return self._ukey_labels[self._index]

    @property
    def state(self) -> bool:
        """
        Returns the state of the pgm.
        """
        return int(self._ukey_state[self._index]) == 1

import aiohttp
import time
from .const import LOGGER
from .exceptions import (
    APIClientConnectorError,
    APIMethodError,
)


class OlarmApi:
    """
    This class provides an interface to the Olarm API. It handles authentication, and provides methods for making requests to arm, disarm, sleep, or stay a security zone.
    params:
        \tdevice_id (str): UUID for the Olarm device.
        \tapi_key (str): The key can be passed in an authorization header to authenticate to Olarm.
    """

    def __init__(self, device_id, api_key) -> None:
        """
        DOCSTRING: Initatiates a connection to the Olarm API.
        params:
        \tdevice_id (str): UUID for the Olarm device.
        \tapi_key (str): The key can be passed in an authorization header to authenticate to Olarm.
        """
        self.device_id = device_id
        self.api_key = api_key
        self.data = []
        self.bypass_data = []
        self.panel_data = []
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def get_devices_json(self) -> dict:
        """
        DOCSTRING: This method gets and returns the data from the Olarm API for a spesific device:

        return:\tdict\tThe info associated with a device
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}",
                    headers=self.headers,
                ) as response:
                    return await response.json()

        except APIClientConnectorError as ex:
            LOGGER.error("Olarm API Devices error\n%s", ex)
            return {}

    async def get_changed_by_json(self, area) -> dict:
        """
        DOCSTRING:\tGets the actions for a spesific device from Olarm and returns the user that last chenged the state of an Area.
        return (str):\tThe user that triggered tha last state change of an area.
        """
        return_data = {"userFullname": "No User",
                       "actionCreated": 0, "actionCmd": None}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    headers=self.headers,
                ) as response:
                    if response.status == 404:
                        LOGGER.debug("actions endpoint returned 404")
                        return return_data

                    changes = await response.json()
                    for change in changes:
                        if (
                            change["actionCmd"]
                            not in [
                                "zone-bypass",
                                "pgm-open",
                                "pgm-close",
                                "pgm-pulse",
                                "ukey-activate",
                            ]
                            and int(change["actionNum"]) == int(area)
                            and return_data["actionCreated"]
                            < int(change["actionCreated"])
                        ):
                            return_data = change

                    return return_data

        except APIClientConnectorError as ex:
            LOGGER.error("Olarm API Changed By error\n%s", ex)
            return {}

    async def check_credentials(self) -> dict:
        """
        DOCSTRING:\tChecks if the details the user provided is valid.

        return (dict):\tThe device json from Olarm.
        """
        return await self.get_devices_json()

    async def get_sensor_states(self, devices_json) -> list:
        """
        DOCSTRING:\tGets the state for each zone for each area of your alarm panel.

        params:\n\t device_json (dict): The device json from get_devices_json.

        return:\tList:\t A sensor for each zone in each area of the alarm panel. As well as the power states.
        """
        olarm_state = devices_json["deviceState"]
        olarm_zones = devices_json["deviceProfile"]

        self.data = []

        for zone in range(0, olarm_zones["zonesLimit"]):
            if str(olarm_state["zones"][zone]).lower() == "a":
                state = "on"

            else:
                state = "off"

            last_changed = time.ctime(
                int(olarm_state["zonesStamp"][zone]) / 1000)

            if "zonesLabels" in olarm_zones and zone in olarm_zones["zonesLabels"] and (olarm_zones["zonesLabels"][zone] or olarm_zones["zonesLabels"][zone] == ""):
                zone_name = olarm_zones["zonesLabels"][zone]

            else:
                zone_name = f"Zone {zone + 1}"

            self.data.append(
                {
                    "name": zone_name,
                    "state": state,
                    "last_changed": last_changed,
                }
            )

        for key, value in olarm_state["power"].items():
            if int(value) == 1:
                state = "on"

            else:
                state = "off"

            if key == "Batt":
                key = "Battery"

            self.data.append(
                {"name": f"Powered by {key}", "state": state, "last_changed": None}
            )

        return self.data

    async def get_sensor_bypass_states(self, devices_json) -> list:
        """
        DOCSTRING:\tGets the bypass state for each zone for each area of your alarm panel.

        params:\n\t device_json (dict): The device json from get_devices_json.

        return:\tList:\t A sensor for each zone's bypass state in each area of the alarm panel.
        """
        olarm_state = devices_json["deviceState"]
        olarm_zones = devices_json["deviceProfile"]

        self.bypass_data = []

        for zone in range(0, olarm_zones["zonesLimit"]):
            if str(olarm_state["zones"][zone]).lower() == "b":
                state = "on"

            else:
                state = "off"

            last_changed = time.ctime(
                int(olarm_state["zonesStamp"][zone]) / 1000)

            if "zonesLabels" in olarm_zones and zone in olarm_zones["zonesLabels"] and olarm_zones["zonesLabels"][zone] or olarm_zones["zonesLabels"][zone] == "":
                zone_name = olarm_zones["zonesLabels"][zone]

            else:
                zone_name = f"Zone {zone + 1}"

            self.bypass_data.append(
                {
                    "name": zone_name,
                    "state": state,
                    "last_changed": last_changed,
                }
            )

        return self.bypass_data

    async def get_panel_states(self, devices_json) -> list:
        """
        DOCSTRING:\tGets the state of each zone for the alarm panel from Olarm.
        params:\n\t device_json (dict): The device json from get_devices_json.

        return: (list):\tThe state for each are of the alarm panel.
        """
        olarm_state = devices_json["deviceState"]
        zones = devices_json["deviceProfile"]
        olarm_zones = zones["areasLabels"]

        self.panel_data = []

        area_count = zones["areasLimit"]
        for area_num in range(area_count):
            try:
                if olarm_zones[area_num] == "":
                    LOGGER.debug(
                        "This device's area names have not been set up in Olarm, generating automatically"
                    )
                    olarm_zones[area_num] = f"Area {area_num + 1}"

                if len(olarm_state["areas"]) > area_num:
                    self.panel_data.extend(
                        [
                            {
                                "name": f"{olarm_zones[area_num]}",
                                "state": olarm_state["areas"][area_num],
                            }
                        ]
                    )

            except APIClientConnectorError as ex:
                LOGGER.error("Olarm API Panel error:\n%s", ex)

        return self.panel_data

    async def get_pgm_zones(self, devices_json) -> list:
        pgm_state = devices_json["deviceState"]["pgm"]
        pgm_labels = devices_json["deviceProfile"]["pgmLabels"]
        pgm_limit = devices_json["deviceProfile"]["pgmLimit"]
        pgm_setup = devices_json["deviceProfile"]["pgmControl"]
        pgms = []
        for i in range(pgm_limit):
            try:
                state = str(pgm_state[i]).lower() == "a"
                name = pgm_labels[i]
                enabled = pgm_setup[i][0] == "1"
                pulse = pgm_setup[i][2] == "1"
                number = i + 1

                if name == "":
                    LOGGER.debug(
                        "PGM name not set. Generating automatically. PGM %s", number
                    )
                    name = f"PGM {number}"

                pgms.append(
                    {
                        "name": name,
                        "enabled": enabled,
                        "pulse": pulse,
                        "state": state,
                        "pgm_number": number,
                    }
                )
                return pgms

            except APIClientConnectorError(None, None) as ex:
                LOGGER.error("Olarm PGM Error:\n%s", ex)
                return []

            except APIMethodError as ex:
                LOGGER.error("Olarm PGM Error:\n%s", ex)
                return []

    async def get_ukey_zones(self, devices_json) -> list:
        ukey_labels = devices_json["deviceProfile"]["ukeysLabels"]
        ukey_limit = devices_json["deviceProfile"]["ukeysLimit"]
        ukey_state = devices_json["deviceProfile"]["ukeysControl"]
        ukeys = []
        for i in range(ukey_limit):
            try:
                state = int(ukey_state[i]) == 1
                name = ukey_labels[i]
                number = i + 1

                if name == "":
                    LOGGER.debug(
                        "Ukey name not set. Generating automatically. Ukey %s", number
                    )
                    name = f"Ukey {number}"

                ukeys.append(
                    {"name": name, "state": state, "ukey_number": number})

            except APIClientConnectorError as ex:
                LOGGER.error("Olarm Ukey Error:\n%s", ex)
                return []

        return ukeys

    async def get_alarm_trigger(self, devices_json) -> list:
        """
        DOCSTRING: Returns the data for the zones that triggered an alarm for the area.
        """
        return devices_json["deviceState"]["areasDetail"]

    async def update_zone(self, post_data):
        """
        DOCSTRING:\tSends an action to the Olarm API to perform an action on the device.
        params:\n\tpost_data (dict): The area to perform the action to. As well as the action.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=post_data,
                    headers=self.headers,
                ) as response:
                    resp = await response.json()
                    return str(resp["actionStatus"]).lower() == "ok"

        except APIClientConnectorError as ex:
            LOGGER.error(
                "Olarm API update zone error:\nCould not set action:\t %s due to error:\n%s",
                post_data,
                ex,
            )
            return False

    async def update_pgm(self, pgm_data):
        """
        DOCSTRING:\tSends an action to the Olarm API to perform a pgm action on the device.
        params:\n\tpost_data (dict): The pgm to perform the action to. As well as the action.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=pgm_data,
                    headers=self.headers,
                ) as response:
                    resp = await response.json()
                    return str(resp["actionStatus"]).lower() == "ok"

        except APIClientConnectorError as ex:
            LOGGER.error(
                "Olarm API update pgm error:\nCould not set action:\t %s due to error:\n%s",
                pgm_data,
                ex,
            )
            return False

    async def update_ukey(self, ukey_data):
        """
        DOCSTRING:\tSends an action to the Olarm API to perform a pgm action on the device.
        params:\n\tukey_data (dict): The ukey to perform the action to. As well as the action.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=ukey_data,
                    headers=self.headers,
                ) as response:
                    resp = await response.json()
                    return str(resp["actionStatus"]).lower() == "ok"

        except APIClientConnectorError as ex:
            LOGGER.error(
                "Olarm API update ukey error:\nCould not set action:\t %s due to error:\n%s",
                ukey_data,
                ex,
            )
            return False

    async def arm_area(self, a=None):
        """
        DOCSTRING: Sends the request to update_zone to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-arm", "actionNum": a.data["area"]}
        return await self.update_zone(post_data)

    async def sleep_area(self, a=None):
        """
        DOCSTRING: Sends the request to update_zone to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-sleep", "actionNum": a.data["area"]}
        return await self.update_zone(post_data)

    async def stay_area(self, a=None):
        """
        DOCSTRING: Sends the request to update_zone to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-stay", "actionNum": a.data["area"]}
        return await self.update_zone(post_data)

    async def disarm_area(self, a=None):
        """
        DOCSTRING: Sends the request to update_zone to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-disarm", "actionNum": a.data["area"]}
        return await self.update_zone(post_data)

    async def bypass_zone(self, zone):
        """
        DOCSTRING: Sends the request to update_zone to bypass a zone.
        params:\n\tzone (dict): The number of the zone to apply the zone to.
        """
        post_data = {
            "actionCmd": "zone-bypass",
            "actionNum": zone.data["zone_num"],
        }
        return await self.update_zone(post_data)

import aiohttp
import time
import logging

_APILOGGER = logging.getLogger(__name__)


class OlarmApi:
    def __init__(self, device_id, api_key) -> None:
        self.device_id = device_id
        self.api_key = api_key
        self.data = []
        self.bypass_data = []
        self.panel_data = {}
        self.post_data = {}
        self.headers = {"Authorization": f"Bearer {api_key}"}
        return None

    async def check_credentials(self):
        """
        DOCSTRING: This function is used to check whether the credential provied by the user are correct.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}",
                headers=self.headers,
            ) as response:
                olarm_json = await response.json()
                olarm_state = olarm_json["deviceState"]
                olarm_zones = olarm_json["deviceProfile"]

                index = 0
                self.data = []
                for zone in olarm_zones["zonesLabels"]:
                    if str(olarm_state["zones"][index]).lower() == "a":
                        state = "on"

                    else:
                        state = "off"

                    self.data.append({"name": zone, "state": state})
                    index = index + 1

                return self.data

    async def get_sensor_states(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}",
                    headers=self.headers,
                ) as response:
                    olarm_json = await response.json()
                    olarm_state = olarm_json["deviceState"]
                    olarm_zones = olarm_json["deviceProfile"]

                    index = 0
                    self.data = []
                    for zone in olarm_zones["zonesLabels"]:
                        if str(olarm_state["zones"][index]).lower() == "a":
                            state = "on"

                        else:
                            state = "off"

                        last_changed = time.ctime(
                            int(olarm_state["zonesStamp"][index]) / 1000
                        )
                        self.data.append(
                            {"name": zone, "state": state, "last_changed": last_changed}
                        )
                        index = index + 1

                    return self.data

        except aiohttp.client_exceptions.ClientConnectorError as ex:
            _APILOGGER.error(f"Olarm API sensor error\n{ex}")
            return self.data

    async def get_sensor_bypass_states(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}",
                    headers=self.headers,
                ) as response:
                    olarm_json = await response.json()
                    olarm_state = olarm_json["deviceState"]
                    olarm_zones = olarm_json["deviceProfile"]

                    index = 0
                    self.bypass_data = []
                    for zone in olarm_zones["zonesLabels"]:
                        if str(olarm_state["zones"][index]).lower() == "b":
                            state = "on"

                        else:
                            state = "off"

                        last_changed = time.ctime(
                            int(olarm_state["zonesStamp"][index]) / 1000
                        )
                        self.bypass_data.append(
                            {"name": zone, "state": state, "last_changed": last_changed}
                        )
                        index = index + 1

                    return self.bypass_data

        except aiohttp.client_exceptions.ClientConnectorError:
            return self.bypass_data

    async def get_panel_states(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}",
                    headers=self.headers,
                ) as response:
                    olarm_json = await response.json()
                    olarm_state = olarm_json["deviceState"]
                    zones = olarm_json["deviceProfile"]
                    olarm_zones = zones["areasLabels"]

                    self.panel_data = []
                    indoor_arm = "off"
                    indoor_sleep = "off"
                    indoor_stay = "off"
                    indoor_disarm = "on"
                    indoor_alarm = "off"
                    outdoor_arm = "off"
                    outdoor_sleep = "off"
                    outdoor_stay = "off"
                    outdoor_disarm = "on"
                    outdoor_alarm = "off"
                    indoor_countdown = "off"
                    outdoor_countdown = "off"

                    if olarm_zones[0] == "":
                        _APILOGGER.info(
                            "This device's area names have not been set up in Olarm, generating automatically."
                        )
                        olarm_zones[0] = "Area 1"

                    if olarm_state["areas"][0] == "arm":
                        indoor_arm = "on"
                        indoor_sleep = "off"
                        indoor_stay = "off"
                        indoor_disarm = "off"
                        indoor_alarm = "off"
                        indoor_countdown = "off"

                    elif olarm_state["areas"][0] == "sleep":
                        indoor_arm = "off"
                        indoor_sleep = "on"
                        indoor_stay = "off"
                        indoor_disarm = "off"
                        indoor_alarm = "off"
                        indoor_countdown = "off"

                    elif olarm_state["areas"][0] == "stay":
                        indoor_arm = "off"
                        indoor_sleep = "off"
                        indoor_stay = "on"
                        indoor_disarm = "off"
                        indoor_alarm = "off"
                        indoor_countdown = "off"

                    elif (
                        olarm_state["areas"][0] == "disarm"
                        or olarm_state["areas"][0] == "notready"
                    ):
                        indoor_arm = "off"
                        indoor_sleep = "off"
                        indoor_stay = "off"
                        indoor_disarm = "on"
                        indoor_alarm = "off"
                        indoor_countdown = "off"

                    elif olarm_state["areas"][0] == "alarm":
                        indoor_arm = "off"
                        indoor_sleep = "off"
                        indoor_stay = "off"
                        indoor_disarm = "off"
                        indoor_alarm = "on"
                        indoor_countdown = "off"

                    elif olarm_state["areas"][0] == "countdown":
                        indoor_arm = "off"
                        indoor_sleep = "off"
                        indoor_stay = "off"
                        indoor_disarm = "off"
                        indoor_alarm = "off"
                        indoor_countdown = "on"

                    # Zone 2
                    if zones["areasLimit"] == 2:
                        try:
                            if olarm_state["areas"][1] == "arm":
                                outdoor_arm = "on"
                                outdoor_sleep = "off"
                                outdoor_stay = "off"
                                outdoor_disarm = "off"
                                outdoor_alarm = "off"
                                outdoor_countdown = "off"

                            elif olarm_state["areas"][1] == "sleep":
                                outdoor_arm = "off"
                                outdoor_sleep = "on"
                                outdoor_stay = "off"
                                outdoor_disarm = "off"
                                outdoor_alarm = "off"
                                outdoor_countdown = "off"

                            elif olarm_state["areas"][1] == "stay":
                                outdoor_arm = "off"
                                outdoor_sleep = "off"
                                outdoor_stay = "on"
                                outdoor_disarm = "off"
                                outdoor_alarm = "off"
                                outdoor_countdown = "off"

                            elif (
                                olarm_state["areas"][1] == "disarm"
                                or olarm_state["areas"][1] == "notready"
                            ):
                                outdoor_arm = "off"
                                outdoor_sleep = "off"
                                outdoor_stay = "off"
                                outdoor_disarm = "on"
                                outdoor_alarm = "off"
                                outdoor_countdown = "off"

                            elif olarm_state["areas"][1] == "alarm":
                                outdoor_arm = "off"
                                outdoor_sleep = "off"
                                outdoor_stay = "off"
                                outdoor_disarm = "off"
                                outdoor_alarm = "on"
                                outdoor_countdown = "off"

                            elif olarm_state["areas"][1] == "countdown":
                                outdoor_arm = "off"
                                outdoor_sleep = "off"
                                outdoor_stay = "off"
                                outdoor_disarm = "off"
                                outdoor_alarm = "off"
                                outdoor_countdown = "on"

                            zone2 = True

                        except IndexError():
                            _APILOGGER.info("This device does not have a zone 2.")
                            zone2 = False

                    if zone2:
                        if olarm_zones[0] == "":
                            _APILOGGER.info(
                                "This device's area names have not been set up in Olarm, generating automatically."
                            )
                            olarm_zones[0] = "Area 1"

                        if olarm_zones[1] == "":
                            _APILOGGER.info(
                                "This device's area names have not been set up in Olarm, generating automatically."
                            )
                            olarm_zones[1] = "Area 2"

                        self.panel_data = [
                            {"name": f"{olarm_zones[0]} Armed", "state": indoor_arm},
                            {"name": f"{olarm_zones[0]} Sleep", "state": indoor_sleep},
                            {"name": f"{olarm_zones[0]} Stay", "state": indoor_stay},
                            {
                                "name": f"{olarm_zones[0]} Disarmed",
                                "state": indoor_disarm,
                            },
                            {
                                "name": f"{olarm_zones[0]} Countdown",
                                "state": indoor_countdown,
                            },
                            {"name": f"{olarm_zones[0]} Alarm", "state": indoor_alarm},
                            {"name": f"{olarm_zones[1]} Armed", "state": outdoor_arm},
                            {"name": f"{olarm_zones[1]} Sleep", "state": outdoor_sleep},
                            {"name": f"{olarm_zones[1]} Stay", "state": outdoor_stay},
                            {
                                "name": f"{olarm_zones[1]} Disarmed",
                                "state": outdoor_disarm,
                            },
                            {
                                "name": f"{olarm_zones[1]} Countdown",
                                "state": outdoor_countdown,
                            },
                            {"name": f"{olarm_zones[1]} Alarm", "state": outdoor_alarm},
                        ]

                    else:
                        if olarm_zones[0] == "":
                            olarm_zones[0] = "Area 1"

                        self.panel_data = [
                            {"name": f"{olarm_zones[0]} Armed", "state": indoor_arm},
                            {"name": f"{olarm_zones[0]} Sleep", "state": indoor_sleep},
                            {"name": f"{olarm_zones[0]} Stay", "state": indoor_stay},
                            {
                                "name": f"{olarm_zones[0]} Disarmed",
                                "state": indoor_disarm,
                            },
                            {
                                "name": f"{olarm_zones[0]} Countdown",
                                "state": indoor_countdown,
                            },
                            {"name": f"{olarm_zones[0]} Alarm", "state": indoor_alarm},
                        ]

                    return self.panel_data

        except aiohttp.client_exceptions.ClientConnectorError as ex:
            _APILOGGER.error(f"Olarm API Panel error:\n{ex}")
            return self.panel_data

    async def arm_zone_1(self, a):
        self.post_data = {"actionCmd": "area-arm", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def sleep_zone_1(self, a):
        self.post_data = {"actionCmd": "area-sleep", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True

        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def stay_zone_1(self, a):
        self.post_data = {"actionCmd": "area-stay", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def disarm_zone_1(self, a):
        self.post_data = {"actionCmd": "area-disarm", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def arm_zone_2(self, a):
        self.post_data = {"actionCmd": "area-arm", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def sleep_zone_2(self, a):
        self.post_data = {"actionCmd": "area-sleep", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def stay_zone_2(self, a):
        self.post_data = {"actionCmd": "area-stay", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def disarm_zone_2(self, a):
        self.post_data = {"actionCmd": "area-disarm", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

    async def bypass_zone(self, zone):
        self.post_data = {
            "actionCmd": "zone-bypass",
            "actionNum": zone.data["zone_num"],
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    await response.json()
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False

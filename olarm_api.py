import aiohttp
import requests


class OlarmApi:
    def __init__(self, device_id:str, api_key:str) -> None:
        """
        DOCSTRING: Creates an instance of the Olarm API to make calls to the api to prefor various actions and get the state of sensors and zones
        (params):
            device_id(str): The device id of your Olarm.
            api_key(str):   Your API key to access the Olarm API.
        """
        self.device_id = device_id
        self.api_key = api_key
        self.data = []
        self.panel_data = {}
        self.post_data = {}
        self.headers = {"Authorization": f"Bearer {api_key}"}
        return None

    async def get_sensor_states(self):
        """
        Function to get the states of the zones from olarm
        """
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

                        self.data.append({"name": zone, "state": state})
                        index = index + 1

                    return self.data

        except Exception(BaseException):
            return self.data

    async def get_panel_states(self):
        """
        DOCSTRING: Makes an http get request to get the state of each zone for Olarm, whether it is armed, sleeped, stayed, disarmed or alarm.
        """
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
                            indoor_arm = "off"
                            indoor_sleep = "off"
                            indoor_stay = "off"
                            indoor_disarm = "off"
                            indoor_alarm = "off"
                            indoor_countdown = "on"

                    if zones["areasLimit"] == 2:
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

        except Exception(BaseException):
            return self.panel_data

    async def arm_zone_1(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to arm Zone 1
        """
        self.post_data = {"actionCmd": "area-arm", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def sleep_zone_1(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to sleep Zone 1
        """
        self.post_data = {"actionCmd": "area-sleep", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def stay_zone_1(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to stay Zone 1
        """
        self.post_data = {"actionCmd": "area-stay", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def disarm_zone_1(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to disarm Zone 1
        """
        self.post_data = {"actionCmd": "area-disarm", "actionNum": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def arm_zone_2(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to arm Zone 2
        """
        self.post_data = {"actionCmd": "area-arm", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def sleep_zone_2(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to sleep Zone 2
        """
        self.post_data = {"actionCmd": "area-sleep", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def stay_zone_2(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to stay Zone 2
        """
        self.post_data = {"actionCmd": "area-stay", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

    async def disarm_zone_2(self, a):
        """
        DOCSTRING: Makes an HTTP Post request to the Olarm API to disarm Zone 2
        """
        self.post_data = {"actionCmd": "area-disarm", "actionNum": 2}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=self.post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except Exception(BaseException):
            return False

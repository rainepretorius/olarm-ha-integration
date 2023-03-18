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

                    area_count = zones["areasLimit"]
                    for area_num in range(area_count):
                        try:
                            arm = "off"
                            sleep = "off"
                            stay = "off"
                            disarm = "off"
                            alarm = "off"
                            countdown = "off"

                            if olarm_zones[area_num] == "":
                                _APILOGGER.info(
                                    "This device's area names have not been set up in Olarm, generating automatically."
                                )
                                olarm_zones[area_num] = "Area 1"

                            if olarm_state["areas"][area_num] == "arm":
                                arm = "on"

                            elif olarm_state["areas"][area_num] == "sleep":
                                sleep = "on"

                            elif olarm_state["areas"][area_num] == "stay":
                                stay = "on"

                            elif (
                                olarm_state["areas"][area_num] == "disarm"
                                or olarm_state["areas"][area_num] == "notready"
                            ):
                                disarm = "on"

                            elif olarm_state["areas"][area_num] == "alarm":
                                alarm = "on"

                            elif olarm_state["areas"][area_num] == "countdown":
                                countdown = "on"

                            self.panel_data.extend(
                                [
                                    {
                                        "name": f"{olarm_zones[area_num]} Armed",
                                        "state": arm,
                                    },
                                    {
                                        "name": f"{olarm_zones[area_num]} Sleep",
                                        "state": sleep,
                                    },
                                    {
                                        "name": f"{olarm_zones[area_num]} Stay",
                                        "state": stay,
                                    },
                                    {
                                        "name": f"{olarm_zones[area_num]} Disarmed",
                                        "state": disarm,
                                    },
                                    {
                                        "name": f"{olarm_zones[area_num]} Countdown",
                                        "state": countdown,
                                    },
                                    {
                                        "name": f"{olarm_zones[area_num]} Alarm",
                                        "state": alarm,
                                    },
                                ]
                            )

                        except aiohttp.client_exceptions.ClientConnectorError as e:
                            _APILOGGER.error(f"Olarm API Panel error:\n{e}")

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

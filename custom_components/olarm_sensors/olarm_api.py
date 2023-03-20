import aiohttp
import time

from .const import LOGGER


class OlarmApi:
    def __init__(self, device_id, api_key) -> None:
        self.device_id = device_id
        self.api_key = api_key
        self.data = []
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def get_devices_json(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}",
                    headers=self.headers,
                ) as response:
                    return await response.json()

        except aiohttp.ClientConnectorError as ex:
            LOGGER.error(f"Olarm API Devices error\n{ex}")
        return {}

    async def get_changed_by_json(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    headers=self.headers,
                ) as response:
                    changed_by = await response.json()
                    return changed_by[0]

        except aiohttp.ClientConnectorError as ex:
            LOGGER.error(f"Olarm API Changed By error\n{ex}")
        return {}

    async def check_credentials(self):
        return await self.get_devices_json()

    async def get_sensor_states(self, devices_json):
        olarm_state = devices_json["deviceState"]
        olarm_zones = devices_json["deviceProfile"]

        index = 0
        self.data = []

        for zone in olarm_zones["zonesLabels"]:
            if str(olarm_state["zones"][index]).lower() == "a":
                state = "on"

            else:
                state = "off"

            last_changed = time.ctime(int(olarm_state["zonesStamp"][index]) / 1000)
            self.data.append(
                {"name": zone, "state": state, "last_changed": last_changed}
            )
            index = index + 1

        for key, value in olarm_state["power"].items():
            if value == 1:
                state = "on"

            else:
                state = "off"
            self.data.append(
                {"name": f"Powered by {key}", "state": state, "last_changed": None}
            )

        return self.data

    async def get_sensor_bypass_states(self, devices_json):
        olarm_state = devices_json["deviceState"]
        olarm_zones = devices_json["deviceProfile"]

        index = 0
        bypass_data = []
        for zone in olarm_zones["zonesLabels"]:
            if str(olarm_state["zones"][index]).lower() == "b":
                state = "on"

            else:
                state = "off"

            last_changed = time.ctime(int(olarm_state["zonesStamp"][index]) / 1000)
            bypass_data.append(
                {"name": zone, "state": state, "last_changed": last_changed}
            )
            index = index + 1

        return bypass_data

    async def get_panel_states(self, devices_json):
        olarm_state = devices_json["deviceState"]
        zones = devices_json["deviceProfile"]
        olarm_zones = zones["areasLabels"]

        panel_data = []

        area_count = zones["areasLimit"]
        for area_num in range(area_count):
            try:
                if olarm_zones[area_num] == "":
                    LOGGER.debug(
                        "This device's area names have not been set up in Olarm, generating automatically."
                    )
                    olarm_zones[area_num] = "Area 1"
                if len(olarm_state["areas"]) > area_num:
                    panel_data.extend(
                        [
                            {
                                "name": f"{olarm_zones[area_num]}",
                                "state": olarm_state["areas"][area_num],
                            }
                        ]
                    )

            except aiohttp.ClientConnectorError as e:
                LOGGER.error(f"Olarm API Panel error:\n{e}")

        return panel_data

    async def update_zone(self, post_data):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self.device_id}/actions",
                    data=post_data,
                    headers=self.headers,
                ) as response:
                    return True
        except aiohttp.ClientConnectorError:
            return False

    async def arm_zone_1(self, a):
        post_data = {"actionCmd": "area-arm", "actionNum": 1}
        return await self.update_zone(post_data)

    async def sleep_zone_1(self, a):
        post_data = {"actionCmd": "area-sleep", "actionNum": 1}
        return await self.update_zone(post_data)

    async def stay_zone_1(self, a):
        post_data = {"actionCmd": "area-stay", "actionNum": 1}
        return await self.update_zone(post_data)

    async def disarm_zone_1(self, a):
        post_data = {"actionCmd": "area-disarm", "actionNum": 1}
        return await self.update_zone(post_data)

    async def arm_zone_2(self, a):
        post_data = {"actionCmd": "area-arm", "actionNum": 2}
        return await self.update_zone(post_data)

    async def sleep_zone_2(self, a):
        post_data = {"actionCmd": "area-sleep", "actionNum": 2}
        return await self.update_zone(post_data)

    async def stay_zone_2(self, a):
        post_data = {"actionCmd": "area-stay", "actionNum": 2}
        return await self.update_zone(post_data)

    async def disarm_zone_2(self, a):
        post_data = {"actionCmd": "area-disarm", "actionNum": 2}
        return await self.update_zone(post_data)

    async def bypass_zone(self, zone):
        post_data = {
            "actionCmd": "zone-bypass",
            "actionNum": zone.data["zone_num"],
        }
        return await self.update_zone(post_data)

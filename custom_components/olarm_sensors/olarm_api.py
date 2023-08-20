"""
Module to interact with the Olarm API.
"""
import aiohttp
import time

from homeassistant.core import HomeAssistant
from .const import LOGGER
from .exceptions import (
    APIClientConnectorError,
    ListIndexError,
    DictionaryKeyError,
    APINotFoundError,
    APIContentTypeError,
)
from aiohttp.client_exceptions import ContentTypeError
from datetime import datetime
import asyncio
from .dataclasses.api_classes import (
    APIAreaResponse,
    APISensorResponse,
    APIBypassResponse,
    APIPowerResponse,
    APIPGMResponse,
    APIUkeyResponse,
)
from .dataclasses import OlarmDevice
from .dataclasses.ha_classes import BypassZone


class OlarmApi:
    """
    This class provides an interface to the Olarm API. It handles authentication, and provides methods for making requests to arm, disarm, sleep, or stay a security zone.
    params:
        \tdevice_id (str): UUID for the Olarm device.
        \tapi_key (str): The key can be passed in an authorization header to authenticate to Olarm.
    """

    _device: OlarmDevice
    _api_key: str
    _sensor_data: list[APISensorResponse, APIPowerResponse]
    _bypass_data: list[APIBypassResponse]
    _panel_data: list[APIAreaResponse]
    _pgm_data: list[APIPGMResponse]
    _devices: list[OlarmDevice]
    _ukey_data: list[APIUkeyResponse]
    devices_json_resp: dict
    _hass: HomeAssistant

    def __init__(self, device: OlarmDevice, api_key: str, hass: HomeAssistant) -> None:
        """
        Initatiates a connection to the Olarm API.
        params:
        \tdevice_id (str): UUID for the Olarm device.
        \tapi_key (str): The key can be passed in an authorization header to authenticate to Olarm.
        """
        self._device = device
        self._api_key = api_key
        self._sensor_data = []
        self._bypass_data = []
        self._panel_data = []
        self._devices = []
        self._pgm_data = []
        self._ukey_data = []
        self._hass = hass
        self.devices_json_resp = {}
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Home Assistant",
        }

    async def get_device_json(self) -> OlarmDevice:
        """
        This method gets and returns the data from the Olarm API for a spesific device:

        return:\tdict\tThe info associated with a device
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self._device.device_id}",
                    headers=self.headers,
                ) as response:
                    try:
                        data = await response.json()
                        self._device = OlarmDevice(data=data, hass=self._hass)
                        return self._device

                    except (APIContentTypeError, ContentTypeError):
                        text = await response.text()
                        if "Forbidden" in text:
                            LOGGER.error(
                                "Could not get JSON data due to incorrect API key. Please update the api key"
                            )
                            self._device.add_error_to_device(text)
                            return self._device

                        elif "Too Many Requests" in text:
                            LOGGER.error(
                                "Your refresh interval is set too frequent for the Olarm API to handle"
                            )
                            self._device.add_error_to_device(text)
                            return self._device

                        else:
                            LOGGER.error(
                                "The api returned text instead of JSON. The text is:\n%s",
                                text,
                            )
                            self._device.add_error_to_device(text)
                            return self._device

        except APIClientConnectorError as ex:
            LOGGER.error("Olarm API Devices error\n%s", ex)
            self._device.add_error_to_device(ex)
            return self._device

    async def get_changed_by_json(self, area) -> dict:
        """
        DOCSTRING:\tGets the actions for a spesific device from Olarm and returns the user that last chenged the state of an Area.
        return (str):\tThe user that triggered tha last state change of an area.
        """
        return_data = {"userFullname": "No User", "actionCreated": 0, "actionCmd": None}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://apiv4.olarm.co/api/v4/devices/{self._device.device_id}/actions",
                    headers=self.headers,
                ) as response:
                    if response.status == 404:
                        LOGGER.warning(
                            "Olarm has no saved history for device (%s)",
                            self._device.device_name,
                        )
                        return return_data

                    try:
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

                    except (APIContentTypeError, ContentTypeError):
                        text = response.text
                        LOGGER.error(
                            "The Olarm API returned text instead of json. The text is:\n%s",
                            text,
                        )

                    try:
                        last_changed = datetime.strptime(
                            time.ctime(int(return_data["actionCreated"])),
                            "%a %b  %d %X %Y",
                        )
                        return_data["actionCreated"] = last_changed.strftime(
                            "%a %d %b %Y %X"
                        )

                    except TypeError:
                        last_changed = None

                    await asyncio.sleep(5)
                    return return_data

        except APIClientConnectorError as ex:
            LOGGER.error("Olarm API Changed By error\n%s", ex)
            return return_data

        except APINotFoundError as ex:
            LOGGER.error("Olarm API Changed By error\n%s", ex)
            return return_data

    async def check_credentials(self) -> dict:
        """
        DOCSTRING:\tChecks if the details the user provided is valid.

        return (dict):\tThe device json from Olarm.
        """
        try:
            resp = await self.get_device_json()
            if resp["error"] is None:
                resp["auth_success"] = True
                return resp

            else:
                resp["auth_success"] = False
                return resp

        except BaseException as ex:
            return {"auth_success": False, "error": ex}

    async def get_sensor_states(
        self, devices_json: OlarmDevice
    ) -> list[APISensorResponse]:
        """
        DOCSTRING:\tGets the state for each zone for each area of your alarm panel.

        params:\n\t device_json (dict): The device json from get_devices_json.

        return:\tList:\t A sensor for each zone in each area of the alarm panel. As well as the power states.
        """
        olarm_state = devices_json.device_state
        olarm_zones = devices_json.device_profile

        self._sensor_data = []

        try:
            for zone in range(0, olarm_zones["zonesLimit"]):
                self._sensor_data.append(
                    APISensorResponse(
                        state_data=olarm_state, zone_data=olarm_zones, index=zone
                    )
                )

            for key, value in olarm_state["power"].items():
                self._sensor_data.append(APIPowerResponse(name=key, state=value))

        except (DictionaryKeyError, KeyError, IndexError, ListIndexError) as ex:
            self._device.add_error_to_device(
                "Olarm sensors error for  device (%s):\n%s",
                self._device.device_name,
                ex,
            )
            LOGGER.error(
                "Olarm sensors error for  device (%s):\n%s",
                self._device.device_name,
                ex,
            )

        finally:
            return self._sensor_data

    async def get_sensor_bypass_states(self, devices_json) -> list[APIBypassResponse]:
        """
        DOCSTRING:\tGets the bypass state for each zone for each area of your alarm panel.

        params:\n\t device_json (dict): The device json from get_devices_json.

        return:\tList:\t A sensor for each zone's bypass state in each area of the alarm panel.
        """
        olarm_state = devices_json.device_state
        olarm_zones = devices_json.device_profile

        self._bypass_data = []
        try:
            for zone in range(0, olarm_zones["zonesLimit"]):
                if zone < len(olarm_state["zones"]):
                    self._bypass_data.append(
                        APIBypassResponse(
                            state_data=olarm_state, zone_data=olarm_zones, index=zone
                        )
                    )

        except (DictionaryKeyError, KeyError, IndexError, ListIndexError) as ex:
            self._device.add_error_to_device(
                "Olarm Bypass sensors error for device (%s):\n%s",
                self._device.device_name,
                ex,
            )
            LOGGER.error(
                "Olarm Bypass sensors error for device (%s):\n%s",
                self._device.device_name,
                ex,
            )
            self._device.add_error_to_device(ex)

        finally:
            return self._bypass_data

    async def get_panel_states(self, devices_json) -> list[APIAreaResponse]:
        """
        DOCSTRING:\tGets the state of each zone for the alarm panel from Olarm.
        params:\n\t device_json (dict): The device json from get_devices_json.

        return: (list):\tThe state for each are of the alarm panel.
        """
        olarm_state = devices_json.device_state
        zones = devices_json.device_profile
        olarm_areas = zones["areasLabels"]

        self._panel_data = []

        for area_num in range(0, zones["areasLimit"]):
            try:
                if area_num < len(olarm_state["areas"]):
                    self._panel_data.append(
                        APIAreaResponse(
                            area_data=olarm_areas,
                            state_data=olarm_state,
                            index=area_num,
                        )
                    )

            except (DictionaryKeyError, KeyError) as ex:
                self._device.add_error_to_device(
                    "Olarm API Panel error for device (%s):\n%s",
                    self._device.device_name,
                    ex,
                )
                LOGGER.error(
                    "Olarm API Panel error for device (%s):\n%s",
                    self._device.device_name,
                    ex,
                )

        return self._panel_data

    async def get_pgm_zones(self, devices_json) -> list[APIPGMResponse]:
        """
        Gets all the pgm's for the alarm panel.
        params:\n\t device_json (dict): The device json from get_devices_json.

        return: (list):\tThe pgm's for the alarm panel.
        """
        try:
            pgm_state = devices_json.device_state["pgm"]
            pgm_labels = devices_json.device_profile["pgmLabels"]
            pgm_setup = devices_json.device_profile["pgmControl"]
            pgm_limit = devices_json.device_profile["pgmLimit"]

            for i in range(0, pgm_limit):
                self._pgm_data.append(
                    APIPGMResponse(
                        pgm_state=pgm_state,
                        pgm_labels=pgm_labels,
                        pgm_setup=pgm_setup,
                        index=i,
                    )
                )

        except (DictionaryKeyError, KeyError):
            # Error with PGM setup from Olarm app. Skipping PGM's
            self._device.add_error_to_device(
                "Error geting pgm setup data for Olarm device (%s)",
                self._device.device_name,
            )
            LOGGER.error(
                "Error geting pgm setup data for Olarm device (%s)",
                self._device.device_name,
            )

        finally:
            return self._pgm_data

    async def get_ukey_zones(self, devices_json) -> list[APIUkeyResponse]:
        """
        Gets all the Utility keys for the alarm panel.
        params:\n\t device_json (dict): The device json from get_devices_json.

        return: (list):\tThe utility keys for the alarm panel.
        """
        try:
            ukey_labels = devices_json.device_profile["ukeysLabels"]
            ukey_limit = devices_json.device_profile["ukeysLimit"]
            ukey_state = devices_json.device_profile["ukeysControl"]
            for i in range(0, ukey_limit):
                self._ukey_data.append(
                    APIUkeyResponse(
                        ukey_state=ukey_state, ukey_labels=ukey_labels, index=i
                    )
                )

        except (DictionaryKeyError, KeyError, IndexError, ListIndexError) as ex:
            self._device.add_error_to_device(
                "Olarm Ukey error for device (%s):\n%s", self._device.device_name, ex
            )
            LOGGER.error(
                "Olarm Ukey error for device (%s):\n%s", self._device.device_name, ex
            )

        finally:
            return self._ukey_data

    async def get_alarm_trigger(self, devices_json) -> list[str]:
        """
        Returns the data for the zones that triggered an alarm for the area.
        """
        return devices_json.device_state["areasDetail"]

    async def send_action(self, post_data) -> bool:
        """
        DOCSTRING:\tSends an action to the Olarm API to perform an action on the device.
        params:\n\tpost_data (dict): The area to perform the action to. As well as the action.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"https://apiv4.olarm.co/api/v4/devices/{self._device.device_id}/actions",
                    data=post_data,
                    headers=self.headers,
                ) as response:
                    try:
                        resp = await response.json()
                        return str(resp["actionStatus"]).lower() == "ok"

                    except (APIContentTypeError, ContentTypeError):
                        text = await response.text()
                        self._device.add_error_to_device(
                            "Error Sending action on device (%s).\n\n%s",
                            self._device.device_name,
                            text,
                        )
                        LOGGER.error(
                            "Error Sending action on device (%s).\n\n%s",
                            self._device.device_name,
                            text,
                        )

        except APIClientConnectorError as ex:
            self._device.add_error_to_device(
                "Olarm API send action error on device (%s):\nCould not set action:\t %s due to error:\n%s",
                self._device.device_name,
                post_data,
                ex,
            )
            LOGGER.error(
                "Olarm API send action error on device (%s):\nCould not set action:\t %s due to error:\n%s",
                self._device.device_name,
                post_data,
                ex,
            )
            return False

    async def update_pgm(self, pgm_data) -> bool:
        """
        DOCSTRING:\tSends an action to the Olarm API to perform a pgm action on the device.
        params:\n\tpost_data (dict): The pgm to perform the action to. As well as the action.
        """
        return await self.send_action(pgm_data)

    async def update_ukey(self, ukey_data) -> bool:
        """
        DOCSTRING:\tSends an action to the Olarm API to perform a pgm action on the device.
        params:\n\tukey_data (dict): The ukey to perform the action to. As well as the action.
        """
        return await self.send_action(ukey_data)

    async def arm_area(self, area=None) -> bool:
        """
        Sends the request to send_action to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-arm", "actionNum": area}
        return await self.send_action(post_data)

    async def sleep_area(self, area=None) -> bool:
        """
        Sends the request to send_action to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-sleep", "actionNum": area}
        return await self.send_action(post_data)

    async def stay_area(self, area=None) -> bool:
        """
        Sends the request to send_action to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-stay", "actionNum": area}
        return await self.send_action(post_data)

    async def disarm_area(self, area=None) -> bool:
        """
        Sends the request to send_action to arm an area.
        params:\n\tarea (int): The number of the area to apply the zone to.
        """
        post_data = {"actionCmd": "area-disarm", "actionNum": area}
        return await self.send_action(post_data)

    async def bypass_zone(self, zone) -> bool:
        """
        Sends the request to send_action to bypass a zone.
        params:\n\tzone (dict): The number of the zone to apply the zone to.
        """
        post_data = {
            "actionCmd": "zone-bypass",
            "actionNum": zone.data["zone_num"],
        }
        return await self.send_action(post_data)

    async def get_all_devices(self) -> list[OlarmDevice]:
        """
        This method gets and returns the devices from the Olarm API:

        return:\tlist\tThe devices assosiated with the api key.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://apiv4.olarm.co/api/v4/devices",
                    headers=self.headers,
                ) as response:
                    try:
                        olarm_resp = await response.json()
                        for device in olarm_resp["data"]:
                            self._devices.append(
                                OlarmDevice(data=device, hass=self._hass)
                            )

                    except (APIContentTypeError, ContentTypeError):
                        text = await response.text()
                        if "Forbidden" in text:
                            LOGGER.error(
                                "Could not get JSON data due to incorrect API key. Please update the api key"
                            )

                        elif "Too Many Requests" in text:
                            LOGGER.error(
                                "Your api key has been blocked due to too many frequent updates. Please regenerate the api key"
                            )

                        else:
                            LOGGER.error(
                                "The api returned text instead of JSON. The text is:\n%s",
                                text,
                            )

        except APIClientConnectorError as ex:
            LOGGER.error("Olarm API Devices error\n%s", ex)

        finally:
            return self._devices


class OlarmSetupApi:
    """
    This class provides an interface to the Olarm API. It handles authentication, and provides methods for making requests to arm, disarm, sleep, or stay a security zone.
    params:
        \tdevice_id (str): UUID for the Olarm device.
        \tapi_key (str): The key can be passed in an authorization header to authenticate to Olarm.
    """

    _devices: list[OlarmDevice]

    def __init__(self, api_key: str) -> None:
        """
        Initatiates a connection to the Olarm API.
        params:
        \tapi_key (str): The key can be passed in an authorization header to authenticate to Olarm.
        """
        self._devices = []
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def get_olarm_devices(self) -> list[OlarmDevice]:
        """
        This method gets and returns the devices from the Olarm API:

        return:\tlist\tThe devices assosiated with the api key.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://apiv4.olarm.co/api/v4/devices",
                    headers=self.headers,
                ) as response:
                    try:
                        olarm_resp = await response.json()
                        for device in olarm_resp["data"]:
                            self._devices.append(OlarmDevice(data=device, hass=None))

                    except (APIContentTypeError, ContentTypeError):
                        text = await response.text()
                        if "Forbidden" in text:
                            LOGGER.error(
                                "Could not get JSON data due to incorrect API key. Please update the api key"
                            )

                        elif "Too Many Requests" in text:
                            LOGGER.error(
                                "Your api key has been blocked due to too many frequent updates. Please regenerate the api key"
                            )

                        else:
                            LOGGER.error(
                                "The api returned text instead of JSON. The text is:\n%s",
                                text,
                            )

        except APIClientConnectorError as ex:
            LOGGER.error("Olarm API Devices error\n%s", ex)

        finally:
            return self._devices

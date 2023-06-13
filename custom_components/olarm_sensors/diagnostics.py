from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import DOMAIN, VERSION, CONF_OLARM_DEVICES, CONF_ALARM_CODE
import asyncio
import datetime

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    return await async_get_device_diagnostics(hass, entry, None)
    
async def async_get_device_diagnostics(hass: HomeAssistant, entry: ConfigEntry, device1: DeviceEntry):
    devices = hass.data[DOMAIN]["devices"]
    try:
        errors = [
            log_entry.to_dict()
            for key, log_entry in hass.data["system_log"].records.items()
            if DOMAIN in key
        ]
        
        # Removinf device_id from url
        ind1 = 0
        ind2 = 0
        for error in errors:
            for er in error['message']:
                if 'devices/' in er:
                    error['message'][ind2] = error['message'][ind2].split('devices/')[0] + "devices/the_device_id')"
                
                ind2 = ind2 + 1
            
            ind1 = ind1 + 1
    
    except Exception as e:
        errors = f"{type(e).__name__}: {e}"
    
    index = 0
    config = {}
    
    for device in devices:
        # Removing unneeded detail
        device.pop("deviceTimestamp")
        device.pop("deviceSerial")
        device.pop("deviceTriggers")
        device["deviceState"].pop("timestamp")
        device["deviceState"].pop("cmdRecv")
        device["deviceState"].pop("type")
        device["deviceState"].pop("areasDetail")
        device["deviceState"].pop("areasStamp")
        device["deviceState"].pop("zones")
        device["deviceState"].pop("zonesStamp")
        device["deviceProfile"].pop("zonesLabels")
        device["deviceProfile"].pop("zonesTypes")
        device["deviceProfile"].pop("pgmLabels")
        device["deviceProfile"].pop("ukeysLabels")
        device["deviceProfile"].pop("ukeysControl")
        device["deviceProfile"].pop("fenceLabels")
        device["deviceProfile"].pop("fenceZonesLabels")
        device["deviceProfile"].pop("fenceGatesLabels")
        
        # Updating the devices
        devices[index] = device

        index += index
        
        if device1 is not None:
            dev_id = device1.identifiers.pop()[1]
            if device['deviceId'] != dev_id:
                continue
        
        # Checking if the Olarm API allows the device to be used.
        data = await hass.data[DOMAIN][device["deviceId"]].api.check_credentials()
        
        config[device["deviceName"]] = {}
        config[device["deviceName"]]['auth_success'] = data['auth_success']
        config[device["deviceName"]]['error'] = data['error']
        config[device["deviceName"]]['code_required'] = entry.data[CONF_ALARM_CODE] is not None
        
        # Removing the device Id
        device['deviceId'] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        devices[index] = device
        
        await asyncio.sleep(2)
    
    config['scan_interval']: entry.data[CONF_SCAN_INTERVAL]

    uuid = str(round(datetime.datetime.now().timestamp())) + str(len(entry.data[CONF_OLARM_DEVICES])) + str(entry.entry_id) + VERSION
    return {
        "version": VERSION,
        "config": config,
        "errors": errors,
        'enabled_devices': entry.data[CONF_OLARM_DEVICES],
        'amount_of_enabled_devices': len(entry.data[CONF_OLARM_DEVICES]),
        'all_devices': devices,
        'amount_of_total_devices': len(devices),
        'uuid': uuid,
        'entry_id': str(entry.entry_id)
    }
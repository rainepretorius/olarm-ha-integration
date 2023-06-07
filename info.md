# Olarm Home Assistant Integration

## Supported Devices
The integration currently supports all the alarm panels and electric fence energizers listed [here](https://olarm.com/works-with) on Olarm's website.

Please note that the integration has currently only been tested on a MG 5050+ alarm system by the maintainer, but should work for all devices.

## Issues
If you encounter an error with the integration, resulting in its malfunction or failure to function as intended, please create an issue on the repository's [Github](https://github.com/rainepretorius/olarm-ha-integration/issues) page.

## Installation Steps
1. Install via HACS.
2. Restart Home Assistant.
3. Get your Olarm API key at: https://user.olarm.co/#/api.
4. Navigate to the Devices and Services tab under Settings.
5. Click on Add Integration.
6. Search for Olarm Sensors.
7. Enter these details in the fields in the popup. (Only API key is needed)
   It gets all the devices associated with the API key automatically.
8. Select the Scan Interval in seconds. This is the interval in seconds that Home Assistant will refresh the entity states.

## Setup of the Integration / Platforms Used

### Binary Sensors
Binary sensors are used for simple alarm panel zones and sensors. The following are examples:
1. Motion Sensors (BinarySensorDeviceClass.MOTION)
2. Door Sensors (BinarySensorDeviceClass.DOOR)
3. Window Sensors (BinarySensorDeviceClass.WINDOW)
4. Powered by AC (BinarySensorDeviceClass.PLUG)
5. Powered by Battery (BinarySensorDeviceClass.POWER)

### Alarm Control Panel
There is an alarm control panel for each area enabled on your alarm panel. This allows you to set the state of each area individually. If you have a nemtek electric fence. It is currently coded to enable arming and disarming of the electric fence.

### Buttons
There are buttons to refresh the data from the Olarm API, activate the PGM's, and activate Utility keys. The following is how it is set up:
1. If your PGM has been set up as pulse or pulsing for the specified PGM has been enabled, it will show up as a button that can be pressed.
2. There is a refresh button that refreshes the data from the Olarm API.
3. There is buttons to toggle Utility Keys set up on your alarm.

### Switch
There are switches that are used to activate or deactivate specified PGM's that were not set up to pulse and switches for bypassing zones. It is set up as follows:
1. There is a switch for each zone/sensor on your alarm panel, which allows you to bypass that certain zone/sensor. (Switch on = bypassed, Switch off = active)
2. If the specified PGM was not set up to pulse/pulsing disabled, there will be a switch that allows you to turn the PGM on and off.

## After Installation
Customize your own frontend or use the [Home Assistant Alarm Panel Card](https://www.home-assistant.io/dashboards/alarm-panel) or the [Mushroom Alarm control panel card](https://github.com/piitaya/lovelace-mushroom/blob/main/docs/cards/alarm-control-panel.md).

## Services
1. The integration has been changed so that most of the services are built in to Home Assistant. To control your alarm panel entities please refer to the [Home Assistant Alarm Panel Services](https://www.home-assistant.io/integrations/alarm_control_panel/#services) for how they can be used.
2. `device_name_bypass_zone`:
   - description: Send a request to Olarm to bypass the zone on your alarm.
   - fields:
     - zone_num:
       - description: "Zone Number (The zone you want to bypass) (Can be found under state attributes for the specified zone.)"
       - example: 1
       - required: true

# Current Issue with Olarm Too Many Requests

Updates regarding the issue can be found [here](https://github.com/rainepretorius/olarm-ha-integration/discussions/85).

# Important Update Regarding Integration

Due to recent changes made by Olarm that have rendered their API unusable for third-party applications, it is no longer possible to make significant updates to this integration. Specifically, the API's imposed limits and frequent "429 Too Many Requests" errors have created issues that can only be fixed by Olarm themselves. 

While I will continue to address critical bugs and errors, new features or enhancements will not be added until Olarm removes these restrictions or provides a direct solution. I encourage users to reach out to Olarm for further assistance. i will provide updates for possible alternatives.

---

# Olarm Home Assistant Integration

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=rainepretorius&button_colour=5F7FFF&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/rainepretorius)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

## Supported Devices

This integration currently supports all alarm panels and electric fence energizers listed on Olarm's website [here](https://olarm.com/products/olarm-pro-4g/datasheet).

Please note that while the integration has been tested on a Paradox MG 5050+ alarm system by the maintainer, it should work with all devices.

## Important Notice

Due to Olarm’s API call limits, issues may arise if the refresh rate is set too frequent or multiple devices are selected/enabled.

## Issues

If you encounter errors or malfunctioning of the integration, please submit an issue on the repository's [GitHub page](https://github.com/rainepretorius/olarm-ha-integration/issues). Ensure that your issue hasn’t already been asked and answered; otherwise, it will be closed.

## Installation Steps

1. Install via HACS.
2. Restart Home Assistant.
3. Get your Olarm API key at: https://user.olarm.co/#/api.
4. [Add Integration Here](https://my.home-assistant.io/redirect/config_flow_start/?domain=olarm_sensors).
5. Enter the API key in the popup field. All devices associated with the key will be fetched automatically.
6. Set the Scan Interval in seconds, which determines how often Home Assistant refreshes the entity states.

## Setup of the Integration / Platforms Used

### Binary Sensors

Binary sensors are available for alarm panel zones and sensors, such as:

1. Motion Sensors (BinarySensorDeviceClass.MOTION)
2. Door Sensors (BinarySensorDeviceClass.DOOR)
3. Window Sensors (BinarySensorDeviceClass.WINDOW)
4. Powered by AC (BinarySensorDeviceClass.PLUG)
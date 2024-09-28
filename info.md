# Current Issue with Olarm Too Many Requests

Updates regarding the issue can be found [here](https://github.com/rainepretorius/olarm-ha-integration/discussions/85).

## Important Update Regarding Integration

Due to recent changes made by Olarm that have rendered their API unusable for third-party applications, it is no longer possible to make significant updates to this integration. Specifically, the API's imposed limits and frequent "429 Too Many Requests" errors have created issues that can only be fixed by Olarm themselves.

While I will continue to address critical bugs and errors, new features or enhancements will not be added until Olarm removes these restrictions or provides a direct solution. I encourage users to reach out to Olarm for further assistance. I will provide updates for possible alternatives.

---

## Possibility of Creating My Own Remote Monitoring solution for Paradox Systems

I am excited to announce that I have begun developing my own version similar to an Olarm that will work on most **Paradox alarm systems**. This solution will be based on the **Paradox Alarm Interface (PAI)**, which will enable full-feature integration for Paradox systems.

### Key Features:
- **PAI Backend**: My custom Olarm will have full Paradox Alarm Interface (PAI) support, ensuring all Paradox alarm features are accessible through the system.
  - **Zone Monitoring and Control**: Control all Paradox alarm zones such as motion, door, and window sensors.
  - **Real-time Alarm Status**: Receive real-time updates on the system’s state, including arming/disarming status.
  - **Event Logging**: Complete event logging for all alarm activities, similar to the current Olarm API but without the limitations.
  - **Battery Monitoring**: In addition to core features, the system will monitor the **battery percentage** of the alarm, ensuring system health checks are more transparent.

- **Garage and Gate Monitoring**: I’m also developing a unit to monitor **garage doors** and **gates**, which will integrate directly into **Home Assistant**. This will provide users with remote control and monitoring of entry points, bringing added security to their automation setup.

Stay tuned for further developments, as this solution will open new possibilities for Paradox alarm owners, free from the current limitations imposed by Olarm’s API.

---

# Olarm Home Assistant Integration

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=rainepretorius&button_colour=5F7FFF&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/rainepretorius)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

## Supported Devices

This integration currently supports all alarm panels and electric fence energizers listed on Olarm's website [here](https://olarm.com/products/olarm-pro-4g/datasheet).

Please note that while the integration has been tested on a Paradox MG 5050+ alarm system by the maintainer, it should work with all devices.

---

## Important Notice

Due to Olarm’s API call limits, issues may arise if the refresh rate is set too frequent or multiple devices are selected/enabled.

---

## Issues

If you encounter errors or malfunctioning of the integration, please submit an issue on the repository's [GitHub page](https://github.com/rainepretorius/olarm-ha-integration/issues). Ensure that your issue hasn’t already been asked and answered; otherwise, it will be closed.

---

## Installation Steps

1. Install via HACS.
2. Restart Home Assistant.
3. Get your Olarm API key at: https://user.olarm.co/#/api.
4. [Add Integration Here](https://my.home-assistant.io/redirect/config_flow_start/?domain=olarm_sensors).
5. Enter the API key in the popup field. All devices associated with the key will be fetched automatically.
6. Set the Scan Interval in seconds, which determines how often Home Assistant refreshes the entity states.

---

## Setup of the Integration / Platforms Used

### Binary Sensors

Binary sensors are available for alarm panel zones and sensors, such as:

1. Motion Sensors (BinarySensorDeviceClass.MOTION)
2. Door Sensors (BinarySensorDeviceClass.DOOR)
3. Window Sensors (BinarySensorDeviceClass.WINDOW)
4. Powered by AC (BinarySensorDeviceClass.PLUG)

More updates will follow soon!

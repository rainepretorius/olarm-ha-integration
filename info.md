# Olarm Home Assistant Integration
# Supported Devices
Currrently only tested on Paradox MG 5050 and MG 5050+ alarm systems</br>
If you receive an error for your panel. Please send the response of:
https://apiv4.olarm.co/api/v4/devices/device_id?accessToken=api_key to an issue on <a href="https://github.com/rainepretorius/olarm-ha-integration/issues">Github</a>.</br>
# Installation steps:<br />
1.) Install via HACS.<br />
2.) Restart Home Assistant.<br />
3.) Get your Olarm API key at : https://user.olarm.co/#/api<br />
4.) Navigate to the Devices and Services tab under Settings.<br />
5.) Click on Add Integration.<br />
6.) Search for Olarm Sensors<br />
7.) Enter these details in the fields in the popup. (Only API key is needed)<br />
It gets all the devices assisiated with the api key automatically.<br />
8.) Select the Scan Interval in seconds. This is the interval in seconds that Home Assistant will refresh the entity states.<br />
# Setup of the integration / Platforms used <br />
# Binary Sensors #
Binary sensors are used for simple alarm panel zones and sensors. The folowing are examples:<br />
1.) Motion Sensors (BinarySensorDeviceClass.MOTION)<br />
2.) Door Sensors (BinarySensorDeviceClass.DOOR)<br />
3.) Window Sensors (BinarySensorDeviceClass.WINDOW)<br />
4.) Powered by AC (BinarySensorDeviceClass.PLUG)<br />
5.) Powered by Battery (BinarySensorDeviceClass.POWER)<br />

# Alarm Control Panel #
There is an alarm control panel for each area enabled on your alarm panel. This allows you to set the state of each area individually. If you have a nemtek electric fence. It is currently coded to enable arming and disarming of the electric fence.<br />

# Buttons #
There are buttons to refresh the data from the Olarm API, activate the PGM's, and activate Utility keys. The following is how it is set up:<br />
1.) If your PGM has been set up as pulse or pulsing for the specified PGM has been enabled, it will show up as a button that can be pressed.<br />
2.) There is a refresh button that refreshes the data from the Olarm API.<br />
3.) There is buttons to toggle Utility Keys set up on your alarm.<br />

# Switch #
There are switches that are used to activate or deactivate specified PGM's that were not set up to pulse and switches for bypassing zones. It is set up as follows:<br/>
1.) There is a switch for each zone/sensor on your alarm panel, which allows you to bypass that certain zone/sensor. (Switch on = bypassed, Switch off = active)<br/>
2.) If the specified PGM was not set up to pulse/pulsing disabled, there will be a switch that allows you to turn the PGM on and off.<br />

# After installation #
Customize your own frontend or use the <a href="https://www.home-assistant.io/dashboards/alarm-panel/">Home Assistant Alarm Panel Card</a><br /> or the <a href="https://github.com/piitaya/lovelace-mushroom/blob/main/docs/cards/alarm-control-panel.md"> Mushroom Alarm control panel card</a><br />
# Services #
1.) The integration has been changed so that most of the services are built in to Home Assistant. To control your alarm panel entities please refer to the <a href="https://www.home-assistant.io/integrations/alarm_control_panel/#services"> Home Assistant Alarm Panel Services</a> for how they can be used.<br />
2.) device_name_bypass_zone:</br>
&nbsp;&nbsp;&nbsp;&nbsp;description: Send a request to Olarm to bypass the zone on your alarm.</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fields:</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zone_num:</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;description: "Zone Number (The zone you want to bypass) (Can be found under state attributes for the specified zone.)"</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;example: 1</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;required: true</br>
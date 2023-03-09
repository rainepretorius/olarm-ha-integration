# Olarm Home Assistant Integration
To install this custom integration you will need to dowload the contents of this repository to a folder under custom_components called olarm_sensors.<br />
<br />
Thereafter follow these steps:<br />
1.) Restart Home Assistant<br />
2.) Enable Advanced mode in Home Assistant if you have not yet done so<br />
3.) Get your Olarm API key at : https://user.olarm.co/#/api<br />
4.) Get your device id here: https://apiv4.olarm.co/api/v4/devices?accessToken=APIKEY (Replace API key with the one from step 3).<br />
5.) Navigate to the Devices and Services tab under Settings.<br />
6.) Click on Add Integration.<br />
7.) Search for Olarm Sensors<br />
8.) Enter these details in the fields in the popup.<br />
9.) Select the Scan Interval in seconds. This is the interval in seconds that Home Assistant will refresh the entity states.<br />
10.) The zones will appear undet the integration and under entities as binary_sensor.{zone name}<br />
11.) The services provided by this integration allows you to Arm, Sleep, Stay and Disarm each individually.<br />
12.) Customize your own frontend<br />
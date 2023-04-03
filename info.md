# Olarm Home Assistant Integration
# Supported Devices
Currrently only tested on Paradox alarm systems</br>
If you receive an error for your panel. Please send the response of:
https://apiv4.olarm.co/api/v4/devices/device_id?accessToken=api_key to raine.pretorius1@gmail.com or create an issue on <a href="https://github.com/rainepretorius/olarm-ha-integration/issues">Github</a>.</br>
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
9.) The zones will appear under the integration and under entities as binary_sensor.{zone name}. The status of each area will be alarm_control_panel.{area name}</br>
10.) The services provided by this integration allows you to Arm, Sleep, Stay and Disarm each area individually.<br />
11.) There are buttons to trigger utility keys and pgm zones of your alarm.
12.) Customize your own frontend or use the <a href="https://www.home-assistant.io/dashboards/alarm-panel/">Home Assistant Alarm Panel Card</a><br /> or the <a href="https://github.com/piitaya/lovelace-mushroom/blob/main/docs/cards/alarm-control-panel.md"> Mushroom Alarm control panel card</a>
<br />
# Services</br>
zone_1_arm:</br>
  description: Send a request to Olarm to arm area 1 on your alarm.</br>

zone_1_sleep:</br>
  description: Send a request to Olarm to set area 1 to sleep on your alarm.</br>

zone_1_stay:</br>
  description: Send a request to Olarm to set area 1 to stay on your alarm.</br>

zone_1_disarm:</br>
  description: Send a request to Olarm to disarm area 1 of your alarm.</br>

zone_2_arm:</br>
  description: Send a request to Olarm to arm area 2 on your alarm.</br>

zone_2_sleep:</br>
  description: Send a request to Olarm to set area 2 to sleep on your alarm.</br>

zone_2_stay:</br>
  description: Send a request to Olarm to set area 2 to stay on your alarm.</br>

zone_2_disarm:</br>
  description: Send a request to Olarm to disarm area 2 of your alarm.</br>

bypass_zone:</br>
&nbsp;&nbsp;&nbsp;&nbsp;description: Send a request to Olarm to bypass the zone on your alarm.</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fields:</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zone_num:</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;description: "Zone Number (The zone you want to bypass)"</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;example: 1</br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;required: true</br>

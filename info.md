# Olarm Home Assistant Integration
Installation steps:<br />
1.) Install via HACS.<br />
2.) Restart Home Assistant.<br />
3.) Get your Olarm API key at : https://user.olarm.co/#/api<br />
4.) Get your device id here: https://apiv4.olarm.co/api/v4/devices?accessToken=APIKEY (Replace API key with the one from step 3).<br />
5.) Navigate to the Devices and Services tab under Settings.<br />
6.) Click on Add Integration.<br />
7.) Search for Olarm Sensors<br />
8.) Enter these details in the fields in the popup.<br />
9.) Select the Scan Interval in seconds. This is the interval in seconds that Home Assistant will refresh the entity states.<br />
10.) The zones will appear under the integration and under entities as binary_sensor.{zone name}<br />The status of each area will be binary_sensor.{area name}_armed, binary_sensor.{area name}_sleep, binary_sensor.{area name}_stay, binary_sensor.{area name}_disarmed, binary_sensor.{area name}_countdown and binary_sensor.{area name}_alarm.</br>
11.) The services provided by this integration allows you to Arm, Sleep, Stay and Disarm each area individually.<br />
12.) Customize your own frontend<br />
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

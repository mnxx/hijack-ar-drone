# hijack-ar-drone
A Python script for hijacking Parrot AR Drones.

## How it works
The script creates a monitor interface with [airmon-ng](http://www.aircrack-ng.org/doku.php?id=airmon-ng) which is used to hop through the channels, sniffing out all the available Wi-Fi Access Points with [scapy](http://www.secdev.org/projects/scapy/). By using regular expressions, it finds the drone's network. Then, it uses [aireplay-ng](http://www.aircrack-ng.org/doku.php?id=aireplay-ng) to execute a deauthentication attack, which cuts the connection between the drone and its current user. After this, a connection between the computer and the drone is established. Finally, with [node-ar-drone](https://github.com/felixge/node-ar-drone), we can give orders to the hijacked drone.

The script is currently using a REPL to command the drone. However, you can also write your own scripts. More information can be found [here](https://github.com/felixge/node-ar-drone).

## Requirements
For automatically executing the needed network configurations, we need **root privileges**.
In addition, make sure that you have the following packages installed:
* [aircrack-ng](http://www.aircrack-ng.org/)
* [scapy](http://www.secdev.org/projects/scapy/)
* [node.js](http://nodejs.org)
* [node-ar-drone](https://github.com/felixge/node-ar-drone)

## Troubleshooting
The script might not work for you since it uses **wlp3s0** as the standard wireless interface. You might want to change all occurences to **wlan0**.

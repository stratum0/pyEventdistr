#!/usr/bin/env python
import socket
import re

EVENTDISTR_IP = "192.168.179.255"
EVENTDISTR_PORT = 31337
EVENTDISTR_MAGIC = "EVENTDISTR"
EVENTDISTR_COMMAND = "%sv%%d;%%s" % EVENTDISTR_MAGIC
EVENTDISTR_RE = re.compile("^%sv(\d);([^=]*)(|=(.*))$" % EVENTDISTR_MAGIC)
EVENT_DOOR_UNTEN = "DoorUnten"
EVENT_DING_DONG = "DingDong"
EVENT_NOW_PLAYING = "NowPlaying"
EVENT_VIRTUAL_MSG = "VirtualMsg"
EVENT_SPACE_CLOSED = "SpaceClosed"
EVEMT_SPACE_OPENED = "SpaceOpened"

AREA_FRICKEL = "A"
AREA_LOUNGE = "B"
AREA_BATH = "0"
AREA_KITCHEN = "K"



def send_event(name, data=None,version=1):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
	if data:
		data = "%s=%s" % (name, data)
	else:
		data = name
	s.sendto(EVENTDISTR_COMMAND % (version, data) , (EVENTDISTR_IP,
		EVENTDISTR_PORT))
	s.close()

def parse_event(data):

	if not data:
		return None
	match = EVENTDISTR_RE.match(data)
	version, cmd, donotuse, data = match.groups()
	return (int(version), cmd, data)


def send_clock(cmd):
	send_event(cmd, "RISING")

def open_door():
	send_clock(EVENT_DOOR_UNTEN)

def ring():
	send_clock(EVENT_DING_DONG)

def now_playing(artist, title, area=AREA_LOUNGE):
	send_event(EVENT_NOW_PLAYING, "%s\x00%s\x00%s\x00" % (area, artist, title))

def virtual_msg(msg):
	send_event(EVENT_VIRTUAL_MSG, msg) 

def run_listener(callback):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	sock.bind((EVENTDISTR_IP, EVENTDISTR_PORT))
	while True:
		data, addr = sock.recvfrom(1024)
		result = parse_event(data)
		if result:
			callback(*result)

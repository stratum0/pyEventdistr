#!/usr/bin/env python
import eventdistr
import dbus, gobject
from dbus.mainloop.glib import DBusGMainLoop
import argparse

area = eventdistr.AREA_LOUNGE;

def propChangedCallback(iface, changedProps, invalidatedProps):
	# listen when the org.mpris.MediaPlayer2.Player.Metadata property changes
	if(iface == "org.mpris.MediaPlayer2.Player"):
		if("Metadata" in changedProps.keys()
				and "mpris:trackid" in changedProps["Metadata"]):
			metadata = changedProps["Metadata"]
			title = metadata["xesam:title"]
			artist = metadata["xesam:artist"][0]

			print("Now Playing: %s - %s" % (artist, title))

			eventdistr.now_playing(artist, title, area)

		elif("PlaybackStatus" in changedProps.keys()
				and changedProps["PlaybackStatus"] == u'Stopped'):
			print("Playback stopped.")
			eventdistr.playback_stopped(area)

if __name__ == "__main__":
	# parse argument
	areas = {
		eventdistr.AREA_FRICKEL: "Frickelraum",
		eventdistr.AREA_LOUNGE: "Lounge",
		eventdistr.AREA_BATH: "Bath",
		eventdistr.AREA_KITCHEN: "Kitchen"
	}
	area_list = []
	area_names = areas.keys()
	area_names.sort()

	for area in area_names:
		area_list.append("%s: %s" % (area, areas[area]))
	parser = argparse.ArgumentParser(description="""Listen for new tracks on the
		MPRIS2 interface and send EVENTDISTR NowPlaying events when the track
		changes.""")
	parser.add_argument('--area', '-a', default=eventdistr.AREA_LOUNGE,
		help='Area where the song is played: '+", ".join(area_list))
	args = parser.parse_args()
	area = args.area.upper()

	found = True
	if area not in areas:
		found = False
		for area_id, name in areas.items():
			if name.upper() == area:
				area = area_id
				found = True
				break
	if not found:
		print "Unkown area: '%s'" % area
		exit(1)

	print "Broadcasting your currently played tracks for area %s..." % areas[area]
	print "(You can change this by using --area on the command line)"
	print "Press Ctrl-C to cancel."
	print ""

	# start main loop for DBus
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SessionBus()

	bus.add_signal_receiver(propChangedCallback,
		dbus_interface="org.freedesktop.DBus.Properties",
		signal_name="PropertiesChanged",
		path="/org/mpris/MediaPlayer2"
	)

	loop = gobject.MainLoop()
	loop.run()

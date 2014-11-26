#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import numpy as np



class ApproxSwissProj:

	@staticmethod
	def LV03toWGS84(east, north, height):
		latitude = CHtoWGSlat(east, north)
		longitude = CHtoWGSlng(east, north)
		ellHeight = CHtoWGSheight(east, north, height)
		return (latitude, longitude, ellHeight)

	@staticmethod
	def WGS84toLV03(latitude, longitude, ellHeight):
		east = WGStoCHy(latitude, longitude)
		north = WGStoCHx(latitude, longitude)
		height = WGStoCHh(latitude, longitude, ellHeight)
		return (east, north, height)

	# Convert WGS lat/long (° dec) to CH y
	@staticmethod
	def WGStoCHy(lat, lng):
		# Converts degrees dec to sex
		lat = ApproxSwissProj.DecToSexAngle(lat)
		lng = ApproxSwissProj.DecToSexAngle(lng)
		# Converts degrees to seconds (sex)
		lat = ApproxSwissProj.SexAngleToSeconds(lat)
		lng = ApproxSwissProj.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000.0
		lng_aux = (lng - 26782.5) / 10000.0
		# Process Y
		y = 600072.37 \
			+ 211455.93 * lng_aux \
			-  10938.51 * lng_aux * lat_aux \
			-      0.36 * lng_aux * np.power(lat_aux, 2) \
			-     44.54 * np.power(lng_aux, 3)
		return y

	# Convert WGS lat/long (° dec) to CH x
	@staticmethod
	def WGStoCHx(lat, lng):
		# Converts degrees dec to sex
		lat = ApproxSwissProj.DecToSexAngle(lat)
		lng = ApproxSwissProj.DecToSexAngle(lng)
		# Converts degrees to seconds (sex)
		lat = ApproxSwissProj.SexAngleToSeconds(lat)
		lng = ApproxSwissProj.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000.0
		lng_aux = (lng - 26782.5) / 10000.0
		# Process X
		x = 200147.07 \
			+ 308807.95 * lat_aux  \
			+   3745.25 * np.power(lng_aux, 2) \
			+     76.63 * np.power(lat_aux, 2) \
			-    194.56 * np.power(lng_aux, 2) * lat_aux \
			+    119.79 * np.power(lat_aux, 3)
		return x

	# Convert WGS lat/long (° dec) and height to CH h
	@staticmethod
	def WGStoCHh(lat, lng, h):
		# Converts degrees dec to sex
		lat = ApproxSwissProj.DecToSexAngle(lat)
		lng = ApproxSwissProj.DecToSexAngle(lng)
		# Converts degrees to seconds (sex)
		lat = ApproxSwissProj.SexAngleToSeconds(lat)
		lng = ApproxSwissProj.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000.0
		lng_aux = (lng - 26782.5) / 10000.0
		# Process h
		h = h - 49.55 \
			  +  2.73 * lng_aux \
			  +  6.94 * lat_aux
		return h

	# Convert CH y/x to WGS lat
	@staticmethod
	def CHtoWGSlat(y, x):
		# Converts militar to civil and  to unit = 1000km
		# Axiliary values (% Bern)
		y_aux = (y - 600000.0) / 1000000.0
		x_aux = (x - 200000.0) / 1000000.0
		# Process lat
		lat = 16.9023892 \
			+  3.238272 * x_aux \
			-  0.270978 * np.power(y_aux, 2) \
			-  0.002528 * np.power(x_aux, 2) \
			-  0.0447   * np.power(y_aux, 2) * x_aux \
			-  0.0140   * np.power(x_aux, 3)
		# Unit 10000" to 1 " and converts seconds to degrees (dec)
		lat = (lat * 100.0) / 36.0
		return lat

	# Convert CH y/x to WGS long
	@staticmethod
	def CHtoWGSlng(y, x):
		# Converts militar to civil and  to unit = 1000km
		# Axiliary values (% Bern)
		y_aux = (y - 600000.0) / 1000000.0
		x_aux = (x - 200000.0) / 1000000.0
		# Process long
		lng = 2.6779094 \
			+ 4.728982 * y_aux \
			+ 0.791484 * y_aux * x_aux \
			+ 0.1306   * y_aux * np.power(x_aux, 2) \
			- 0.0436   * np.power(y_aux, 3)
		# Unit 10000" to 1 " and converts seconds to degrees (dec)
		lng = (lng * 100.0) / 36.0
		return lng

	# Convert CH y/x/h to WGS height
	@staticmethod
	def CHtoWGSheight(y, x, h):
		# Converts militar to civil and  to unit = 1000km
		# Axiliary values (% Bern)
		y_aux = (y - 600000.0) / 1000000.0
		x_aux = (x - 200000.0) / 1000000.0
		# Process height
		h = h + 49.55 \
			- 12.60 * y_aux \
			- 22.64 * x_aux
		return h

	# Convert sexagesimal angle (degrees, minutes and seconds "dd.mmss") to decimal angle (degrees)
	@staticmethod
	def SexToDecAngle(dms):
		# Extract DMS
		# Input: dd.mmss(,)ss
		deg = np.floor(dms)
		min = np.floor((dms - deg) * 100.0)
		sec = (((dms - deg) * 100.0) - min) * 100.0
		# Result in degrees dec (dd.dddd)
		return deg + min/60.0 + sec/3600.0

	# Convert decimal angle (degrees) to sexagesimal angle (degrees, minutes and seconds dd.mmss,ss)
	@staticmethod
	def DecToSexAngle(dec):
		deg = np.floor(dec)
		min = np.floor((dec - deg) * 60.0)
		sec = (((dec - deg) * 60) - min) * 60.0
		# Output: dd.mmss(,)ss
		return deg + min/100.0 + sec/10000.0

	# Convert sexagesimal angle (degrees, minutes and seconds dd.mmss,ss) to seconds
	@staticmethod
	def SexAngleToSeconds(dms):
		deg = np.floor(dms)
		min = np.floor((dms - deg) * 100.0)
		sec = (((dms - deg) * 100.0) - min) * 100.0
		# Result in degrees sex (dd.mmss)
		return sec + min * 60.0 + deg * 3600.0

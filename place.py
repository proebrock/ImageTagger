#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import json
import numpy as np
import webbrowser



class Place:

	def __init__(self, node_or_array):
		if isinstance(node_or_array, np.ndarray):
			self.name = 'Unknown'
			self.height = 0
			self.ch1903 = node_or_array
		else:
			node = node_or_array
			self.name = node['Name']
			self.height = float(node['Height'])
			self.ch1903 = np.array([ float(node['CH1903'][0]), \
				float(node['CH1903'][1]) ])

	def __str__(self):
		return self.name + ' ' + str(self.height) + \
			'm @' +  str(self.ch1903[0]) + ',' + str(self.ch1903[1])

	def ShowOnMap(self):
		url = 'http://map.geo.admin.ch/?selectedNode=node_ch.swisstopo.swisstlm3d-wanderwege1&Y={0}&X={1}&zoom=6&bgLayer=ch.swisstopo.pixelkarte-farbe&lang=de&topic=ech&layers=ch.swisstopo.swisstlm3d-wanderwege&crosshair=bowl'.format(self.ch1903[0], self.ch1903[1])
		webbrowser.open_new_tab(url)

	def Distance(self, otherPlace):
		delta = self.ch1903 - otherPlace.ch1903
		return np.sqrt(np.sum(np.square(delta)))

	def Azimut(self, targetPlace):
		delta = self.ch1903 - targetPlace.ch1903
		magneticDeclination = 1.56 # Place and time dependent ...
		return magneticDeclination + \
			(180.0 * np.arctan2(delta[1], delta[0])) / np.pi

	def WGS84(self):
		y = (self.ch1903[0] - 600000.0) / 1000000.0
		x = (self.ch1903[1] - 200000.0) / 1000000.0
		lat = 16.9023892 + 3.238272 * x - 0.270978 * pow(y,2) \
			- 0.002528 * pow(x,2) - 0.0447 * pow(y,2) * x \
			- 0.0140 * pow(x,3)
		lat = (lat * 100.0) / 36.0
		lng = 2.6779094 + 4.728982 * y + 0.791484 * y * x \
			+ 0.1306 * y * pow(x,2) - 0.0436 * pow(y,3)
		lng = (lng * 100.0) / 36.0
		return np.array([lat, lng])
	
	@staticmethod
	def LoadListFromFile(filename):
		places = {}
		f = open(filename)
		if f is not None:
			placesRoot = json.load(f)
			f.close()
			for node in placesRoot:
				p = Place(node)
				places[p.name + ' ' + str(p.height) + 'm'] = p
		return places


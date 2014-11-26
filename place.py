#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import json
import numpy as np
import webbrowser
from wgs84_ch1903 import ApproxSwissProj



class Place:

	def __init__(self, node=None, ch1903=None, wgs84=None):
		if node is not None:
			self.name = node['Name']
			self.height = float(node['Height'])
			self.ch1903 = np.array([ float(node['CH1903'][0]), \
				float(node['CH1903'][1]) ])
		elif ch1903 is not None:
			self.name = 'Unknown'
			self.height = 0
			self.ch1903 = ch1903
		elif wgs84 is not None:
			self.name = 'Unknown'
			self.height = 0
			self.ch1903 = np.array([ ApproxSwissProj.WGStoCHy(wgs84[0], wgs84[1]), \
				ApproxSwissProj.WGStoCHx(wgs84[0], wgs84[1]) ])

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
	
	def CH1903(self):
		return self.ch1903

	def WGS84(self):
		return np.array([ ApproxSwissProj.CHtoWGSlat(y, x), \
			ApproxSwissProj.CHtoWGSlon(y, x) ])
	
	@staticmethod
	def LoadListFromFile(filename):
		places = {}
		f = open(filename)
		if f is not None:
			placesRoot = json.load(f)
			f.close()
			for node in placesRoot:
				p = Place(node=node)
				places[p.name + ' ' + str(p.height) + 'm'] = p
		return places


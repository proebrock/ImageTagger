#!/usr/bin/env python3



import json
import numpy as np
import sys, os
from place import Place
from PyQt5.QtCore import QDir, QSize, QPoint, QRect, Qt
from PyQt5.QtGui import QColor, QPen, QImage, QPainter, QPalette, QPixmap, QFont
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel, QLineEdit,
	QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QDialog,
	QGroupBox, QLayout, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton)



mountains = {}
if os.path.exists('mountains.json'):
	mountains = Place.LoadListFromFile('mountains.json')



class Marker:
	def __init__(self, x=None, y=None, key=''):
		self.key = key
		self.x = x
		self.y = y

	def Load(self, node):
		self.key = node['Key']
		self.x = float(node['X'])
		self.y = float(node['Y'])

class MarkerEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Marker):
			return { 'Key': obj.key, 'X': obj.x, 'Y': obj.y }
		# Let the base class default method raise the TypeError
		return json.JSONEncoder.default(self, obj)



class MarkerPropertyDialog(QDialog):
	def __init__(self, parent=None):
		super(MarkerPropertyDialog, self).__init__(parent)
		self.setWindowTitle('Marker Properties')
		self.setWindowFlags(Qt.Dialog | Qt.WindowMinimizeButtonHint)
		mainLayout = QVBoxLayout(self)
		mainLayout.setSizeConstraint(QLayout.SetFixedSize)

		coordLayout = QVBoxLayout()
		xLayout = QHBoxLayout()
		xLayout.addWidget(QLabel('X'))
		self.xedit = QLineEdit('')
		self.xedit.setReadOnly(True)
		self.xedit.setAlignment(Qt.AlignRight)
		self.xedit.setFixedWidth(70)
		xLayout.addWidget(self.xedit)
		coordLayout.addLayout(xLayout)
		yLayout = QHBoxLayout()
		yLayout.addWidget(QLabel('Y'))
		self.yedit = QLineEdit('')
		self.yedit.setReadOnly(True)
		self.yedit.setAlignment(Qt.AlignRight)
		self.yedit.setFixedWidth(70)
		yLayout.addWidget(self.yedit)
		coordLayout.addLayout(yLayout)
		gb = QGroupBox('Screen Coordinates')
		gb.setLayout(coordLayout)
		mainLayout.addWidget(gb)

		cboxLayout = QVBoxLayout()
		self.cbox = QComboBox(self)
		cboxLayout.addWidget(self.cbox)
		gb = QGroupBox('Marker key')
		gb.setLayout(cboxLayout)
		mainLayout.addWidget(gb)

		buttonLayout = QHBoxLayout()
		delButton = QPushButton('Delete Marker', self)
		delButton.clicked.connect(self.reject)
		buttonLayout.addWidget(delButton)
		okButton = QPushButton('OK', self)
		okButton.clicked.connect(self.accept)
		okButton.setDefault(True)
		okButton.setFocus()
		buttonLayout.addWidget(okButton)
		mainLayout.addLayout(buttonLayout)

	@staticmethod
	def GetMarkerSelection(marker, places, parent=None):
		dialog = MarkerPropertyDialog(parent)
		index = 0
		for i in range(len(places)):
			dialog.cbox.addItem(places[i])
			if places[i] == marker.key:
				index = i
		dialog.cbox.setCurrentIndex(index)
		dialog.xedit.setText(str(marker.x))
		dialog.yedit.setText(str(marker.y))
		result = dialog.exec_()
		return (result == QDialog.Accepted, dialog.cbox.currentText())



class MyLabel(QLabel):
	def __init__(self, parent=None):
		super(MyLabel, self).__init__(parent)
		self.setBackgroundRole(QPalette.Base)
		self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.setScaledContents(True)
		self.jsonFilename = None
		self.markerList = []
		self.showMarkers = True
		self.scaleFactor = 1.0
		self.radius = 10
	
	def open(self, filename):
		# Load image data
		image = QImage(filename)
		if image.isNull():
			QMessageBox.information(self, 'Image Viewer', 'Cannot load %s.' % filename)
			return		
		self.setPixmap(QPixmap.fromImage(image))
		# Load marker list
		self.jsonFilename = os.path.splitext(filename)[0] + '.json'
		self.markerList = []
		with open(self.jsonFilename, 'r') as f:
			markersRoot = json.load(f)
			f.close()
			for node in markersRoot:
				m = Marker()
				m.Load(node)
				self.markerList.append(m)

	def save(self):
		if self.jsonFilename is not None:
			with open(self.jsonFilename, 'w') as f:
				f.write(json.dumps(self.markerList, cls=MarkerEncoder, \
					indent=4, separators=(',', ': '), sort_keys=True))

	def getScaleFactor(self):
		return self.scaleFactor

	def normalSize(self):
		self.scaleFactor = 1.0
		self.adjustSize()

	def scale(self, factor):
		self.scaleFactor *= factor
		self.resize(self.scaleFactor * self.pixmap().size())
	
	def deleteAllMarkers(self):
		self.markerList = []
	
	def toggleShowMarkers(self):
		self.showMarkers = not self.showMarkers
		self.update()

	def mouseDoubleClickEvent(self, event):
		if not self.showMarkers:
			return
		pos = event.pos() / self.scaleFactor
		index = -1
		for i in range(len(self.markerList)):
			dx = self.markerList[i].x - pos.x()
			dy = self.markerList[i].y - pos.y()
			if np.sqrt(dx * dx + dy * dy) <= self.radius:
				index = i
				break
		if index == -1:
			self.markerList.append(Marker(pos.x(), pos.y()))
			index = len(self.markerList) - 1
			self.update()
		(accepted, markerKey) = MarkerPropertyDialog.GetMarkerSelection(self.markerList[index],
			sorted(mountains.keys()), self)
		if accepted:
			self.markerList[index].key = markerKey
		else:
			del self.markerList[index]
			

	def paintEvent(self, event):
		super(MyLabel, self).paintEvent(event)
		if self.showMarkers and self.pixmap() is not None:
			painter = QPainter(self)
			painter.setRenderHint(QPainter.Antialiasing, True)
			painter.setPen(QPen(QColor(255, 0, 0, 255), 3))
			for marker in self.markerList:
				x = marker.x * self.scaleFactor - self.radius
				y = marker.y * self.scaleFactor - self.radius
				painter.drawEllipse(QRect(x, y, 2*self.radius, 2*self.radius))
				x = marker.x * self.scaleFactor + 1.5 * self.radius
				y = marker.y * self.scaleFactor
				painter.drawText(QPoint(x, y), marker.key)



class ImageViewer(QMainWindow):
	def __init__(self):
		super(ImageViewer, self).__init__()

		self.imageLabel = MyLabel()
		
		self.scrollArea = QScrollArea()
		self.scrollArea.setBackgroundRole(QPalette.Dark)
		self.scrollArea.setWidget(self.imageLabel)
		self.setCentralWidget(self.scrollArea)
		
		self.createActions()
		self.createMenus()
		
		self.setWindowTitle('Image Viewer')
		self.resize(600, 400)

	def open(self):
		fileName, _ = QFileDialog.getOpenFileName(self, 'Open File',
			QDir.currentPath(), filter='JPEG (*.jpeg *.jpg)')
		if fileName:
			self.imageLabel.open(fileName)
			
			self.fitToWindowAct.setEnabled(True)
			self.updateActions()
			
			if not self.fitToWindowAct.isChecked():
			    self.imageLabel.adjustSize()
	
	def save(self):
		self.imageLabel.save()
	
	def viewMarkers(self):
		self.imageLabel.toggleShowMarkers()
	
	def zoomIn(self):
		self.scaleImage(1.25)
	
	def zoomOut(self):
		self.scaleImage(0.8)
	
	def normalSize(self):
		self.imageLabel.normalSize()

	def fitToWindow(self):
		fitToWindow = self.fitToWindowAct.isChecked()
		self.scrollArea.setWidgetResizable(fitToWindow)
		if not fitToWindow:
			self.normalSize()
		self.updateActions()
	
	def about(self):
		QMessageBox.about(self, 'About Image Viewer',
			'<p>The <b>Image Viewer</b> example shows how to combine '
			'QLabel and QScrollArea to display an image. QLabel is '
			'typically used for displaying text, but it can also display '
			'an image. QScrollArea provides a scrolling view around '
			'another widget. If the child widget exceeds the size of the '
			'frame, QScrollArea automatically provides scroll bars.</p>'
			'<p>The example demonstrates how QLabel\'s ability to scale '
			'its contents (QLabel.scaledContents), and QScrollArea\'s '
			'ability to automatically resize its contents '
			'(QScrollArea.widgetResizable), can be used to implement '
			'zooming and scaling features.</p>'
			'<p>In addition the example shows how to use QPainter to '
			'print an image.</p>')
	
	def createActions(self):
		self.openAct = QAction('&Open...', self, shortcut='Ctrl+O',
			triggered=self.open)
		self.saveAct = QAction('&Save Markers...', self, shortcut='Ctrl+S',
			triggered=self.save)
		self.exitAct = QAction('E&xit', self, shortcut='Ctrl+Q',
			triggered=self.close)
		self.viewMarkersAct = QAction('View &Markers', self, enabled=True,
			checkable=True, shortcut='Ctrl+M', triggered=self.viewMarkers)
		self.viewMarkersAct.setChecked(True)
		self.zoomInAct = QAction('Zoom &In (25%)', self, shortcut='Ctrl++',
			enabled=False, triggered=self.zoomIn)
		self.zoomOutAct = QAction('Zoom &Out (25%)', self, shortcut='Ctrl+-',
			enabled=False, triggered=self.zoomOut)
		self.normalSizeAct = QAction('&Normal Size', self, shortcut='Ctrl+R',
			enabled=False, triggered=self.imageLabel.normalSize)
		self.fitToWindowAct = QAction('&Fit to Window', self, enabled=False,
			checkable=True, shortcut='Ctrl+F', triggered=self.fitToWindow)
		self.aboutAct = QAction('&About', self, triggered=self.about)
		self.aboutQtAct = QAction('About &Qt', self,
			triggered=QApplication.instance().aboutQt)
	
	def createMenus(self):
		self.fileMenu = QMenu('&File', self)
		self.fileMenu.addAction(self.openAct)
		self.fileMenu.addAction(self.saveAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)
		
		self.viewMenu = QMenu('&View', self)
		self.viewMenu.addAction(self.viewMarkersAct)
		self.viewMenu.addSeparator()
		self.viewMenu.addAction(self.zoomInAct)
		self.viewMenu.addAction(self.zoomOutAct)
		self.viewMenu.addAction(self.normalSizeAct)
		self.viewMenu.addSeparator()
		self.viewMenu.addAction(self.fitToWindowAct)
		
		self.helpMenu = QMenu('&Help', self)
		self.helpMenu.addAction(self.aboutAct)
		self.helpMenu.addAction(self.aboutQtAct)
		
		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)
	
	def updateActions(self):
		self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
		self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
		self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
	
	def scaleImage(self, factor):
		self.imageLabel.scale(factor)
		
		self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
		self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
		
		#self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
		#self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)
	
	def adjustScrollBar(self, scrollBar, factor):
		scrollBar.setValue(int(factor * scrollBar.value()
			+ ((factor - 1) * scrollBar.pageStep()/2)))



if __name__ == '__main__':
	app = QApplication(sys.argv)
	imageViewer = ImageViewer()
	imageViewer.show()
	sys.exit(app.exec_())

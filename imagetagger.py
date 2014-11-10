#!/usr/bin/env python3

import sys
from PyQt5.QtCore import QDir, QSize, QRect, Qt
from PyQt5.QtGui import QColor, QPen, QImage, QPainter, QPalette, QPixmap, QFont
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
	QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy)



class Marker:
	def __init__(self, x, y):
		self.x = x
		self.y = y



class MyLabel(QLabel):
	def __init__(self, parent=None):
		super(MyLabel, self).__init__(parent)
		self.markerList = []
		self.scaleFactor = 1.0
	
	def getScaleFactor(self):
		return self.scaleFactor

	def normalSize(self):
		self.scaleFactor = 1.0
		imageLabel.adjustSize()

	def scale(self, factor):
		self.scaleFactor *= factor
		self.resize(self.scaleFactor * self.pixmap().size())

	def paintEvent(self, event):
		super(MyLabel, self).paintEvent(event)
		if self.pixmap() is not None:
			painter = QPainter(self)
			painter.setRenderHint(QPainter.Antialiasing, True)
			painter.setPen(QPen(QColor(255, 0, 0, 255), 7))
			radius = 20
			for marker in self.markerList:
				x = marker.x * self.scaleFactor - radius
				y = marker.y * self.scaleFactor - radius
				painter.drawEllipse(QRect(x, y, 2*radius, 2*radius))

	def addMarker(self, x, y):
		self.markerList.append(Marker(x, y))



class ImageViewer(QMainWindow):
	def __init__(self):
		super(ImageViewer, self).__init__()
		
		self.imageLabel = MyLabel()
		self.imageLabel.setBackgroundRole(QPalette.Base)
		self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.imageLabel.setScaledContents(True)
		
		self.scrollArea = QScrollArea()
		self.scrollArea.setBackgroundRole(QPalette.Dark)
		self.scrollArea.setWidget(self.imageLabel)
		self.setCentralWidget(self.scrollArea)
		
		self.createActions()
		self.createMenus()
		
		self.setWindowTitle("Image Viewer")
		self.resize(500, 400)

	def open(self):
		fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
			QDir.currentPath())
		if fileName:
			image = QImage(fileName)
			if image.isNull():
				QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
				return
			
			self.imageLabel.setPixmap(QPixmap.fromImage(image))
			
			self.fitToWindowAct.setEnabled(True)
			self.updateActions()
			
			if not self.fitToWindowAct.isChecked():
			    self.imageLabel.adjustSize()
	
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
		QMessageBox.about(self, "About Image Viewer",
			"<p>The <b>Image Viewer</b> example shows how to combine "
			"QLabel and QScrollArea to display an image. QLabel is "
			"typically used for displaying text, but it can also display "
			"an image. QScrollArea provides a scrolling view around "
			"another widget. If the child widget exceeds the size of the "
			"frame, QScrollArea automatically provides scroll bars.</p>"
			"<p>The example demonstrates how QLabel's ability to scale "
			"its contents (QLabel.scaledContents), and QScrollArea's "
			"ability to automatically resize its contents "
			"(QScrollArea.widgetResizable), can be used to implement "
			"zooming and scaling features.</p>"
			"<p>In addition the example shows how to use QPainter to "
			"print an image.</p>")
	
	def createActions(self):
		self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
			triggered=self.open)
		self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
			triggered=self.close)
		self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
			enabled=False, triggered=self.zoomIn)
		self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
			enabled=False, triggered=self.zoomOut)
		self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S",
			enabled=False, triggered=self.imageLabel.normalSize)
		self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
			checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)
		self.aboutAct = QAction("&About", self, triggered=self.about)
		self.aboutQtAct = QAction("About &Qt", self,
			triggered=QApplication.instance().aboutQt)
	
	def createMenus(self):
		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction(self.openAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)
		
		self.viewMenu = QMenu("&View", self)
		self.viewMenu.addAction(self.zoomInAct)
		self.viewMenu.addAction(self.zoomOutAct)
		self.viewMenu.addAction(self.normalSizeAct)
		self.viewMenu.addSeparator()
		self.viewMenu.addAction(self.fitToWindowAct)
		
		self.helpMenu = QMenu("&Help", self)
		self.helpMenu.addAction(self.aboutAct)
		self.helpMenu.addAction(self.aboutQtAct)
		
		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)
	
	def updateActions(self):
		self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
		self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
		self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
	
	def mouseDoubleClickEvent(self, event):
		pos = self.imageLabel.mapFrom(self, event.pos()) / self.imageLabel.getScaleFactor()
		self.imageLabel.addMarker(pos.x(), pos.y())
		self.imageLabel.update()

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

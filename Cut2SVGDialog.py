# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cut2SVG
                                 A QGIS plugin
 Cut layers' vectors according to the map extent of the print composer for a clean svg export
                             -------------------
        begin                : 2018-03-23
        copyright            : (C) 2018 by S.Poudroux / Éveha
        email                : sebastien.poudroux@eveha.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

#using Unicode for all strings
from __future__ import unicode_literals

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import *
from qgis.core import *
from qgis.gui import *
from enum import Enum

# Import the processing functions 
from Cut2SVG_Process import Process

def selectComposer(name):
    composers = iface.activeComposers()
    for comp in composers:
        comp.composerWindow().close()
    for comp in composers:
        if comp.composerWindow().windowTitle() == name:
            comp.composerWindow().show()
            return comp


def closeComposer():
    composers = iface.activeComposers()
    for comp in composers:
        comp.composerWindow().close()

class Cut2SvgDialg(QDialog):
    def __init__(self):
        QDialog.__init__(self)


    def tr(self, message):
            return QCoreApplication.translate('Cut2SvgDialg', message)

    def ComposerList(self):
        self.comboBox_comp.clear()
        comp = iface.activeComposers()       
        comp_list = []
        for item in comp:
            name = item.composerWindow().windowTitle()
            comp_list.append(name)
        self.comboBox_comp.addItems(comp_list)

    def selectedComp(self):	 
		if self.comboBox_comp.currentText():
			return selectComposer(self.comboBox_comp.currentText())

    def getcompName(self):
        composers = iface.activeComposers()
        name = self.comboBox_comp.currentText()
        for comp in composers:
            nameComp = comp.composerWindow().windowTitle()
            if nameComp == name:
                return nameComp

    def getmapName(self):
        name = self.comboBox_map.currentText()
        comp = self.selectedComp()
        if comp is not None:
            mapItem = comp.composition()
            for item in mapItem.items():
                if item.type() == QgsComposerItem.ComposerMap and item.scene() and item.displayName() == name:
                    return item.displayName()

    def updateMap(self):
        self.comboBox_map.clear()
        comp = self.selectedComp()
        item_list =[]
        if comp is not None:
            mapItem = comp.composition()        
            for item in mapItem.items():
                if item.type() == QgsComposerItem.ComposerMap and item.scene():
                    item_list.append(item.displayName())
        self.comboBox_map.addItems(item_list)

    def selectMap(self):
        name = self.comboBox_map.currentText()
        comp = self.selectedComp()
        if comp is not None:
            mapItem = comp.composition()
            for item in mapItem.items():
                if item.type() == QgsComposerItem.ComposerMap and item.scene() and item.displayName() == name:
                    extent = item.extent()           
                    return extent
    
    def showExtent(self):
        name = self.comboBox_map.currentText()
        comp = self.selectedComp()
        if comp is not None:
            mapItem = comp.composition()
            for item in mapItem.items():
                if item.type() == QgsComposerItem.ComposerMap and item.scene() and item.displayName() == name:
                    extent = item.extent()  
                    canvas = iface.mapCanvas()
                    R = QgsRubberBand(canvas,True)
                    poly = QgsGeometry.fromRect(extent)
                    R.setToGeometry(poly, None)
                    R.setColor(QColor(0,0,255, 150))
                    R.setWidth(1)
                    R.show()
                    canvas.setExtent(extent)
                    canvas.refresh()

    def delRubber(self):
        scene = iface.mapCanvas().scene()
        rubber = [i for i in scene.items() if issubclass(type(i), QgsRubberBand)]
        for r in rubber:
            if r in scene.items():
                scene.removeItem(r)

    def selectedExtent(self):
        self.textEdit.clear()
        self.delRubber()
        name = self.comboBox_map.currentText()
        comp = self.selectedComp()
        if comp is not None:           
            self.showExtent()
            mapItem = comp.composition()
            for item in mapItem.items():
                if item.type() == QgsComposerItem.ComposerMap and item.scene() and item.displayName() == name:
                    coord= item.extent()    
                    xmin = coord.xMinimum()
                    xmax = coord.xMaximum()
                    ymin = coord.yMinimum()
                    ymax = coord.yMaximum()
                    coords = 'Xmin : {}'.format(xmin) + '\n' + 'Xmax : {}'.format(xmax) + '\n' + 'Ymin : {}'.format(ymin) + '\n' + 'Ymax : {}'.format(ymax)
                    self.textEdit.insertPlainText(coords)       
                    return self.textEdit.toPlainText()

    def zoomback(self):
        layer = iface.activeLayer()
        canvas = iface.mapCanvas()
        if layer:
            extent = layer.extent()
            canvas.setExtent(extent)
            canvas.refresh()

    def closeEvent(self, event):
        self.reset()
        	
    def reset(self):
        self.textEdit.clear()
        self.lineEdit_output.clear()
        self.delRubber()
        self.zoomback()

    def selectDirectory(self):
        self.lineEdit_output.setText(QFileDialog.getExistingDirectory(self)) 

    def output(self):
        directory = self.lineEdit_output.text() + '/' + self.getcompName() + '_' + self.getmapName()
        if not os.path.exists(directory):
            os.makedirs(directory)            
        return directory

    def outputName(self):
        return self.lineEdit_output.text()         
        
    def check(self):
        output = self.outputName()
        if output == '':
            msg = self.tr("Please specify an export folder.")
            QMessageBox.warning(self, 'Cut2SVG', msg)
            return

        layers = iface.mapCanvas().layers()
        if not layers:
            msg = self.tr("No activated layer(s) in the canvas!")
            QMessageBox.warning(self, 'Cut2SVG', msg)
            return

        crsproject=iface.mapCanvas().mapRenderer().destinationCrs()
        crs = crsproject.authid()
        layers = iface.mapCanvas().layers()
        list_error = []
           
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                lyrCRS = layer.crs().authid()
                if lyrCRS != crs:
                    list_error.append(layer.name())
        if list_error:
            ErrorDlg = QMessageBox(self)
            ErrorDlg.setWindowTitle('Cut2SVG')
            msg = self.tr("Some crs of the selected vector layers differ from the project's crs. Please reproject them.")
            ErrorDlg.setText(msg)
            error = self.tr('Layer concerned :' + '\n' + '\n'.join(str(name) for name in set(list_error)))
            ErrorDlg.setDetailedText(error)
            ErrorDlg.setIcon(QMessageBox.Critical)
            ErrorDlg.show()
            return

        layers = iface.mapCanvas().layers()
        list_error = []
          
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                for f in layer.getFeatures():
                    geom = QgsGeometry(f.geometry())
                    if not geom.isGeosValid():
                        list_error.append(layer.name())
        if list_error:
            ErrorDlg = QMessageBox(self)
            ErrorDlg.setWindowTitle('Cut2SVG')
            msg = self.tr('Invalid geometry in selected vector layer(s).')
            ErrorDlg.setText(msg)
            msg = self.tr('Please fix it with the help of the Qgis algorithm "Check Validity", for example.')
            ErrorDlg.setInformativeText(msg)
            error = self.tr('Number of errors : ' + str(len(list_error)) + '\n' + 'Layer containing invalid geometry :' + '\n' + '\n'.join(str(name) for name in set(list_error)))
            ErrorDlg.setDetailedText(error)
            ErrorDlg.setIcon(QMessageBox.Critical)
            ErrorDlg.show()
            return

        legend = iface.legendInterface()
        layers = iface.legendInterface().layers()
        #Disable displayed vector layer if completely overlapped by clipper or not inside clipper
        sel_list = []
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.wkbType()!=100 and legend.isLayerVisible(layer) == True:
                poly = QgsGeometry.fromRect(self.selectMap())
                extent = QgsGeometry.fromRect(layer.extent())
                if poly.intersects(extent):
                    sel_list.append(layer)
                    if poly.contains(extent):
                        sel_list.remove(layer)

        if not sel_list:
            ErrorDlg = QMessageBox()
            ErrorDlg.setWindowTitle('Cut2SVG')   
            msg = self.tr('''No layer to be cutted : The extent of the selected layers is already completely overlapped by the extent of the map composer,or doesn't intersecting it.''' + '\n' + 'You can export the map in SVG with confidence!')
            ErrorDlg.setText(msg)
            ErrorDlg.setIcon(QMessageBox.Critical)
            ErrorDlg.exec_()
            return

        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        output = self.output()
        files = []
        for f in os.listdir(output):
            if os.path.isfile(os.path.join(output, f)) and 'cut2SVG_' in f:
                files.append(f)
        if os.path.exists(output) and files != []:
            msg = self.tr("The export folder already contains the concerned shapefiles. Do you want to overwrite them?")
            pathdlg = QMessageBox.question(self,'cut2SVG', msg, QMessageBox.Yes, QMessageBox.No)
            if pathdlg == QMessageBox.Yes:
                for lyr in layers:
                    if 'cut2SVG_' in lyr.source():
                        QgsMapLayerRegistry.instance().removeMapLayers([lyr])
                for f in files :
                    QgsVectorFileWriter.deleteShapeFile(output + '/' + f)			
            else:
                return

        comp = self.selectedComp()
        mapName = self.comboBox_map.currentText()
        if comp is not None:
            mapItem = comp.composition()
            list_unlockedMap = []
            for item in mapItem.items():
                if item.type() == QgsComposerItem.ComposerMap and item.scene() and item.displayName() != mapName:
                    if not item.keepLayerSet():
                        list_unlockedMap.append(item)
            if list_unlockedMap:
                ErrorDlg = QMessageBox(self)
                ErrorDlg.setWindowTitle('Cut2SVG')
                msg = self.tr("Make sure to lock layers and styles for the other maps of the composer!")
                ErrorDlg.setText(msg)
                ErrorDlg.setIcon(QMessageBox.Warning)
                ErrorDlg.show()
                return
                       
        return True
        
    def accept(self):
        if not self.check():
            return
        map_extent = self.selectMap()
        output = self.output()
        compName = self.getcompName()
        mapName = self.getmapName()
        
        Process(map_extent, output, compName, mapName)
        self.close()
       
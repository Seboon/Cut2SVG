# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cut2SVG
                                 A QGIS plugin
 Cut layers' shapes according to the map extent of the print composer for a clean svg export
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

from __future__ import unicode_literals

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import *
from qgis.gui import *
import processing
import os

""" Processing functions for Cut2SVG."""


def replaceByIndex(text,index=0,replacement=''):
    return '%s%s%s'%(text[:index],replacement,text[index+1:])

def Process(extent, export, compName, mapName):
    # Create memory layer with polygon from map's extent
    crsproject = iface.mapCanvas().mapRenderer().destinationCrs()
    crs = str(crsproject.authid())
    clipper = QgsVectorLayer('Polygon?crs=' + crs , 'Cutter', 'memory')
    prov = clipper.dataProvider()
    QgsMapLayerRegistry.instance().addMapLayer(clipper)
    poly = QgsGeometry.fromRect(extent)
    feat = QgsFeature()
    feat.setGeometry(poly)
    prov.addFeatures([feat])

 
    legend = iface.legendInterface()
    layers = iface.legendInterface().layers()
    #Disable displayed vector layer if completely overlapped by clipper or not inside clipper
    sel_list = []
    for layer in layers:
        if layer.type() == QgsMapLayer.VectorLayer and layer.wkbType()!=100 and layer != clipper and legend.isLayerVisible(layer) == True:
            extent = QgsGeometry.fromRect(layer.extent())
            if poly.intersects(extent):
                sel_list.append(layer)
                if poly.contains(extent):
                    sel_list.remove(layer)

    #clip vector layer
    num = len(sel_list) + 1
    for layer in sel_list:
        num += -1
        output = export + "/cut2SVG_" + str(num) + "_" + layer.name() + ".shp"
        processing.runalg("qgis:intersection",layer,clipper,True,output)

    #create group
    root = QgsProject.instance().layerTreeRoot()
    group = root.insertGroup(0,"Cut2SVG")

    #load layers into created group
    groups = legend.groups()
    groupId = groups.index("Cut2SVG")
    layers_list =[]
    filename = [f for f in os.listdir(export) if f.startswith('cut2SVG_') and f.endswith('.shp')]
    for f in filename:
             name = f.strip('.shp')
             name = replaceByIndex(name,8)
             layer = QgsVectorLayer(os.path.join(export, f),name, 'ogr')
             layers_list.append(layer)
    
    for layer in layers_list:
        QgsMapCanvas().setExtent(layer.extent())
        QgsMapCanvas().setLayerSet([QgsMapCanvasLayer(layer)])
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        legend.moveLayer(layer,groupId) 

    #copy/paste style from originals layers 
    layer_source = []
    layer_target = []
    for layer in sel_list:
        layer_source.append(layer.name())
        layer_source_sorted = sorted(layer_source, key = str.lower)
    for child in group.children():
        node = root.findLayer(child.layer().id())
        layer_target.append(node.name())
        layer_target_sorted = sorted(layer_target, key = str.lower)

    for source,target in zip(layer_source_sorted, layer_target_sorted):
        layername = QgsMapLayerRegistry.instance().mapLayersByName(source)
        layertarget = QgsMapLayerRegistry.instance().mapLayersByName(target)
        for layer in layername:
            iface.setActiveLayer(layer)
            iface.actionCopyLayerStyle().trigger()
        for layer2 in layertarget:
            iface.setActiveLayer(layer2)
            iface.actionPasteLayerStyle().trigger()
            layer2.setProviderEncoding('SYSTEM') 
            layer2.dataProvider().setEncoding('SYSTEM') 

    #Hide originals layers
    for layer in sel_list:
        node = root.findLayer(layer.id())
        toogle = Qt.Checked if node.isVisible() == Qt.Unchecked else Qt.Unchecked
        node.setVisible(toogle)

    #Remove memory polygon layer
    QgsMapLayerRegistry.instance().removeMapLayer(clipper.id())
    
    #Update Canvas and Composer
    layer = iface.activeLayer()
    canvas = iface.mapCanvas()
    canvas.refreshAllLayers()
    legend = iface.legendInterface()
    layers = iface.legendInterface().layers()
    sel_list = []
    for layer in layers:
        if legend.isLayerVisible(layer) == True:
            sel_list.append(layer.id())
    for comp in iface.activeComposers():
        if comp.composerWindow().windowTitle() == compName:
            mapItem = comp.composition()
            item = [f for f in mapItem.items() if f.type() == QgsComposerItem.ComposerMap and f.scene() and f.displayName() == mapName]
            item = item[0]
            item.setKeepLayerSet(False) 
            item.updateItem()
            item.setLayerSet(sel_list)
            item.setPreviewMode(0)
            item.updateCachedImage()   
            item.setKeepLayerSet(True)
            item.setKeepLayerStyles(True)
            item.updateItem()
            mapItem.refreshItems() 
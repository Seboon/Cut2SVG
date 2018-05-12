# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cut2SVGDialog
                                 A QGIS plugin
 Cut layers' vectors according to the map extent of the print composer for a clean svg export
                             -------------------
        begin                : 2018-03-23
        git sha              : $Format:%H$
        copyright            : (C) 2018 by S.Poudroux / Éveha
        email                : sebastien.poudroux@eveha.fr
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

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Cut2SVGDialog import*

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Cut_2_SVG_dialog_base.ui'))


class Cut2SVGDialog(Cut2SvgDialg, FORM_CLASS):
    def __init__(self):
        """Constructor."""
        Cut2SvgDialg.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.ComposerList()
        QObject.connect(self.comboBox_comp, SIGNAL('currentIndexChanged(QString)'), self.updateMap)
        QObject.connect(self.comboBox_map, SIGNAL('currentIndexChanged(QString)'), self.selectedExtent)
        QObject.connect(self.pushButton, SIGNAL('clicked()'),self.selectDirectory)
        QObject.connect(self.button_box, SIGNAL('rejected()'), self.delRubber)
        QObject.connect(self.button_box, SIGNAL('rejected()'), closeComposer)
        QObject.connect(self.button_box, SIGNAL('rejected()'), self.zoomback)  
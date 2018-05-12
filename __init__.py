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
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Cut2SVG class from file Cut2SVG.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .Cut_2_SVG import Cut2SVG
    return Cut2SVG(iface)

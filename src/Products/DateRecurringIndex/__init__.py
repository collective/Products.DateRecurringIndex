#
# Copyright (c) 2007 by BlueDynamics Alliance, Klein & Partner KEG, Austria
#
# Zope Public License (ZPL)
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

__author__ = """Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

import logging
from App.Common import package_home

PROJECTNAME = 'Products.DateRecurringIndex'
logger = logging.getLogger(PROJECTNAME)
product_globals = globals()

def initialize(context):
    import index
    context.registerClass(
            index.DateRecurringIndex,
            permission='Add Pluggable Index',
            constructors=(index.manage_addDRIndexForm,
                          index.manage_addDRIndex),
            icon='www/index.gif',
            visibility=None
    )
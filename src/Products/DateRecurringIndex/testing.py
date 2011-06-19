from plone.testing import z2
from plone.testing import Layer

class DRILayer(Layer):

    defaultBases = (z2.STARTUP,)

    def setUp(self):
        with z2.zopeApp() as app:
            z2.installProduct(app, 'Products.DateRecurringIndex')

    def teasDown(self):
        with z2.zopeApp() as app:
            z2.uninstallProduct(app, 'Products.DateRecurringIndex')

DRI_FIXTURE = DRILayer()

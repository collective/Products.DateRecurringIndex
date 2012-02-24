from setuptools import setup, find_packages
import os

version = '2.0b1'
shortdesc = "Zope 2 date index with support for recurring events."
longdesc = open('README.rst').read() + "\n\n" +\
           open(os.path.join("docs", "HISTORY.rst")).read()
license = open(os.path.join("docs", "LICENSE.rst")).read()

setup(name='Products.DateRecurringIndex',
      version=version,
      description=shortdesc,
      long_description=longdesc + '\n\n' + license,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='zope zope2 index catalog date recurring',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='https://github.com/collective/Products.DateRecurringIndex',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ZODB3',
          'Zope2',
          'plone.event',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'interlude',
              'pytz',
              'plone.testing'
          ]},
)

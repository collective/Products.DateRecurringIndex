# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

from setuptools import setup, find_packages
import sys, os

version = '2.0-dev'
shortdesc = "Recurring Events, Index for Zope 2 Catalog. Replacement for old DateIndex."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
license = open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')).read()

setup(name='Products.DateRecurringIndex',
      version=version,
      description=shortdesc,
      long_description=longdesc + license,
      classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
      url='https://svn.plone.org/svn/collective/Products.DateRecurringIndex',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.event',
          # Zope 2 dependencies are missing
      ],
      extras_require={'test': [#'interlude',
                               'pytz']},
      entry_points={'console_scripts':
                    ['bench_dri = Products.DateRecurringIndex.bench:run']},
)


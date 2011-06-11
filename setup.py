# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD derivative License

from setuptools import setup, find_packages
import sys, os

version = '2.0-dev'
shortdesc = "Zope 2 date index with support for recurring events."
longdesc = open('README.txt').read() + "\n\n" +\
           open(os.path.join("docs", "HISTORY.txt")).read()
license = open(os.path.join("docs", 'LICENSE.txt')).read()

setup(name='Products.DateRecurringIndex',
      version=version,
      description=shortdesc,
      long_description=longdesc + '\n\n' + license,
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
          # -*- Extra requirements: -*-
          'ZODB3',
          'Zope2',
          'plone.event',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={'test': ['interlude',
                               'pytz']},
      entry_points={'plone.recipe.zope2instance.ctl':
                    ['benchmark_DateRecurringIndex_vs_DateIndex = Products.DateRecurringIndex.benchmark:run']},
)

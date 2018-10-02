# -*- coding: utf-8 -*-
"""Installer for the bda.aaf.site package."""

from setuptools import find_packages
from setuptools import setup


version = '3.0.1.dev0'
short_description = "Zope 2 date index with support for recurring events."
long_description = ('\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
    open('LICENSE.rst').read(),
]))


setup(
    name='Products.DateRecurringIndex',
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope2',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='zope zope2 index catalog date recurring',
    author='BlueDynamics Alliance',
    author_email='dev@bluedynamics.com',
    url='https://github.com/collective/Products.DateRecurringIndex',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['Products', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'BTrees',
        'plone.event',
        'Products.ZCatalog',
        'ZODB',
        'zope.interface',
        'zope.schema',
    ],
    extras_require={
        'test': [
            'pytz',
            'plone.testing'
        ]
    },
)

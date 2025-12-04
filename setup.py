"""Installer for the bda.aaf.site package."""

from setuptools import setup


version = "4.0.0a1.dev0"
short_description = "Zope 2 date index with support for recurring events."
long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
        open("LICENSE.rst").read(),
    ]
)


setup(
    name="Products.DateRecurringIndex",
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope2",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="zope zope2 index catalog date recurring",
    author="BlueDynamics Alliance",
    author_email="dev@bluedynamics.com",
    url="https://github.com/collective/Products.DateRecurringIndex",
    license="BSD",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "AccessControl",
        "BTrees",
        "plone.event",
        "ZODB",
        "Zope",
        "zope.interface",
        "zope.schema",
    ],
    extras_require={
        "test": [
            "pytz",
            "plone.testing",
            "Products.ZCatalog",
        ]
    },
)

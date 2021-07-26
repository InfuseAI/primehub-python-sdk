#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(name='primehub-python-sdk',
      version='1.0',
      description='PrimeHub SDK',
      author='qrtt1',
      author_email='qrtt1@infuseai.io',
      url='',
      entry_points={
          'console_scripts': ['primehub = primehub.cli:main']
      },
      python_requires=">=3.6",
      packages=find_packages(),
      install_requires=['requests'],
      package_data={
          'primehub': ['*.json']
      })

#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages  # type: ignore

setup(name='primehub-python-sdk',
      version='0.1',
      description='PrimeHub SDK',
      author='qrtt1',
      author_email='qrtt1@infuseai.io',
      url='https://github.com/InfuseAI/primehub-python-sdk',
      entry_points={
          'console_scripts': ['primehub = primehub.cli:main', 'doc-primehub = primehub.extras.doc_generator:main']
      },
      python_requires=">=3.6",
      packages=find_packages(),
      install_requires=['requests'],
      extras_require={'dev': [
          'pytest>=4.6',
          'pytest-flake8',
          'pytest-mypy',
          'pytest-cov',
          'Jinja2'
      ]},
      package_data={
          'primehub': ['*.json']
      })

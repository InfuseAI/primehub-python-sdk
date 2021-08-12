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
      install_requires=['requests', 'tabulate==0.8.9', 'types-tabulate==0.8.2'],
      extras_require={
          'dev': [
              'pytest>=4.6',
              'pytest-flake8',
              'pytest-mypy',
              'pytest-cov',
              'Jinja2',
              'twine'
          ],
      },
      project_urls={
          "Bug Tracker": "https://github.com/InfuseAI/primehub/issues",
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
          "Development Status :: 2 - Pre-Alpha"
      ],
      package_data={
          'primehub': ['*.json']
      })

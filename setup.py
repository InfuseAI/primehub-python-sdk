#!/usr/bin/env python
import os
from distutils.core import setup

from setuptools import find_packages  # type: ignore


def _get_version():
    version_file = os.path.normpath(os.path.join(os.path.dirname(__file__), 'primehub', 'VERSION'))
    with open(version_file) as fh:
        version = fh.read().strip()
        return version


setup(name='primehub-python-sdk',
      version=_get_version(),
      description='PrimeHub Python SDK',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='qrtt1',
      author_email='qrtt1@infuseai.io',
      url='https://github.com/InfuseAI/primehub-python-sdk',
      entry_points={
          'console_scripts': ['primehub = primehub.cli:main', 'doc-primehub = primehub.extras.doc_generator:main']
      },
      python_requires=">=3.6",
      packages=find_packages(),
      install_requires=['requests', 'tabulate==0.8.9', 'types-tabulate==0.8.2', 'types-requests'],
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
          "Development Status :: 4 - Beta"
      ],
      package_data={
          'primehub': ['*.json', 'VERSION']
      })

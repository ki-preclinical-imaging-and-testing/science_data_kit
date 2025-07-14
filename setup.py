#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the long description from README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='science_data_kit',
    version='0.1.0',
    description='A comprehensive toolkit for indexing, curating, and integrating multimodal research data using knowledge graph capabilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Science Data Kit Team',
    author_email='example@example.com',
    url='https://github.com/your-username/science_data_kit',
    packages=find_packages(exclude=['isa-api*', 'tests*']) + ['science_data_kit_extensions'],
    include_package_data=True,
    # Removed package_data for non-existent 'app' package
    install_requires=requirements,
    extras_require={
        'msgraph': [
            'msgraph-sdk-python>=1.0.0',
            'azure-identity>=1.12.0',
        ],
        'dropbox': [
            'dropbox>=11.36.0',
        ],
        'google': [
            'google-api-python-client>=2.86.0',
            'google-auth-httplib2>=0.1.0',
            'google-auth-oauthlib>=1.0.0',
        ],
        'jupyter': [
            'ipython>=9.0.0',
            'jupyter>=1.0.0',
        ],
        'viz': [
            'pillow>=11.0.0',
        ],
        'dev': [
            'mypy>=1.10.0',
            'black>=24.4.0',
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'sphinx>=7.3.0',
            'sphinx-rtd-theme>=2.0.0',
            'sphinx-autoapi>=3.0.0',
        ],
        'all': [
            'science_data_kit[msgraph,dropbox,google,jupyter,viz,dev]',
        ],
    },
    entry_points={
        'console_scripts': [
            'science_data_kit=science_data_kit.cli:main',
            'sdk=science_data_kit.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.12',
)

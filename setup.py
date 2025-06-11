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
    packages=find_packages(exclude=['isa-api*', 'tests*']),
    include_package_data=True,
    package_data={
        'app': [
            '.streamlit/*',
            'utils/*',
        ],
    },
    install_requires=requirements,
    extras_require={
        'isatools': [
            'isatools>=0.14.2',
        ],
        'isatools_full': [
            'isatools[mzml]>=0.14.2',
            'mzml2isa==1.1.1',
            'fastobo==0.13.0',
            'SQLAlchemy==1.4.52',
        ],
    },
    entry_points={
        'console_scripts': [
            'science_data_kit=run_app:main',
            'install_isatools=install_isatools:main',
            'install_isatools_py312=install_isatools_py312:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.10',
)

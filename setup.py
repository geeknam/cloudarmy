#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup


install_requires = [
    'troposphere', 'pyyaml', 'boto3', 'click'
]

print find_packages()

setup(
    name='cloudarmy',
    version='0.1',
    description='Cloudformation templating engine',
    url='https://blog.namis.me/',
    author='Nam Ngo',
    license='Apache License 2.0',
    packages=find_packages(exclude=['examples.*', 'examples']),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'cloudarmy = cloudarmy.cli.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
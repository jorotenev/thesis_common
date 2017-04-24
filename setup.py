"""
https://github.com/pypa/sampleproject
http://python-packaging.readthedocs.io/en/latest/minimal.html
"""
from setuptools import setup, find_packages
from os import path

setup(
    name='thesis_common',
    version='0.2.1',
    description='Common data structures, functions and modules for working with Venue data',
    long_description="Common data structures, functions and modules for working with Venue data",
    url='https://github.com/jorotenev/thesis_venue_common',
    author='Georgi Tenev & Ward Schodts',
    author_email='georgetenevbg@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    install_requires=['python-dateutil', 'redis>=2.10.5','enum34>=1.1.6']

)

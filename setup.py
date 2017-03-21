"""
https://github.com/pypa/sampleproject
http://python-packaging.readthedocs.io/en/latest/minimal.html
"""
from setuptools import setup, find_packages
from os import path

setup(
    name='venue_common',
    version='0.1',
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
    ],
    packages=find_packages(),
    install_requires=['python-dateutils']

)

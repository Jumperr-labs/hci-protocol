from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import setup
from codecs import open
from os import path

from hci_protocol import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hci-protocol',
    version=__version__,

    description='HCI Packet Parser',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/Jumperr-labs/hci-protocol',
    download_url='https://github.com/Jumperr-labs/hci-protocol/archive/{}.tar.gz'.format(__version__),

    # Author details
    author='Jumper Team',
    author_email='info@jumper.io',

    keywords=['ble', 'bluetooth', 'hci', 'parsing', 'jumper'],
    license='Apache 2.0',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Embedded Systems',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=['construct'],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
)

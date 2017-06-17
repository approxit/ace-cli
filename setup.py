from distutils.core import setup

from ace import __version__ as VERSION

setup(
    name='ace-cli',
    version=VERSION,
    packages=[
        'ace',
    ],
    entry_points={
        'console_scripts': [
            'ace=ace.cli:main',
        ],
    },
)

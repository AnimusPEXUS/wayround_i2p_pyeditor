#!/usr/bin/python3

from setuptools import setup


setup(
    name='wayround_i2p_pyeditor',
    version='0.4',
    description='Simple extansible editor with projects and outline',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_i2p_pyeditor',
    packages=[
        'wayround_i2p.pyeditor',
        'wayround_i2p.pyeditor.modes'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    entry_points={
        'console_scripts': 'pyeditor = wayround_i2p.pyeditor.main'
        },
    install_requires=['wayround_i2p_utils']
    )

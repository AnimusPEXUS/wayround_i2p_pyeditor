#!/usr/bin/python3

from setuptools import setup


setup(
    name='org_wayround_pyeditor',
    version='0.2.3',
    description='Simple extansible editor with projects and outline',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/org_wayround_pyeditor',
    packages=[
        'org.wayround.pyeditor',
        'org.wayround.pyeditor.modes'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    entry_points = {
        'console_scripts': 'pyeditor = org.wayround.pyeditor.main'
        },
    install_requires = ['org_wayround_utils']
    )

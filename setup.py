#!/usr/bin/python3

from distutils.core import setup


setup(
    name='org_wayround_pyeditor',
    version='0.2',
    description='Simple extansible editor with projects and outline',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/PyEditor',
    packages=[
        'org.wayround.pyeditor',
        'org.wayround.pyeditor.modules'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    entry_points = {
        'pyeditor': 'org.wayround.pyeditor.main'
        }
    )

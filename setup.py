#!/usr/bin/python3

from distutils.core import setup


setup(
    name='PyEditor',
    version='0.1',
    description='Simple editor with projects and outline',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    packages=[
        'org.wayround.pyeditor',
        'org.wayround.pyeditor.modules'
        ],
    classifiers=[
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ]
    )

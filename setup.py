#!/usr/bin/python3

from setuptools import setup


setup(
    name='wayround_org_pyeditor',
    version='0.3.3',
    description='Simple extansible editor with projects and outline',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_pyeditor',
    packages=[
        'wayround_org.pyeditor',
        'wayround_org.pyeditor.modes'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    entry_points={
        'console_scripts': 'pyeditor = wayround_org.pyeditor.main'
        },
    install_requires=['wayround_org_utils']
    )

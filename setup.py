#/usr/bin/env python3

from setuptools import setup

setup(
        name="korminote",
        version="0.71",
        author="Charles Schimmelpfennig",
        url="https://github.com/CharlesSchimmel/korminote",
        description="A full-featured Kodi remote with command or TUI interface",
        long_description=("Korminote is a python program that controls a kodi instance remotely. It has a terminal user interface and a command interface."),
        license="Creative Commons by-nc-sa",
        packages=['korminote'],
        scripts=['bin/korminote'],
        install_requires=['requests','blessed','fuzzywuzzy'],
        install_package_data=True,
    )


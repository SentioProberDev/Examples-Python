<!--
[![GitHub issues](https://img.shields.io/github/issues/SentioProberDev/SentioProberControlSamples.svg?maxAge=360)](https://github.com/SentioProberDev/SentioProberControlSamples/issues)
[![Version](https://img.shields.io/github/release/SentioProberDev
SentioProberControlSamples .svg?maxAge=360)](https://github.com/beltoforion/Magnetic-Pendulum/releases/tag/v1.3)
[![Github All Releases](https://img.shields.io/github/downloads/beltoforion/Magnetic-Pendulum/total.svg)](https://github.com/beltoforion/Magnetic-Pendulum/releases/tag/v1.3)
-->
# SentioProberControl - Samples

## Prerequisites

We recommand using Visual Studio Code for the development of Python code. Visual Studio Code is a free IDE with python support.
https://code.visualstudio.com/

Please make sure to also install the Python extensions. Visual Studio Code will prompt you for their installation when you open a
python project for the first time.

## Table of Contents

### [map_setup.py](https://github.com/SentioProberDev/SentioProberControlSamples/blob/master/map_setup.py)
Set up a round wafermap remotely

### [map_setup_rect.py](https://github.com/SentioProberDev/SentioProberControlSamples/blob/master/map_setup_rect.py)
Set up a recangular wafermap remotely

### [map_stepping.py](https://github.com/SentioProberDev/SentioProberControlSamples/blob/master/map_stepping.py)
Basic stepping over a wafermap without subsites

### [commands_direct_send.py](https://github.com/SentioProberDev/Examples-Python/blob/master/commands_direct_send.py)
Direct sending of low level remote commands via TCP/IP or GPIB (ADLINK)

## Instructions
1.) Download or clone the SentioProberControlSamples repository

2.) Download the latest version of the [Python bindings for SENTIO](https://github.com/SentioProberDev/SentioProberControl/releases/)
* Open the Assets Combobox and download the \*.tar.gz archive (i.e. sentio_prober_control-3.5.2.tar.gz)

3.) Install the SentioProberControl python bindings for SENTIO probe stations
You can install the package with pip from a terminal by typing the following command:

```python -m pip install --user sentio-prober-control-3.5.2.tar.gz```

<!--
[![GitHub issues](https://img.shields.io/github/issues/SentioProberDev/SentioProberControlSamples.svg?maxAge=360)](https://github.com/SentioProberDev/SentioProberControlSamples/issues)
[![Version](https://img.shields.io/github/release/SentioProberDev
SentioProberControlSamples .svg?maxAge=360)](https://github.com/beltoforion/Magnetic-Pendulum/releases/tag/v1.3)
[![Github All Releases](https://img.shields.io/github/downloads/beltoforion/Magnetic-Pendulum/total.svg)](https://github.com/beltoforion/Magnetic-Pendulum/releases/tag/v1.3)
-->
# SentioProberControl - Samples

This archive contains python sample code for remotely controlling a MPI Probe Station running the MPI SENTIO Software Suite.
In order to use the code you need a physical probe station or an Installation of the SENTIO control software running in demo mode on a local PC.

## Prerequisites

* To use this examples you need a Version of the [SENTIO Probe Station Control software](https://www.mpi-corporation.com/ast/engineering-probe-systems/mpi-sentio-software-suite/). You can run the software either in demo mode or in combination with a real probe station.
* We recommend using Visual Studio Code for the development of Python code. Visual Studio Code is a free IDE with python support. You can download it from here: https://code.visualstudio.com/. Please make sure to also install the Python extensions. Visual Studio Code will prompt you for their installation when you open a python project for the first time.

## Getting the samples to work

* Download or Clone this Archive
* Install Required Python Packages: ```pip install -r requirements.txt```
* Select and start a python file

## Table of Contents

### [map_setup.py](https://github.com/SentioProberDev/SentioProberControlSamples/blob/master/map_setup.py)
Set up a round wafermap remotely

### [map_setup_rect.py](https://github.com/SentioProberDev/SentioProberControlSamples/blob/master/map_setup_rect.py)
Set up a recangular wafermap remotely

### [map_stepping.py](https://github.com/SentioProberDev/SentioProberControlSamples/blob/master/map_stepping.py)
This example demonstrates basic stepping over a wafermap without subsites

### [commands_direct_send.py](https://github.com/SentioProberDev/Examples-Python/blob/master/commands_direct_send.py)
Direct sending of low level remote commands via TCP/IP or GPIB (ADLINK)

### [vision_camera_settings.py](https://github.com/SentioProberDev/Examples-Python/blob/master/vision_camera_settings.py)
This script shows how to set and change basic camera parameters.

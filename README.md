# eGuard_backend
Low power project backend
> More information about this project in the [eGuard_octa](https://github.com/eGuard-lopow/eGuard_octa) folder.

## Getting Started
- In order to pull submodules (nested git repos) run `git submodule update --init`
- Install dependencies by running `pip install -r requirements.txt`
- duplicate your keys template file by running `cp template_keys.json keys.json`
- Add your login information to `keys.json`
- run application by typing `python backend.py`

## Overview

The main application of the backend has the following structure:

![Backend UML](images/backend_uml.png?raw=true "Backend UML")

The Backend is the main application. It creates and initializes devices. Every device will be running in a seperate thread. the Device class contains everything to operate a device and handle it's data flow. Device objects can't communicate to each other and are completely isolated on the backend application.

## Miscellaneous Scripts

### split_data.py
Used to splits the dataset into 2 datasets for training and testing.

### test_fingerprinting.py
Benchmarks the multiple distance functions and k values of the knn algorithm. The dataset needs to be split prior to running this script. This makes use of the dataset.

### mapper.py
Gives u an overview of locations and amount of fingerprints on that location. Can be used to get an brief overview of the dataset.

## What's Next

- Improve dashboard scalability
- Allow downlink communication to set alert parameters remotely
- Arrange devices in seperate groups to be able to serve multiple costumers with the same backend application
- Interface to add, remove and manage devices while backend is running.

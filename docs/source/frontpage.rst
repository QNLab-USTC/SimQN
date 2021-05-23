
An introduction to QuantNetSim
=======================================

Brief
---------------------------------------

QuantNetSim is a discrete time scheduler designed for Quantum Network.
It is writen in ``python3`` with out any 3th-party libraries. Some examples are in ``example``.
The source code is in `Github <https://github.com/ertuil/QuantNetSim/>`_ .

**QuantNetSim is still in heavy development, API and Documents may change frequently.**
The documents is in `Documents <https://www.elliot98.top/QuantNetSim/>`_ 
including an `development manual <https://www.elliot98.top/QuantNetSim/develop.html>`_ and 
`api manual <https://www.elliot98.top/QuantNetSim/modules.html>`_


Features
--------------------------------------

* Easy: easy to use and develop quantum protocols
* Multifunctional: multiply models enabled, including Classic Model, BB84 Model and EPR Model
* High performance: in a benchmark, it is possible to deal 30000 events per second

.. todo::
    - [Y] Schedular, Topo, Timer and log
    - [Y] BB84 photon Sender and Receiver
    - [Y] Entanglement Network, Node, Link and Controller
    - [Y] Simple swapping, distillation and generation
    - [Y] Refact classic Sender, Receiver and repeator
    - [N] Physical Simulation on entanglement (Bell State, GHZ State)
    - [N] Performance enhancement
    - [N] Documents, Unit Testing

Packages
------------

This project has the following packages and directories.

.. code-block:: 

    - QuantNetSim       
    |- docs             Docs and manual
    |- dist             Packaged distribution package
    |- example          Some examples
    |- qns
    |  |- schedular     The module including a the discrete time scheduar and basic class
    |  |- timer         The timer module including a timer entity
    |  |- topo          The module for network topology
    |  |- log           The log module
    |  |- classic       A classic message network model
    |  |- bb84          A single photon network model
    |  |- quantum       A entanglement based network model
    |
    |- LICENSE          Open source license
    |- README.md        Readme
    |- setup.py         Package setup script

License
------------

> Copyright (C) 2021 Elliot Chen <elliot.98@outlook.com>

This repo is under MIT License, please refer to ``LICENSE`` file
# QuantNetSim

A discrete time scheduler designed for Quantum Network. QuantNetSim is writen in python3 with out any 3th-party libraries.

**Still in heavy development, api may change**

## Features
* Easy: easy to use and develop quantum protocols
* Multifunctional: multiply models enabled, including Classic Model, BB84 Model and EPR Model
* High performance: in a benchmark, it is possible to deal 30000 events per seconds

Todo List:
- [x] Schedular, Topo, Timer and log
- [x] BB84 photon Sender and Receiver
- [x] Entanglement Network, Node, Link and Controller
- [x] Simple swapping, distillation and generation
- [ ] Refact classic Sender, Receiver and repeator
- [ ] Physical Simulation on entanglement
- [ ] Documents 

## Requirements and installation
Python version > 3.7 is reiqured. To build QuantNetSim, setuptools is needed:
```
pip3 install
```

Run the following command to build QuantNetSim:
```
python3 setup.py build
```
Or
```
python3 setup.py install
```
to install a copy into system library

## Usage
TBD

## Models
TBD

## License
See `LICENSE` file
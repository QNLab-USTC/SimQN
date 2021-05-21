# QuantNetSim

A discrete time scheduler designed for Quantum Network. QuantNetSim is writen in python3 with out any 3th-party libraries. Some examples are in `example`.

**Still in heavy development, api may change**

## Features
* Easy: easy to use and develop quantum protocols
* Multifunctional: multiply models enabled, including Classic Model, BB84 Model and EPR Model
* High performance: in a benchmark, it is possible to deal 30000 events per second

Todo List:
- [x] Schedular, Topo, Timer and log
- [x] BB84 photon Sender and Receiver
- [x] Entanglement Network, Node, Link and Controller
- [x] Simple swapping, distillation and generation
- [ ] Refact classic Sender, Receiver and repeator
- [ ] Physical Simulation on entanglement
- [ ] Documents 

## Requirements and compile
Python version > 3.7 is reiqured. To build QuantNetSim, `setuptools` and `wheel` is needed:
```
pip3 install setuptools wheel
```

Run the following command to build QuantNetSim:
```
python3 setup.py bdist_wheel # build wheel format package
```

The following command will install QuantNetSim in system:
```
pip3 install dist/qns-<version>-none-any.whl
```

## Usage
TBD

## Models
TBD

## License

> Copyright (C) 2021 Elliot Chen <elliot.98@outlook.com>

This repo is under MIT License, please refer to `LICENSE` file
# QuantNetSim

A discrete time scheduler designed for Quantum Network. QuantNetSim is writen in python3 with out any 3th-party libraries. Some examples are in `example`.

> **进行开发请务必阅读[开发手册](https://github.com/ertuil/QuantNetSim/blob/dev/doc/%E5%BC%80%E5%8F%91%E6%89%8B%E5%86%8C.md)**
> **API documents are in [Documents](https://www.elliot98.top/QuantNetSim/)**

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
- [x] Refact classic Sender, Receiver and repeator
- [ ] Physical Simulation on entanglement (Bell State, GHZ State)
- [ ] Performance enhancement
- [ ] Documents, Unit Testing

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

## License

> Copyright (C) 2021 Elliot Chen <elliot.98@outlook.com>

This repo is under MIT License, please refer to `LICENSE` file
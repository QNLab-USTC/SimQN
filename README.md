# QuantNetSim

QuantNetSim is a network-layer simulator for the quantum networks. It is designed for quantum network evaluation, such as routing algorithms, transmission control protocols, network applications, resource allocations, and other scenarios. For more information, please refer to the [Documents](https://ertuil.github.io/QuantNetSim/).

## Features

* General Propose: For both QKD and entanglement based networks
* Multiple Backends: We provide Qubit backend and EPR backend
* Easy-to-Use: Utilities for large-scale network evaluation

## Requirements and compile

Python version > 3.7 is required. To build QuantNetSim, `setuptools` and `wheel` is needed:
```
pip3 install setuptools wheel
```

Run the following command to build QuantNetSim as a python package:
```
python3 setup.py bdist_wheel # build wheel format package
```

The following command will install QuantNetSim into the system library:
```
pip3 install dist/qns-<version>-none-any.whl
```

## License

> Copyright (C) 2021 Elliot Chen <elliot.98@outlook.com>

This repo is under MIT License, please refer to `LICENSE` file
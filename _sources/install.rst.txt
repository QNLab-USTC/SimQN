Install Guide
================================

Install stable version using `pip`
------------------------------------

The SimQN packet is provided by `pypi`. Thus, the stable version can be installed and upgraded with the following command:

.. code-block:: bash

   pip install -U qns

Install develop version from source
--------------------------------------

Also, the develop version can be installed from source. First, checkout the source code from `Github <https://github.com/ertuil/SimQN>`_.

.. code-block:: bash

    git checkout https://github.com/ertuil/SimQN.git
    cd SimQN

Then, install setuptools as the package tool:

.. code-block:: bash

    pip3 install setuptools wheel

And build the package:

.. code-block:: bash

   python3 setup.py bdist_wheel

This command build the package and it should be located in the `dist` directory, named `qns-<version>-py3-none-any.whl`. Finally, install the package to the system python library:

.. code-block:: bash

   pip3 install qns-<version>-py3-none-any.whl

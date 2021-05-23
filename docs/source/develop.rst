开发手册-CN
=======================================

项目介绍
-----------

本项目是一个离散时间调度器和一个量子网络仿真器。项目使用Python编写，以来的Python版本是 > 3.7.0。
在开发过程中，我们使用  `setuptools <https://pypi.org/project/setuptools/>`_
库来完成代码库的打包和分发，需要首先安装这个依赖：

.. code-block:: bash

    pip3 install setuptools wheel


代码开发和合作规范
---------------------------

我们代码和其他资料存放在 `Github <https://github.com/ertuil/QuantNetSim>`_ 上。
我们开发时候，请将代码上传到 ``dev`` 分支（非 `master` 分支）。

Python代码的编码规范和变量命名请参考 `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ 标准。
项目中每一个类、方法都需要存在注释（docstrings)，以便于文档自动生成工具可以快速生成API文档。
具体格式可以参考 ``scheduar`` 模块下的注释的语法。

代码运行和编译方法
----------------------

我们的项目使用 `setuptools <https://pypi.org/project/setuptools/>`_ 进行打包。

我们在开发的时候，可以使用命令

.. code-block:: bash

    python3 setup.py develop

将整个 qns 库通过软连接的方式安装到系统的Python库中，这样我们就可以import qns 库了。
这个时候，理论上 example 中的实例程序就可以正常运行了。

当我们完成一个阶段开发的之后，我们可以将整个 qns 库打包成二进制进行分发（比如上传到 pypi 网站上，这样任何人都可以使用 pip 命令安装了）。我们使用

.. code-block:: bash

    python3 setup.py bdist_wheel

命令就可以在 dist 文件夹中看到打包好的库文件`qns-<version>-py3-none-any.whl`了。

任何人只需要拿到这个 whl 文件，然后使用 pip 命令就可以将这个包安装到系统中：

.. code-block:: bash

    pip3 install qns-<version>-py3-none-any.whl

构建API文档
----------------------

我们使用 sphinx 来自动构建API文档，需要首先安装 sphinx 库:

.. code-block:: bash

    pip3 install sphinx sphinx_rtd_theme sphinx-autobuild

之后，在 docs 文件夹下运行命令

.. code-block:: bash

    sphinx-apidoc -o docs/source qns
    make html
    
即可编译生成静态文档。最后，使用下面的命令将其 push 到 github pages 上：

.. code-block:: bash

    git subtree push --prefix docs/build/html origin gh-pages

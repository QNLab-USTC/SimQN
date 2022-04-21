#    SimQN: a discrete-event simulator for the quantum networks
#    Copyright (C) 2021-2022 Lutong Chen, Jian Li, Kaiping Xue
#    University of Science and Technology of China, USTC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


ext_modules = [
    Extension('qns.simulator.ts', ['qns/simulator/ts.pyx']),
    Extension('qns.simulator.pool', ['qns/simulator/pool.pyx']),
    Extension('qns.simulator.simulator', ['qns/simulator/simulator.py']),
    Extension('qns.models.qubit.const', ['qns/models/qubit/const.py']),
    Extension('qns.models.qubit.gate', ['qns/models/qubit/gate.py']),
    Extension('qns.models.qubit.qubit', ['qns/models/qubit/qubit.py']),
    Extension('qns.models.qubit.decoherence', ['qns/models/qubit/decoherence.py']),
    Extension('qns.models.qubit.factory', ['qns/models/qubit/factory.py']),
    Extension('qns.models.qubit.utils', ['qns/models/qubit/utils.py']),
    Extension('qns.models.epr.bell', ['qns/models/epr/bell.py']),
    Extension('qns.models.epr.entanglement', ['qns/models/epr/entanglement.py']),
    Extension('qns.models.epr.maxed', ['qns/models/epr/mixed.py']),
    Extension('qns.models.epr.werner', ['qns/models/epr/werner.py']),
    Extension('qns.entity.cchannel.cchannel', ['qns/entity/cchannel/cchannel.py']),
    Extension('qns.entity.qchannel.qchannel', ['qns/entity/qchannel/qchannel.py']),
    Extension('qns.entity.qchannel.losschannel', ['qns/entity/qchannel/losschannel.py']),
    Extension('qns.entity.operator.operator', ['qns/entity/operator/operator.py']),
    Extension('qns.entity.memory.memory', ['qns/entity/memory/memory.py']),
    Extension('qns.network.route.dijkstra', ['qns/network/route/dijkstra.py']),
    Extension('qns.network.topology.topo', ['qns/network/topology/topo.py']),
    Extension('qns.network.topology.basictopo', ['qns/network/topology/basictopo.py']),
    Extension('qns.network.topology.gridtopo', ['qns/network/topology/gridtopo.py']),
    Extension('qns.network.topology.linetopo', ['qns/network/topology/linetopo.py']),
    Extension('qns.network.topology.randomtopo', ['qns/network/topology/randomtopo.py']),
    Extension('qns.network.topology.treetopo', ['qns/network/topology/treetopo.py']),
    Extension('qns.network.topology.waxmantopo', ['qns/network/topology/waxmantopo.py']),
    Extension('qns.network.protocol.bb84', ['qns/network/protocol/bb84.py']),
    Extension('qns.network.protocol.classicforward', ['qns/network/protocol/classicforward.py']),
    Extension('qns.network.protocol.node_process_delay', ['qns/network/protocol/node_process_delay.py']),
    ]


setup(
    name='qns',
    author='elliot',
    version="0.1.5",
    description='A discrete-event scheduler designed for quantum networks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/ertuil/SimQN",
    exclude_package_data={'docs': ['.gitkeep']},
    cmdclass={'build_ext': build_ext},
    ext_modules=cythonize(ext_modules),
    setup_requires=["numpy", "cython", "pandas", "twine", "wheel"],
    install_requires=["numpy", "pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)

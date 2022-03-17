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
    Extension('qns.simulator.simulator', ['qns/simulator/simulator.py']),
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
    ]


setup(
    name='qns',
    author='elliot',
    version='0.1.4',
    description='A discrete-event scheduler designed for quantum networks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/ertuil/SimQN",
    exclude_package_data={'docs': ['.gitkeep']},
    cmdclass={'build_ext': build_ext},
    ext_modules=cythonize(ext_modules),
    setup_requires=["numpy", "cython"],
    install_requires=["numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)

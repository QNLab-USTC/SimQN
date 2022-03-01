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
#    along with this program. If not, see <https://www.gnu.org/licenses/>.


from types import MethodType
from typing import Optional
import numpy as np
from qns.models.qubit.const import QUBIT_STATE_0
from qns.models.qubit.decoherence import PrefectMeasureErrorModel, PrefectOperateErrorModel, PrefectStorageErrorModel,\
        PrefectTransferErrorModel
from qns.models.qubit.qubit import Qubit


class QubitFactory():
    """
    QubitFactory is the factory class for building qubits with special error models.
    """
    def __init__(self, operate_decoherence_rate: float = 0, measure_decoherence_rate: float = 0,
                 store_error_model=PrefectStorageErrorModel, transfer_error_model=PrefectTransferErrorModel,
                 operate_error_model=PrefectOperateErrorModel, measure_error_model=PrefectMeasureErrorModel) -> None:
        """
        Args:
            operate_decoherence_rate (float): the operate decoherence rate
            measure_decoherence_rate (float): the measure decoherence rate
            store_error_model: a callable function for handing errors in quantum memory
            transfer_error_model: a callable function for handing errors in quantum channel
            operate_error_model: a callable function for handing errors in operating quantum gates
            measure_error_model: a callable function for handing errors in measuing the status
        """
        self.operate_decoherence_rate = operate_decoherence_rate
        self.measure_decoherence_rate = measure_decoherence_rate
        self.store_error_model = store_error_model
        self.transfer_error_model = transfer_error_model
        self.operate_error_model = operate_error_model
        self.measure_error_model = measure_error_model

    def __call__(self, state=QUBIT_STATE_0, rho: np.ndarray = None,
                 operate_decoherence_rate: Optional[float] = None, measure_decoherence_rate: Optional[float] = None,
                 name: Optional[str] = None) -> Qubit:
        """
        Args:
            state (list): the initial state of a qubit, default is |0> = [1, 0]^T
            operate_decoherence_rate (float): the operate decoherence rate
            measure_decoherence_rate (float): the measure decoherence rate
            name (str): the qubit's name
        """
        if operate_decoherence_rate is None:
            operate_decoherence_rate = self.operate_decoherence_rate
        if measure_decoherence_rate is None:
            measure_decoherence_rate = self.measure_decoherence_rate
        qubit = Qubit(state=state, rho=rho, operate_decoherence_rate=operate_decoherence_rate,
                      measure_decoherence_rate=measure_decoherence_rate, name=name)
        qubit.store_error_model = MethodType(self.store_error_model, qubit)
        qubit.transfer_error_model = MethodType(self.transfer_error_model, qubit)
        qubit.operate_error_model = MethodType(self.operate_error_model, qubit)
        qubit.measure_error_model = MethodType(self.measure_error_model, qubit)
        return qubit

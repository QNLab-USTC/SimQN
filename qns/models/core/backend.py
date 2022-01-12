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

class QuantumModel(object):
    """
    The interface to present the backend models, including qubit, epr and other models.
    """
    def storage_error_model(self, t: float = 0, **kwargs):
        """
        The error model for quantum memory.
        This function will change the quantum state or fidelity
        according to different backend models.

        Args:
            t: the time stored in a quantum memory. The unit it second.
            kwargs: other parameters
        """
        pass

    def transfer_error_model(self, length: float, **kwargs):
        """
        The error model for transmitting a qubit in quantum channel.
        This function will change the quantum state or fidelity
        according to different backend models.

        Args:
            length (float): the length of the channel
            kwargs: other parameters
        """
        pass

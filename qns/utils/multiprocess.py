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

import itertools
import multiprocessing
from typing import Optional, Dict
import pandas as pd
from qns.utils.log import logger as log

import signal


class MPSimulations():
    """
    MultiProcessSimulations will help users to perfrom multiple simulations
    with different experiment settings and leverage multiple processes.
    """
    def __init__(self, settings: Dict = {}, iter_count: int = 1, aggregate: bool = True,
                 cores: int = -1, name: Optional[str] = None) -> None:
        """
        Args:
            settings: a dictionary object that contains simulation settings,
                      e.g., {"node_num": [10, 20, 30], "request_num": [1, 2, 3], "memory_size": [50, 100]}
            iter_count (int): for each setting, the repeat number of the same experiments. (with different random seed)
            aggregate (bool): aggregate experiments with the same settings and
                              calculate mean and std
            cores (int): the number of CPUs, default is -1 means to use all CPUs.
            name (str): the name of this simulation.
        """
        self.settings = settings
        self.iter_count = iter_count
        self.name = name
        self.aggregate = aggregate
        self.cores = cores if cores > 0 else multiprocessing.cpu_count()

        self.data = pd.DataFrame()
        self.aggregated_data = pd.DataFrame()

        self._setting_list = []
        self._current_simulation_count = 0
        self._total_simulation_count = 0
        self._start_time = None
        self._end_time = None

    def run(self, setting: Dict = {}) -> Dict:
        """
        This function should be overwited by users to provide codes that run a single simulation.

        Args:
            setting (Dict): the simulation setting, e.g. {'node_num': 10, 'req_num': 10, 'memory_size': 50}
        Returns:
            a dictionary that contains all results, e.g. {'throughput': 100, 'fidelity': 0.88}
        """
        raise NotImplementedError
        return {}

    def _single_run(self, setting: Dict = {}):
        raw = {}
        log.info(f"start simulation [{setting['_id']+1}/{self._total_simulation_count}] {setting}")
        result = self.run(setting=setting)
        raw.update(setting)
        raw.update(result)
        log.info(f"finish simulation [{setting['_id']+1}/{self._total_simulation_count}] {result}")
        return raw

    def _init_worker(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def start(self):
        """
        Start the multiple process simulation
        """
        self.prepare_setting()
        pool = multiprocessing.Pool(processes=self.cores, initializer=self._init_worker)
        try:
            result = []
            for setting in self._setting_list:
                result.append(pool.apply_async(self._single_run, (setting,)))
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            print("terminating simulation")
            pool.terminate()
            pool.join()

        for r in result:
            try:
                raw_data = r.get()
            except Exception:
                print("[simulator] error in simulation")
                continue
            new_result = {}
            for k, v in raw_data.items():
                new_result[k] = [v]
            result_pd = pd.DataFrame(new_result)
            self.data = pd.concat([self.data, result_pd], ignore_index=True)

        if self.aggregate:
            mean = pd.DataFrame(self.data).drop(columns=["_id", "_group", "_repeat"])
            new_name = {}
            ck = mean.columns
            for k in ck:
                if k not in self.settings.keys():
                    new_name[k] = k+"_mean"
            mean = mean.rename(columns=new_name)
            mean = mean.groupby(by=list(self.settings.keys())).mean()

            std = pd.DataFrame(self.data).drop(columns=["_id", "_group", "_repeat"])
            new_name = {}
            ck = std.columns
            for k in ck:
                if k not in self.settings.keys():
                    new_name[k] = k+"_std"
            std = std.rename(columns=new_name)
            std = std.groupby(by=list(self.settings.keys())).std()
            self.aggregated_data = pd.merge(mean, std, on=list(self.settings.keys()))

    def prepare_setting(self):
        """
        Generate the experiment setting for each experiments.
        """
        keys = self.settings.keys()
        _tmp = []
        for k in keys:
            _tmp.append(self.settings.get(k, []))

        id_count = 0
        for setting in itertools.product(*_tmp):
            for j in range(self.iter_count):
                setting_dict = {}
                for i, k in enumerate(keys):
                    setting_dict[k] = setting[i]
                setting_dict["_repeat"] = j
                setting_dict["_group"] = id_count
                setting_dict["_id"] = id_count * self.iter_count + j
                self._setting_list.append(setting_dict)
            id_count += 1
        self._total_simulation_count = len(self._setting_list)
        self._current_simulation_count = 0

    def get_data(self):
        """
        Get the simulation results

        Returns:
            a result data in pd.DataFrame
        """
        return self.aggregated_data if self.aggregate else self.data

    def get_raw_data(self):
        """
        Get the original raw results, no matter aggregate is ``True`` or not.

        Returns:
            a result data in pd.DataFrame
        """
        return self.data

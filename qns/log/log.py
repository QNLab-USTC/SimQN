import os
import sys
from typing import Any, Optional
from qns.schedular.simulator import Simulator


class Log():
    '''
    ``Log`` is a simple log module to generate debug or statistics log.

    :param str filename: the log will be output to ``filename`` file.
    :param bool debug: the initial ``debug`` mode. 
    '''
    def __init__(self, filename=None, debug=False):
        self.simulator = None
        self.filename = filename
        self.set_debug(debug)
        self.set_file(filename)

    def __del__(self):
        self.file.close()

    def install(self, simulator: Simulator):
        '''
        ``install`` must be run to inject this log object into simulator.

        :param simulator: the simulator
        '''
        self.simulator = simulator
        self.simulator.log = self

    def _current_time(self):
        if self.simulator.status == "run":
            return "[ {:10.8f} ]\t".format(self.simulator.current_time)
        else:
            return "[ {:10} ]\t".format(self.simulator.status)

    def _exp_time(self):
        if self.simulator.status == "run":
            return "{:},\t".format(self.simulator.current_time)
        else:
            return self.simulator.status+","

    def set_debug(self, debug: bool):
        '''
        Set the ``debug`` mode

        :param bool debug: output debug log or not
        '''
        self.is_debug = debug

    def set_file(self, filename=None):
        '''
        Write log into ``filename``. If ``filename`` is ``None``, ``sys.stdout`` will be used.

        :param str filename: output filename
        '''
        if filename is None:
            self.file = sys.stdout
        else:
            self.file = open(filename, 'w')

    def info(self, fmt: str, *args):
        '''
        write ``info`` level log

        :param str fmt: the format string
        :param \*args: the string's parameters
        '''
        self.file.write(self._current_time())
        self.file.write("[info]\t")
        self.file.write(fmt.format(*args))
        self.file.write("\n")

    def warn(self, fmt: str, *args):
        '''
        write ``warn`` level log

        :param str fmt: the format string
        :param \*args: the string's parameters
        '''
        self.file.write(self._current_time())
        self.file.write("[warn]\t")
        self.file.write(fmt.format(*args))
        self.file.write("\n")

    def error(self, fmt: str, *args):
        '''
        write ``error`` level log

        :param str fmt: the format string
        :param \*args: the string's parameters
        '''
        self.file.write(self._current_time())
        self.file.write("[error]\t")
        self.file.write(fmt.format(*args))
        self.file.write("\n")

    def debug(self, fmt: str, *args):
        '''
        write ``debug`` level log. If ``debug`` is set to ``False``, the log will not be written.

        :param str fmt: the format string
        :param \*args: the string's parameters
        '''
        if self.is_debug:
            self.file.write(self._current_time())
            self.file.write("[debug]\t")
            self.file.write(fmt.format(*args))
            self.file.write("\n")

    def exp(self, fmt: str, *args):
        '''
        Write log in csv format. It can be used to output experiment data.

        :param str fmt: the format string
        :param \*args: the string's parameters
        '''
        self.file.write(self._exp_time())
        self.file.write(fmt.format(*args))
        self.file.write("\n")


log = Log()

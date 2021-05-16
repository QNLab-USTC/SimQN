import os, sys
from typing import Any, Optional
from qns.schedular.simulator import Simulator

class Log():
    def __init__(self, filename = None, debug = False):
        self.simulator = None
        self.filename = filename
        self.is_debug = debug
        if filename is None:
            self.file = sys.stdout
        else:
            self.file = open(filename,'w')

    def __del__(self):
        self.file.close()

    def install(self, simulator: Simulator):
        self.simulator = simulator

    def current_time(self):
        if self.simulator.status == "run":
            return "[ {:12.8f} ]\t".format(self.simulator.current_time)
        else:
            return self.simulator.status

    def exp_time(self):
        if self.simulator.status == "run":
            return "{:},\t".format(self.simulator.current_time)
        else:
            return self.simulator.status+","

    def set_debug(self, debug: bool):
        self.is_debug = debug

    def info(self,fmt: str, *args):
        self.file.write(self.current_time())
        self.file.write("[info]\t")
        self.file.write(fmt.format(*args))
        self.file.write("\n")

    def warn(self,fmt: str, *args):
        self.file.write(self.current_time())
        self.file.write("[warn]\t")
        self.file.write(fmt.format(*args))
        self.file.write("\n")
    
    def error(self,fmt: str, *args):
        self.file.write(self.current_time())
        self.file.write("[error]\t")
        self.file.write(fmt.format(*args))
        self.file.write("\n")

    def debug(self,fmt: str, *args):
        if self.is_debug:
            self.file.write(self.current_time())
            self.file.write("[debug]\t")
            self.file.write(fmt.format(*args))
            self.file.write("\n")

    # used for experiment output 
    def exp(self,fmt: str, *args):
        self.file.write(self.exp_time())
        self.file.write(fmt.format(*args))
        self.file.write("\n")


log = Log()
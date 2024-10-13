"""
Sleep Timer
Ixonblitz-MatOS
"""
from datetime import datetime
from typing import Optional,Any,TypeAlias
from multiprocessing import Process
from time import sleep as s
from sys import exit
Enumerable: TypeAlias = list|tuple|set|frozenset
class Sleep:
    def __init__(self,t:str,func:Any=exit,params: Optional[Enumerable]=None,debug:bool=False)->None:
        """
        init for sleep timer

        :param str t: Time to alert sleep; FORMAT: "03:57 AM"
        :return: None
        :rtype None
        :raises ValueError: Time string was in incorrect format
        """
        self.time=t
        self.runningProcess: Process|None = None
        self.finishFunction=func
        self.debug=debug
        self.params=params

    def _getTime(self)->str:
        """
        Get the current time to check on time

        :return: Time String
        :rtype str
        """
        return datetime.now().strftime("%I:%M %p")
    
    def _finish(self,forced:bool=False)->None:
        """
        End process and do finish function

        :param bool forced: if force kill
        :return: None
        :rtype None
        """
        if self.debug:print("_Finish Called")
        if forced:exit(-1)
        if self.params:
            if isinstance(self.params, (list, tuple)) and len(self.params) > 0:self.finishFunction(*self.params)
            elif len(self.params) == 1:self.finishFunction(self.params[0])
            else:self.finishFunction()
        self.finishFunction()
    
    def _start(self)->Any:
        """
        Actual Start Function

        :return: Any
        :rtype Any        
        """
        if self.debug:print("_Start Called")
        try:
            while True:
                if self._getTime()==self.time:break
                s(5)
                if self.debug:print(f"Time wrong: (EXPECTED: {self.time}) GOT {self._getTime()}")
            print(f"Time Passed;Finishing")
            self._finish()
        except KeyboardInterrupt:self._finish(True)
    def start(self,join:bool=False)->None:
        """
        Shell for starting the timer checker

        :param bool join: if joins process or not
        :return: None
        :rtype None
        """
        if self.debug:print("Start Called")
        a=Process(name="Sleep Timer",daemon=True,target=self._start)
        self.runningProcess=a
        self.runningProcess.start()
        if join:self.runningProcess.join()
    def finish(self)->None:
        """
        Shell for finish function

        :return: None
        :rtype None
        """
        self._finish()

from sleep import Sleep
from os import system
from sys import argv
import re
from multiprocessing import freeze_support
def finishFunction():
    print("shutdown")
    system("shutdown /s /t 1")
    

def validate_time_format(pattern,time_str):
    return pattern.match(time_str) is not None

if __name__=="__main__":
    freeze_support()
    time_pattern = re.compile(r'^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$')
    try:
        if validate_time_format(time_pattern,argv[1]):
            a=Sleep(argv,finishFunction)
            a.start(join=True)
    except Exception as e:pass
    print("The Time format is incorrect")
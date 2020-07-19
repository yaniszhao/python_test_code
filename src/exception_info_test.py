
import os,re,xlrd,types,sys

from datetime import *

def func():
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
        raise Exception
        print sys.exc_info()

    return (str(datetime.now()), f.f_code.co_filename, f.f_code.co_name, str(f.f_lineno))

def fun():
    x=1
    info=func()
    for i in info:
        print i
fun()
x=1



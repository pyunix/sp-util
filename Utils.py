from datetime import datetime
import logging
import os
import time
import sys

class SPVar():
       
    def __init__(self):
        self.StartTime = datetime.now()
        if os.environ.get("DateStamp") == None:
            self.DateStamp = f"{datetime.now():%Y%m%d-}"
        else:
            self.DateStamp = os.environ.get("DateStamp")
            
    def NewDateStamp(self,datestamp):
        if datestamp == None:
            self.DateStamp = f"{datetime.now():%Y%m%d-}"
        else:
            self.DateStamp = datestamp
            

class Logger():
        
    def __init__(self,name):
        self.SPBLACK="\033[30m"
        self.SPRED="\033[91m"
        self.SPGREEN="\033[92m"
        self.SPYELLOW="\033[93m"
        self.SPBLUE="\033[34m"
        self.SPMAGENTA="\033[95m"
        self.SPCYAN="\033[36m"
        self.SPWHITE="\033[37m"
        self.SPNORM="\033[00m"
        self.DEBUG_VVV = 7
        self.DEBUG_VV = 8
        self.DEBUG_V = 9
        self.DEBUG = logging.DEBUG
        self.INFO = logging.INFO
        self.WARN = logging.WARN
        self.ERROR = logging.ERROR
        self.CRITICAL = logging.CRITICAL
        self.debugcolor = self.SPBLUE
        self.warncolor = self.SPYELLOW
        self.infocolor = self.SPGREEN
        self.errorcolor = self.SPRED
        self.criticalcolor = self.SPMAGENTA
        self.level = self.INFO
        
        #logging.addLevelName(self.DEBUG_V,"v")
        logging.basicConfig(level=self.level)
        self.mylog = logging.getLogger(name)


    def SetLevel(self,level):
        self.mylog.setLevel(level)
        self.level = level
    
    #def v(self,msg,*args,**kws):
    #    self._log(self.DEBUG_V,f"{self.SPBLUE}{sys.argv[0]}: {msg}{self.SPNORM}\n",args,**kwargs)

    def debug(self,msg):
        if self.WARN >= self.level:
            print(f"{self.debugcolor}",end='',flush=True)
            self.mylog.debug(f"{sys.argv[0]}: {msg}{self.SPNORM}")

    def warn(self,msg):
        if self.WARN >= self.level:
            print(f"{self.warncolor}",end='',flush=True)
            self.mylog.warn(f"{sys.argv[0]}: {msg}{self.SPNORM}")
    
    def info(self,msg):
        if self.INFO >= self.level:
            print(f"{self.infocolor}",end='',flush=True)
            self.mylog.info(f"{sys.argv[0]}: {msg}{self.SPNORM}")
        
    def error(self,msg):
        if self.ERROR >= self.level:
            print(f"{self.errorcolor}",end='',flush=True)
            self.mylog.error(f"{sys.argv[0]}: {msg}{self.SPNORM}")
    
    def critical(self,msg):
        if self.CRITICAL >= self.level:
            print(f"{self.criticalcolor}",end='',flush=True)
            self.mylog.critical(f"{sys.argv[0]}: {msg}{self.SPNORM}")
#!/usr/local/bin/hrpsysjy
import os
import sys
import socket
import traceback
import math
import time
import java.lang.System

import rtm
import waitInput
#import bodyinfo
import OpenHRP
from OpenHRP.RobotHardwareServicePackage import SwitchStatus

from org.omg.CORBA import *
from org.omg.CosNaming import *
from org.omg.CosNaming.NamingContextPackage import *
from com.sun.corba.se.impl.encoding import EncapsOutputStream

from java.lang import System, Class

from RTC import *
from RTM import *
from OpenRTM import *
from _SDOPackage import *


import string, math, socket, time, sys
global rootnc, nshost

java.lang.System.setProperty('NS_OPT', '-ORBInitRef NameService=corbaloc:iiop:localhost:2809/NameService')
rtm.initCORBA()
global kobuki 
kobuki= rtm.findRTC("MobileRobot0")

if kobuki==None:
    print "no robot"

prof = kobuki.port("vel").get_port_profile()
prop = prof.properties
for p in prop:
    print "kobu",p.name
    if p.name == "dataport.data_type":
        print p.value.extract_string()



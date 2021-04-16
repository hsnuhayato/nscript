#!/usr/bin/jython
import os
import sys
import java.lang.System

from org.omg.CORBA import *
from org.omg.CosNaming import *
from org.omg.CosNaming.NamingContextPackage import *
from com.sun.corba.se.impl.encoding import EncapsOutputStream

from java.lang import System, Class

#should export path where includes openrtm.jar here
sys.path.append("/usr/local/share/java/openrtm.jar") 

from RTC import *
from RTM import *
from OpenRTM import *
from _SDOPackage import *


import string, math, socket
##
# \brief root naming context
#
rootnc = None

##
# \brief hostname where naming service is running
#
nshost = None
 

##
# \brief wrapper class of RT component
#
class RTcomponent:
	##
	# \brief constructor
	# \param self this object
	# \param ref IOR of RT component
	#
	def __init__(self, ref):
		self.ref = ref
		self.owned_ecs = ref.get_owned_contexts()
		self.ec = self.owned_ecs[0]
		self.ports = {}
		ports = self.ref.get_ports()
		for p in ports:
			prof = p.get_port_profile()
			name = prof.name.split('.')[1]
			self.ports[name] = p
	
	##
	# \brief get IOR of port
	# \param self this object
	# \param name name of the port
	# \return IOR of the port
	def port(self, name):
		try:
			p = self.ports[unicode(name)]
		except KeyError:
			p = findPort(self.ref, name)
			self.ports[unicode(name)] = p
		return p

	##
	# \brief get IOR of the service
	# \param self this object
	# \param instance_name instance name of the service
	# \param type_name type name of hte service
	# \param port_name port name which provides the service
	# \return IOR of the service
	def service(self, instance_name, type_name="", port_name=""):
		return findService(self, port_name, type_name, instance_name)

	##
	# \brief update default configuration set
	# \param self this object
	# \param nvlist list of pairs of name and value
	def setConfiguration(self, nvlist):
		setConfiguration(self.ref, nvlist)

        ##
	# \brief update value of the default configuration set
	# \param self this object	
	# \param name name of the property
	# \param value new value of the property
	def setProperty(self, name, value):
		self.setConfiguration([[name, value]])

        ##
	# \brief get value of the property in the default configuration set
	# \param self this object	
	# \param name name of the property
        # \return value of the property or None if the property is not found
	def getProperty(self, name):
		cfg = self.ref.get_configuration()
		cfgsets = cfg.get_configuration_sets()
		if len(cfgsets) == 0:
			print "configuration set is not found"
			return None
		cfgset = cfgsets[0]
		for d in cfgset.configuration_data:
			if d.name == name:
				return d.value.extract_string()
		return None		

	##
	# \brief show list of property names and values
	# \param self this object
	def properties(self):
		cfg = self.ref.get_configuration()
		cfgsets = cfg.get_configuration_sets()
		if len(cfgsets) == 0:
			print "configuration set is not found"
			return
		cfgset = cfgsets[0]
		for d in cfgset.configuration_data:
			print d.name,":",d.value.extract_string()
		

	##
	# \brief activate this component
	# \param self this object
	# \param ec execution context used to activate this component
	def start(self, ec=None):
		if ec == None:
			ec = self.ec
		if ec != None:
			ec.activate_component(self.ref)
			while self.isInactive(ec):
				time.sleep(0.01)

	##
	# \brief deactivate this component
	# \param self this object
	# \param ec execution context used to deactivate this component
	def stop(self, ec=None):
		if ec == None:
			ec = self.ec
		if ec != None:
			ec.deactivate_component(self.ref)
			while self.isActive(ec):
				time.sleep(0.01)

	##
	# \brief get life cycle state of the main execution context
	# \param self this object
	# \param ec execution context from which life cycle state is obtained
        # \return one of LifeCycleState value or None if the main execution context is not set
	def getLifeCycleState(self, ec=None):
		if ec == None:
			ec = self.ec
		if ec != None:
			return ec.get_component_state(self.ref)
		else:
			return None

	##
	# \brief check the main execution context is active or not
	# \param ec execution context
        # \retval 1 this component is active
        # \retval 0 this component is not active
        def isActive(self, ec=None):
		return LifeCycleState.ACTIVE_STATE == self.getLifeCycleState(ec)

	##
	# \brief check the main execution context is inactive or not
	# \param ec execution context
        # \retval 1 this component is inactive
        # \retval 0 this component is not inactive
        def isInactive(self, ec=None):
		return LifeCycleState.INACTIVE_STATE == self.getLifeCycleState(ec)

	##
	# \brief get instance name
	# \return instance name
	def name(self):
		cprof = self.ref.get_component_profile()
		return cprof.instance_name

def initCORBA():
    global rootnc, nshost, orb
    try:
        props = System.getProperties()
	
        NS_OPT="-ORBInitRef NameService=corbaloc:iiop:localhost:2809/NameService" 
    #args = string.split(System.getProperty("NS_OPT"))
        args = string.split(NS_OPT)
        #nshost = System.getProperty("NS_OPT").split(':')[2]
        #if nshost == "localhost" or nshost == "127.0.0.1":
        #    nshost = socket.gethostname()
        #print 'nshost =',nshost
        orb = ORB.init(args, props)

        nameserver = orb.resolve_initial_references("NameService");
        rootnc = NamingContextHelper.narrow(nameserver);
        return None
    except:
        print "initCORBA failed"


def findRTC(name, rnc=None):
    try:
        obj = findObject(name, "rtc", rnc)
        rtc = RTcomponent(RTObjectHelper.narrow(obj))
        cxts = rtc.ref.get_participating_contexts()
        if len(cxts) > 0:
            rtc.ec = cxts[0]
        return rtc
    except:
        return None

def findObject(name, kind="", rnc=None):
    nc = NameComponent(name,kind)
    path = [nc]
    if not rnc:
        rnc = rootnc
    return rnc.resolve(path)


initCORBA()

kobuki= findRTC("MobileRobot0")

if kobuki==None:
    print "no robot"
else:
    prof = kobuki.port("vel").get_port_profile()
    prop = prof.properties
    for p in prop:
        print "kobuki",p.name
#        if p.name == "dataport.data_type":
#            print p.value.extract_string()

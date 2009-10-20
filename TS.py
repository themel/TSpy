from SOAPpy.Client import SOAPProxy
import SOAPpy.Types
from sys import stderr


class Cell:
    """A generic interface to call TriggerSupervisor cell commands."""
    
    _ns = 'urn:ts-soap:3.0'
    _action='urn:xdaq-application:lid=13'
    _name=''
    _debug=False
    _proxy=None
    exceptionThreshold = -1

    _defaultAttributes = {'async':'false',
                          'cid':'2314893',
                          'sid':'2',               
                         }
    
    def __init__(self, uri, name):
        """Constructs a TSCell object that accesses a cell with SOAP interface at URI. name is used for debug purposes only."""
        self._name = name

        self._proxy = SOAPProxy(uri,
                                namespace = self._ns,
                                methodattrs = self._defaultAttributes,
                                soapaction = self._action
                                )
        self.handleWarning = self.defaultWarningHandler

    def setDebug(self,debug):
        self._debug = debug
        if(debug):
            SOAPpy.Config.debug = 1
        else:
            SOAPpy.Config.debug = 0

    def __getattr__(self, name):
        """ Returns either a TSProxy object that represents the command, so that
            cell.foo is a callable object (and you can do cell.foo(bar='bla'))."""
        return TSProxy(self, name)

    def defaultWarningHandler(self, method, res):
        if res.warningLevel > self.exceptionThreshold:
            raise CellException(method, res)
        else:
            stderr.write("**Warning**: Command %s of cell %s returned warning level %d: %s" % (method._method, self._name, res.warningLevel, res.warningMessage))
            return res.payload
        

        
class TSProxy:
    """A callable object that represents a TS cell command. Usually instantiated by accessing an attribute
       of a  TSCell instance."""
    _cell = None
    _method = ''
    
    def __init__(self, cell, methodName):
        self._cell = cell
        self._method = methodName

    def __call__(self, params=None, **kw):
        """The actual call handler. This supports calling the method in two styles - either using keyword arguments to specify
           name/value pairs like cell.method(arg1='foo', arg2=False) or with a single dictionary argument like
           cell.method({arg1 : 'foo', arg2 : False}). The latter is neccessary to support argument names that contain spaces.
           Note: the two conventions don't mix!"""
        if self._cell._debug:
            print "Calling command %s of cell %s..." % (self._method, self._cell._name) 

        if params:
            if kw:
                raise ValueError, "Called method %s of cell %s with mixed keyword/argument parameter style!" % (self._method, self._cell._name)
            # replace keyword arguments with the single dict argument
            kw = params

        # list comprehension: convert all args to SOAP types
        soapArgs = [ self.convertArgument(arg, kw) for arg in kw]

        # This looks worse than it is - it just gets python to call the method
        # specified by this proxy through the SOAPProxy object of the cell
        # (and with the transformed arguments).
        res = self._cell._proxy.__getattr__(self._method)(*soapArgs)

        if isinstance(res, SOAPpy.Types.compoundType) and hasattr(res, 'warningLevel') and res.warningLevel:
            return self._cell.handleWarning(self, res)

        return res
        
    def convertArgument(self,arg,dict):
        """Converts arguments given to the method call from Python to their appropriate encoding in
           TS SOAP."""
        value = dict[arg]

        # strings are clearly meant as strings
        if type(value) is str:
            value = String(value)

        # booleans are clearly booleans
        if type(value) is bool:
            value = Bool(value)

        # other types need to be specified (we don't know specifically
        # what type of integer is expected on the other end, for example)
        if isinstance(value,WrapType):
            return value.toSOAP(arg, self._cell)
        else:
            raise TypeError, "Unable to convert argument %s to appropriate TS type, please use a TS wrapper type (eg TS.UnsignedShort)!" % arg


class WrapType:
    """A wrapper that handles the mapping of the trigger supervisor command parameter types to SOAPpy types."""
    _type = None
    _value = None

    def __init__(self,value):
        self._value = value
    
    def toSOAP(self, name, cell):
        return self._type(name='param', data=self._value, attrs = {'xmlns' : cell._ns, 'name' : name})

# A laundry list of trivial implementations: We just need to map these basic types and encode
# like in the base class.
class UnsignedShort(WrapType):
    _type = SOAPpy.unsignedShortType

class UnsignedLong(WrapType):
    _type = SOAPpy.unsignedLongType

class String(WrapType):
    _type = SOAPpy.stringType

class Bool(WrapType):
    _type = SOAPpy.booleanType

class CellException(Exception):    
    _errorResult = None
    _method = None
    warningMessage = ''
    warningLevel = 0
    payload = None
    
    def __init__(self, method, errorResult):
        # internal data

        self._errorResult = errorResult
        self._method = method
        # easy access methods
        self.warningLevel = errorResult.warningLevel
        self.warningMessage = errorResult.warningMessage
        self.payload = errorResult.payload

    def __str__(self):
        return "Error from command %s in cell %s (warning level = %u): %s" % (self._method._method, self._method._cell._name,
                                                                              self._errorResult.warningLevel, self._errorResult.warningMessage)
    
                
    
        


# tweak SOAPpy - this is really evil stuff, but neccessary because the TS SOAP code
# is not very generous in what it accepts. We manipulate SOAPpy into using the XSIv3 and XSVv3
# namespaces, but using the tags 'xsi' and 'xsd' for them, since this is what TS expects.
from SOAPpy.NS import NS,invertDict

# set the tag -> namespace map to map xsi/xsd to the 2001 namespaces
NS.NSMAP[NS.XSI_T] = NS.XSI3
NS.NSMAP[NS.XSD_T] = NS.XSD3

# delete the mappings from xsi3/xsd3 to the 2001 namespaces
del NS.NSMAP[NS.XSI3_T]
del NS.NSMAP[NS.XSD3_T]

# correct the inverse map
NS.NSMAP_R = invertDict(NS.NSMAP)

# make sure that namespaceStyle='2001' also leads to xsi,xsd prefixes
NS.STMAP['2001'] = (NS.XSD_T, NS.XSI_T)
NS.STMAP_R = invertDict(NS.STMAP)

from SOAPpy.SOAPBuilder import SOAPBuilder

# override redundant definitions in SOAPBuilder to fit with NS
SOAPBuilder._env_ns = {NS.ENC: NS.ENC_T, NS.ENV: NS.ENV_T,
        NS.XSD: NS.XSD_T, NS.XSD2: NS.XSD2_T, NS.XSD3: NS.XSD_T,
        NS.XSI: NS.XSI_T, NS.XSI2: NS.XSI2_T, NS.XSI3: NS.XSI_T}

import SOAPpy.Config

# all three may be overkill, but at least it's clear what we're doing.
SOAPpy.Config.namespaceStyle='2001'
SOAPpy.Config.typesNamespaceURI = 'http://www.w3.org/2001/XMLSchema'
SOAPpy.Config.schemaNamespaceURI = 'http://www.w3.org/2001/XMLSchema-instance'

import TS
import xml.dom.minidom
import re

class HardwareFunction:
    """A class describing a GT Cell hardware function."""
    def __init__(self, name, description):
        self.name = name
        self.__doc__ = description    

class Board:
    """A class that represents a board in the GT crate. Mostly
       used as an accessor for the HardwareFunctio objects it contains
       (eg board.SOME_HW_FUNCTION = 'NewValue')"""

    _cell=None
    _functions={}
    _boardSlot=0
    _boardType=''

    def __init__(self, cell, boardType, boardSlot=0):
        self._cell = cell
        self._boardType = boardType
        self._boardSlot=boardSlot
        self._functions = {}
        
    def loadHardwareFunctions(self):
        """Initializes the list of hardware functions from the cell."""
        self._functions = {}
        # Ask cell for all hardware functions
        listString = self._cell.HardwareFunctionGet({'Board Type' : self._boardType, 'ONLY LIST ITEMS' : True})
        doc = xml.dom.minidom.parseString(listString)

        # fill _functions with the hw objects
        for el in doc.getElementsByTagName('HardwareFunction'):
            name = el.getAttribute('name').encode('utf-8')
            self._functions[name] = HardwareFunction(name, el.getAttribute('description').encode('utf-8'))
            
    def describe(self, name):
        """Returns the description of the HardwareFunction of a given name."""
        return self._functions[name].__doc__

    def functions(self):
        return self._functions.keys()

    def __getattr__(self, name):
        """Converts attribute get access to HardwareFunctionGet calls in the cell."""
        # if name start with _, it's a real attribute
        if name[0] == '_': return self.__dict__[name]
        
        # else it' probably a hardwareFunction
        if name in self._functions:
            value = self._cell.HardwareFunctionGet({'Board Type' : self._boardType,
                                                    'Board Slot' : TS.UnsignedShort(self._boardSlot),
                                                    'ONLY LIST ITEMS' : False,
                                                    'Item' : name })
            # TODO: Coerce numeric values or other stuff that's not a string per se?
            return value

        raise AttributeError, "No such hardware function on %s board: %s" % (self._boardType, name)


    def __setattr__(self,name,value):
        """Converts attribute set access to HardwareFunctionSet calls in the cell."""
        # if name start with _, it's a real attribute
        if name[0] == '_':
            self.__dict__[name] = value
            return
        
        if name in self._functions:
            self._cell.HardwareFunctionSet({'Board Type' : self._boardType,
                                            'Board Slot' : TS.UnsignedShort(self._boardSlot),
                                            'ONLY LIST ITEMS' : False,
                                            'Item' : name, 
                                            'Value' : str(value)})
        else:
            raise AttributeError, "Can't set %s: Not an attribute and not a hardware function!" % name

    def __setitem__(self,name,value):
        """A workaround for getting HWFs with characters that can't be in a python identifier."""
        return self.__setattr__(name,value)

    def __getitem__(self,name):
        """A workaround for getting HWFs with characters that can't be in a python identifier."""
        return self.__getattr__(name)   


class GTCell(TS.Cell):
    _boards = {}

    _boardNames = [
        'FDL', 'GTFE',
        'PSB9', 'PSB13', 'PSB14',
        'PSB15', 'PSB19', 'PSB20',
        'PSB21', 'GTL',
        'TCS', 'TIM' ]

    _boardAliases = {
        'PSBTT' : 'PSB9',
        'PSB1' : 'PSB13',
        'PSB2' : 'PSB14',
        'PSB3' : 'PSB15',
        }

        
    def __init__(self, uri, boards=_boardNames, aliases=_boardAliases):
        TS.Cell.__init__(self, uri, "GT Cell")

        # load all boards (or those specified)
        for name in boards:
            self.createBoard(name)

        # Create aliases (at least for the specified boards
        for alias in aliases:
            target = aliases[alias]
            if target in self._boards: 
                self._boards[alias] = self._boards[target]

        

    def createBoard(self, name):
        """Create a new board. Any letters are the board name, numbers at the end
           indicate a board slot."""
        match = re.match(r'([A-Za-z]+)([0-9]*)', name)
        if match:
            boardType = match.group(0)
            try:
                boardSlot = int(match.group(1))
            except:
                boardSlot = 0

            newBoard = Board(self, boardType, boardSlot)
            newBoard.loadHardwareFunctions()
            self._boards[name] = newBoard            
        else:
            raise AttributeError, "Don't understand board name %s!" % name
                
    def __getattr__(self, name):
        # real atributes start with _
        if name[0]=='_': return self.__dict__[name]

        # is this a board name?
        if name in self._boards:
            return self._boards[name]

        # else: pass to base class (it's a command call)
        return TS.Cell.__getattr__(self, name)

    




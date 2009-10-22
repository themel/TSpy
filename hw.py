import GTCrate
import TS
import xml.dom.minidom

cell = GTCrate.getGTCell()
cell.setDebug(False)

print "Value was: " + cell.GTFE.DAQ_BOARD_SLOT
print "Setting. "
cell.GTFE.DAQ_BOARD_SLOT = 93
print "Value is: " + cell.GTFE.DAQ_BOARD_SLOT


psb = cell.GTFE

print psb.functions()

# ignore errors here
cell.exceptionThreshold = 9999
for item in psb.functions():
    print "HardwareFunction %s has value %s.\nDescription:%s\n" % (item, psb[item], psb.describe(item))

import GTCrate

cell = GTCrate.getGTCell()



print "Value was: %d " % cell.GTFE.DAQ_BOARD_SLOT
old = cell.GTFE.DAQ_BOARD_SLOT
print "Setting. "
cell.GTFE.DAQ_BOARD_SLOT = old+1
print "Value is now %d "% cell.GTFE.DAQ_BOARD_SLOT

print "DAQ status for TCS: %s" % cell.GTFE['DAQ.Status.to.TCS']

psb = cell.PSB19
print psb.functions()

# ignore errors here
cell.exceptionThreshold = 9999
for item in psb.functions():
    print "HardwareFunction %s has value %s.\nDescription:%s\n" % (item, psb[item], psb.describe(item))

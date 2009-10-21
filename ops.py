import GTCrate
import TS

cell = GTCrate.getGTCell()
cell.setDebug(True)

print "Ping response: ", cell.PingMe()

op1 = cell.createOperation("GtRunOperation") 

print "Created new operation, id=%s" % op1._id

try:
    op2 = cell.createOperation("GtRunOperation", 'exists')
    # Don't destroy the operation when the object goes!
    op2.selfDestruct = False
except:
    # If creation failed, reuse existing instance.
    op2 = TS.Operation(cell, 'exists')

op2.configure(KEY='undead')



import GTCrate
import TS

cell = GTCrate.getGTCell()
cell.setDebug(True)

print "GTL.REC3.Status = ", cell.HardwareFunctionGet({
    'Board Type' : 'GTL',
    'Item' : 'REC3.Status'
    })

print "Crate status: ", cell.GetCrateStatus()

print "Read result: ",  cell.Read({ 'Board Serial Number' : 'TCS',
                  'Board Slot' : TS.UnsignedShort(7),
                  'Offset' : '0',
                  'Register' : 'TIMESLOT0'
                 })


# ignore warning levels <= 2000
cell.exceptionThreshold = 2000

print "Configure result:"
res = cell.Configure({ 'TSC KEY' : 'gt_2009_0' })

print cell.InterconnectionTest(configure = True,
                               load_pattern = True,
                               particle = 'CA1',
                               pattern = 'COUNTER_8',
                               seed = TS.UnsignedInt(923))

import TS

cell = TS.Cell('http://localhost:3228', "GT Cell");
#cell.setDebug(True)

params = {}
params['Board Type'] = 'GTL'
params['Item'] = 'REC3.Status'


print "GTL.REC3.Status=", cell.HardwareFunctionGet(params)

print cell.HardwareFunctionGet({
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

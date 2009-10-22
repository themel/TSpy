from GTCell import GTCell

host = 'localhost'
GTCellPort = 3228
TestCellPort = 3838
TestPort = 4328

def makeUrl(host, port):
    return 'http://%s:%d' % (host, port)

def getGTCell(**kw):
    return GTCell(makeUrl(host, GTCellPort), **kw)

def getGMTCell():
    return TS.Cell(makeUrl(host, GMTCellPort), "GMT Cell")

def getTestCell():
    return TS.Cell(makeUrl(host, TestCellPort), "Test Cell")



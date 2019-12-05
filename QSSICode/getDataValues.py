import sys
from QSSICode.createDatasets import createInitialDatasets


class Point():
    def __init__(self, datasetDict, xPoint, yPoint):
        self.dataValues = {}
        self.dataValues['x'] = xPoint
        self.dataValues['y'] = yPoint        
        for key in datasetDict:
            if key == 'velocity':
                self.dataValues[key] = round(((datasetDict['VY'].getInterpolatedValue(yPoint, xPoint))** 2 + (datasetDict['VX'].getInterpolatedValue(yPoint, xPoint)) **2)**.5, 3)    
            else:
                self.dataValues[key] = round(datasetDict[key].getInterpolatedValue(yPoint, xPoint), 3)
        # millimeters -> meters then water-equivalent to ice-equivalent
        self.dataValues['smb'] = round(self.dataValues['smb'] * (1.0 / 1000.0) * (916.7 / 1000.0), 2)
        if abs(self.dataValues['surface'] - self.dataValues['thickness'] - self.dataValues['bed']) < 2:
            self.dataValues['bed'] = round(self.dataValues['surface'] - self.dataValues['thickness'],3)
def main(argv):
    myDictionary = createInitialDatasets()
    myPoint = Point(myDictionary, -98998.55768989387, -2159531.8275367804)
    print(myPoint.dataValues)

if __name__ == '__main__':
    main(sys.argv)

import time
import h5py
import numpy as np
import sys
from pylab import sqrt, linspace
from scipy.interpolate import RectBivariateSpline






def createInitialDatasets(fileName):
    print("Creating data sets")
    t0 = time.time()

    datasetDict = {}

    dataFile = h5py.File(fileName, 'r')
    x = dataFile['x'][:]
    y = dataFile['y'][:]
    dataFile.close()
    velocity = Dataset('velocity',fileName, x, y)
    datasetDict['velocity'] = velocity

    smb = Dataset('smb',fileName, x, y)
    datasetDict['smb'] = smb

    bed = Dataset('bed',fileName, x, y)
    datasetDict['bed'] = bed

    surface = Dataset('surface',fileName, x, y)
    datasetDict['surface'] = surface

    thickness = Dataset('thickness',fileName, x, y)
    datasetDict['thickness'] = thickness

    t2m = Dataset('t2m',fileName, x, y)
    datasetDict['t2m'] = t2m

    datasetDict['VX'] = Dataset('vx',fileName, x, y)
    datasetDict['VY'] = Dataset('vy',fileName, x, y)


    for i in range(12):
        keyName = 'precip' + str(i)
        datasetDict[keyName] = Dataset(keyName,fileName, x, y)

    print("Loaded all data sets in ", time.time() - t0, " seconds")
    return datasetDict



class Dataset:
    def __init__(self, name,fileName, x, y):
        self.name = name
        self.x = x
        self.y = y

        self.data = self.setData(name, fileName)
        if self.y[0] > self.y[1]:
            self.y = self.y[::-1]
            self.data = np.flipud(self.data)
      
        self.interp = None
        #Storing this Rect object is importante!
        if self.name == 'vx' or self.name =='vy':
            self.interp = RectBivariateSpline(self.y, self.x, self.data)


    def setData(self, name, fileName):
        dataFile = h5py.File(fileName, 'r')
        if name == 'velocity':
            vx = dataFile['vx'][:]
            vy = dataFile['vy'][:]
            data = sqrt(vx ** 2 + vy ** 2).astype(np.float64)
            dataFile.close()
            return data
        elif 'precip' in name:
            whichMonth = int(name[6:])
            data = dataFile['precip'][whichMonth][:]
            return data
        else:
            data = dataFile[name][:]
            dataFile.close()
            return data

    def getInterpolatedValue(self, yPosition, xPosition):
        if self.name == 'vx' or self.name == 'vy':
            return self.interp(yPosition, xPosition)[0][0]
        else:
            xMin, xMax = self.x[0], self.x[-1]
            yMin, yMax = self.y[0], self.y[-1]
            spacingX = (xMax - xMin)/(len(self.x)-1)
            spacingY = (yMax - yMin)/(len(self.y)-1)
            xIndex = int(round(xPosition - xMin)/spacingX)
            yIndex = int(round(yPosition - yMin)/spacingY)
            return self.data[yIndex][xIndex]
           
            
            
            



def main(argv):
    myDataset = createInitialDatasets()
    print(myDataset['velocity'])

if __name__ == '__main__':
    main(sys.argv)

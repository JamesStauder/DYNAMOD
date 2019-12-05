import sys
import numpy as np
from QSSICode.support.FlowIntegrator import FlowIntegrator
from QSSICode.getDataValues import Point
from QSSICode.translation import LonLatToProj, ProjToLatLon


class Flowline():
    def __init__(self, xStart, yStart, datasetDict, threshold, stepSize, extLength, projCode):

        self.mainUp = []
        self.mainDown = []  
        self.terminusUp = []
        self.terminusDown = []
        self.shearOne = []
        self.shearTwo = []

        integrator = FlowIntegrator(datasetDict['VX'], datasetDict['VY'])
        
        extensionLength = extLength

        self.mainUp.append([xStart,yStart])
        self.mainUp = integrator.integrate(xStart, yStart, self.mainUp, stepSize, threshold, -1, -1)

        self.mainDown.append([xStart, yStart])
        self.mainDown = integrator.integrate(xStart, yStart, self.mainDown, stepSize, threshold, 1, 1, extensionDist = extensionLength)
        self.mainDown = self.mainDown[1:]

        termStepFactor = 3
        termIndex = -10 - extensionLength
        velAtTerminus = integrator.vMags[termIndex]
        termThreshold = velAtTerminus * .5
        shearIndex = -1
        lengthFactor = .5

        self.terminusUp.append(self.mainDown[termIndex])
        self.terminusUp = integrator.integrate(self.terminusUp[0][0], self.terminusUp[0][1], self.terminusUp, stepSize/termStepFactor, termThreshold, 1, -1, perpendicular = True)
        
        self.terminusDown = integrator.integrate(self.terminusUp[0][0], self.terminusUp[0][1], self.terminusDown, stepSize/termStepFactor, termThreshold, -1, 1, perpendicular = True)

        self.shearOne.append(self.terminusDown[shearIndex])
        self.shearOne = integrator.integrate(self.shearOne[0][0], self.shearOne[0][1], self.shearOne, stepSize, threshold, -1,-1)
        
        self.shearTwo.append(self.terminusUp[shearIndex])
        self.shearTwo = integrator.integrate(self.shearTwo[0][0], self.shearTwo[0][1], self.shearTwo, stepSize, threshold, -1, -1)

        shearMoveIndexCounter = 1
        while (len(self.shearOne) < lengthFactor * (len(self.mainDown) + len(self.mainUp))):
            self.shearOne = []
            self.shearOne.append(self.terminusDown[shearIndex - shearMoveIndexCounter])
            self.shearOne = integrator.integrate(self.shearOne[0][0], self.shearOne[0][1], self.shearOne, stepSize, threshold, -1,-1)
            shearMoveIndexCounter += 1

        shearMoveIndexCounter = 1
        while (len(self.shearTwo) < lengthFactor * (len(self.mainDown) + len(self.mainUp))):
            self.shearTwo = []
            self.shearTwo.append(self.terminusUp[shearIndex - shearMoveIndexCounter])
            self.shearTwo = integrator.integrate(self.shearTwo[0][0], self.shearTwo[0][1], self.shearTwo, stepSize, threshold, -1,-1)
            shearMoveIndexCounter += 1


        self.shearTwoDown  = []
        self.shearTwoDown.append(self.shearTwo[0])
        self.shearTwoDown = integrator.integrate(self.shearTwoDown[0][0], self.shearTwoDown[0][1], self.shearTwoDown, stepSize, threshold, 1, 1, extensionDist = extensionLength)
        self.shearTwo = self.shearTwoDown[::-1] + self.shearTwo[1:]

        self.shearOneDown  = []
        self.shearOneDown.append(self.shearOne[0])
        self.shearOneDown = integrator.integrate(self.shearOneDown[0][0], self.shearOneDown[0][1], self.shearOneDown, stepSize, threshold, 1, 1, extensionDist = extensionLength)
        self.shearOne = self.shearOneDown[::-1] + self.shearOne[1:]
 
        self.mainDown = self.mainDown[::-1]
        self.shearOne = np.asarray(self.shearOne)
        self.shearTwo = np.asarray(self.shearTwo)

        self.midFlowline = self.mainDown + self.mainUp
        self.midFlowline = np.asarray(self.midFlowline)

        self.clickedIndex = len(self.mainDown) - extLength - 1
        
        minShear = min(len(self.shearOne), len(self.shearTwo), len(self.midFlowline))

        self.shearOne = self.shearOne[:minShear]
        self.shearTwo = self.shearTwo[:minShear]
        self.midFlowline = self.midFlowline[:minShear]
        

        self.widths = ((self.shearOne[:,:1] - self.shearTwo[:,:1])**2 + (self.shearOne[:,1:]-self.shearTwo[:,1:])**2)**.5

        shearOneX = self.shearOne[:,:1]
        shearOneY = self.shearOne[:,1:]

        shearTwoX = self.shearTwo[:,:1]
        shearTwoY = self.shearTwo[:,1:]

        numSamplePoints = 10
        changeX = (shearTwoX - shearOneX)/numSamplePoints
        changeY = (shearTwoY - shearOneY)/numSamplePoints        

        self.samplePoints = []
        self.samplePoints.append(self.shearOne)

        for i in range(numSamplePoints):
            newX = self.samplePoints[-1][:,:1] + changeX
            newY = self.samplePoints[-1][:,1:] + changeY
            self.samplePoints.append(np.column_stack((newX,newY)))

        self.samplePoints = np.asarray(self.samplePoints)

        flowlineLatLon = ProjToLatLon(self.midFlowline,projCode)

        flowlineData = {}
        avgFlowlineData = {}

        for i in range(len(self.midFlowline)):
            flowlineData[i] = Point(datasetDict, self.midFlowline[i][0], self.midFlowline[i][1]).dataValues
            flowlineData[i]['lat'], flowlineData[i]['lng'] = flowlineLatLon.latPoints[i], flowlineLatLon.lonPoints[i]
            flowlineData[i]['width'] = np.ndarray.tolist(self.widths[i])[0]

            vels, beds, surfs, smbs, thicks, t2ms = [], [], [], [], [], []
            precips = []
            avgFlowlineData[i] = {}
            for month in range(12):
                precips.append([]) 
            for j in range(len(self.samplePoints)):
                samplePoint = Point(datasetDict, self.samplePoints[j][i][0], self.samplePoints[j][i][1]).dataValues
                vels.append(samplePoint['velocity'])
                beds.append(samplePoint['bed'])
                surfs.append(samplePoint['surface'])
                thicks.append(samplePoint['thickness'])
                t2ms.append(samplePoint['t2m'])
                smbs.append(samplePoint['smb'])
                for month in range(12):
                    keyString = 'precip' + str(month)
                    precips[month].append(samplePoint[keyString])

            avgFlowlineData[i]['smb'] = np.average(smbs)
            avgFlowlineData[i]['velocity'] = (np.average(vels))
            avgFlowlineData[i]['surface'] = (np.average(surfs))
            avgFlowlineData[i]['thickness'] = (np.average(thicks))
            avgFlowlineData[i]['t2m'] = (np.average(t2ms))
            for month in range(12):
                keyString = 'precip' + str(month)
                avgFlowlineData[i][keyString] = (np.average(precips[month]))

            avgBed = np.average(beds)
            if 1 > abs(avgFlowlineData[i]['surface'] - avgFlowlineData[i]['thickness'] - avgBed):
                avgFlowlineData[i]['bed'] = avgFlowlineData[i]['surface'] - avgFlowlineData[i]['thickness']
            else:
                avgFlowlineData[i]['bed'] = avgBed

        self.flowlineData = flowlineData
        self.avgFlowlineData = avgFlowlineData       

##This is a lot of repeated code however this algorithm is different, and could change drastically so we made it it's own class
class FlowlineAnt():
    def __init__(self, xStart, yStart, datasetDict, threshold, stepSize, extLength, projCode):


        self.mainUp = []
        self.mainDown = []  
        self.terminusUp = []
        self.terminusDown = []
        self.shearOne = []
        self.shearTwo = []
        shearIndex = -1

        integrator = FlowIntegrator(datasetDict['VX'], datasetDict['VY'])
        
        extensionLength = extLength

        self.mainUp.append([xStart,yStart])
        self.mainUp = integrator.integrate(xStart, yStart, self.mainUp, stepSize, threshold, -1, -1)

        self.mainDown.append([xStart, yStart])
        self.mainDown = integrator.integrate(xStart, yStart, self.mainDown, stepSize, threshold, 1, 1)
        self.mainDown = self.mainDown[1:]

        termStepFactor = 5
        termIndex = 10
        velAtTerminus = integrator.vMags[termIndex]
        termThreshold = velAtTerminus * .5
        lengthFactor = .6


        self.terminusUp.append(self.mainUp[termIndex])
        self.terminusUp = integrator.integrate(self.terminusUp[0][0], self.terminusUp[0][1], self.terminusUp, stepSize/termStepFactor, termThreshold, 1, -1, perpendicular = True)
        
        self.terminusDown = integrator.integrate(self.terminusUp[0][0], self.terminusUp[0][1], self.terminusDown, stepSize/termStepFactor, termThreshold, -1, 1, perpendicular = True)

        self.shearOne.append(self.terminusDown[shearIndex])
        self.shearOne = integrator.integrate(self.shearOne[0][0], self.shearOne[0][1], self.shearOne, stepSize, threshold, 1, 1)
        
        self.shearTwo.append(self.terminusUp[shearIndex])
        self.shearTwo = integrator.integrate(self.shearTwo[0][0], self.shearTwo[0][1], self.shearTwo, stepSize, threshold, 1, 1)

        print (velAtTerminus)
        print (len(self.shearOne))
        print (len(self.shearTwo))
        print (len(self.mainDown) + len(self.mainUp))
        print ("shears found, centering")
        shearMoveIndexCounter = 1
        while (len(self.shearOne) < lengthFactor * (len(self.mainDown) + len(self.mainUp))):
            self.shearOne = []
            self.shearOne.append(self.terminusDown[shearIndex - shearMoveIndexCounter])
            self.shearOne = integrator.integrate(self.shearOne[0][0], self.shearOne[0][1], self.shearOne, stepSize, threshold, 1, 1)
            shearMoveIndexCounter += 1

        shearMoveIndexCounter = 1
        while (len(self.shearTwo) < lengthFactor * (len(self.mainDown) + len(self.mainUp))):
            self.shearTwo = []
            self.shearTwo.append(self.terminusUp[shearIndex - shearMoveIndexCounter])
            self.shearTwo = integrator.integrate(self.shearTwo[0][0], self.shearTwo[0][1], self.shearTwo, stepSize, threshold, 1, 1)
            shearMoveIndexCounter += 1


        print ("centered")
        
        print (len(self.shearOne))
        print (len(self.shearTwo))
        print (len(self.mainDown) + len(self.mainUp))
 
        self.mainDown = self.mainDown[::-1]
        self.shearOne = np.asarray(self.shearOne)
        self.shearTwo = np.asarray(self.shearTwo)

        self.midFlowline = self.mainDown + self.mainUp
        self.midFlowline = np.asarray(self.midFlowline[::-1])

        self.clickedIndex = len(self.mainDown) - extLength - 1
        
        minShear = min(len(self.shearOne), len(self.shearTwo), len(self.midFlowline))

        self.shearOne = self.shearOne[:minShear]
        self.shearTwo = self.shearTwo[:minShear]
        self.midFlowline = self.midFlowline[:minShear]


        self.shearOne = self.shearOne[::-1]
        self.shearTwo = self.shearTwo[::-1]
        self.midFlowline = self.midFlowline[::-1]

        

        self.widths = ((self.shearOne[:,:1] - self.shearTwo[:,:1])**2 + (self.shearOne[:,1:]-self.shearTwo[:,1:])**2)**.5

        shearOneX = self.shearOne[:,:1]
        shearOneY = self.shearOne[:,1:]

        shearTwoX = self.shearTwo[:,:1]
        shearTwoY = self.shearTwo[:,1:]

        numSamplePoints = 10
        changeX = (shearTwoX - shearOneX)/numSamplePoints
        changeY = (shearTwoY - shearOneY)/numSamplePoints        

        self.samplePoints = []
        self.samplePoints.append(self.shearOne)

        for i in range(numSamplePoints):
            newX = self.samplePoints[-1][:,:1] + changeX
            newY = self.samplePoints[-1][:,1:] + changeY
            self.samplePoints.append(np.column_stack((newX,newY)))

        self.samplePoints = np.asarray(self.samplePoints)

        flowlineLatLon = ProjToLatLon(self.midFlowline,projCode)

        flowlineData = {}
        avgFlowlineData = {}


        for i in range(len(self.midFlowline)):
            flowlineData[i] = Point(datasetDict, self.midFlowline[i][0], self.midFlowline[i][1]).dataValues
            flowlineData[i]['lat'], flowlineData[i]['lng'] = flowlineLatLon.latPoints[i], flowlineLatLon.lonPoints[i]
            flowlineData[i]['width'] = 10

            vels, beds, surfs, smbs, thicks, t2ms = [], [], [], [], [], []
            precips = []
            avgFlowlineData[i] = {}
            for month in range(12):
                precips.append([]) 
            for j in range(len(self.samplePoints)):
                samplePoint = Point(datasetDict, self.samplePoints[j][i][0], self.samplePoints[j][i][1]).dataValues
                vels.append(samplePoint['velocity'])
                beds.append(samplePoint['bed'])
                surfs.append(samplePoint['surface'])
                thicks.append(samplePoint['thickness'])
                t2ms.append(samplePoint['t2m'])
                smbs.append(samplePoint['smb'])
                for month in range(12):
                    keyString = 'precip' + str(month)
                    precips[month].append(samplePoint[keyString])

            avgFlowlineData[i]['smb'] = np.average(smbs)
            avgFlowlineData[i]['velocity'] = (np.average(vels))
            avgFlowlineData[i]['surface'] = (np.average(surfs))
            avgFlowlineData[i]['thickness'] = (np.average(thicks))
            avgFlowlineData[i]['t2m'] = (np.average(t2ms))
            for month in range(12):
                keyString = 'precip' + str(month)
                avgFlowlineData[i][keyString] = (np.average(precips[month]))

            avgBed = np.average(beds)
            if 1 > abs(avgFlowlineData[i]['surface'] - avgFlowlineData[i]['thickness'] - avgBed):
                avgFlowlineData[i]['bed'] = avgFlowlineData[i]['surface'] - avgFlowlineData[i]['thickness']
            else:
                avgFlowlineData[i]['bed'] = avgBed

 

        self.flowlineData = flowlineData
        self.avgFlowlineData = avgFlowlineData    
if __name__ == '__main__':
    latPoint = 69.87
    longPoint = -47.01

    from QSSICode.translation import LonLatToProj, ProjToLatLon

    myTranslator = LonLatToProj([[longPoint, latPoint]])

    from QSSICode.createDatasets import createInitialDatasets

    myDatasetDict = createInitialDatasets()

    #Original
    myFlowline = Flowline(myTranslator.xPoints[0], myTranslator.yPoints[0], myDatasetDict, 100)

    #Translation from xy back to lat,long
    xyTrans = ProjToLatLon(myFlowline.flowLine)

    #I FOUND THEM! STORE THESE xyTrans VALUES
    print("long values: ")
    print(xyTrans.lonPoints)
    print("lat values: ")
    print(xyTrans.latPoints)
    print("")
    tempDict = {'lon':xyTrans.lonPoints, 'lat':xyTrans.latPoints}
    print(tempDict)
    print("")

    print(myFlowline.flowLine)
    print(myFlowline.flowLine[0])
    print(myFlowline.flowLine[1])

from pyproj import Proj

import sys

'''
Converter class for converting 
an array of [x,y] points into an
array of [lon,lat] for epsg:3413 projection
Example Input:  [[x1, y1], [x2, y2], ..., [xN, yN]]
Example Output: [[Lon(x1), Lat(y1)], [Lon(x2), Lat(y2)], ... [Lon(xN), Lat(yN)]]
Resource: http://jswhit.github.io/pyproj/

'''
class ProjToLatLon:
    def __init__(self, values, code):
        self.valuesXY = values
        self.xPoints = []
        self.yPoints = []
        self.latPoints = []
        self.lonPoints = []
        self.valuesLonLat = []

        for x in range(len(self.valuesXY)):
            self.xPoints.append(self.valuesXY[x][0])
            self.yPoints.append(self.valuesXY[x][1])

        initProj = Proj(init = code)

        for a in range(len(self.xPoints)):
            lons, lat = initProj(self.xPoints[a], self.yPoints[a], inverse = True)
            self.lonPoints.append(lons)
            self.latPoints.append(lat)
            self.valuesLonLat.append([lons, lat])

'''
Converter class for converting 
an array of [lon, lat] points into an
array of [x, y] for epsg:3413 projection
Example Input:  [[x1, y1], [x2, y2], ..., [xN, yN]]
Example Output: [[Lon(x1), Lat(y1)], [Lon(x2), Lat(y2)], ... [Lon(xN), Lat(yN)]]
Resource: http://jswhit.github.io/pyproj/
'''
class LonLatToProj:
    def __init__(self, values, code):
        self.valuesLonLat = values
        self.latPoints = []
        self.lonPoints = []
        self.xPoints = []
        self.yPoints = []
        self.valuesXY = []

        for x in range(len(self.valuesLonLat)):
            self.latPoints.append(self.valuesLonLat[x][1])
            self.lonPoints.append(self.valuesLonLat[x][0])

        initProj = Proj(init = code)

        for a in range(len(self.latPoints)):
            x, y = initProj(self.lonPoints[a], self.latPoints[a])
            self.xPoints.append(x)
            self.yPoints.append(y)
            self.valuesXY.append([x,y])

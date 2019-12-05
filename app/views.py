from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.context_processors import csrf

from QSSICode.createDatasets import createInitialDatasets
from QSSICode.createDatasets import Dataset
from QSSICode.translation import LonLatToProj, ProjToLatLon
from QSSICode.createFlowline import Flowline, FlowlineAnt
from QSSICode.getDataValues import Point
from QSSICode.support.flow_model.modelRunner import ModelRunner
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
from django.core.cache import caches
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
import numpy as np


dataFileName = 'QSSICode/data/surtGreenland.h5'
dataFileNameAnt = 'QSSICode/data/surtAntarctica.h5'

#Code to set second dataset to GL for faster load times
#dataFileNameAnt = 'QSSICode/data/surtGreenland.h5'

datasetDict = createInitialDatasets(dataFileName)
lcache = caches['default']
lcache.set('dict', datasetDict, None)


datasetDictAnt = createInitialDatasets(dataFileNameAnt)
lcache.set('dictAnt', datasetDictAnt, None)

# Create your views here.
# ---------------------------

# This view sends the user to the landing/home page
def display_home(request):
    #return render(request, 'UGP/index.bk.html', {})
    return render(request, 'landing/index.html', {})

def display_greenland(request):
    return render(request, 'greenland/index.html', {})

def display_antarctica(request):
    return render(request, 'antarctica/index.html', {})

def display_about(request):
    return render(request, 'about/index.html', {})

def display_lessons(request):
    return render(request, 'lessons/index.html', {})

def display_references(request):
    return render(request, 'references/index.html', {})


#@ensure_csrf_cookie
@csrf_exempt
def get_point_data(request):
    # c = {}
    # c.update(csrf(request))
    if request.method == 'POST':
        json_data = json.loads(request.body)

        code = ""
        dictCode = ""
        if (json_data['which'] == 'Ant'):
            projCode = 'epsg:3031'
            dictCode = 'dictAnt'
        else:
            projCode = 'epsg:3413'
            dictCode = 'dict'

        if 'lng' in json_data.keys():
            lng = json_data['lng']
            lat = json_data['lat']
            lonLatTrans = LonLatToProj([[lng, lat]], projCode)
            interp_point = Point(lcache.get(dictCode), lonLatTrans.xPoints[0], lonLatTrans.yPoints[0])
            interp_point.dataValues['lng'] = round(float(lng), 4)
            interp_point.dataValues['lat'] = round(float(lat), 4)
        elif 'x' in json_data.keys():
            x = json_data['x']
            y = json_data['y']
            interp_point = Point(lcache.get(dictCode), x, y)
            latLng = ProjToLatLon([[x,y]], projCode)
            interp_point.dataValues['lng'] = round(latLng.lonPoints[0], 4)
            interp_point.dataValues['lat'] = round(latLng.latPoints[0], 4)

        return JsonResponse(interp_point.dataValues)
        # else: return print("Not a valid point");

    else:
        return HttpResponse("This is not a POST request")

@csrf_exempt
def get_flowline_with_data(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)

        termMinimum = 15

        code = ""
        dictCode = ""
        if (json_data['which'] == 'Ant'):
            projCode = 'epsg:3031'
            dictCode = 'dictAnt'
        else:
            projCode = 'epsg:3413'
            dictCode = 'dict'

        stepSize = 1000
        glacier = ""
        if 'lng' in json_data.keys():
            lng = json_data['lng']
            lat = json_data['lat']
            lonLatTrans = LonLatToProj([[lng, lat]], projCode)
            if (json_data['which'] == 'Ant'):
                glacier = FlowlineAnt(lonLatTrans.xPoints[0], lonLatTrans.yPoints[0], lcache.get(dictCode), int(json_data['threshold']), stepSize*5, json_data['extLength'], projCode)
            else:
                glacier = Flowline(lonLatTrans.xPoints[0], lonLatTrans.yPoints[0], lcache.get(dictCode), int(json_data['threshold']), stepSize, json_data['extLength'], projCode)
        elif 'x' in json_data.keys():         
            x = json_data['x']
            y = json_data['y']
            if (json_data['which'] == 'Ant'):
                glacier = FlowlineAnt(x, y, lcache.get(dictCode), int(json_data['threshold']), stepSize*5, json_data['extLength'], projCode)
            else:
                glacier = Flowline(x, y, lcache.get(dictCode), int(json_data['threshold']), stepSize, json_data['extLength'], projCode)




        glacierData = {}
        glacierData['clickedIndex'] = glacier.clickedIndex
        glacierData['flowline'] = glacier.flowlineData
        glacierData['avgFlowline'] = glacier.avgFlowlineData
        glacierData['shears'] = [np.ndarray.tolist(glacier.shearOne), np.ndarray.tolist(glacier.shearTwo)]


        for i in range(json_data['extLength']):
            glacierData['avgFlowline'][i]['t2m'] = glacierData['avgFlowline'][json_data['extLength']]['t2m']
            glacierData['flowline'][i]['t2m'] = glacierData['flowline'][json_data['extLength']]['t2m']
            glacierData['flowline'][i]['width'] = glacierData['flowline'][json_data['extLength']]['width']

        if (glacierData['avgFlowline'][0]['thickness'] > termMinimum):
            glacierData['avgFlowline'][0]['thickness'] = termMinimum
            thickAtTerm = glacierData['avgFlowline'][json_data['extLength']]['thickness']
            for i in range(1, json_data['extLength']):
                glacierData['avgFlowline'][i]['thickness'] = min(glacierData['avgFlowline'][i]['thickness'], i * (thickAtTerm - termMinimum)/ json_data['extLength'] + termMinimum)
        
        
        if (glacierData['flowline'][0]['thickness'] > termMinimum):
            glacierData['flowline'][0]['thickness'] = termMinimum
            thickAtTerm = glacierData['flowline'][json_data['extLength']]['thickness']
            for i in range(1, json_data['extLength']):
                glacierData['flowline'][i]['thickness'] = min(glacierData['flowline'][i]['thickness'], i * (thickAtTerm - termMinimum)/ json_data['extLength'] + termMinimum)
            



        return JsonResponse(glacierData)
    else:
        return HttpResponse("This is not a POST request")

@csrf_exempt
def run_model(request):
    if request.method == 'POST':
        import numpy as np
        json_data = json.loads(request.body)

        tractValue = 1.2e-3

        dataDictForModel = {}
        dataDictForModel['bed'] = []
        dataDictForModel['surface'] = []
        dataDictForModel['precip'] = []
        dataDictForModel['t2m'] = []
        dataDictForModel['width'] = []
        dataDictForModel['beta2'] = []
        dataDictForModel['thickness'] = []

        deltaTs = np.array([-10.1,-10.6,-9.4,-2.3,5.5,11.7,13.7,11.3,5.7,-1.,-5.5,-8.9])
        for i in range(len(json_data['avgFlowline'])-1, -1, -1):
            precipValues = []
            t2mValues = []
            flowKey = str(i)
            for j in range(12):
                keyValue = 'precip' + str(j)
                precipValues.append(float(json_data['avgFlowline'][flowKey][keyValue]) * (12./1000.) * float(json_data['precipPerturb'])/100)
                t2mValues.append(float(json_data['avgFlowline'][flowKey]['t2m']) - 273.15 + float(json_data['tempPerturb']) + deltaTs[j])
            dataDictForModel['precip'].append(precipValues)
            dataDictForModel['t2m'].append(t2mValues)
            dataDictForModel['bed'].append(float(json_data['avgFlowline'][flowKey]['bed']))
            dataDictForModel['surface'].append(float(json_data['avgFlowline'][flowKey]['surface']))
            dataDictForModel['beta2'].append(float(tractValue) * float(json_data['frictPerturb'])/100)
            dataDictForModel['thickness'].append(float(json_data['avgFlowline'][flowKey]['thickness']))
            dataDictForModel['width'].append(float(json_data['flowline'][flowKey]['width']))

        dataDictForModel['precip'] = np.asarray(dataDictForModel['precip']).T
        dataDictForModel['t2m'] = np.asarray(dataDictForModel['t2m']).T
        dataDictForModel['bed'] = np.asarray(dataDictForModel['bed'])
        dataDictForModel['bed'] = np.asarray(dataDictForModel['bed'])
        dataDictForModel['width'] = np.asarray(dataDictForModel['width'])
        dataDictForModel['beta2'] = np.asarray(dataDictForModel['beta2'])
        dataDictForModel['thickness'] = np.asarray(dataDictForModel['thickness'])

        
        mr = ModelRunner(dataDictForModel)
        mrDict = mr.run()


        returnDict = {}
        minX = 9999
        
        returnDict['data'] = {}
        
        for year in mrDict:
            returnDict['data'][year] = {}
            dom = []
            for xPoi in mrDict[year]['x']:
                dom.append(xPoi[0]/1000)
                if dom[-1] < minX:
                    minX = dom[-1]
            returnDict['data'][year]['bed'] = {}
            returnDict['data'][year]['bed']['x'] = len(dataDictForModel['bed'])
            returnDict['data'][year]['bed']['y'] = dataDictForModel['bed'][:].tolist()
            
            returnDict['data'][year]['b0'] = {}
            returnDict['data'][year]['b0']['x'] = dom
            returnDict['data'][year]['b0']['y'] = (mrDict[year]['Bhat']).tolist()

            returnDict['data'][year]['surface'] = {}
            returnDict['data'][year]['surface']['x'] = dom
            returnDict['data'][year]['surface']['y'] = (mrDict[year]['surface']).tolist()


        dataDictForModel = {}
        dataDictForModel['bed'] = []
        dataDictForModel['surface'] = []
        dataDictForModel['precip'] = []
        dataDictForModel['t2m'] = []
        dataDictForModel['width'] = []
        dataDictForModel['beta2'] = []
        dataDictForModel['thickness'] = []


        for i in range(len(json_data['avgFlowline'])-1, -1, -1):
            precipValues = []
            t2mValues = []
            flowKey = str(i)
            for j in range(12):
                keyValue = 'precip' + str(j)
                precipValues.append(float(json_data['avgFlowline'][flowKey][keyValue]) * (12./1000.))
                t2mValues.append(float(json_data['avgFlowline'][flowKey]['t2m']) - 273.15 + deltaTs[j])
            dataDictForModel['precip'].append(precipValues)
            dataDictForModel['t2m'].append(t2mValues)
            dataDictForModel['bed'].append(float(json_data['avgFlowline'][flowKey]['bed']))
            dataDictForModel['surface'].append(float(json_data['avgFlowline'][flowKey]['surface']))
            dataDictForModel['beta2'].append(float(tractValue))
            dataDictForModel['thickness'].append(float(json_data['avgFlowline'][flowKey]['thickness']))
            dataDictForModel['width'].append(float(json_data['flowline'][flowKey]['width']))

        dataDictForModel['precip'] = np.asarray(dataDictForModel['precip']).T
        dataDictForModel['t2m'] = np.asarray(dataDictForModel['t2m']).T
        dataDictForModel['bed'] = np.asarray(dataDictForModel['bed'])
        dataDictForModel['bed'] = np.asarray(dataDictForModel['bed'])
        dataDictForModel['width'] = np.asarray(dataDictForModel['width'])
        dataDictForModel['beta2'] = np.asarray(dataDictForModel['beta2'])
        dataDictForModel['thickness'] = np.asarray(dataDictForModel['thickness'])


        mr = ModelRunner(dataDictForModel)
        mrDict = mr.run()

        for year in mrDict:
            dom = []
            for xPoi in mrDict[year]['x']:
                dom.append(xPoi[0]/1000)
                if dom[-1] < minX:
                    minX = dom[-1]
            
            returnDict['data'][year]['b00'] = {}
            returnDict['data'][year]['b00']['x'] = dom
            returnDict['data'][year]['b00']['y'] = (mrDict[year]['Bhat']).tolist()

            returnDict['data'][year]['surface0'] = {}
            returnDict['data'][year]['surface0']['x'] = dom
            returnDict['data'][year]['surface0']['y'] = (mrDict[year]['surface']).tolist()
        
        returnDict['minX'] = minX
        returnDict['maxX'] = len(dataDictForModel['bed'])




        return JsonResponse(returnDict)
    else:
        return HttpResponse("This is not a POST request")

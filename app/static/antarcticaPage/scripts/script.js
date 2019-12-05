var mapEdge = 255;
var tileSize = 255;
var maxZoom = 7;
var minZoom = 2;

var lastPointsToCutOff = 1;

var projection = new ol.proj.Projection({
    code: 'ZOOMIFY',
    units: 'pixels',
    extent: [0, 0, mapEdge, mapEdge]
});
var projectionExtent = projection.getExtent();

var maxResolution = ol.extent.getWidth(projectionExtent) / tileSize;
var resolutions = [];
for (var z = minZoom; z <= maxZoom; z++) {
    resolutions[z] = maxResolution / Math.pow(2, z - 1);
}

var mapTypes = [
    'velocity',
    'bed',
    'surface',
    'smb',
    'thickness',
    't2m'
]

var currentMap = mapTypes[0];
var tileLayers = [];

var flowlineLayers = [];
var pointLayers = [];

for (i = 0; i < mapTypes.length; i++) {
    localMapType = mapTypes[i];
    tileLayers.push(new ol.layer.Tile({
        visible: false,
        source: new ol.source.TileImage({
            tileUrlFunction: function(tileCoord, pixelRatio, projection) {
                var z = tileCoord[0];
                var x = tileCoord[1];
                var y = -tileCoord[2] - 1;
                return staticURL + "tiles/" + currentMap + "/" + z + "_" + x + "_" + y + ".png";

            },
            projection: projection,
            tileGrid: new ol.tilegrid.TileGrid({
                origin: ol.extent.getTopLeft(projectionExtent),
                resolutions: resolutions,
                tileSize: tileSize
            }),
        }),
        extent: projectionExtent
    }))

}
var map = new ol.Map({
    target: 'map',
    layers: tileLayers,
    view: new ol.View({
        projection: projection,
        center: [mapEdge / 2, mapEdge / 2],
        zoom: 2,
        minZoom: minZoom,
        maxZoom: maxZoom,
        extent: projectionExtent
    })
});

tileLayers[0].setVisible(true);
var menu = document.getElementById("mapType");
menu.addEventListener("change", changeMap);

function changeMap(event) {
    value = parseInt(menu.value);
    for (var i = 0; i < mapTypes.length; i++) {
        tileLayers[i].setVisible(i === value);
    }
    currentMap = mapTypes[value];
    fileName = 'url(' + staticURL + 'img/legends/' + mapTypes[value] + '.png)';
    $('#legend').css('background-image', fileName);
}

function drawFlowline(d, flowlineName) {
    loadFlowlineData(d);

    clickedIndex = d['clickedIndex']
    lengthFlowline = (Object.keys(d['flowline']).length);


    markers = {}
    markers['down'] = []

    console.log(d);
    for (var i = 0; i < clickedIndex; i++) {
        if (i > lastPointsToCutOff) {
            console.log(i);
            mapPoint = gridToCoord([d['flowline'][i].x, d['flowline'][i].y]);
            tempMarker = new ol.Feature({
                geometry: new ol.geom.Point(mapPoint),
            });
            markers['down'].push(tempMarker);
        }
    }

    markers['clicked'] = []
    mapPoint = gridToCoord([d['flowline'][clickedIndex].x, d['flowline'][clickedIndex].y])
    tempMarker = new ol.Feature({
        geometry: new ol.geom.Point(mapPoint),
    });
    markers['clicked'].push(tempMarker);

    markers['up'] = [];
    for (var i = clickedIndex + 1; i < lengthFlowline; i++) {
        mapPoint = gridToCoord([d['flowline'][i].x, d['flowline'][i].y]);
        tempMarker = new ol.Feature({
            geometry: new ol.geom.Point(mapPoint),
        });
        markers['up'].push(tempMarker);
    }

    markers['shear'] = [];
    for (var point in d['shears'][0]) {
        if (point > lastPointsToCutOff) {
            mapPoint = gridToCoord([d['shears'][0][point][0], d['shears'][0][point][1]]);
            tempMarker = new ol.Feature({
                geometry: new ol.geom.Point(mapPoint),
            });
            markers['shear'].push(tempMarker);
        }
    }

    for (var point in d['shears'][1]) {
        if (point > lastPointsToCutOff) {
            mapPoint = gridToCoord([d['shears'][1][point][0], d['shears'][1][point][1]]);
            tempMarker = new ol.Feature({
                geometry: new ol.geom.Point(mapPoint),
            });
            markers['shear'].push(tempMarker);
        }
    }

    styles = {}
    styles['down'] = new ol.style.Style({
        image: new ol.style.Circle({
            radius: 2,
            stroke: new ol.style.Stroke({
                color: '#fff'
            }),
            fill: new ol.style.Fill({
                color: 'green'
            })
        }),
    });

    styles['clicked'] = new ol.style.Style({
        image: new ol.style.Circle({
            radius: 4,
            stroke: new ol.style.Stroke({
                color: '#fff'
            }),
            fill: new ol.style.Fill({
                color: 'black'
            })
        }),
    });


    styles['up'] = new ol.style.Style({
        image: new ol.style.Circle({
            radius: 2,
            stroke: new ol.style.Stroke({
                color: '#fff'
            }),
            fill: new ol.style.Fill({
                color: 'red'
            })
        }),
    });


    styles['shear'] = new ol.style.Style({
        image: new ol.style.Circle({
            radius: 2,
            stroke: new ol.style.Stroke({
                color: '#fff'
            }),
            fill: new ol.style.Fill({
                color: 'white'
            })
        }),
    });


    for (var style in styles) {
        vectorSource = new ol.source.Vector({
            features: markers[style]
        });
        markerVectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: styles[style]
        });
        map.addLayer(markerVectorLayer);
        flowlineLayers.push(markerVectorLayer);
    }

    myFlowlines.push(d);
    $("#flowlineSelector").append(new Option(flowlineName, value = myFlowlines.length - 1));
    $('#flowlineSelector').val(myFlowlines.length - 1);


}
map.on('dblclick', function(e) {

    gridPoint = coordToGrid(e.coordinate);
    threshold = document.getElementById('flow-vel-threshold-input').value;

    clickPoint = {
        'x': gridPoint[0],
        'y': gridPoint[1],
        'threshold': threshold,
        'extLength': (lastPointsToCutOff - 1),
        'which': 'Ant'
    };
    $.ajax({
        type: 'POST',
        url: '/ajax/get_flowline_with_data/',
        data: JSON.stringify(clickPoint),
        contentType: 'application/json',

        success: function(d) {
            flowIndex = myFlowlines.length + 1;
            flowName = 'Clicked Flowline ' + flowIndex;
            drawFlowline(d, flowName);
        },
        error: function(d){
            alert("Flowline not found. Try double clicking in a higher speed area.");
        },
        failure: function(d) {
            alert("AJAX FAILED!");
        }

    });
});

map.on('singleclick', function(e) {

    gridPoint = coordToGrid(e.coordinate);

    clickPoint = {
        'x': gridPoint[0],
        'y': gridPoint[1],
        'which': 'Ant'
    };

    $.ajax({
        type: 'POST',
        url: '/ajax/get_point_data/',
        data: JSON.stringify(clickPoint),
        contentType: 'application/json',

        success: function(d) {
            mapPoint = gridToCoord([d.x, d.y]);

            marker = new ol.Feature({
                geometry: new ol.geom.Point(mapPoint),
            });

            vectorSource = new ol.source.Vector({
                features: [marker]
            });

            markerVectorLayer = new ol.layer.Vector({
                source: vectorSource,
            });

            map.addLayer(markerVectorLayer);
            pointLayers.push(markerVectorLayer);

            pointName = 'Point ' + myPoints.length;
            $('#point-table tbody').append(
                "<tr><td>" + pointName +
                "</td><td>" + d.lat.toFixed(4) +
                "</td><td>" + d.lng.toFixed(4) +
                "</td><td>" + parseFloat(d.velocity) +
                "</td><td>" + parseFloat(d.bed) +
                "</td><td>" + parseFloat(d.surface) +
                "</td><td>" + parseFloat(d.smb) +
                "</td><td>" + parseFloat(d.thickness) +
                "</td><td>" + parseFloat(d.t2m) + "</td></tr>"
            );
            myPoints.push(d);
        },
        error: function(d) {
            alert("Error! Please click inside the data.");
        },
        failure: function(d) {
            alert("AJAX FAILED!");
        }

    });
});


function coordToGrid(point) {
    x = point[0]
    y = point[1]


    gridXMin = -3333500;
    gridXMax = 3332500;

    gridYMax = 3332500;
    gridYMin = -3333500;

    gridX = gridXMin + (gridXMax - gridXMin) / tileSize * x;
    gridY = gridYMin + (gridYMax - gridYMin) / tileSize * y;

    return [gridX, gridY];

}

function gridToCoord(point) {
    x = point[0]
    y = point[1]

    gridXMin = -3333500;
    gridXMax = 3332500;

    gridYMax = 3332500;
    gridYMin = -3333500;

    coordX = ((x - gridXMin) * tileSize) / (gridXMax - gridXMin)
    coordY = ((y - gridYMin) * tileSize) / (gridYMax - gridYMin)

    return [coordX, coordY];

}
//loadFlowline();

function loadFlowline() {



    nameText = $('#flowline-name').val();
    latText = $('#flow-lat-input').val();
    lngText = $('#flow-long-input').val();

    if (!nameText) {
        alert("Please Enter a flowline Name!");
        return;
    }
    if (!latText) {
        alert("Please Enter a Latitude!");
        return;
    }
    if (!lngText) {
        alert("Please Enter a Longitude!");
        return;
    }

    threshold = document.getElementById('flow-vel-threshold-input').value;

    pointVals = {
        lat: parseFloat(latText),
        lng: parseFloat(lngText),
        threshold: threshold,
        extLength: (lastPointsToCutOff - 1),
        'which': 'Ant'
    }


    $.ajax({
        type: 'POST',
        url: '/ajax/get_flowline_with_data/',
        data: JSON.stringify(pointVals),
        contentType: 'application/json',

        success: function(d) {
            drawFlowline(d, nameText);
        },
        error: function(d) {
            alert("Flowline Not Found. Please Enter a valid lat/long that is slightly(10 km or so) inland)");
        },
        failure: function(d) {
            alert("AJAX FAILED!");
        }

    });
}

$('#flowline-lookup').on("click", function() {
    loadFlowline();
});

var flowlineMenu = document.getElementById('flowlineSelector');
flowlineMenu.addEventListener('change', flowMenuChange);

function flowMenuChange(event) {
    value = parseInt(flowlineMenu.value);
    flowline = myFlowlines[value];
    loadFlowlineData(flowline);
}

$('#flowline-download').on('click', function() {
    downloadFlowline('flowline');
});
$('#flowlineAvg-download').on('click', function() {
    downloadFlowline('avgFlowline');
});
$('#run-model').on('click', function() {
    $('#run-model').attr("disabled", true);
    runModel();

})

function downloadFlowline(key) {
    value = parseInt(flowlineMenu.value);
    flowline = myFlowlines[value];
    flowName = flowlineMenu[value].text;
    fileName = flowName + '.txt';

    text = 'Flowline Name: ' + flowName;
    text = text + '\nClicked Index: ' + flowline['clickedIndex'];
    text = text + '\n (x, y) Projection: Polar Stereographic North (70N, 45W)  || EPSG:3413'
    text = text + '\n\n';
    text = text + 'Point\tLat\tLong\tx\ty\tSpeed(m/yr)\tBed(m)\tSurface(m)\tSMB(m/y) *ice equiv\tThickness(m)\tT2M(K)\tWidth(m)\t';

    for (var j = 0; j < 12; j++) {
        text = text + 'precip' + j + '\t';

    }
    text = text + '\n';

    lengthFlowline = (Object.keys(flowline['flowline']).length)
    for (var i = lastPointsToCutOff; i < lengthFlowline; i++) {
        point = i - lastPointsToCutOff;
        lat = flowline['flowline'][i]['lat'].toFixed(4);
        lng = flowline['flowline'][i]['lng'].toFixed(4);
        x = flowline['flowline'][i]['x'].toFixed(4);
        y = flowline['flowline'][i]['y'].toFixed(4);
        vel = flowline[key][i]['velocity'];
        bed = flowline[key][i]['bed'];
        surface = flowline[key][i]['surface'];
        smb = flowline[key][i]['smb'];
        thickness = flowline[key][i]['thickness'];
        t2m = flowline[key][i]['t2m'];
        width = flowline['flowline'][i]['width'].toFixed(4);


        text = text + point + '\t' + lat + '\t' + lng + '\t' + x + '\t' + y + '\t' + vel + '\t' + bed + '\t' + surface + '\t' + smb + '\t' + thickness + '\t' + t2m + '\t' + width + '\t';

        precips = [];
        for (var j = 0; j < 12; j++) {
            newKey = 'precip' + j;
            text = text + flowline[key][i][newKey].toFixed(4) + '\t';
        }
        text = text + '\n';

    }

    element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', fileName);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function loadFlowlineData(flowline) {
    $('#flowline-table td').remove();
    velocities = [];
    beds = [];
    surfaces = [];
    smbs = [];
    thicknesses = [];
    t2ms = [];
    widths = [];

    avgVels = [];
    avgBeds = [];
    avgSurfs = [];
    avgThicks = [];
    avgSmbs = [];
    avgT2ms = [];

    console.log(flowline);



    $('#selectedIndexLabel').text('Clicked Point: ' + flowline['clickedIndex']);
    for (var i in flowline['flowline']) {
        if (i > lastPointsToCutOff-1){
            velocities.push(flowline['flowline'][i].velocity);
            beds.push(flowline['flowline'][i].bed);
            surfaces.push(flowline['flowline'][i].surface);
            smbs.push(flowline['flowline'][i].smb);
            thicknesses.push(flowline['flowline'][i].thickness);
            t2ms.push(flowline['flowline'][i].t2m);
            widths.push(flowline['flowline'][i].width);
            avgVels.push(flowline['avgFlowline'][i].velocity);
            avgBeds.push(flowline['avgFlowline'][i].bed);
            avgSurfs.push(flowline['avgFlowline'][i].surface);
            avgThicks.push(flowline['avgFlowline'][i].thickness);
            avgSmbs.push(flowline['avgFlowline'][i].smb);
            avgT2ms.push(flowline['avgFlowline'][i].t2m);
            $('#flowline-table tbody').append(
                "<tr><td>" + (i-lastPointsToCutOff).toString() +
                "</td><td>" + parseFloat(flowline['flowline'][i].lat.toFixed(4)) +
                "</td><td>" + parseFloat(flowline['flowline'][i].lng.toFixed(4)) +
                "</td><td>" + parseFloat(flowline['flowline'][i].velocity) +
                "</td><td>" + parseFloat(flowline['flowline'][i].bed) +
                "</td><td>" + parseFloat(flowline['flowline'][i].surface) +
                "</td><td>" + parseFloat(flowline['flowline'][i].smb) +
                "</td><td>" + parseFloat(flowline['flowline'][i].thickness) +
                "</td><td>" + parseFloat(flowline['flowline'][i].t2m) +
                "</td><td>" + parseFloat(flowline['flowline'][i].width.toFixed(4)) + "</td></tr>"

            );
        }
    }

    graphingDataBed = [];
    graphingDataVel = [];
    graphingDataSMB = [];
    graphingDataTemp = [];
    graphingDataWidth = []

    for (var i = 0; i < beds.length; i++) {
        pointVar = {};
        pointVar.point = i;
        pointVar.bed = beds[i];
        pointVar.surface = surfaces[i];
        pointVar.b0 = surfaces[i] - thicknesses[i];
        graphingDataBed.push(pointVar);


        velVar = {};
        velVar.point = i;
        velVar.speed = velocities[i];
        velVar.avgSpeed = avgVels[i];
        graphingDataVel.push(velVar);


        smbVar = {};
        smbVar.point = i;
        smbVar.smb = smbs[i];
        smbVar.avgSmb = avgSmbs[i];
        graphingDataSMB.push(smbVar);

        t2mVar = {};
        t2mVar.point = i;
        t2mVar.t2m = t2ms[i];
        t2mVar.avgT2m = avgT2ms[i];
        graphingDataTemp.push(t2mVar);

        widthVar = {}
        widthVar.point = i;
        widthVar.width = widths[i];
        graphingDataWidth.push(widthVar);
    }

    multiChart(graphingDataSMB, '#graphSMBContainer', 'SMB(m/y *ice equiv)');
    multiChart(graphingDataTemp, '#graphTempContainer', 'Temp (K)');
    multiChart(graphingDataBed, '#graphBedSurfContainer', 'Elevation (m)');
    multiChart(graphingDataVel, '#graphVelContainer', 'Speed (m/y)');
    multiChart(graphingDataWidth, '#graphWidthContainer', 'Width(m)');
}

function runModel(event) {
    value = parseInt(flowlineMenu.value);
    flowline = myFlowlines[value];

    flowline['precipPerturb'] = param4Text.text();
    flowline['tempPerturb'] = param3Text.text();
    flowline['frictPerturb'] = param1Text.text();

    $('#model-graph img:last-child').remove();
    Plotly.purge('model-graph');

    var imgPath = '<img src= "' + staticURL + 'img/loading.gif">';
    $('#model-graph').append(imgPath);

    $.ajax({
        type: 'POST',
        url: '/ajax/run_model/',
        data: JSON.stringify(flowline),
        contentType: 'application/json',

        success: function(d) {
            $('#run-model').attr("disabled", false);
            $('#model-graph img:last-child').remove();



            initializeChart(d);

        },
        error: function(d){
            $('#model-graph img:last-child').remove();
            alert("Model Run Failed, it is likely this was caused by a flowline data issue. Please select a new flowline.")
            $('#run-model').attr("disabled", false);

        },
        failure: function(d) {
            alert("AJAX FAILED!");
        }
        

    });


}
$("#point-lookup").on("click", function() {

    nameText = $("#point-name").val();
    latText = $("#lat-input").val();
    lngText = $("#long-input").val();

    if (!nameText) {
        alert("Please Enter a Point Name!");
        return;
    }
    if (!latText) {
        alert("Please Enter a Latitude!");
        return;
    }
    if (!lngText) {
        alert("Please Enter a Longitude!");
        return;
    }

    pointVals = {
        lat: latText,
        lng: lngText,
        'which': 'Ant'
    }
    $.ajax({
        type: 'POST',
        url: '/ajax/get_point_data/',
        data: JSON.stringify(pointVals),
        contentType: 'application/json',

        success: function(d) {

            mapPoint = gridToCoord([d.x, d.y]);

            marker = new ol.Feature({
                geometry: new ol.geom.Point(mapPoint),
            });

            vectorSource = new ol.source.Vector({
                features: [marker]
            });

            markerVectorLayer = new ol.layer.Vector({
                source: vectorSource,
            });

            map.addLayer(markerVectorLayer);
            pointLayers.push(markerVectorLayer);

            $('#point-table tbody').append(
                "<tr><td>" + nameText +
                "</td><td>" + latText +
                "</td><td>" + lngText +
                "</td><td>" + parseFloat(d.velocity) +
                "</td><td>" + parseFloat(d.bed) +
                "</td><td>" + parseFloat(d.surface) +
                "</td><td>" + parseFloat(d.smb) +
                "</td><td>" + parseFloat(d.thickness) +
                "</td><td>" + parseFloat(d.t2m) + "</td></tr>"
            );
            myPoints.push(d);
        },
        error: function(d){
            alert("Point not found. Please enter a valid lat/long within Antarctica");
        },
        failure: function(d) {
            alert("AJAX FAILED!");
        }

    });
});

$('#point-remove').on('click', function() {
    $('#point-table td').remove();
    myPoints = [];
    for (var i = 0; i < pointLayers.length; i++) {
        map.removeLayer(pointLayers[i]);
    }
});

$('#map-remove').on('click', function() {
    $('#point-table td').remove();
    $('#flowline-table td').remove();

    myPoints = [];
    for (var i = 0; i < pointLayers.length; i++) {
        map.removeLayer(pointLayers[i]);
    }
    myFlowlines = [];

    $("#flowlineSelector").empty();
    for (var i = 0; i < flowlineLayers.length; i++) {
        map.removeLayer(flowlineLayers[i]);
    }

    d3.select('#graphSMBContainer').select("svg").remove();
    d3.select('#graphTempContainer').select("svg").remove();
    d3.select('#graphBedSurfContainer').select("svg").remove();
    d3.select('#graphVelContainer').select("svg").remove();
    d3.select('#graphWidthContainer').select("svg").remove();

});


var slider1 = $("#slider1");
var param1Text = $("#param1Value");

var slider3 = $("#slider3");
var param3Text = $("#param3Value");

var slider4 = $("#slider4");
var param4Text = $("#param4Value");

slider1.on("input change", function(e) {
    param1Text.text($(this).val());
})

slider3.on("input change", function(e) {
    param3Text.text($(this).val());
})

slider4.on("input change", function(e) {
    param4Text.text($(this).val());
})

function multiChart(myData, whichContainer, yLabel) {
    d3.select(whichContainer).select("svg").remove();

    var margin = {
            top: 25,
            right: 50,
            bottom: 25,
            left: 50
        },
        width = (window.innerWidth - margin.left - margin.right)/3; // Use the window's width 
        height = (window.innerHeight * .5 - margin.top - margin.bottom)/3; // Use the window's height



    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var color = d3.scale.category10();

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var line = d3.svg.line()
        .interpolate("basis")
        .x(function(d) {
            return x(d.point);
        })
        .y(function(d) {
            return y(d.elevation);
        });

    var svg = d3.select(whichContainer).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data = myData;
    color.domain(d3.keys(data[0]).filter(function(key) {
        return key !== "point";
    }));

    var variables = color.domain().map(function(name) {
        return {
            name: name,
            values: data.map(function(d) {
                return {
                    point: d.point,
                    elevation: +d[name]
                };
            })
        };
    });

    x.domain(d3.extent(data, function(d) {
        return d.point;
    }));

    y.domain([
        d3.min(variables, function(c) {
            return d3.min(c.values, function(v) {
                return v.elevation;
            });
        }),
        d3.max(variables, function(c) {
            return d3.max(c.values, function(v) {
                return v.elevation;
            });
        })
    ]);

    var legend = svg.selectAll('g')
        .data(variables)
        .enter()
        .append('g')
        .attr('class', 'legend');

    legend.append('rect')
        .attr('x', width - 20)
        .attr('y', function(d, i) {
            return i * 20;
        })
        .attr('width', 10)
        .attr('height', 10)
        .style('fill', function(d) {
            return color(d.name);
        });

    legend.append('text')
        .attr('x', width - 8)
        .attr('y', function(d, i) {
            return (i * 20) + 9;
        })
        .text(function(d) {
            return d.name;
        });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(yLabel);

    var variable = svg.selectAll(".variable")
        .data(variables)
        .enter().append("g")
        .attr("class", "city");

    variable.append("path")
        .attr("class", "line")
        .attr("d", function(d) {
            return line(d.values);
        })
        .style("stroke", function(d) {
            return color(d.name);
        });

    variable.append("text")
        .datum(function(d) {
            return {
                name: d.name,
                value: d.values[d.values.length - 1]
            };
        })
        .attr("transform", function(d) {
            return "translate(" + x(d.value.point) + "," + y(d.value.elevation) + ")";
        })
        .attr("x", 3)
        .attr("dy", ".35em")
        .text(function(d) {
            return d.name;
        });

    var mouseG = svg.append("g")
        .attr("class", "mouse-over-effects");

    mouseG.append("path") // this is the black vertical line to follow mouse
        .attr("class", "mouse-line")
        .style("stroke", "black")
        .style("stroke-width", "1px")
        .style("opacity", "0");

    var lines = document.getElementsByClassName('line');

    var mousePerLine = mouseG.selectAll('.mouse-per-line')
        .data(variables)
        .enter()
        .append("g")
        .attr("class", "mouse-per-line");

    mousePerLine.append("circle")
        .attr("r", 7)
        .style("stroke", function(d) {
            return color(d.name);
        })
        .style("fill", "none")
        .style("stroke-width", "1px")
        .style("opacity", "0");

    mousePerLine.append("text")
        .attr("transform", "translate(10,3)");

    mouseG.append('svg:rect') // append a rect to catch mouse movements on canvas
        .attr('width', width) // can't catch mouse events on a g element
        .attr('height', height)
        .attr('fill', 'none')
        .attr('pointer-events', 'all')
        .on('mouseout', function() { // on mouse out hide line, circles and text
            d3.select(".mouse-line")
                .style("opacity", "0");
            d3.selectAll(".mouse-per-line circle")
                .style("opacity", "0");
            d3.selectAll(".mouse-per-line text")
                .style("opacity", "0");
        })
        .on('mouseover', function() { // on mouse in show line, circles and text
            d3.select(".mouse-line")
                .style("opacity", "1");
            d3.selectAll(".mouse-per-line circle")
                .style("opacity", "1");
            d3.selectAll(".mouse-per-line text")
                .style("opacity", "1");
        })
        .on('mousemove', function() { // mouse moving over canvas
            var mouse = d3.mouse(this);
            d3.select(".mouse-line")
                .attr("d", function() {
                    var d = "M" + mouse[0] + "," + height;
                    d += " " + mouse[0] + "," + 0;
                    return d;
                });

            d3.selectAll(".mouse-per-line")
                .attr("transform", function(d, i) {
                    var xDate = x.invert(mouse[0]),
                        bisect = d3.bisector(function(d) {
                            return d.point;
                        }).right;
                    idx = bisect(d.values, xDate);

                    var beginning = 0,
                        end = lines[i].getTotalLength(),
                        target = null;

                    while (true) {
                        target = Math.floor((beginning + end) / 2);
                        pos = lines[i].getPointAtLength(target);
                        if ((target === end || target === beginning) && pos.x !== mouse[0]) {
                            break;
                        }
                        if (pos.x > mouse[0]) end = target;
                        else if (pos.x < mouse[0]) beginning = target;
                        else break; //position found
                    }

                    d3.select(this).select('text')
                        .text(y.invert(pos.y).toFixed(2));

                    return "translate(" + mouse[0] + "," + pos.y + ")";
                });
        });

}

function initializeChart(inpDict) {

    
    var dataInput = inpDict['data'];
    var minX = inpDict['minX'];
    var maxX = inpDict['maxX'];
    
    // Get the group names:
    var years = Object.keys(dataInput);
    // In this case, every year includes every continent, so we
    // can just infer the continents from the *first* year:
    var firstYear = dataInput[years[0]];
    var variables = Object.keys(firstYear);

    // Create the main traces, one for each continent:
    var traces = [];
    for (i = 0; i < variables.length; i++) {
        var data = firstYear[variables[i]];
        traces.push({
            name: variables[i],
            x: data.x,
            y: data.y,
            mode: 'lines',
        });
    }

    // Create a frame for each year. Frames are effectively just
    // traces, except they don't need to contain the *full* trace
    // definition (for example, appearance). The frames just need
    // the parts the traces that change (here, the data).
    var frames = [];
    for (i = 0; i < years.length; i++) {
        frames.push({
            name: years[i],
            data: variables.map(function(variable) {
                return dataInput[years[i]][variable];
            })
        })
    }

    // Now create slider steps, one for each frame. The slider
    // executes a plotly.js API command (here, Plotly.animate).
    // In this example, we'll animate to one of the named frames
    // created in the above loop.
    var sliderSteps = [];
    for (i = 0; i < years.length; i++) {
        sliderSteps.push({
            method: 'animate',
            label: years[i],
            args: [
                [years[i]], {
                    mode: 'immediate',
                    transition: {
                        duration: 300
                    },
                    frame: {
                        duration: 300,
                        redraw: false
                    },
                }
            ]
        });
    }

    var layout = {
        xaxis: {
            title: 'Model Run',
            range: [minX, maxX]
        },
        yaxis: {
            title: 'Elevation (m)',
            type: 'linear'
        },
        hovermode: 'closest',
        // We'll use updatemenus (whose functionality includes menus as
        // well as buttons) to create a play button and a pause button.
        // The play button works by passing `null`, which indicates that
        // Plotly should animate all frames. The pause button works by
        // passing `[null]`, which indicates we'd like to interrupt any
        // currently running animations with a new list of frames. Here
        // The new list of frames is empty, so it halts the animation.
        updatemenus: [{
            x: 0,
            y: 0,
            yanchor: 'top',
            xanchor: 'left',
            showactive: false,
            direction: 'left',
            type: 'buttons',
            pad: {
                t: 87,
                r: 10
            },
            buttons: [{
                method: 'animate',
                args: [null, {
                    mode: 'immediate',
                    fromcurrent: true,
                    transition: {
                        duration: 1
                    },
                    frame: { 
                        duration: 100,
                        redraw: false
                    }
                }],
                label: 'Play'
            }, {
                method: 'animate',
                args: [
                    [null], {
                        mode: 'immediate',
                        transition: {
                            duration: 1
                        },
                        frame: {
                            duration: 100,
                            redraw: false
                        }
                    }
                ],
                label: 'Pause'
            }]
        }],
        // Finally, add the slider and use `pad` to position it
        // nicely next to the buttons.
        sliders: [{
            pad: {
                l: 130,
                t: 55
            },
            currentvalue: {
                visible: true,
                prefix: 'Year:',
                xanchor: 'right',
                font: {
                    size: 20,
                    color: '#666'
                }
            },
            steps: sliderSteps
        }]
    };

    // Create the plot:
    Plotly.plot('model-graph', {
        data: traces,
        layout: layout,
        config: {
            showSendToCloud: true
        },
        frames: frames,
    });
}
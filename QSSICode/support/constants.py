import pyqtgraph as pg
from dolfin import Constant


map = {'x0': 0, 'y0': 0,  'x1': 10018, 'y1': 17946,
       'cmap_x0': 0, 'cmap_y0': 0,
       'cmap_x1': 10018, 'cmap_y1': 17946,
       'proj_x0': -637925, 'proj_x1': 864625,
       'proj_y0': -657675, 'proj_y1': -3349425,
       'cmap_proj_x0': -637925, 'cmap_proj_x1': 864625,
       'cmap_proj_y0': -657675, 'cmap_proj_y1': -3349425}

skinnyBlackPlotPen = pg.mkPen(color=(0, 0, 0), width=1)
whitePlotPen = pg.mkPen(color=(255, 255, 255), width=2)
blackPlotPen = pg.mkPen(color=(0, 0, 0), width=2)
greyPlotPen = pg.mkPen(color=(200, 200, 200), width=2)
redPlotPen = pg.mkPen(color=(100, 0, 0), width=2)
bluePlotPen = pg.mkPen(color=(0, 0, 255), width=2)
greenPlotPen = pg.mkPen(color=(76, 153, 0), width=2)
purplePlotPen = pg.mkPen(color=(102, 0, 204), width=2)
orangePlotPen = pg.mkPen(color=(255, 128, 0), width=2)
bluePlotPen = pg.mkPen(color=(0, 0, 255), width=2)
tealPlotPen = pg.mkPen(color=(0, 204, 204), width=2)
pinkPlotPen = pg.mkPen(color=(153, 0, 153), width=2)
brownPlotPen = pg.mkPen(color=(92, 64, 51), width=2)

dataFileName = './data/GreenlandInBedCoord_V2.h5'
cmFileName = './data/dataCMValues_V2.h5'

dt_float = 5.0  # Time step
thklim = 10.0
eps_reg = 1e-5  # Regularization parameter
dt = Constant(dt_float)
theta = Constant(0.5)  # Crank-Nicholson parameter

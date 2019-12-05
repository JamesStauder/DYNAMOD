from scipy.integrate import ode
import numpy as np


'''
Class: FlowIntegrator
Integration class developed my Jake Downs. 


Dependencies: scipy ode
Creator: Jake Downs
Date created: Unknown
Last edited: 3/2/18
'''


class FlowIntegrator:
    def __init__(self, vxDataSet, vyDataSet):

        self.vxDataSet = vxDataSet
        self.vyDataSet = vyDataSet

        self.vMags = []        
        self.xFactor = 1
        self.yFactor = 1
        # Velocity right hand side function
        def rhs(t, u):
            x = u[0]
            y = u[1]
            d = u[2]

            vx = vxDataSet.getInterpolatedValue(y, x)
            vy = vyDataSet.getInterpolatedValue(y, x)
            v_mag = np.sqrt(vx**2 + vy**2)
            if (self.perpendicular):
                vx, vy = vy, vx

            vx = vx*self.xFactor
            vy = vy*self.yFactor
            return np.array([vx / v_mag,  vy / v_mag, v_mag])

        # ODE integrator
        self.integrator = ode(rhs).set_integrator('vode', method = 'adams')
    # Set the currently displayed data field
    def integrate(self, x0, y0, flowline, resolution, threshold, xFactor, yFactor, perpendicular = False, extensionDist = 0):
        self.vMags = []
        self.perpendicular = perpendicular
        u0 = np.array([x0, y0, 0.])
        self.integrator.set_initial_value(u0, 0.0)

        self.xFactor = xFactor
        self.yFactor = yFactor

        vx = self.vxDataSet.getInterpolatedValue(y0, x0)
        vy = self.vyDataSet.getInterpolatedValue(y0, x0)

        v_mag = np.sqrt(vx**2 + vy**2)

        while self.integrator.successful() and v_mag > threshold:
            u = self.integrator.integrate(self.integrator.t + resolution)
            x, y  = u[0], u[1]
            vx = self.vxDataSet.getInterpolatedValue(y, x)
            vy = self.vyDataSet.getInterpolatedValue(y, x)
            v_mag = np.sqrt(vx**2 + vy**2)
            flowline.append([x, y])
            self.vMags.append(v_mag)

        #extend past the shear margin
        if (xFactor == 1 and yFactor == 1):
            flowline = flowline[:-1]  
            lastPointX, lastPointY = flowline[-1][0], flowline[-1][1]
            prevPointX, prevPointY = flowline[-2][0], flowline[-2][1]

            dx = lastPointX - prevPointX
            dy = lastPointY - prevPointY

            for i in range(extensionDist):
                flowline.append([flowline[-1][0] + dx , flowline[-1][1] + dy])
                self.vMags.append(0)
        return flowline

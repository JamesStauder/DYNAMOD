from dolfin import Constant, Min, Max, ln, exp
dt_float = 5.0              # Time step
thklim = 10.0
eps_reg = 1e-5              # Regularization parameter
dt = Constant(dt_float)
theta = Constant(0.5)       # Crank-Nicholson parameter


def softplus(y1, y2, alpha=1):
    # The softplus function is a differentiable approximation
    # to the ramp function.  Its derivative is the logistic function.
    # Larger alpha makes a sharper transition.
    return Max(y1, y2) + (1./alpha)*ln(1+exp(alpha*(Min(y1, y2)-Max(y1, y2))))

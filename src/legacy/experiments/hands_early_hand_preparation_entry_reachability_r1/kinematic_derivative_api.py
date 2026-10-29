"""Generic frozen-rig derivative dependency pruning; geometry output stays intact."""
import casadi as ca

def wrist_state_function(frozen_skin):
    q = ca.SX.sym("rig_state", frozen_skin.size1_in(0), frozen_skin.size2_in(0))
    _, wrist, engineering_state = frozen_skin(q)
    return ca.Function("wrist_state_only", [q], [wrist, engineering_state])

def motion_derivatives(frozen_skin):
    f = wrist_state_function(frozen_skin)
    n = frozen_skin.numel_in(0)
    q, qd, qdd = [ca.MX.sym(s, n) for s in ("state", "velocity", "acceleration")]
    wrist, engineering_state = f(q)
    velocity = ca.jtimes(wrist, q, qd) * 1000
    acceleration = ca.jtimes(velocity, q, qd) + ca.jtimes(velocity, qd, qdd)
    rates = ca.jtimes(engineering_state[6:], q, qd)
    return ca.Function("motion_derivatives", [q, qd, qdd], [velocity, acceleration, rates])

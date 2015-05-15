
import numpy
import pylab
import math

''' NOTATION:
  R0      initial radius of the bubble
  R       current radius of the bubble
  dR      d R / d t
  ddR     d^2 R / d t^2
  p0_l    initial pressure in liquid
  p0_g    initial pressure in gas
  rho_l   liquid density
  rho0_g  initial gas density
  gamma   gas constant of specific heats
  mu      kinematic viscosity coefficient
  S       surface tension coefficient
'''

# approximate collapse time (no integration)
def approximate_collapse_time (R0, p0_l, p0_g, rho_l):
  return 0.915 * R0 * math.sqrt (rho_l / (p0_l - p0_g))

# isothermal adiabatic gas pressure
def pressure (p0_g, R0, R):
    return p0_g * (R0 / R) ** 3

# isothermal adiabatic gas density
def density (rho0_g, R0, R):
  return rho0_g * (R0 / R) ** 3

'''
  Rayleigh and Plesset
  '''
class RayleighPlesset (object):

  name = 'Rayleigh-Plesset'
  
  # evaluate the right hand side of the ODE for the second derivative of bubble radius
  def rhs (self, R, dR, R0, p0_l, p0_g, rho_l, rho0_g, gamma, mu, S):
    ddR = (pressure (p0_g, R0, R) - p0_l) / (rho_l * R) - 1.5 * dR ** 2 / R
    if mu != 0:
      ddR += - 4 * mu * dR / (R ** 2)
    if S != 0:
      ddR += - 2 * S / (rho_l * R **2)
    return ddR

'''
Thomas L. Geers
"Optimization of an augmented Prosperetti-Lezzi bubble model"
DOI: 10.1121/1.4883356, 2014.
'''
class OptPL2 (object):
  
  name = 'OptPL+'
  
  # evaluate the right hand side of the ODE for the second derivative of bubble radius
  def rhs (self, R, dR, R0, p0_l, p0_g, rho_l, rho0_g, gamma, mu, S):
    
    # compute required parameters
    c_l     = numpy.sqrt (1.0 * p0_l / rho_l)           # invariant speed of sound in liquid
    R_eq    = R0 * (1.0 * p0_g / p0_l) ** (1.0 / 3.0)   # equillibrium radius (assuming adiabaticity)
    rho_eq  = density (rho0_g, R0, R_eq)                # gas density at ambient equilibrium
    P0      = p0_l * ( (R / R_eq) ** -(3 * gamma) - 1 ) # according to the definition
    dP0     = p0_l / (R_eq ** -(3 * gamma))             # derivative of p0 w.r.t R (constants)
    dP0    *= -(3 * gamma) * (R ** -(3 * gamma + 1))    # derivative of p0 w.r.t R (derivative terms)
    dP0    *= dR                                        # derivative of p0 w.r.t R (chain rule)
    '''
    print 'input:'
    print R, dR, R0, p0_l, p0_g, rho_l, rho0_g, gamma, mu, S
    # output: 0.0846361439426 0 0.0846361439426 100 0.0234 1000 1 1.4 0 0
    
    print 'parameters:'
    print c_l, R_eq, rho_eq, P0, dP0
    # output: 0.0 0.00521548244154 4273.5042735 -99.999174148 -0.0
    '''
    # evaluate the RHS
    factor = R * ( 1.0 - 0.36 * dR / c_l + 0.2 * (rho_eq / rho_l) * (R / R_eq) ** (-3) )
    #print factor
    ddR  = 1.0 / rho_l * ( P0 * ( 1.0 + 1.64 * dR / c_l ) + (R / c_l) * dP0 )
    #print ddR
    ddR -= 1.5 * dR * dR * (1.0 + 23.0 / 75.0 * dR / c_l)
    #print ddR
    ddR /= factor
    
    # diffusion
    if mu != 0:
      ddR += - 4 * mu * dR / (R ** 2)
    
    # surface tension
    if S != 0:
      ddR += - 2 * S / (rho_l * R ** 2)
    
    return ddR

def integrate (R0, p0_l, p0_g, rho_l, rho0_g, gamma=1.4, tend=None, dR0=0, mu=0, S=0, model=OptPL2()):
    time    = 0.0
    step    = 0
    max_dt  = 5e-7
    min_dt  = 1e-10
    
    if tend == None:
      tend = 1.2 * approximate_collapse_time (R0, p0_l, p0_g, rho_l)
    
    Rs    = [R0]
    dRs   = [dR0]
    Ps    = [p0_g]
    times = [0]
    
    while time < tend:
      
        R  = Rs  [-1]
        dR = dRs [-1]
        dt = 1e-6 * R / R0
        dt = min (dt, max_dt)
        dt = max (dt, min_dt)
        dt = min (dt, tend - time)
        
        # RK2 sub-step 1
        ddR = model.rhs (R, dR, R0, p0_l, p0_g, rho_l, rho0_g, gamma, mu, S)
        R_star   = R  + dR  * dt
        dR_star  = dR + ddR * dt
        
        # RK2 sub-step 2
        ddR_star = model.rhs (R_star, dR_star, R0, p0_l, p0_g, rho_l, rho0_g, gamma, mu, S)
        
        # RK2 result
        Rs  .append ( R  + 0.5 * (dR  + dR_star ) * dt )
        dRs .append ( dR + 0.5 * (ddR + ddR_star) * dt )
        Ps  .append ( pressure (p0_g, R0, R) )
        
        time += dt
        step += 1
        
        times.append (time)
        
        if Rs [-1] < 1e-6 * R0:
          break

    return times, Rs, Ps, dRs, model.name

if __name__ == "__main__":

  r0     = 0.15
  p0_l   = 100
  p0_g   = 0.0234
  rho_l  = 1000
  rho0_l = 1
  
  pylab.figure(123)
  
  [t,r,p,dr] = integrate (r0, p0_l, p0_g, rho_l, rho0_g)
  
  pylab.subplot(1,3,1)
  pylab.plot(t,r,lw=3)
  pylab.ylim(0,1)
  
  pylab.subplot(1,3,2)
  pylab.plot(t,[x/1e5 for x in p],lw=3)
  
  pylab.subplot(1,3,3)
  pylab.plot(t,dr,lw=3)
  
  pylab.show()

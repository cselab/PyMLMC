
import scipy as sp
#import scipy.integrate
import numpy as np
import matplotlib.pyplot as plt
import functools
import math

#isothermal
def pressure_fn (pb0, r0, r):
    return pb0*(r0/r)**3

def rhs_rp (cur_R, r0, pb0, pinf, ro, mu, S):
    dR = cur_R[1]
    ddR = (pressure_fn(pb0,r0,cur_R[0])-pinf)/(ro*cur_R[0]) - 1.5*dR**2/cur_R[0]
    if mu != 0:
      ddR += - 4*mu*dR/(cur_R[0]**2)
    if S != 0:
      ddR += - 2*S/(ro*cur_R[0]**2)
    return [dR, ddR]

# Thomas L. Geers
# "Optimization of an augmented Prosperetti-Lezzi bubble model"
# DOI: 10.1121/1.4883356, 2014.
class OptPL (object):
  
  name = 'OptPL+'
  
  # evaluate the right hand side of the systems of ODEs
  def rhs (R, R0, p0_g, p0_l, rho_l, gamma, mu, S):
    
    # compatibility checks
    if mu != 0:
      print ' :: WARNING: mu > 0 is NOT implemented for OptPL+'
    if S != 0:
      print ' :: WARNING: S > 0 is NOT implemented for OptPL+'
    
    # compute required parameters
    
    rho_g = todo                                      # gas density at ambient equilibrium
    c_l   = numpy.sqrt (p0_l / rho_l)                 # invariant speed of sound in liquid
    R_eq  = R0 * (p0_g / p0_l) ** (1.0 / 3.0)         # equillibrium radius (assuming adiabaticity)
    p0    = p0_l * ( (R / R_eq) ** -(3 * gamma) - 1 ) # according to the definition
    
    # evaluate the RHS
    dR = R [1]
    # factor = R [0] * ( 1 - 9.0 / 25.0 * dR / c_l + 1.0 / 5.0 * (rho_g / rho_l) * (R [0] / R_eq) ** (-3) )
    factor = R [0] * ( 1 - 0.36 * dR / c_l + 0.2 * (rho_g / rho_l) * (R [0] / R_eq) ** (-3) )
    ddR =   (pressure_fn(pb0,r0,cur_R[0])-pinf)/(ro*cur_R[0]) - 1.5*dR**2/cur_R[0]

    return [dR, ddR]

def integrate (r0, pinf, pb0, ro, tend=None, dr0=0, mu=0, S=0, rhs=rhs_rp):
    time=0.
    step_id=0
    dt=5e-7
    t_rp = 0.915*r0*math.sqrt(ro/(pinf-pb0))
    if tend == None:
      tend = t_rp * 1.2
    nsteps = int(tend/dt)
    
    R = [[r0,dr0]]
    pressure = [pb0]
    times=[0]
    
    while(time<tend):
        cur_R = R[-1]

        if(cur_R[0]<0.1*r0):
            dt=1e-7

        if(cur_R[0]<0.01*r0):
            dt=1e-8
        
        if(cur_R[0]<0.001*r0):
            dt=1e-9
        
        #rk2
        [dR, ddR] = rhs(cur_R, r0, pb0, pinf, ro, mu, S)
        
        R_star = [cur_R[0]+dR*dt,cur_R[1]+ddR*dt]
        [dR_star, ddR_star] = rhs(R_star, r0, pb0, pinf, ro, mu, S)
        R.append([cur_R[0]+0.5*(dR+dR_star)*dt,cur_R[1]+0.5*(ddR+ddR_star)*dt])
        pressure.append(pressure_fn(pb0,r0,cur_R[0]))
        
        time+=dt
        step_id+=1
        
        times.append(time)

        if((R[-1])[0]<1e-6*r0):
            break

    return times, [x[0] for x in R[:]], pressure, [x[1] for x in R[:]]

if __name__ == "__main__":

  r0   = 0.15
  pinf = 100
  pb0  = 0.0234
  ro   = 1000
  
  plt.figure(123)
  
  [t,r,p,dr] = integrate (r0, pinf, pb0, ro)
  
  plt.subplot(1,3,1)
  plt.plot(t,r,lw=3)
  plt.ylim(0,1)
  
  plt.subplot(1,3,2)
  plt.plot(t,[x/1e5 for x in p],lw=3)
  
  plt.subplot(1,3,3)
  plt.plot(t,dr,lw=3)
  
  plt.show()

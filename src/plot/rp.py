
import scipy as sp
#import scipy.integrate
import numpy as np
import matplotlib.pyplot as plt
import functools
import math

#isothermal
def pressure_fn(pb0, r0, r):
    return pb0*(r0/r)**3

def rhs(cur_R, r0, pb0, pinf, ro, mu, S):
    dR = cur_R[1]
    ddR = (pressure_fn(pb0,r0,cur_R[0])-pinf)/(ro*cur_R[0]) - 1.5*dR**2/cur_R[0]
    if mu != 0:
      ddR += - 4*mu*dR/(cur_R[0]**2)
    if S != 0:
      ddR += - 2*S/(ro*cur_R[0]**2)
    return [dR, ddR]

def integrate (req, pinf, pb0, ro, tend=None, dr0=0, mu=0, S=0):
    time=0.
    step_id=0
    dt=5e-7
    t_ray = 0.915*req*math.sqrt(ro/(pinf-pb0))
    if tend == None:
      tend = t_ray * 1.2
    nsteps = int(tend/dt)
    
    R = [[req,dr0]]
    pressure = [pb0]
    times=[0]
    
    while(time<tend):
        cur_R = R[-1]

        if(cur_R[0]<0.1*req):
            dt=1e-7

        if(cur_R[0]<0.01*req):
            dt=1e-8
        
        if(cur_R[0]<0.001*req):
            dt=1e-9
        
        #rk2
        [dR, ddR] = rhs(cur_R, req, pb0, pinf, ro, mu, S)
        
        R_star = [cur_R[0]+dR*dt,cur_R[1]+ddR*dt]
        [dR_star, ddR_star] = rhs(R_star, req, pb0, pinf, ro, mu, S)
        R.append([cur_R[0]+0.5*(dR+dR_star)*dt,cur_R[1]+0.5*(ddR+ddR_star)*dt])
        pressure.append(pressure_fn(pb0,req,cur_R[0]))
        
        time+=dt
        step_id+=1
        
        times.append(time)

        if((R[-1])[0]<1e-6*req):
            print "reached mininum radius...no more integration"
            break
    
    print ' Collapse time: %f' % time
    return times, [x[0] for x in R[:]], pressure, [x[1] for x in R[:]]

if __name__ == "__main__":

  req  = 0.15
  pinf = 100
  pb0  = 0.0234
  ro   = 1000
  
  plt.figure(123)
  
  [t,r,p,dr] = rp (req, pinf, pb0, ro)
  
  plt.subplot(1,3,1)
  plt.plot(t,r,lw=3)
  plt.ylim(0,1)
  
  plt.subplot(1,3,2)
  plt.plot(t,[x/1e5 for x in p],lw=3)
  
  plt.subplot(1,3,3)
  plt.plot(t,dr,lw=3)
  
  plt.show()

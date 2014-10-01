
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Python MLMC wrapper (PyMLMC)
# TODO: add paper, description and link
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import sys
import subprocess

# === local imports

from MC import *

sys.path.append ( os.path.dirname(__file__) + "/samples" )
sys.path.append ( os.path.dirname(__file__) + "/stats" )
sys.path.append ( os.path.dirname(__file__) + "/balancer" )

from samples  import *
from stats    import *
from balancer import *

# === classes

class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, sampler, solver, discretizations, params, run_id=1):
    
    # store parameters
    self.params = params
    
    # store configuration
    self.solver = solver
    self.discretizations = discretizations
    self.run_id = run_id
    
    # enumeration of fine and coarse mesh levels in one level difference
    self.FINE   = 0
    self.COARSE = 1
  
  # load MLMC status
  def status_load (self):
    
    if restart:
      self.status.init = 1
      self.status.converged = 0
      self.status.finished = 0
  
  # save MLMC status
  def status_save (self):

  # initial phase
  def init (self):
    
    # init samples and schedule simulations
    # TODO
    
    mlmc.status.init = 0
  
  # iterative updating phase
  def update (self):
    
  
  def assemble (self, stats_list):
    
    for i, stat in enumerate (stats_list):
      Q [i] = 
      for 


if __name__ == "__main__":
  
  # parse input parameters
  # TODO
  params = ??
  
  # create MLMC simulation
  mlmc = MLMC (params)
  
  # load status of MLMC simulation
  mlmc.status_load()
  
  # initialize MLMC simulation
  if mlmc.status.init:
    mlmc.samples.init()
    mlmc.run()
    mlmc.status_save()
    if not params.interactive:
      exit()
    
  # update MLMC simulation
  while not mlmc.status.converged:
    
    # wait for jobs to finish 
    mlmc.join()
    
    # compute error indicators
    mlmc.get_indicators()
    
    if mlmc.indicators.error <= params.tol:
      mlmc.status.converged = 1
      break
    
    # display estimated errors and required number of samples
    mlmc.samples.update()
    
    if mlmc.params.interactive:
      mlmc.user_query()
      mlmc.samples.update()
    
    # compute additional samples
    mlmc.run()
  
  # save status of MLMC simulation
  mlmc.status_save()



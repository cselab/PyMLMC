
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

import re
import os
import sys

# === local imports

libs = [ "rng", "samples", "balancer", "stats" ]
for lib in libs:
  sys.path.append ( os.path.dirname(__file__) + "/" + lib )

class MLMC (object):
  
  # initialize MLMC
  def __init__ (self, L, NX, NY, NZ, sampler, RUN_ID=1):
    
    # store parameters
    self.params = params
    
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




# # # # # # # # # # # # # # # # # # # # # # # # # #
# General MC classes
# TODO: add paper, description and link
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import os
import sys

# === local imports



# === classes

class MC (object):
  
  # initialize MC
  def __init__ (self, level, type, samples, solver, discretization, params, run_id=1):
    
    # store configuration
    self.level   = level
    self.type    = type
    self.samples = samples
    self.solver  = solver
    self.params  = params
    self.discretization = discretization
    self.run_id  = run_id
  
  # launch all samples
  def run (self):
    for sample in samples:
      self.solver.run (level, type, sample, discretization, params, run_id)
  
  # load the results
  def load (self):
    for i, sample in enumerate (samples):
      self.results [i] = solver.load (level, type, sample, discretization, params, run_id)
  
  # assmble MC estimates
  def assemble (self, stats_list):
    for i, stat in enumerate (stats_list):
      self.Q [i] = stat.compute (self.results)
    return self.Q


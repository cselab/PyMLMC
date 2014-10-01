
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
  def __init__ (self, config, params, run_id):
    
    # store configuration
    self.level          = config ['level']
    self.type           = config ['type']
    self.samples        = config ['samples']
    self.solver         = config ['solver']
    self.discretization = config ['discretization']
    self.params         = params
    self.run_id         = run_id

    # list of results
    self.results = [ None ] * len ( self.samples )

    # dictionary of stats
    self.stats = {}
    
  # launch all samples
  def run (self):
    for sample in samples:
      self.solver.run (level, type, sample, discretization, params, run_id)
  
  # load the results
  def load (self):
    for i, sample in enumerate (samples):
      self.results [i] = solver.load (level, type, sample, discretization, params, run_id)
  
  # assmble MC estimates
  def assemble (self, stats):
    self.stats = {}
    for stat in stats:
      self.stats [ stat.name ] = stat.compute (self.results)
    return self.stats



# # # # # # # # # # # # # # # # # # # # # # # # # #
# General Monte Carlo (MC) classes
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
  def __init__ (self, config, params, id):
    
    # store configuration
    self.level          = config ['level']
    self.type           = config ['type']
    self.samples        = config ['samples']
    self.solver         = config ['solver']
    self.discretization = config ['discretization']
    self.params         = params
    self.id             = id

    # list of results
    self.results = [ None ] * len ( self.samples )

    # dictionary of stats
    self.stats = {}
    
  # launch all samples
  def run (self):
    for sample in self.samples:
      self.solver.run (self.level, self.type, sample, self.id, self.discretization, self.params)
  
  def finished (self):
    for sample in self.samples:
      if not self.solver.finished (self.level, self.type, sample, self.id):
        return 0
    return 1
  
  # load the results
  def load (self):
    for i, sample in enumerate (self.samples):
      self.results [i] = self.solver.load (self.level, self.type, sample, self.id)
  
  # assmble MC estimates
  def assemble (self, stats):
    self.stats = {}
    for stat in stats:
      self.stats [ stat.name ] = stat.compute (self.results)
    return self.stats


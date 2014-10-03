
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
  def __init__ (self, config, params):
    
    # store configuration
    vars (self) .update ( locals() )
    
    # list of results
    self.results = [ None ] * len ( self.config.samples )
    
    # dictionary of stats
    self.stats = {}
    
  # launch all samples
  def run (self):
    print ' :: MC run: level %d type %d with %d sample(s)' % ( self.config.level, self.config.type, len(self.config.samples) )
    config = self.config
    for sample in config.samples:
      config.solver.run (config.level, config.type, sample, config.id, config.discretization, self.params)
  
  def finished (self):
    config = self.config
    for sample in config.samples:
      if not config.solver.finished (config.level, config.type, sample, config.id):
        return 0
    return 1
  
  # load the results
  def load (self):
    config = self.config
    for i, sample in enumerate (config.samples):
      self.results [i] = config.solver.load (config.level, config.type, sample, config.id)
  
  # assmble MC estimates
  def assemble (self, stats):
    self.stats = {}
    for stat in stats:
      self.stats [ stat.name ] = stat.compute (self.results)
    return self.stats


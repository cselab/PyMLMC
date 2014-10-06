
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

from helpers import intf

# === classes

class MC (object):
  
  # initialize MC
  def __init__ (self, config, params, parallelization):
    
    # store configuration
    vars (self) .update ( locals() )
    
    # list of results
    self.results = [ None ] * len ( self.config.samples )
    
    # dictionary of stats
    self.stats = {}
  
  # validate all samples
  def validate (self): 
    with self.config as config:
      config.solver.validate ( config.discretization, self.multi )
  
  # launch all samples
  def run (self):
    args = ( self.config.level, self.config.type, intf(len(self.config.samples)), intf(self.parallelization.cores) )
    print ' :: MC run:  |  level %2d  |  type %d  |  with %s sample(s)  |  on %s cores' % args
    with self.config as config:
      for sample in config.samples:
        config.solver.run ( config.level, config.type, sample, config.id, config.discretization, self.params, self.parallelization )
  
  def finished (self):
    with self.config as config:
      for sample in config.samples:
        if not config.solver.finished ( config.level, config.type, sample, config.id ):
          return 0
    return 1
  
  # load the results
  def load (self):
    with self.config as config:
      for i, sample in enumerate (config.samples):
        self.results [i] = config.solver.load ( config.level, config.type, sample, config.id )
  
  # assmble MC estimates
  def assemble (self, stats):
    self.stats = {}
    for stat in stats:
      self.stats [ stat.name ] = stat.compute (self.results)
    return self.stats


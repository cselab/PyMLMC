
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

from helpers import intf, pair

# === classes

# configuration class for MC simulations
class MC_Config (object):
  
  def __init__ (self, mlmc_config, level, type, samples):
    vars (self) .update ( locals() )
    self.solver         = mlmc_config.solver
    self.discretization = mlmc_config.discretizations [level - type]
    self.id             = mlmc_config.id

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
    self.config.solver.validate ( self.config.discretization, self.parallelization )
  
  # return the seed for the specified sample
  def seed (self, sample):
    return pair ( pair (self.config.level, sample), self.config.id )
  
  # launch all samples
  def run (self):
    args = ( self.config.level, self.config.type, intf(len(self.config.samples)), intf(self.parallelization.cores), self.parallelization.hours, self.parallelization.minutes )
    print ' :: MC run:  |  level %2d  |  type %d  |  with %s sample(s)  |  on %s cores  |  for %dh:%2dm ' % args
    config = self.config
    for sample in config.samples:
      config.solver.run ( config.level, config.type, sample, config.id, self.seed (sample), config.discretization, self.params, self.parallelization )
  
  def finished (self):
    config = self.config
    for sample in config.samples:
      if not config.solver.finished ( config.level, config.type, sample, config.id ):
        return 0
    return 1
  
  # load the results
  def load (self):
    config = self.config
    for i, sample in enumerate (config.samples):
      self.results [i] = config.solver.load ( config.level, config.type, sample, config.id )
  
  # assmble MC estimates
  def assemble (self, stats):
    self.stats = {}
    for stat in stats:
      self.stats [ stat.name ] = stat.compute (self.results)
    return self.stats


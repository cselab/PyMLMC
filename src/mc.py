
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
import math

# === local imports

from helpers import intf, pair, Progress
import local

# === classes

# configuration class for MC simulations
class MC_Config (object):
  
  def __init__ (self, mlmc_config, level, type, samples):
    vars (self) .update ( locals() )
    self.solver         = mlmc_config.solver
    self.discretization = mlmc_config.discretizations [level - type]
    self.id             = mlmc_config.id
    self.root           = mlmc_config.root
    self.available      = 0

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
  
  # return information string describing the MC run and the prescribed parallelization
  def info (self):
    
    config = self.config
    
    typestr = [' FINE ', 'COARSE'] [config.type]

    resolution = config.solver.resolution_string (config.discretization)
    resolution = resolution.rjust ( len ('RESOLUTION') )

    if self.parallelization.cores % local.cores == 0:
      args = ( config.level, typestr, resolution, intf(len(config.samples), table=1), intf(self.parallelization.cores/local.cores, table=1), 'N' )
    else:
      args = ( config.level, typestr, resolution, intf(len(config.samples), table=1), intf(self.parallelization.cores, table=1), 'C' )
    
    if self.parallelization.walltime and local.cluster:
      batch = '    '
      count = intf (1, table=1)
      if self.parallelization.batch and self.parallelization.batchmax != None:
        batch = intf (self.parallelization.batchmax, table=1)
        count = intf (math.ceil (float (len(config.samples)) / self.parallelization.batchmax), table=1)
      args += ( self.parallelization.hours, self.parallelization.minutes, batch, count )
      if local.ensembles:
        merge = intf (self.parallelization.mergemax, table=1)
        args += (merge, )
        return '  :  %5d  |  %s  |  %s  |     %s  |   %s %s   |   %2dh %2dm  |   %s  |  %s  |   %s  |' % args
      else:
        return '  :  %5d  |  %s  |  %s  |     %s  |   %s %s   |   %2dh %2dm  |   %s  |  %s  |' % args
    else:
      return '  :  %5d  |  %s  |  %s  |     %s  |   %s %s   |' % args

  # launch all samples
  def run (self):
    
    config = self.config
    
    # if the simulation is not supposed to proceed further,
    # check if nothing is overwritten
    if not self.params.proceed:
      for sample in config.samples:
        config.solver.check ( config.level, config.type, sample )
    
    # adjust parallelization according to the number of samples
    self.parallelization.adjust ( len (config.samples) )
    
    # get information of the MC run and the prescribed parallelization
    info_mc = self.info()
    
    # initialize solver
    config.solver.initialize (config.level, config.type, self.parallelization)

    # use progress indicator, report MC info each time
    prefix = info_mc + '  Progress: '
    progress = Progress (prefix=prefix, steps=len(config.samples), length=20)

    import time
    # run all samples
    for step, sample in enumerate (config.samples):
      config.solver.run ( config.level, config.type, sample, self.seed (sample), config.discretization, self.params, self.parallelization )
      progress.update (step + 1)

    # reset progress indicator
    progress.reset()

    # finalize solver
    info_solver = config.solver.finalize (config.level, config.type, self.parallelization)

    # print combined info: MC info and additional (scheduler-related) information from the solver
    info_solver = info_solver if info_solver != None else ''
    info = info_mc + '  ' + info_solver
    print info

    # return combined info
    return info
  
  # check how many runs are still pending
  def pending (self):
    
    config = self.config
    return sum ( [ not config.solver.finished ( config.level, config.type, sample ) for sample in config.samples ] )
  
  # report timer results
  def timer (self, batch):
    
    config = self.config
    runtimes = [ config.solver.timer ( config.level, config.type, sample, batch ) for sample in config.samples ]
    return max ( runtimes )
  
  # load the results
  def load (self):
    
    config = self.config

    for i, sample in enumerate (config.samples):
      if self.params.verbose >= 1:
        self.results [i] = config.solver.load ( config.level, config.type, sample )
      else:
        try:
          self.results [i] = config.solver.load ( config.level, config.type, sample )
        except:
          self.results [i] = None
            
    loaded = [ i for i, result in enumerate (self.results) if result != None ]

    self.available = (len (loaded) > 0)

    return loaded
  
  # assmble MC estimates
  def assemble (self, stats):

    self.stats = {}
    for stat in stats:
      if self.available:
        self.stats [ stat.name ] = stat.compute_all ( self.results, self.config.solver.DataClass )
      else:
        self.stats [ stat.name ] = None
    return self.stats
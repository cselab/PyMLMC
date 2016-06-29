
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
  
  def __init__ (self, mlmc_config, level, type, samples, iteration):
    vars (self) .update ( locals() )
    self.solver         = mlmc_config.solver
    self.discretization = mlmc_config.discretizations [level - type]
    self.id             = mlmc_config.id
    self.root           = mlmc_config.root
    self.available      = 0

class MC (object):
  
  # initialize MC
  def __init__ (self, config, params, parallelization, recycle):
    
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

    if self.config.id == 0:
      return pair (self.config.level, sample)
    else:
      return pair ( pair (self.config.level, sample), self.config.id )

  # return information string describing the MC run and the prescribed parallelization
  def info (self):
    
    config = self.config
    
    typestr = [' FINE ', 'COARSE'] [config.type]

    resolution = config.solver.resolution_string (config.discretization)
    resolution = resolution.rjust ( len ('RESOLUTION') )

    format = '  :  %5d  |'
    args   = ( config.level, )
    if not config.solver.recycle:
      format += '  %s  |'
      args   += ( typestr, )

    format += '  %s  |    %s  |  %s %s   |'
    args += ( resolution, intf(len(config.samples), table=1) )
    if self.parallelization.cores % local.cores == 0:
      args += ( intf(self.parallelization.cores/local.cores, table=1), 'N' )
    else:
      args += ( intf(self.parallelization.cores, table=1), 'C' )
    
    if self.parallelization.walltime and local.cluster:
      format += '   %2dh %2dm  |  %s  ->  %s  |'
      if self.parallelization.batch and self.parallelization.batchmax != None:
        batch = intf (self.parallelization.batchmax, table=1)
        count = intf (math.ceil (float (len(config.samples)) / self.parallelization.batchmax), table=1)
      else:
        batch = intf (0,                   table=1, empty=1)
        count = intf (len(config.samples), table=1, empty=1)
      args += ( self.parallelization.hours, self.parallelization.minutes, batch, count )
      if local.ensembles and self.parallelization.batch:
        merge = intf (self.parallelization.mergemax, table=1)
        format += '  %s  ->'
        args   += (merge, )
    
    return format % args

  # launch all samples
  def run (self):
    
    config = self.config
    
    # check if nothing is overwritten
    # unless the simulation is specified to proceed further or override is allowed
    if not self.params.proceed and not self.params.override:
      for sample in config.samples:
        config.solver.check ( config.level, config.type, sample )
    
    # get information of the MC run and the prescribed parallelization
    info_mc = self.info()
    
    # initialize solver
    config.solver.initialize (config.level, config.type, self.parallelization, config.iteration)

    # use progress indicator, report MC info each time
    prefix = info_mc + '  '
    progress = Progress (prefix=prefix, steps=len(config.samples), length=20)
    progress.init ()

    import time
    # run all samples
    for step, sample in enumerate (config.samples):
      config.solver.run ( config.level, config.type, sample, self.seed (sample), config.discretization, self.params, self.parallelization )
      progress.update (step + 1)

    # reset progress indicator
    progress.message ('Finalizing...')

    # finalize solver
    info_solver = config.solver.finalize (config.level, config.type, self.parallelization)

    # print combined info: MC info and additional (scheduler-related) information from the solver
    info = progress.message (info_solver)
    progress.finalize ()

    # return combined info
    return info

  # check how many runs are already finished
  def finished (self):

    config = self.config
    return sum ( [ config.solver.finished ( config.level, config.type, sample ) for sample in config.samples ] )

  # check how many runs are still pending
  def pending (self):
    
    config = self.config
    return sum ( [ not config.solver.finished ( config.level, config.type, sample ) for sample in config.samples ] )

  # check if some loaded results are invalid
  def invalid (self):

    invalid = [ (self.config.solver.invalid (result) if result != None else 0) for result in self.results ]
    indices = [ i for i, status in enumerate (invalid) if status ]

    return indices

  # report timer results
  def timer (self, walltime=None, batch=0):
    
    config = self.config

    if batch:
      runtimes = config.solver.timer ( config.level, config.type )
    else:
      runtimes = [ config.solver.timer ( config.level, config.type, sample ) for sample in config.samples ]

    # set maximum runtime for runs that went over walltime limit
    for sample, runtime in enumerate (runtimes):
      if runtime == -1:
        if walltime != None:
          runtimes [sample] = 3600 * walltime
        else:
          runtimes [sample] = None

    # filter out invalid entries (pending and failed simulations)
    runtimes = [ runtime for runtime in runtimes if runtime != None ]

    if len (runtimes) > 0:
      return { 'min' : min (runtimes), 'max' : max (runtimes) }
    else:
      return { 'min' : None, 'max' : None }

  # report progress
  def progress (self):

    print
    print '  : Level %d, type %s:' % (self.config.level, ['FINE', 'COARSE'] [self.config.type])
    for sample, result in enumerate (self.results):
      if sample > 8:
        break
      progress = self.config.solver.progress (result)
      bar      = int ( math.ceil (progress * 20) )
      percent  = int ( math.ceil (100 * progress) )
      print '  -> sample %6d: [%s] %d%%' % (sample, '#' * bar + ' ' * (20 - bar), percent)

  # report efficiency
  def efficiency (self, batch=0):

    config = self.config
    if batch:
      efficiencies = config.solver.efficiencies ( config.level, config.type )
    else:
      efficiencies = [ config.solver.efficiencies ( config.level, config.type, sample ) for sample in config.samples ]

    efficiencies = [ efficiency for efficiency in efficiencies if efficiency != None ]

    if len (efficiencies) > 0:
      return { 'min' : min (efficiencies), 'max' : max (efficiencies) }
    else:
      return { 'min' : None, 'max' : None }

  # load the results
  def load (self):
    
    config = self.config

    for i, sample in enumerate (config.samples):
      if self.params.verbose >= 2:
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
  def assemble (self, stats, indices, qois):

    print '  : -> level %d, type %d' % (self.config.level, self.config.type)

    '''
    # assemble MC estimates from all available samples
    print '    -> all samples:'
    self.stats_all = {}
    for stat in stats:
      if self.available:
        self.stats_all [ stat.name ] = stat.compute_all ( self.results, qois=qois, check=1 )
      else:
        self.stats_all [ stat.name ] = None
    '''
    
    # assemble MC estimates using only specified subset of all samples
    print '    -> valid pairs of samples (both fine and coarse samples loaded):'
    self.stats = {}
    for stat in stats:
      self.stats [ stat.name ] = stat.compute_all ( self.results, indices=indices, qois=qois )

# # # # # # # # # # # # # # # # # # # # # # # # # #
# Scheduler base class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers
from math import modf, ceil
import local

class Parallelization (object):
  
  def __init__ (self, cores, walltime, sharedmem, batch, batchmax=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # set scope (for batch)
    if batch:
      self.scope = 'batch'
    else:
      self.scope = 'single'
    
    # convert walltime to hours and minutes
    self.set_walltime (walltime)
    
    # memory usage is per core
    self.memory  = local.memory
    
    # compute nodes
    self.nodes = max ( 1, self.cores / local.cores )
    
    # if shared memory is available, use one rank per node
    if sharedmem:
      self.ranks   = self.nodes
      self.threads = local.threads * min ( local.cores, cores )
    
    # otherwise, use 'local.threads' ranks per core
    else:
      self.ranks   = self.cores * local.threads
      self.threads = 1
    
    # compute tasks = ranks_per_node
    self.tasks = self.ranks / self.nodes
  
  # convert walltime to hours and minutes
  def set_walltime (self, walltime):
    
    if walltime:
      frac, whole  = modf ( walltime )
      self.hours   = int  ( whole )
      self.minutes = int  ( ceil ( 60 * frac ) )
    else:
      self.hours   = None
      self.minutes = None
  
  # setup parallelization based on the number of samples
  def setup (self, count):
    
    # walltime is cumulative for all samples if batch mode
    if self.batch:
      self.set_walltime ( self.walltime * count )
    
    # take bootup time into account
    if self.hours == 0 and self.minutes < 2 * local.bootup:
      self.minutes += local.bootup
  
  # distribute ranks for ndims dimensions
  def reshape (self, ndims):
    counts = [1 for dim in range(ndims)]
    dim = 0
    from operator import mul
    while reduce(mul, counts, 1) != self.ranks:
      counts [ dim % ndims ] *= 2
      dim += 1
    return counts

class Scheduler (object):
  
  def setup (self, levels, levels_types, works, ratios, sharedmem):
    
    vars (self) .update ( locals() )
    
    self.L = len(levels) - 1
    self.parallelizations = helpers.level_type_list (levels)
    
    # if 'cores' is not provided
    if self.cores == None:

      # 'cores' is computed from 'nodes'
      if self.nodes == None:
        self.cores = local.cores * self.nodes
      
      # or 1 node is used
      else:
        self.nodes = 1
        self.cores = local.cores
    
    # if 'cores' is provided, 'nodes' is ignored and is computed from 'cores'
    else:
      self.nodes = max ( 1, self.cores / local.cores )
    
    # if 'walltime' is not provided, default value is used
    if self.walltime == None:
      self.walltime = local.walltime


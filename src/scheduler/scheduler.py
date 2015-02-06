
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

import sys

class Parallelization (object):
  
  def __init__ (self, cores, walltime, sharedmem, batch, batchmax=None):
    
    # save configuration
    vars (self) .update ( locals() )
    self.batchsize = None
    
    # set scope (for batch)
    if batch:
      self.scope = 'per batch'
    else:
      self.scope = 'per run'
    
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
    
    self.walltime = walltime
    
    if walltime:
      frac, whole  = modf ( walltime )
      self.hours   = int  ( whole )
      self.minutes = int  ( ceil ( 60 * frac ) )
    else:
      self.hours   = None
      self.minutes = None

  # adjust 'batchsize' and 'walltime' based on 'count' and 'batchmax'
  def adjust (self, count):
    
    # only for batch mode
    if not self.batch:
      return
    
    # check if we are not adjusting twice
    if self.batchsize != None:
      print ' :: ERROR: Parallelization.adjust() can be called only once!'
      sys.exit()
    
    # determine 'batchsize': required size of one part of the batch job
    if self.batchmax != None:
      self.batchsize = self.batchmax
    else:
      batchsize = count
    
    # adjust 'walltime' according to 'batchsize'
    if self.walltime != None:
      self.set_walltime ( self.walltime * batchsize )
  
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
      if self.nodes != None:
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


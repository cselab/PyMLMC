
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Parallelization class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers
from math import modf, floor, ceil
import local

import copy

class Parallelization (object):
  
  def __init__ (self, cores, walltime, sharedmem, batch=None, merge=None, email='', limit=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # convert walltime to hours and minutes
    self.set_walltime (walltime)
    
    # memory usage is per core
    self.memory = local.memory
    
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
    
    # set number of cores per cpu
    self.cpucores = local.cores
    
    # compute tasks = ranks_per_node
    self.tasks = self.ranks / self.nodes

    # set maximal batch size such that the total walltime does not exceed maximum walltime
    # remark: total walltime might still exceed the user-specified walltime
    if local.max_walltime (cores) != None:
      self.batchmax = max ( 1, int ( floor ( local.max_walltime (cores) / float (walltime) ) ) )
    else:
      self.batchmax = None

    # batchsize should not exceed the limit
    if limit != None:
      self.batchmax = min ( self.batchmax, int ( floor ( limit / float (walltime) ) ) )

    # set maximal merge size such that the maximum number of cores is not exceeded
    if local.max_cores != None:
      self.mergemax = int ( floor ( local.max_cores / float (cores) ) )
    else:
      self.mergemax = None
    
    # default merge size is 1 (no merging)
    self.merge = 1
  
  # convert walltime to hours and minutes
  def set_walltime (self, walltime):
    
    if walltime == None and local.walltime != None:
      walltime = local.walltime
    
    self.walltime = walltime
    
    if walltime:
      frac, whole  = modf ( walltime )
      self.hours   = int  ( whole )
      self.minutes = int  ( ceil ( 60 * frac ) )
    else:
      self.hours   = None
      self.minutes = None

  # adjust 'walltime' and 'cores'/'nodes' based on 'batch' and 'merge'
  def adjust (self):

    adjusted = copy.deepcopy (self)

    # only for batch mode
    if self.batch:

      # adjust 'walltime' according to 'batch'
      if self.walltime != None:
        adjusted.set_walltime ( self.walltime * self.batch )

    # only for ensembles mode
    if self.merge:

      # adjust 'cores'/'nodes' based on 'merge'
      adjusted.cores *= self.merge
      adjusted.nodes *= self.merge

    return adjusted

  # validate parallelization: minimum and maximum walltimes, bootup time, etc.
  def validate (self):

    # check if walltime does not exceed 'local.max_walltime'
    if self.walltime > local.max_walltime (self.cores):
      helpers.error ('\'walltime\' exceeds \'max_walltime\' in \'local.py\'', details = '%.2f > %.2f' % (self.walltime, local.max_walltime))

    # respect the minimal walltime of the machine
    if local.min_walltime != None:
      walltime = max ( local.min_walltime (self.cores), self.walltime )
      self.set_walltime (walltime)

    # take bootup time into account
    if self.hours == 0 and self.minutes < 2 * local.bootup:
      self.minutes += local.bootup

    return self

  # return dictionary of arguments
  def args (self):

    args = {}

    args ['ranks']    = self.ranks
    args ['threads']  = self.threads
    args ['cores']    = self.cores
    args ['nodes']    = self.nodes
    args ['tasks']    = self.tasks
    args ['cpucores'] = self.cpucores
    args ['merge']    = self.merge
    args ['hours']    = self.hours
    args ['minutes']  = self.minutes
    args ['memory']   = self.memory
    args ['email']    = self.email
    args ['envs']     = local.envs.rstrip()
    
    return args

  # distribute ranks for ndims dimensions
  def reshape (self, ndims):
    counts = [1 for dim in range(ndims)]
    dim = 0
    from operator import mul
    while reduce (mul, counts, 1) != self.ranks:
      counts [ dim % ndims ] *= 2
      dim += 1
    return counts
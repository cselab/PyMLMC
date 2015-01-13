
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Static scheduler class
# Load balancing is offloaded to the underlying job scheduling sub-system (LSF, SLURM, etc.)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from scheduler import *
import local
from numpy import round

class Static (Scheduler):
  
  def __init__ ( self, nodes=None, walltime=None, cores=None, separate=2 ):
    
    self.walltime = walltime
    self.nodes    = nodes
    self.cores    = cores
    self.separate = separate
  
  def distribute (self):
    
    print
    print ' :: SCHEDULER: static'
    
    for level, type in self.levels_types:
      
      required = self.cores / float(self.ratios [level - type])
      cores = max ( min ( local.threads, self.cores ), int ( round ( required ) ) )
      
      # walltime is decreased due to level (w.r.t to L) and increased due to fewer cores
      walltime = self.walltime * (float(self.works [level - type]) / self.works [self.L]) * (float(self.cores) / required)
      #walltime = self.walltime * (float(self.works [level - type]) / self.works [self.L]) * (float(self.cores) / cores)
      
      # process in batch all levels, except the 'self.separate' finest ones
      batch = ( level - type <= self.L - self.separate )
      
      # set maximal batch size such that the required walltime does not exceed specified walltime
      batchmax = int ( round ( self.walltime / walltime ) )
      
      # construct parallelization according to all computed parameters
      self.parallelizations [level] [type] = Parallelization ( cores, walltime, self.sharedmem, batch, batchmax )

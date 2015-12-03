
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Static scheduler class
# Load balancing is offloaded to the underlying job scheduling sub-system (LSF, SLURM, Cobalt, LoadLeveller, etc.)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from scheduler import *
import local
from numpy import round, floor, ceil

class Static (Scheduler):
  
  def __init__ ( self, nodes=None, walltime=None, cores=None, email='', separate=0, batchsize=1, ratios=None ):
    
    self.walltime  = walltime
    self.nodes     = nodes
    self.cores     = cores
    self.email     = email
    self.separate  = separate
    self.batchsize = batchsize
    self.ratios    = ratios
  
  def distribute (self):
    
    print
    print ' :: SCHEDULER: static'
    self.report ()

    for level, type in self.levels_types:
      
      required = self.cores / float (self.ratios [level - type])

      # respect the minimal amount of cores on the machine
      cores = max ( min ( local.min_cores, self.cores ), int ( round ( required ) ) )
      
      # walltime is decreased due to level (w.r.t to L) and increased due to fewer cores
      walltime = self.walltime * (float(self.works [level - type]) / self.works [self.L]) * (float(self.cores) / cores)

      # walltime is decreased if batching is enabled also on the finest level
      walltime /= self.batchsize

      # respect the minimal walltime of the machine
      if local.min_walltime (cores) != None:
        walltime = max ( local.min_walltime (cores), walltime )

      # process in batch all levels, except the 'self.separate' finest ones
      self.batch [level] [type] = ( level - type <= self.L - self.separate )

      # merge layers which are processed in batch to ensembles, if ensembles are supported
      if local.ensembles:
        self.merge [level] [type] = self.batch [level] [type]
      else:
        self.merge [level] [type] = 0

      # construct parallelization according to all computed parameters
      self.parallelizations [level] [type] = Parallelization ( cores, walltime, self.sharedmem, self.batch [level] [type], self.merge [level] [type], self.email )

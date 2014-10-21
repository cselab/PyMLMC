
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Static load balancing class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from balancer import *
import local

class Static (Balancer):
  
  def __init__ (self, cores=None, walltime=None ):
    
    self.cores = cores
    self.walltime = walltime
    
    if self.cores == None:
      self.cores = local.cores
    
    if self.walltime == None:
      self.walltime = local.walltime
  
  def distribute (self):
    
    print
    print ' :: BALANCER: static'
    
    for level, type in self.levels_types:
      cores = max ( min ( local.threads, self.cores ), int ( round ( self.cores / self.ratios [level - type] ) ) )
      walltime = self.walltime
      self.parallelizations [level] [type] = Parallelization ( cores, walltime )

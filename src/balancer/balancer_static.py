
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Static load balancing class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from balancer import Balancer

class Static (Balancer):
  
  def __init__ (self, cores):
    
    self.cores = cores
  
  def distribute (self):
    
    print
    print ' :: BALANCER: static'
    
    for level, type in self.levels_types:
      factor = self.works [ self.L ] / self.works [ level - type ]
      self.multi [level] [type] = max ( 1, int ( round ( self.cores / factor ) ) )

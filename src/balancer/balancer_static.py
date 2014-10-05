
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
    
    print ' :: BALANCER: static'
    
    for level, type in self.levels_types:
      factor = work [ self.L ] / work [ level - type ]
      self.multi [level] [type] = max ( 1, round ( self.cores / factor ) )

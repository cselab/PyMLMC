
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Static load balancing class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers

class Static (Balancer):
  
  def __init__ (self, cores):
    
    self.cores = cores
  
  def print (self):
    
    print ' :: BALANCER: static'
  
  def distribute (self):
    
    self.multi = helpers.level_type_list ()
    for level, type in helpers.level_type_list ():
      self.multi [level] [type] = max (1, self.cores / 2 ** (self.L - ( level - type ) ) )
  
  def multi (self, level, discretization):
    
    return

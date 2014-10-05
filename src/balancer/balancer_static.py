
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Static load balancing class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Static (Balancer):
  
  def __init__ (self, cores):
    
    self.cores = cores
  
  def print (self):
    
    print ' :: BALANCER: static'
  
  def distribute (self):
    
    self.multi = [ max (1, cores / 2 ** (self.L - level) ) for level in self.levels ]
  
  def multi (self, level, discretization):
    
    return

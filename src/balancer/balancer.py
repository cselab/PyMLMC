
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Balancer base class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Balancer (object):
  
  def setup (self, levels, works):
    
    self.levels = levels
    self.L      = len(levels) - 1
    self.works  = works
    
    self.print()

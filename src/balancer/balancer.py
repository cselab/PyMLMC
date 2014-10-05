
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Balancer base class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers

class Balancer (object):
  
  def setup (self, levels, levels_types, works):
    
    vars (self) .update ( locals() )
    self.L = len(levels) - 1
    self.multi = helpers.level_type_list (levels)

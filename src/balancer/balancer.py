
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Balancer base class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers
from math import modf, floor

class Parallelization (object):
  
  def __init__ (self, cores, walltime):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # convert walltime to hours and minutes
    frac, whole = modf ( self.walltime )
    self.hours  = int ( whole )
    self.minutes = int ( floor ( 100 * frac ) )

class Balancer (object):
  
  def setup (self, levels, levels_types, works, ratios):
    
    vars (self) .update ( locals() )
    
    self.L = len(levels) - 1
    self.parallelizations = helpers.level_type_list (levels)

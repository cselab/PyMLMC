
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
    vars (self) .update ( locals() )

class Balancer (object):
  
  def setup (self, levels, levels_types, works, ratios):
    
    vars (self) .update ( locals() )
    
    self.L = len(levels) - 1
    self.parallelizations = helpers.level_type_list (levels)
  
  def parse_walltime (self):
    
    frac, whole = modf (self.walltime )
    self.walltime_hours  = int ( whole )
    self.walltime_minutes = int ( floor ( 60 * frac ) )


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (one sample per each level)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from samples import *

class One_Per_Level (Samples):
  
  def init (self):
    
    print
    print ' :: SAMPLES: one sample per each level'
    
    self.counts.computed   = [ 0 for level in self.levels ]
    self.counts.additional = [ 1 for level in self.levels ]
    
    # set simulation type (deterministic or stochastic)
    self.deterministic = ( self.L == 0 )
  
  def finished (self, errors):
    return 1

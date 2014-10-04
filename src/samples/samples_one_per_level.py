
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
    
    self.counts  = Counts  ()
    self.indices = Indices ()
    
    print
    print ' :: SAMPLES: one sample per each level'
    
    self.counts.computed   = [ 0 for level in self.levels ]
    self.counts.additional = [ 1 for level in self.levels ]
  
  def finished (self):
    return 1

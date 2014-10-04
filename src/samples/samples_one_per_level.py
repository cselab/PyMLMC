
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (one sample per each level)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from samples import Samples

class One_Per_Level (Samples):
  
  def init (self, levels, works):
    
    # store configuration
    vars (self) .update ( locals() )
    
    print
    print ' :: SAMPLES: estimated'
    
    self.counts.additional = [ 1 ] * len (levels)
  
  def finished (self):
    return 1

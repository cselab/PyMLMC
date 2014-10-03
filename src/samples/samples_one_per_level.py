
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
    
    self.counts  = [ 1 ] * len (levels)
    self.indices = [ [1] ] * len (levels)
  
  def finished (self):
    return 1

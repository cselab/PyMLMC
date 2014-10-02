
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (one sample per each level)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class One_Per_Level (object):
  
  def init (self, levels):
    
    self.levels  = levels
    self.counts  = [ 1 ] * len (levels)
    self.indices = [ [1] ] * len (levels)


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
    self.counts  = [ None ] * len (levels)
    self.indices = [ None ] * len (levels)
    
    for level in self.levels:
      self.counts  [level] = 1
      self.indices [level] = [1]

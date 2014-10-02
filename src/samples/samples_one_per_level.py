
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (one sample per each level)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class One_per_level (object):
  
  def __init__ (self, levels, work):
    
    self.levels  = levels
    self.work    = work
    self.counts  = [ None ] * len (levels)
    self.indices = [ None ] * len (levels)
  
  def init (self):
    for level in levels:
      counts  [level] = 1
      indices [level] = [1]

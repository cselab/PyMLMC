
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Statistics class for general statistics from NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from stats import Stat
import numpy

class NumPy_Stat (Stat):
  
  def __init__ (self, stat, name=None):
    self.stat = getattr ( numpy, stat )
    if name:
      self.name = name
    else:
      self.name = stat
  
  # compute statistic 'self.stat' of given samples
  def compute (self, samples):
    
    return self.stat (samples)

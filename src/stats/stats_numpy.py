
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
  
  def __init__ (self, stat, name=None, params=None, style=''):
    self.stat = getattr ( numpy, stat )
    if name:
      self.name = name
    else:
      self.name = stat
    self.style  = style
    self.params = params
  
  # compute statistic 'self.stat' of given samples
  def compute (self, samples):
    
    if self.params:
      return self.stat (samples, self.params)
    else:
      return self.stat (samples)

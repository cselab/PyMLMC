
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
import warnings

class NumPy_Stat (Stat):
  
  def __init__ (self, stat, name=None, params=None, clip=None, alpha=0):
    
    self.size   = 1
    self.limit  = 1
    self.online = 0
    self.alpha  = min (1.0, 0.2 + 0.3 * factor)

    self.stat = getattr ( numpy, stat )

    if name:
      self.name = name
    else:
      self.name = stat
    
    self.params = params
    self.clip   = clip
    self.alpha  = alpha
  
  # compute statistic 'self.stat' of given samples
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')
    
    if self.params:
      return self.stat (samples, self.params)
    else:
      return self.stat (samples)

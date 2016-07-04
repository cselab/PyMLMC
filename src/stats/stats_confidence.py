
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Statistics class for confidence intervals using NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from stats import Stat
import numpy
import warnings

class Confidence (Stat):
  
  def __init__ (self, name=None, lower=5, upper=95):
    
    self.size = 2
    if name == None:
      self.name = 'confidence %d%% - %d%%' % (lower, upper)
    
  # compute statistic 'self.stat' of given samples
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')
    
    interval = numpy.empty (2)

    interval [0] = self.percentile (samples, lower)
    interval [1] = self.percentile (samples, upper)
    
    return interval
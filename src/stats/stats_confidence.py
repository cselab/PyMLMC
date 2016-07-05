
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
  
  def __init__ (self, name=None, level=5, lower=None, upper=None):
    
    self.size  = 2
    self.level = level
    self.lower = lower
    self.upper = upper
    if lower == None or upper == None:
      self.lower = level
      self.upper = 1.0 - level
    if level == None:
      self.level = min ( 0.5, max (self.lower, 1.0 - self.upper) )
    self.alpha = 1.0 - self.level

    if name == None:
      self.name = 'confidence %.2f - %.2f' % (self.lower, self.upper)
    
  # compute percentiles to form a confidence interval
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')
    
    interval = numpy.empty (2)

    interval [0] = numpy.percentile (samples, 100 * self.lower)
    interval [1] = numpy.percentile (samples, 100 * self.upper)
    
    return interval
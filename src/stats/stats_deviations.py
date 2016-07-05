
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Statistics class for standard deviations using NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from stats import Stat
import numpy
import warnings

class Deviations (Stat):
  
  def __init__ (self, name=None, factor=1):
    
    self.size   = 2
    self.factor = factor
    self.alpha  = min (1.0, 0.2 + 0.3 * factor)
    
    if name == None:
      self.name = 'mean +/- %d std. dev.' % self.factor

    self.clip = 0
    
  # compute mean and standard deviation
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')
    
    result = numpy.empty (2)

    mean = numpy.mean (samples)
    std  = numpy.std (samples, ddof=1)

    result [0] = mean - self.factor * std
    result [1] = mean + self.factor * std
    
    return result
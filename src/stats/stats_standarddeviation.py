
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

class Standard_Deviation_Interval (Stat):
  
  def __init__ (self, name=None):
    
    self.size  = 2
    self.alpha = 0.5

    if name == None:
      self.name = 'mean +/- std. dev.'
    
  # compute mean and standard deviation
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')
    
    result = numpy.empty (2)

    mean = numpy.mean (samples)

    result [0] = mean - numpy.std (samples, ddof=1)
    result [1] = mean + numpy.std (samples, ddof=1)
    
    return result
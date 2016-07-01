
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Statistics class for histograms using NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from stats import Stat
import numpy
import warnings

class Histogram (Stat):
  
  def __init__ (self, name='histogram', bins=100, range=None):
    
    self.size  = bins
    self.name  = name
    self.range = range
  
  # compute histogram using NumPy
  def compute (self, samples, range=None):

    warnings.simplefilter ('ignore')
    
    histogram, intervals = numpy.histogram (samples, bins=self.size, range=self.range)

    return histogram / float ( len (samples) )
  
  # return empty result in case no samples are available
  def empty (self):

    return numpy.full ( self.size, float ('nan') )

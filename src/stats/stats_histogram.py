
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
  
  def __init__ (self, name='histogram', bins=100):
    
    self.size = bins
    self.name = name
    self.clip = [0.0, 1.0]
  
  # compute histogram using NumPy
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')
    
    histogram, intervals = numpy.histogram (samples, bins=self.size, range=extent)

    return histogram / float ( len (samples) )


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
    
    self.name   = name
    self.size   = bins
    self.limit  = 1
    self.online = 0

    self.clip = [0.0, 1.0]
  
  # compute histogram using NumPy
  def compute (self, samples, extent):

    warnings.simplefilter ('ignore')

    histogram, intervals = numpy.histogram (samples, bins=self.size, range=extent)

    return histogram / float ( len (samples) )

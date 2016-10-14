
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Stats class for mean
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from stats import Stat
import copy

class Deviation (Stat):
  
  def __init__ (self, name='std. dev.', factor=1):

    self.size   = 1
    self.limit  = 2
    self.online = 1
    self.clip   = [0, None]

    self.name   = name
    self.factor = factor
    
  # initialize
  def init (self):
    
    self.count     = 0
    self.deviation = None
  
  # update estimate with a sample
  def update (self, sample, extent):

    # first sample is simply copied
    if self.count == 0:

      self.delta     = copy.deepcopy (sample)
      self.mean      = copy.deepcopy (self.delta)
      self.M2        = self.delta * (sample - self.mean)

      self.variance  = None
      self.deviation = None

      self.count     = 1
    
    # append additional sample in a numerically stable way
    else:
      
      self.count    += 1

      self.delta     = sample - self.mean
      self.mean     += self.delta / float (self.count)
      self.M2       += self.delta * (sample - self.mean)

      self.variance  = self.M2 / float (self.count - 1)
      self.deviation = self.variance ** 0.5
  
  # return the current estimate
  def result (self):

    return self.deviation
    

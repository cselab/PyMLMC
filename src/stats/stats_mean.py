
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

class Mean (Stat):
  
  def __init__ (self, name='mean'):
    
    self.name  = name

    self.size   = 1
    self.limit  = 1
    self.online = 1
    self.alpha  = 0
  
  # initialize
  def init (self):
    
    self.mean  = None
    self.count = 0
  
  # update estimate with a sample
  def update (self, sample, extent):

    # first sample is simply copied
    if self.count == 0:

      self.mean  = copy.deepcopy (sample)
      self.count = 1
    
    # append additional sample in a numerically stable way
    else:
      
      self.count += 1
      self.mean  = self.mean + (sample - self.mean) / float (self.count)
  
  # return the current estimate
  def result (self):

    return self.mean
    

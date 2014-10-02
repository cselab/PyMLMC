
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Stats class for general statistics from NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy

class NumPy_Stat (object):
  
  def __init__ (self, stat, name=None):
    self.stat = stat
    if name:
      self.name = name
    else:
      self.name = stat
  
  def compute (self, samples):
    return getattr (numpy, self.stat) (samples)


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Stats class for general stats from NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy

class NumPy_Stat (object):
  
  def __init__ (self, stat):
    self.stat = stat
  
  def compute (self, samples):
    return getattr (numpy, self.stat) (samples)


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Error indicators class
# TODO: add paper, description and link
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import numpy

# === local imports

import helpers

# === classes

class Indicators (object):
  
  def __init__ (self, indicator, levels, levels_types):
    
    # store configuration 
    self.indicator = indicator
    self.levels = levels
    self.levels_types = levels_types
  
  def compute (self, mcs):
    
    # list of results
    self.mean           = helpers.level_type_list(self.levels)
    self.variance       = helpers.level_type_list(self.levels)
    self.mean_diff      = self.levels [:]
    self.variance_diff  = self.levels [:]
    
    # compute indicators form MC results
    values = helpers.level_type_list(self.levels)
    for i, (level, type) in enumerate(self.levels_types):
      values [level] [type] = numpy.array ( [ self.indicator (result) for result in mcs [i] .results ] )
    
    # compute plain error indicators
    for level, type in self.levels_types:
      self.mean      [level] [type] = numpy.mean (values [level] [type])
      self.variance  [level] [type] = numpy.var  (values [level] [type])
    
    # compute error indicators for differences
    for level in self.levels:
      self.mean_diff      [level] = numpy.mean (values [level] [0] - values [level] [1])
      self.variance_diff  [level] = numpy.var  (values [level] [0] - values [level] [1])
    
  def report (self):
    
    print ' :: WARNING: indicator report() not yet implemented.'

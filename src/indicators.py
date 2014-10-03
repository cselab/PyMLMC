
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
    self.mean_diff      = numpy.array(self.levels [:], dtype=float)
    self.variance_diff  = numpy.array(self.levels [:], dtype=float)
    self.covariance     = numpy.array(self.levels [:], dtype=float)
    self.correlation    = numpy.array(self.levels [:], dtype=float)
    
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
    
    # compute covariance and correlation
    for level in self.levels:
      self.covariance     [level] = numpy.cov      (values [level] [0], values [level] [1]) [0][1]
      self.correlation    [level] = numpy.corrcoef (values [level] [0], values [level] [1]) [0][1]
  
  def report (self):
    
    # report mean
    print '    -> EPSILON [FI]:'
    for level in self.levels:
      print '%.2e' % self.mean [level] [0],
    print
    
    # report mean
    print '    -> EPSILON [CO]:'
    for level in self.levels:
      print '%.2e' % self.mean [level] [1],
    print
    
    # report variance
    print '    -> SIGMA   [FI]:'
    for level in self.levels:
      print '%.2e' % self.variance [level] [0] if self.variance [level] else '    N/A',
    print
    
    # report variance
    print '    -> SIGMA   [CO]:'
    for level in self.levels:
      print '%.2e' % self.variance [level] [1] if self.variance [level] else '    N/A',
    print
    
    # report mean_diff
    print '    -> EPSILON_DIFF:'
    for level in self.levels:
      print '%.2e' % self.mean_diff [level],
    print
    
    # report variance_diff
    print '    -> SIGMA_DIFF:  '
    for level in self.levels:
      print '%.2e' % self.variance_diff [level] if self.variance_diff [level] else '    N/A',
    print
    
    # report covariance
    print '    -> COVARIANCE:  '
    for level in self.levels:
      print '%.2e' % self.covariance [level] if self.covariance [level] else '    N/A',
    print
    
    # report correlation
    print '    -> CORRELATION: '
    for level in self.levels:
      print '%.2e' % self.correlation [level] if self.correlation [level] else '    N/A',
    print

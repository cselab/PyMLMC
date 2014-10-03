
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
from math import isnan

# === local imports

import helpers

# === classes

class Indicators (object):
  
  def __init__ (self, indicator, levels, levels_types):
    
    # store configuration 
    vars (self) .update ( locals() )
    self.L = len (self.levels) - 1
  
  def compute (self, mcs):
    
    # list of results
    self.mean           = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.variance       = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.mean_diff      = numpy.zeros ( self.L + 1, dtype=float)
    self.variance_diff  = numpy.zeros ( self.L + 1, dtype=float)
    self.covariance     = numpy.zeros ( self.L + 1, dtype=float)
    self.correlation    = numpy.zeros ( self.L + 1, dtype=float)
    
    # compute indicators form MC results
    values = helpers.level_type_list(self.levels)
    for i, (level, type) in enumerate(self.levels_types):
      values [level] [type] = numpy.array ( [ self.indicator (result) for result in mcs [i] .results ] )
    
    # compute plain error indicators
    for level, type in self.levels_types:
      self.mean     [level] [type] = numpy.abs ( numpy.mean (values [level] [type]) )
      self.variance [level] [type] = numpy.cov  (values [level] [type])
    
    # compute error indicators for differences
    self.mean_diff     [0] = numpy.abs ( numpy.mean (values [0] [0]) )
    self.variance_diff [0] = numpy.cov  (values [0] [0])
    for level in self.levels [1:] :
      self.mean_diff     [level] = numpy.abs ( numpy.mean (values [level] [0] - values [level] [1]) )
      self.variance_diff [level] = numpy.cov  (values [level] [0] - values [level] [1])
    
    # compute covariance and correlation
    self.covariance  [0] = float('NaN')
    self.correlation [0] = float('NaN')
    for level in self.levels [1:] :
      self.covariance  [level] = numpy.cov      (values [level] [0], values [level] [1]) [0][1]
      self.correlation [level] = numpy.corrcoef (values [level] [0], values [level] [1]) [0][1]
  
  def report (self):
    
    # report mean
    print '    -> EPSILON [FI]:',
    for level in self.levels:
      print '%.1e' % self.mean [level] [0],
    print
    
    # report mean
    print '    -> EPSILON [CO]:',
    for level in self.levels:
      print '%.1e' % self.mean [level] [1],
    print
    
    # report variance
    print '    -> SIGMA   [FI]:',
    for level in self.levels:
      print '%.1e' % self.variance [level] [0] if not isnan ( self.variance [level] [0] ) else '    N/A',
    print
    
    # report variance
    print '    -> SIGMA   [CO]:',
    for level in self.levels:
      print '%.1e' % self.variance [level] [1] if not isnan ( self.variance [level] [1] ) else '    N/A',
    print
    
    # report mean_diff
    print '    -> EPSILON_DIFF:',
    for level in self.levels:
      print '%.1e' % self.mean_diff [level],
    print
    
    # report variance_diff
    print '    -> SIGMA_DIFF:  ',
    for level in self.levels:
      print '%.1e' % self.variance_diff [level] if not isnan ( self.variance_diff [level] ) else '    N/A',
    print
    
    # report covariance
    print '    -> COVARIANCE:  ',
    for level in self.levels:
      print '%.1e' % self.covariance [level] if not isnan ( self.covariance [level] ) else '    N/A',
    print
    
    # report correlation
    print '    -> CORRELATION: ',
    for level in self.levels:
      print '   %.2f' % self.correlation [level] if not isnan ( self.correlation [level] ) else '    N/A',
    print

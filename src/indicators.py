
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

# === warnings suppression

import warnings
warnings.filterwarnings ("ignore", message="Degrees of freedom <= 0 for slice")

# === classes

class Indicators (object):
  
  def __init__ (self, indicator, levels, levels_types):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L = len (self.levels) - 1
    
    self.indicators_file = 'indicators.dat'

    self.available = 0

    self.nans      = 0
  
  def compute (self, mcs):

    # list of results
    self.mean           = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.variance       = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.mean_diff      = numpy.zeros ( self.L + 1, dtype=float)
    self.variance_diff  = numpy.zeros ( self.L + 1, dtype=float)
    self.covariance     = numpy.zeros ( self.L + 1, dtype=float)
    self.correlation    = numpy.zeros ( self.L + 1, dtype=float)

    # evaluate indicators for all samples on all levels and types
    values = helpers.level_type_list (self.levels)
    for i, (level, type) in enumerate (self.levels_types):
      values [level] [type] = numpy.array ( [ self.indicator ( result.data ) if result else float('NaN') for result in mcs [i] .results ] )
    
    # compute plain indicators
    for level, type in self.levels_types:
      self.mean     [level] [type] = numpy.abs ( numpy.mean (values [level] [type]) )
      self.variance [level] [type] = numpy.cov  (values [level] [type])
      if numpy.isnan ( self.mean     [level] [type] ) .any() :
        self.nans = 1
      if numpy.isnan ( self.variance [level] [type] ) .any() :
        self.nans = 1
    self.mean     [0] [1] = float ('NaN')
    self.variance [0] [1] = float ('NaN')
    
    # compute indicators for differences
    self.mean_diff     [0] = numpy.abs ( numpy.mean (values [0] [0]) )
    self.variance_diff [0] = numpy.cov  (values [0] [0])
    for level in self.levels [1:] :
      self.mean_diff     [level] = numpy.abs ( numpy.mean (values [level] [0] - values [level] [1]) )
      self.variance_diff [level] = numpy.cov  (values [level] [0] - values [level] [1])
      if numpy.isnan ( self.mean_diff     [level] ) .any() :
        self.nans = 1
      if numpy.isnan ( self.variance_diff [level] ) .any() :
        self.nans = 1

    # compute covariance and correlation
    self.covariance  [0] = float ('NaN')
    self.correlation [0] = float ('NaN')
    for level in self.levels [1:] :
      self.covariance  [level] = numpy.cov      (values [level] [0], values [level] [1]) [0][1]
      self.correlation [level] = numpy.corrcoef (values [level] [0], values [level] [1]) [0][1]
      if numpy.isnan ( self.covariance  [level] ) .any() :
        self.nans = 1
      if numpy.isnan ( self.correlation [level] ) .any() :
        self.nans = 1

    # set the normalization
    self.normalization = self.mean [self.L] [0]

    # set availability
    if numpy.isnan (self.normalization):
      self.available = 0
    else:
      self.available = 1

  def report (self):

    if not self.available:
      print
      print ' :: INDICATORS: not available since \'normalization\' is N/A'
      return

    print
    print ' :: INDICATORS: (normalized to %.1e)' % self.normalization
    
    # report mean (fine)
    print '  : EPSILON [FI]:',
    for level in self.levels:
      print '%.1e' % (self.mean [level] [0] / self.normalization) if not numpy.isnan ( self.mean [level] [0] ) else '    N/A',
    print
    
    # report mean (coarse)
    print '  : EPSILON [CO]:',
    print '    ---',
    for level in self.levels [1:]:
      print '%.1e' % (self.mean [level] [1] / self.normalization) if not numpy.isnan ( self.mean [level] [1] ) else '    N/A',
    print
    
    # report mean_diff
    print '  : EPSILON DIFF:',
    for level in self.levels:
      print '%.1e' % (self.mean_diff [level] / self.normalization) if not numpy.isnan ( self.mean_diff [level] ) else '    N/A',
    print
    
    # report variance (fine)
    print '  : SIGMA   [FI]:',
    for level in self.levels:
      print '%.1e' % (self.variance [level] [0] / (self.normalization) ** 2) if not numpy.isnan ( self.variance [level] [0] ) else '    N/A',
    print
    
    # report variance (coarse)
    print '  : SIGMA   [CO]:',
    print '    ---',
    for level in self.levels [1:]:
      print '%.1e' % (self.variance [level] [1] / (self.normalization) ** 2) if not numpy.isnan ( self.variance [level] [1] ) else '    N/A',
    print

    # report variance_diff
    print '  : SIGMA   DIFF:',
    for level in self.levels:
      print '%.1e' % (self.variance_diff [level] / (self.normalization) ** 2) if not numpy.isnan ( self.variance_diff [level] ) else '    N/A',
    print
    
    # report covariance
    print '  : COVARIANCE  :',
    print '    ---',
    for level in self.levels [1:]:
      print '%.1e' % (self.covariance [level] / (self.normalization) ** 2) if not numpy.isnan ( self.covariance [level] ) else '    N/A',
    print
    
    # report correlation
    print '  : CORRELATION :',
    print '    ---',
    for level in self.levels [1:]:
      print '   %.2f' % self.correlation [level] if not numpy.isnan ( self.correlation [level] ) else '    N/A',
    print
  
  def save (self):
    
    # save mean (fine)
    epsilon_fi = [ self.mean [level] [0] for level in self.levels ]
    helpers.dump (epsilon_fi, '%f', 'epsilon_fi', self.indicators_file)
    
    # save mean (coarse)
    epsilon_co = [ self.mean [level] [1] for level in self.levels ]
    helpers.dump (epsilon_co, '%f', 'epsilon_co', self.indicators_file)

    # save variance (fine)
    sigma_fi = [ self.variance [level] [0] for level in self.levels ]
    helpers.dump (sigma_fi, '%f', 'sigma_fi', self.indicators_file)

    # save variance (coarse)
    sigma_co = [ self.variance [level] [1] for level in self.levels ]
    helpers.dump (sigma_co, '%f', 'sigma_co', self.indicators_file)
    
    # save mean_diff
    helpers.dump (self.mean_diff, '%f', 'epsilon_diff', self.indicators_file)

    # save variance_diff
    helpers.dump (self.variance_diff, '%f', 'variance_diff', self.indicators_file)

    # save covariance
    helpers.dump (self.covariance, '%f', 'covariance', self.indicators_file)

    # save correlation
    helpers.dump (self.correlation, '%f', 'correlation', self.indicators_file)
  
  # extrapolate missing variance estimates using available estimates
  def extrapolate (self):

    for level in self.levels:
      if numpy.isnan ( self.variance_diff [level] ):
        if level != 0:
          self.variance_diff [level] = self.variance_diff [level-1] / 2
        else:
          self.variance_diff [level] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA DIFF\' not possible!')

    for level in self.levels:
      if numpy.isnan ( self.variance [level] [0] ):
        if level != 0:
          self.variance [level] [0] = self.variance [level-1] [0]
        else:
          self.variance [level] [0] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA [FINE]\' not possible!')
    
    for level in self.levels [1:]:
      if numpy.isnan ( self.variance [level] [1] ):
        if level != 1:
          self.variance [level] [1] = self.variance [level-1] [1]
        else:
          self.variance [level] [1] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA [COARSE]\' not possible!')

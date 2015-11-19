
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

import os
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
    
    self.L               = len (self.levels) - 1
    self.indicators_file = 'indicators.dat'
    self.available       = 0
    self.nans            = 0
    self.history         = {}
  
  def compute (self, mcs, loaded):

    # list of results
    self.mean           = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.variance       = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.mean_diff      = numpy.zeros ( self.L + 1, dtype=float)
    self.variance_diff  = numpy.zeros ( self.L + 1, dtype=float)
    self.covariance     = numpy.zeros ( self.L + 1, dtype=float)
    self.correlation    = numpy.zeros ( self.L + 1, dtype=float)

    values      = helpers.level_type_list (self.levels)
    values_diff = helpers.level_type_list (self.levels)

    # evaluate indicators for all samples on all levels and types
    for i, (level, type) in enumerate (self.levels_types):

      # compute plain values and values meant for level differences
      values      [level] [type] = numpy.array ( [ self.indicator ( result.data ) for result in mcs [i] .results if result != None ] )
      results_diff               = [ result for sample, result in enumerate (mcs [i] .results) if sample in loaded [level] ]
      values_diff [level] [type] = numpy.array ( [ self.indicator ( result.data ) for result in results_diff ] )

      # handle unavailable simulations
      if len (values [level] [type]) == 0:
        values [level] [type] = numpy.array ( [ float('NaN') ] )
      if len (values_diff [level] [type]) == 0:
        values_diff [level] [type] = numpy.array ( [ float('NaN') ] )

      # check if NaN's are present
      if numpy.isnan ( values [level] [type] ) .any():
        self.nans = 1
      if numpy.isnan ( values_diff [level] [type] ) .any():
        self.nans = 1
      if len ( values_diff [level] [type] ) < 2:
        self.nans = 1
      if len ( values_diff [level] [type] ) < 2:
        self.nans = 1
    
    # compute plain indicators
    for level, type in self.levels_types:
      self.mean     [level] [type] = numpy.abs ( numpy.mean (values [level] [type]) )
      self.variance [level] [type] = numpy.cov ( values [level] [type] )
    self.mean     [0] [1] = float ('NaN')
    self.variance [0] [1] = float ('NaN')
    
    # compute indicators for differences
    self.mean_diff     [0] = numpy.abs ( numpy.mean (values_diff [0] [0]) )
    self.variance_diff [0] = numpy.cov ( values_diff [0] [0] )
    for level in self.levels [1:] :
      self.mean_diff     [level] = numpy.abs ( numpy.mean (values_diff [level] [0] - values_diff [level] [1]) )
      self.variance_diff [level] = numpy.cov ( values_diff [level] [0] - values_diff [level] [1] )

    # compute covariance and correlation
    self.covariance  [0] = float ('NaN')
    self.correlation [0] = float ('NaN')
    for level in self.levels [1:] :
      self.covariance  [level] = numpy.cov      ( values_diff [level] [0], values_diff [level] [1] ) [0][1]
      self.correlation [level] = numpy.corrcoef ( values_diff [level] [0], values_diff [level] [1] ) [0][1]

    # set the normalization
    if numpy.isnan (self.mean [0] [0]):
      self.normalization = 1
      helpers.warning ('Defaulting \'normalization\' to 1.0 for indicators')
    else:
      self.normalization = self.mean [0] [0]

  def report (self):

    print
    print ' :: INDICATORS: (normalized to %.1e)' % self.normalization

    print '  :    LEVEL    :' + ''.join ( ['       %d' % level for level in self.levels ] )
    print '  :--------------' + (len (self.levels) * '--------')
    
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
  
  def save (self, iteration):

    # append history
    self.history ['epsilon_fi']    [iteration] = [ self.mean [level] [0] for level in self.levels ]
    self.history ['epsilon_co']    [iteration] = [ self.mean [level] [1] for level in self.levels ]
    self.history ['sigma_fi']      [iteration] = [ self.variance [level] [0] for level in self.levels ]
    self.history ['sigma_co']      [iteration] = [ self.variance [level] [1] for level in self.levels ]
    self.history ['epsilon_diff']  [iteration] = self.mean_diff
    self.history ['variance_diff'] [iteration] = self.variance_diff
    self.history ['covariance']    [iteration] = self.covariance
    self.history ['correlation']   [iteration] = self.correlation

    # dump history
    helpers.delete (self.indicators_file)
    for i in range (iteration):
      for variable in self.history:
        helpers.dump (self.history [variable] [i], '%f', variable, self.indicators_file, i)

  def load (self, config):

    if config.iteration > 0:
      self.history = {}
      execfile ( os.path.join (config.root, self.indicators_file), globals(), self.history )

  # extrapolate missing variance estimates using available estimates
  def extrapolate (self):
    
    self.available = 1

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

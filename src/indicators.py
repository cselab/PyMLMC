
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
  
  def __init__ (self, indicator, distance, levels, levels_types, pick):
    
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
    
    values    = helpers.level_type_list (self.levels)
    distances = helpers.level_list      (self.levels)

    # evaluate indicators for all samples on all levels and types
    for i, (level, type) in enumerate (self.levels_types):

      # compute plain values
      values [level] [type] = numpy.array ( [ self.indicator (result) for result in mcs [i] .results if result != None ] )

      # handle unavailable simulations
      if len (values [level] [type]) == 0:
        values [level] [type] = numpy.array ( [ float('NaN') ] )

      # check if NaN's are present
      # TODO: this should be checked later, after actual computations... :)
      if numpy.isnan (values [level] [type]) .any():
        self.nans = 1
      if len (values [level] [type]) < 2:
        self.nans = 1

    # evaluate level distances for all samples on all levels
    for level in self.levels:

      # compute distances for level differences
      results_f = [ result for sample, result in enumerate (mcs [ self.pick [level][0] ] .results) if sample in loaded [level] ]
      if level == 0:
        distances [level] = numpy.array ( [ self.distance (fi, None) for fi in results_f ] )
      else:
        results_c = [ result for sample, result in enumerate (mcs [ self.pick [level][1] ] .results) if sample in loaded [level] ]
        distances [level] = numpy.array ( [ self.distance (rf, rc) for rf, rc in zip (results_f, results_c) ] )

      # handle unavailable simulations
      if len (distances [level]) == 0:
        distances [level] = numpy.array ( [ float('NaN') ] )

      # check if NaN's are present
      # TODO: this should be checked later, after actual computations... :)
      if numpy.isnan (distances [level]) .any():
        self.nans = 1
      if len (distances [level]) < 2:
        self.nans = 1
      if len (distances [level]) < 1: # zero variance is NOT an option! (should be extrapolated!)
        self.nans = 1

    # compute indicators
    for level, type in self.levels_types:
      self.mean     [level] [type] = numpy.mean ( values [level] [type] )
      #self.mean     [level] [type] = numpy.nanmean ( values [level] [type] )
      self.variance [level] [type] = numpy.var  ( values [level] [type] ) if len (values [level] [type]) > 1 else float('nan')
      #self.variance [level] [type] = numpy.nanvar  ( values [level] [type] )  if len (values [level] [type]) > 1 else float('nan')
    self.mean     [0] [1] = float ('NaN')
    self.variance [0] [1] = float ('NaN')

    # compute level distances
    for level in self.levels:
      self.mean_diff     [level] = numpy.mean ( distances [level] )
      #self.mean_diff     [level] = numpy.nanmean ( distances [level] )
      self.variance_diff [level] = numpy.var  ( distances [level] ) if len (distances [level]) > 1 else float('nan')
      #self.variance_diff [level] = numpy.nanvar  ( distances [level] )  if len (distances [level]) > 1 else float('nan')

    # compute covariance and correlation
    self.covariance  [0] = float ('NaN')
    self.correlation [0] = float ('NaN')

    for level in self.levels [1:] :

      results_f = [ result for sample, result in enumerate (mcs [ self.pick [level][0] ] .results) if sample in loaded [level] ]
      results_c = [ result for sample, result in enumerate (mcs [ self.pick [level][1] ] .results) if sample in loaded [level] ]
      values_f  = numpy.array ( [ self.indicator (result) for result in results_f ] )
      values_c  = numpy.array ( [ self.indicator (result) for result in results_c ] )
      if len (loaded [level]) > 1:
        self.covariance  [level] = numpy.cov      ( values_f, values_c ) [0][1]
        self.correlation [level] = numpy.corrcoef ( values_f, values_c ) [0][1]
      else:
        self.covariance  [level] = float('nan')
        self.correlation [level] = float('nan')

      '''
      self.covariance  [level] = 0.5 * (self.variance [level] [0] + self.variance [level] [1] - self.variance_diff [level])
      self.correlation [level] = self.covariance [level] / numpy.sqrt (self.variance [level] [0] * self.variance [level] [1])
      '''

    # set the normalization
    if numpy.isnan (self.mean [0] [0]):
      self.normalization = 1
      helpers.warning ('Defaulting \'normalization\' to 1.0 for indicators')
    else:
      self.normalization = numpy.abs (self.mean [0] [0])

    # set availability
    self.available = 1

  def report (self):

    print
    print ' :: INDICATORS: (normalized to %s)' % helpers.scif (self.normalization)
    print '  :'
    print '  :    LEVEL    : ' + ' '.join ( [ '  ' + helpers.intf (level, table=1)       for level in self.levels ] )
    print '  :---------------' + '-'.join ( [        helpers.scif (None, table=1, bar=1) for level in self.levels ] )
    
    # report mean (fine)
    print '  : EPSILON [FI]:',
    for level in self.levels:
      print helpers.scif (self.mean [level] [0] / self.normalization, table=1),
    print
    
    # report mean (coarse)
    print '  : EPSILON [CO]:',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.mean [level] [1] / self.normalization, table=1),
    print
    
    # report mean_diff
    print '  : EPSILON DIFF:',
    for level in self.levels:
      print helpers.scif (self.mean_diff [level] / self.normalization, table=1),
    print
    
    # report variance (fine)
    print '  : SIGMA   [FI]:',
    for level in self.levels:
      print helpers.scif (self.variance [level] [0] / (self.normalization) ** 2, table=1),
    print
    
    # report variance (coarse)
    print '  : SIGMA   [CO]:',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.variance [level] [1] / (self.normalization) ** 2, table=1),
    print

    # report variance_diff
    print '  : SIGMA   DIFF:',
    for level in self.levels:
      print helpers.scif (self.variance_diff [level] / (self.normalization) ** 2, table=1),
    print
    
    # report covariance
    print '  : COVARIANCE  :',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.covariance [level] / (self.normalization) ** 2, table=1),
    print
    
    # report correlation
    print '  : CORRELATION :',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.correlation [level], table=1),
    print
  
  def save (self, iteration):

    # initialize history
    if len (self.history) == 0:
      self.history ['epsilon_fi']    = {}
      self.history ['epsilon_co']    = {}
      self.history ['sigma_fi']      = {}
      self.history ['sigma_co']      = {}
      self.history ['epsilon_diff']  = {}
      self.history ['variance_diff'] = {}
      self.history ['covariance']    = {}
      self.history ['correlation']   = {}

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
    for variable in self.history:
      for i in range (iteration + 1):
        helpers.dump (self.history [variable] [i], '%f', variable, self.indicators_file, i)

  def load (self, config):

    if config.iteration > 0:
      self.history = {}
      execfile ( os.path.join (config.root, self.indicators_file), globals(), self.history )

  # extrapolate missing indicators from the courser levels
  def extrapolate (self):
    
    self.available = 1

    for level in self.levels:
      if numpy.isnan ( self.variance_diff [level] ):
        if level != 0:
          self.mean_diff     [level] = self.mean_diff     [level-1] / 2
          self.variance_diff [level] = self.variance_diff [level-1] / 2
        else:
          self.mean_diff     [level] = numpy.nan
          self.variance_diff [level] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA DIFF\' not possible!')
    
    for level in self.levels:
      if numpy.isnan ( self.variance [level] [0] ):
        if level != 0:
          self.mean     [level] [0] = self.mean     [level-1] [0]
          self.variance [level] [0] = self.variance [level-1] [0]
        else:
          self.mean     [level] [0] = numpy.nan
          self.variance [level] [0] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA [FINE]\' not possible!')
    
    for level in self.levels [1:]:
      if numpy.isnan ( self.variance [level] [1] ):
        if level != 1:
          self.mean     [level] [1] = self.mean     [level-1] [1]
          self.variance [level] [1] = self.variance [level-1] [1]
        else:
          self.mean     [level] [1] = numpy.nan
          self.variance [level] [1] = numpy.nan
          helpers.warning ('Extrapolation of indicators \'SIGMA [COARSE]\' not possible!')

    # report indicators including extrapolated values
    self.report ()

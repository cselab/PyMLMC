
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
import sys
import numpy
from itertools import izip

# === local imports

import helpers
from coefficients import *

# === warnings suppression

import warnings
warnings.filterwarnings ("ignore", message="Degrees of freedom <= 0 for slice")

# === classes

class Indicators (object):
  
  def __init__ (self, indicator, distance, levels, levels_types, pick, works, recycle):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L               = len (self.levels) - 1
    self.indicators_file = 'indicators.dat'
    self.available       = 0
    self.nans            = 0
    self.extrapolated    = 0
    self.history         = {}
  
  def compute (self, mcs, indices):

    print
    print ' :: Computing INDICATORS...',
    sys.stdout.flush ()

    # set availability
    self.available = 1

    # === control variate COEFFICIENTS

    # initialize coefficients
    self.coefficients = Coefficients (self.levels, self.recycle)

    # === VALUES and DISTANCES

    # evaluates indicators for each level, type and sample for the specified indices
    values = self.values (mcs, indices)

    # evaluate distances between indicators for every two consecute levels of each sample for the specified indices
    distances = self.distances (mcs, indices)

    # === EPSILON (mean) & SIGMA (variance) indicators

    self.mean     = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )
    self.variance = numpy.zeros ( [ self.L + 1, 2 ], dtype=float )

    # compute mean and variance for all levels and types
    for level, type in self.levels_types:
      self.mean     [level] [type] = numpy.mean ( values [level] [type] )
      self.variance [level] [type] = numpy.var  ( values [level] [type] ) if len (values [level] [type]) > 1 else float ('nan')
    self.mean     [0] [1] = float ('nan')
    self.variance [0] [1] = float ('nan')

    # set the normalization
    if numpy.isnan (self.mean [0] [0]):
      self.normalization = 1
      helpers.warning ('Defaulting \'normalization\' to 1.0 for indicators')
    else:
      self.normalization = numpy.abs (self.mean [0] [0])

    # === COVARIANCES and CORRELATIONS

    self.covariance  = numpy.zeros ( self.L + 1, dtype=float)
    self.correlation = numpy.zeros ( self.L + 1, dtype=float)

    # compute covariance and correlation

    self.covariance  [0] = float ('nan')
    self.correlation [0] = float ('nan')

    # remark: computing covariances and correlations from 'values' leads to inconsistent estimations and should be avoided
    for level in self.levels [1:] :
      if len (indices [level]) > 1:
        self.covariance  [level] = 0.5 * ( self.variance [level] [0] + self.variance [level] [1] - numpy.var ( distances [level] ) )
        self.correlation [level] = self.covariance [level] / numpy.sqrt (self.variance [level] [0] * self.variance [level] [1])
      else:
        self.covariance  [level] = float ('nan')
        self.correlation [level] = float ('nan')
        self.nans = 1

    # extrapolate missing indicators
    if self.nans:
      self.extrapolate ()

    # === EPSILON_DIFF_PLAIN and SIGMA_DIFF_PLAIN level distance indicators
    # (WITHOUT optimal control variate coefficients computed above)

    self.mean_diff_plain     = numpy.zeros ( self.L + 1, dtype=float)
    self.variance_diff_plain = numpy.zeros ( self.L + 1, dtype=float)

    # compute level distances
    for level in self.levels:
      self.mean_diff_plain     [level] = numpy.mean ( distances [level] )
      if len (distances [level]) > 1:
        self.variance_diff_plain [level] = numpy.var  ( distances [level] ) if len (distances [level]) > 1 else float ('nan')
      else:
        self.variance_diff_plain [level] = float ('nan')
        self.nans = 1
    
    # extrapolate missing difference indicators
    if self.nans:
      self.extrapolate_diffs ()

    # === OPTIMAL control variate COEFFICIENTS

    # compute optimal control variate coefficients
    self.coefficients.optimize (self)

    # re-evaluate distances between indicators for every two consecute levels of each sample for the specified indices
    distances = self.distances (mcs, indices)

    # === EPSILON_DIFF and SIGMA_DIFF level distance indicators
    # (WITH optimal control variate coefficients computed above)

    self.mean_diff     = numpy.zeros ( self.L + 1, dtype=float)
    self.variance_diff = numpy.zeros ( self.L + 1, dtype=float)

    # compute level distances
    for level in self.levels:
      self.mean_diff     [level] = numpy.mean ( distances [level] )
      if len (distances [level]) > 1:
        self.variance_diff [level] = numpy.var  ( distances [level] ) if len (distances [level]) > 1 else float ('nan')
      else:
        self.variance_diff [level] = float ('nan')
        self.nans = 1

    # extrapolate missing difference indicators
    if self.nans:
      self.extrapolate_diffs_plain ()

    print 'done.'

  # evaluates indicators for each sample (alternatively, specific indices can also be provided)
  def values (self, mcs, indices=None):

    # container for results
    values = helpers.level_type_list (self.levels)

    # evaluate indicators for all samples on all levels and types
    for level, type in self.levels_types:

      # evaluate indicators
      if indices == None:
        values [level] [type] = numpy.array ( [ self.indicator (result) for result in mcs [ self.pick [level][type] ] .results if result != None ] )
      else:
        values [level] [type] = numpy.array ( [ self.indicator (result) for sample, result in enumerate (mcs [ self.pick [level][type] ] .results) if sample in indices [level] ] )

      # handle unavailable simulations
      if len (values [level] [type]) == 0:
        values [level] [type] = numpy.array ( [ float('NaN') ] )

      # check if NaN's are present
      # TODO: this should be checked later, after actual computations... :)
      if numpy.isnan (values [level] [type]) .any() or len (values [level] [type]) < 2:
        self.nans = 1

    return values

  # evaluates distances between indicators on every two consecute levels for each sample (alternatively, specific indices can also be provided)
  def distances (self, mcs, indices=None):

    # container for results
    distances = helpers.level_list (self.levels)

    # evaluate level distances for all samples on all levels
    for level in self.levels:

      # TODO: take into account optimal control variate coefficients!

      # for coarsest level, distance is taken w.r.t. 'None'
      if level == 0:
        if indices == None:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * result, None) for result in mcs [ self.pick [level][0] ] .results ] )
        else:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * result, None) for sample, result in enumerate (mcs [ self.pick [level][0] ] .results) if sample in indices [level] ] )

      # for the remaining levels, evaluate distance indicators between every two consecutive levels
      else:
        zipped = izip (mcs [ self.pick [level][0] ] .results, mcs [ self.pick [level][1] ] .results)
        if indices == None:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * fine, self.coefficients.values [level - 1] * coarse) for fine, coarse in zipped ] )
        else:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * fine, self.coefficients.values [level - 1] * coarse) for sample, (fine, coarse) in enumerate (zipped) if sample in indices [level] ] )

      # handle unavailable simulations
      if len (distances [level]) == 0:
        distances [level] = numpy.array ( [ float('NaN') ] )

      # check if NaN's are present
      # TODO: this should be checked later, after actual computations... :)
      if numpy.isnan (distances [level]) .any() or len (distances [level]) < 2:
        self.nans = 1

    return distances

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
    
    # report variance (fine)
    print '  : SIGMA   [FI]:',
    for level in self.levels:
      print helpers.scif (self.variance [level] [0] / (self.normalization ** 2), table=1),
    print
    
    # report variance (coarse)
    print '  : SIGMA   [CO]:',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.variance [level] [1] / (self.normalization ** 2), table=1),
    print

    # report mean_diff_plain
    print '  : EPSILON DIFF:',
    for level in self.levels:
      print helpers.scif (self.mean_diff_plain [level] / self.normalization, table=1),
    print

    # report variance_diff_plain
    print '  : SIGMA   DIFF:',
    for level in self.levels:
      print helpers.scif (self.variance_diff_plain [level] / (self.normalization ** 2), table=1),
    print

    # report covariance
    print '  : COVARIANCE  :',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.covariance [level] / (self.normalization ** 2), table=1),
    print

    # report correlation
    print '  : CORRELATION :',
    print '    ---',
    for level in self.levels [1:]:
      print helpers.scif (self.correlation [level], table=1),
    print

    # splitter
    print '  :---------------' + '-'.join ( [        helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report coefficients
    print '  : COEFFICIENT :',
    for level in self.levels:
      print helpers.scif (self.coefficients.values [level], table=1),
    print

    # report mean_diff
    print '  : EPSILON DIFF:',
    for level in self.levels:
      print helpers.scif (self.mean_diff [level] / self.normalization, table=1),
    print

    # report variance_diff
    print '  : SIGMA   DIFF:',
    for level in self.levels:
      print helpers.scif (self.variance_diff [level] / (self.normalization ** 2), table=1),
    print

    # issue a warning if some indicator values were extrapolated
    if self.extrapolated:
      helpers.warning ('Missing indicator values are extrapolated!')
  
  def save (self, iteration):

    # initialize history
    if len (self.history) == 0:
      self.history ['epsilon_fi']    = {}
      self.history ['epsilon_co']    = {}
      self.history ['sigma_fi']      = {}
      self.history ['sigma_co']      = {}
      self.history ['covariance']    = {}
      self.history ['correlation']   = {}
      self.history ['coefficients']  = {}
      self.history ['epsilon_diff']  = {}
      self.history ['variance_diff'] = {}

    # append history
    self.history ['epsilon_fi']    [iteration] = [ self.mean [level] [0] for level in self.levels ]
    self.history ['epsilon_co']    [iteration] = [ self.mean [level] [1] for level in self.levels ]
    self.history ['sigma_fi']      [iteration] = [ self.variance [level] [0] for level in self.levels ]
    self.history ['sigma_co']      [iteration] = [ self.variance [level] [1] for level in self.levels ]
    self.history ['covariance']    [iteration] = self.covariance
    self.history ['correlation']   [iteration] = self.correlation
    if 'coefficients' in self.history:
      self.history ['coefficients']  [iteration] = self.coefficients.values
    self.history ['epsilon_diff']  [iteration] = self.mean_diff
    self.history ['variance_diff'] [iteration] = self.variance_diff

    # dump history
    helpers.delete (self.indicators_file)
    for variable in self.history:
      for i in range (iteration + 1):
        helpers.dump (self.history [variable] [i], '%f', variable, self.indicators_file, i)

  def load (self, config):

    if config.iteration > 0:
      self.history = {}
      execfile ( os.path.join (config.root, self.indicators_file), globals(), self.history )

  # extrapolate missing indicators from the coarser levels
  def extrapolate (self):

    self.extrapolated = 1
    self.available    = 1

    # TODO: if at least two data points are available, use least squares interpolation to fit a linear function in log-log scale

    for level in self.levels:
      if numpy.isnan ( self.mean [level] [0] ):
        if level != 0:
          self.mean     [level] [0] = self.mean [level-1] [0]
        else:
          self.mean     [level] [0] = numpy.nan
          helpers.warning ('Extrapolation of indicators \'EPSILON [FINE]\' not possible!')

    for level in self.levels:
      if numpy.isnan ( self.variance [level] [0] ):
        if level != 0:
          self.variance [level] [0] = self.variance [level-1] [0]
        else:
          self.variance [level] [0] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA [FINE]\' not possible!')

    for level in self.levels [1:]:
      if numpy.isnan ( self.mean [level] [1] ):
        if level != 1:
          self.mean     [level] [1] = self.mean [level-1] [1]
        else:
          self.mean     [level] [1] = numpy.nan
          helpers.warning ('Extrapolation of indicators \'EPSILON [COARSE]\' not possible!')

    for level in self.levels [1:]:
      if numpy.isnan ( self.variance [level] [1] ):
        if level != 1:
          self.variance [level] [1] = self.variance [level-1] [1]
        else:
          self.variance [level] [1] = numpy.nan
          helpers.warning ('Extrapolation of indicators \'SIGMA [COARSE]\' not possible!')

    for level in self.levels [1:]:
      if numpy.isnan ( self.correlation [level] ):
        if level != 0:
          self.correlation [level] = self.correlation [level-1] + 0.5 * (1.0 - self.correlation [level-1])
        else:
          self.correlation [level] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'CORRELATION\' not possible!')

    for level in self.levels [1:]:
      if numpy.isnan ( self.covariance [level] ):
        if level != 0 and not numpy.isnan ( self.correlation [level] ):
          self.covariance [level] = self.correlation [level] * numpy.sqrt (self.variance [level] [0] * self.variance [level-1] [0])
        else:
          self.covariance [level] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'COVARIANCE\' not possible!')

    self.nans = 0

  # extrapolate missing difference indicators from the coarser levels
  def extrapolate_diffs (self):

    # TODO: if at least two data points are available, use least squares interpolation to fit a linear function in log-log scale

    for level in self.levels:
      if numpy.isnan ( self.mean_diff [level] ):
        if level != 0:
          self.mean_diff [level] = self.mean_diff [level-1] / 2
        else:
          self.mean_diff [level] = numpy.nan
          helpers.warning ('Extrapolation of indicators \'EPSILON DIFF\' not possible!')

    for level in self.levels:
      if numpy.isnan ( self.variance_diff [level] ):
        if level != 0:
          self.variance_diff [level] = self.variance_diff [level-1] / 2
        else:
          self.variance_diff [level] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA DIFF\' not possible!')

    self.nans = 0

  # extrapolate missing plain difference indicators from the coarser levels
  def extrapolate_diffs_plain (self):

    # TODO: if at least two data points are available, use least squares interpolation to fit a linear function in log-log scale

    for level in self.levels:
      if numpy.isnan ( self.mean_diff_plain [level] ):
        if level != 0:
          self.mean_diff_plain [level] = self.mean_diff_plain [level-1] / 2
        else:
          self.mean_diff_plain [level] = numpy.nan
          helpers.warning ('Extrapolation of indicators \'EPSILON DIFF\' not possible!')

    for level in self.levels:
      if numpy.isnan ( self.variance_diff_plain [level] ):
        if level != 0:
          self.variance_diff_plain [level] = self.variance_diff_plain [level-1] / 2
        else:
          self.variance_diff_plain [level] = numpy.nan
          self.available = 0
          helpers.warning ('Extrapolation of indicators \'SIGMA DIFF\' not possible!')

    self.nans = 0

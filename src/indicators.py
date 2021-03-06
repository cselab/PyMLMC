
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

# class for a single indicator with measured and infered valuess
class Indicator (object):

  def __init__ (self, name, levels, start=0):
    
    self.name   = name
    self.levels = levels
    self.start  = start

    # weights for each level
    #self.weights  = numpy.empty (len (levels))
    #self.weights.fill (float('nan'))

    # measured values (signed)
    self.measured = numpy.empty (len (levels))
    self.measured.fill (float('nan'))

    # accuracy of estimates
    self.accuracy = numpy.empty (len (levels))
    self.accuracy.fill (float('nan'))

    # infered values (magnitude)
    self.infered  = numpy.empty (len (levels))
    self.infered.fill (float('nan'))
  
  def __getitem__ (self, key):
    return getattr (self, key)

  def __setitem__(self, key, item):
    setattr (self, key, item) 
  
  def report (self, key, normalization=1.0):

    print '  : %-18s:' % self.name,
    #for level in self.levels [ : self.start ]:
    #  print '    ---',
    #for level in self.levels [ self.start : ]:
    for level in self.levels:
      if numpy.isnan (self [key] [level]):
        print '    N/A',
      else:
        print helpers.scif (self [key] [level] / normalization, table=1),
    print

# class for computation, inference and reporting of all indicators
class Indicators (object):
  
  def __init__ (self, indicator, distance, levels, levels_types, pick, FINE, COARSE, works, pairworks, recycle, inference = 'diffs', enforce = True, ocv = False):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L               = len (self.levels) - 1
    self.indicators_file = 'indicators.dat'
    self.available       = 0
    self.history         = {}
    self.infered         = 0

    # initialize control variate COEFFICIENTS
    self.coefficients = Coefficients (self.levels, self.recycle)

  def accuracy_mean (self, deviation, size):

    if size < 1:
      return float ('nan')
    else:
      return deviation / numpy.sqrt (size)

  def accuracy_variance (self, variance, size):

    if size < 2:
      return float ('nan')
    else:
      return variance * numpy.sqrt (2.0 / (size - 1))

  def accuracy_deviation (self, deviation, size):

    if size < 2:
      return float ('nan')
    else:
      return deviation * numpy.sqrt (0.5 / (size - 1))

  def compute (self, mcs, indices, L0):

    print
    print ' :: Computing INDICATORS...',
    sys.stdout.flush ()

    self.L0 = L0

    self.available = 1

    # === VALUES and DISTANCES

    # evaluates indicators for each level, type and sample for the specified indices
    values = self.values (mcs, indices)

    # evaluate distances between indicators for every two consecute levels of each sample for the specified indices
    distances = self.distances (mcs, indices)

    # === MEAN, VARIANCE & DEVIATION indicators

    self.mean      = [ Indicator ('MEAN      FINE', self.levels), Indicator ('MEAN      COARSE', self.levels, start = self.L0 + 1) ]
    self.variance  = [ Indicator ('VARIANCE  FINE', self.levels), Indicator ('VARIANCE  COARSE', self.levels, start = self.L0 + 1) ]
    self.deviation = [ Indicator ('DEVIATION FINE', self.levels), Indicator ('DEVIATION COARSE', self.levels, start = self.L0 + 1) ]

    # compute mean, variance and deviation for all levels and types
    for level, type in self.levels_types:
      #self.mean      [type] ['weights']  [level] = numpy.sqrt ( values [level] [type] .size )
      #self.variance  [type] ['weights']  [level] = numpy.sqrt ( values [level] [type] .size )
      self.mean      [type] ['measured'] [level] = numpy.mean ( numpy.abs ( values [level] [type] ) )
      self.variance  [type] ['measured'] [level] = numpy.var  ( values [level] [type], ddof = 1 ) if len (values [level] [type]) > 1 else float ('nan')
      self.deviation [type] ['measured'] [level] = numpy.std  ( values [level] [type], ddof = 1 ) if len (values [level] [type]) > 1 else float ('nan')
    
    # compute accuracy of mean, variance and deviations indicators for all levels and types
    for level, type in self.levels_types:
      size = values [level] [type] .size
      self.mean      [type] ['accuracy'] [level] = self.accuracy_mean      (self.deviation [type] ['measured'] [level], size)
      self.variance  [type] ['accuracy'] [level] = self.accuracy_variance  (self.variance  [type] ['measured'] [level], size)
      self.deviation [type] ['accuracy'] [level] = self.accuracy_deviation (self.deviation [type] ['measured'] [level], size)

    # set the normalization
    if numpy.isnan (self.mean [self.FINE] ['measured'] [self.L0]):
      self.normalization = 1
      helpers.warning ('Defaulting \'normalization\' to 1.0 for indicators')
    else:
      self.normalization = numpy.abs (self.mean [self.FINE] ['measured'] [self.L0])
    
    # least squares inference of indicator level values based on the magnitudes of measured level values
    self.infer (self.mean     [self.FINE  ], degree = 1, log = False, critical = False, min = 0)
    self.infer (self.mean     [self.COARSE], degree = 1, log = False, critical = False, min = 0)
    self.infer (self.variance [self.FINE  ], degree = 1, log = False, critical = True,  min = 0)
    self.infer (self.variance [self.COARSE], degree = 1, log = False, critical = True,  min = 0)

    # === MEAN DIFF and VARIANCE DIFF level distance indicators
    # (WITHOUT optimal control variate coefficients computed below)

    self.mean_diff      = Indicator ('MEAN      DIFF', self.levels, start = self.L0 + 1)
    self.variance_diff  = Indicator ('VARIANCE  DIFF', self.levels, start = self.L0 + 1)
    self.deviation_diff = Indicator ('DEVIATION DIFF', self.levels, start = self.L0 + 1)
    
    # compute level distances
    for level in self.levels:
      #self.mean_diff     ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      #self.variance_diff ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.mean_diff      ['measured'] [level] = numpy.mean ( numpy.abs ( distances [level] ) )
      self.variance_diff  ['measured'] [level] = numpy.var  ( distances [level], ddof = 1 ) if len (distances [level]) > 1 else float ('nan')
      self.deviation_diff ['measured'] [level] = numpy.std  ( distances [level], ddof = 1 ) if len (distances [level]) > 1 else float ('nan')
    
    # compute accuracy of mean diff and variance diff indicators for all levels and types
    for level, type in self.levels_types:
      size = distances [level] .size
      self.mean_diff      ['accuracy'] [level] = self.accuracy_mean      (self.deviation_diff ['measured'] [level], size)
      self.variance_diff  ['accuracy'] [level] = self.accuracy_variance  (self.variance_diff  ['measured'] [level], size)
      self.deviation_diff ['accuracy'] [level] = self.accuracy_deviation (self.deviation_diff ['measured'] [level], size)

    # least squares inference of indicator level values based on the magnitudes of measured level values
    # REMARK: in such case, 'infered' and 'optimal' values are inconsistent (differ even if all coeffs = 1), due to inconsistent computation
    #self.infer (self.mean_diff, degree=1, log=True, critical = False, min = 0)
    # compute 'mean diff' from infered 'mean'
    # REMARK: not very useful, since decay to zero is usually lost in such case (unless inference order > 0)
    self.mean_diff ['infered'] [ self.L0       ] = self.mean [self.FINE] ['infered'] [ self.L0 ]
    self.mean_diff ['infered'] [ self.L0 + 1 : ] = numpy.abs ( self.mean [self.FINE] ['infered'] [ self.L0 + 1 : ] - self.mean [self.COARSE] ['infered'] [ self.L0 + 1 : ] )

    # least squares inference of 'variance diff' indicator level values based on the magnitides of measured level values
    if self.inference == 'diffs':
      self.infer (self.variance_diff, degree = 1, log = True, critical = True, min = 0)

    # infered value of VARIANCE DIFF is always by default the infered value of VARIANCE [FINE]
    # REMARK: this needs to be after inference, which overwrites non-infered values from the measured ones
    self.variance_diff ['infered'] [self.L0] = self.variance [self.FINE] ['infered'] [self.L0]

    # === COVARIANCES and CORRELATIONS
    
    self.covariance  = Indicator ('COVARIANCE',  self.levels, start = self.L0 + 1)
    self.correlation = Indicator ('CORRELATION', self.levels, start = self.L0 + 1)
    
    # compute covariance and correlation (measured)
    # remark: computing covariances and correlations from 'values' leads to inconsistent estimations and should be avoided
    for level in self.levels [ self.L0 + 1 : ]:
      self.covariance  ['measured'] [level] = 0.5 * ( self.variance [self.FINE] ['measured'] [level] + self.variance [self.COARSE] ['measured'] [level] - self.variance_diff ['measured'] [level] )
      self.correlation ['measured'] [level] = self.covariance ['measured'] [level] / numpy.sqrt ( self.variance [self.FINE] ['measured'] [level] * self.variance [self.COARSE] ['measured'] [level] )

    # for 'diffs' inference, correlations and covariances are computed from infered 'variance_diff'
    if self.inference == 'diffs':

      # compute covariance and correlation (infered)
      for level in self.levels [ self.L0 + 1 : ]:
        self.covariance  ['infered'] [level] = 0.5 * ( self.variance [self.FINE] ['infered'] [level] + self.variance [self.COARSE] ['infered'] [level] - self.variance_diff ['infered'] [level] )
        max_covariance_magnitude = numpy.sqrt ( self.variance [self.FINE] ['infered'] [level] * self.variance [self.COARSE] ['infered']  [level] )
        if numpy.abs (self.covariance ['infered'] [level]) > max_covariance_magnitude:
          self.covariance ['infered'] [level] = numpy.sign (self.covariance ['infered'] [level]) * max_covariance_magnitude
        self.correlation ['infered'] [level] = self.covariance ['infered'] [level] / numpy.sqrt ( self.variance [self.FINE] ['infered'] [level] * self.variance [self.COARSE] ['infered']  [level] )
        #self.correlation ['infered'] [level] = numpy.minimum (  1, self.correlation ['infered']  [level] )
        #self.correlation ['infered'] [level] = numpy.maximum ( -1, self.correlation ['infered']  [level] )

    # for 'correlations' inference, 'correlations' is infered and variance diffs with covariances and computed from it
    elif self.inference == 'correlations':
      
      # least squares inference of indicator level values based on the magnitides of measured level values
      self.infer (self.correlation, degree = 1, log = True, offset = -1, factor = -1, critical = True, min = -1.0, max = 1.0)

      # compute covariance and variance diffs (infered)
      for level in self.levels [ self.L0 + 1 : ]:
        self.covariance    ['infered'] [level] = self.correlation ['infered'] [level] * numpy.sqrt ( self.variance [self.FINE] ['infered'] [level] * self.variance [self.COARSE] ['infered'] [level] )
        self.variance_diff ['infered'] [level] = self.variance [self.FINE] ['infered'] [level] + self.variance [self.COARSE] ['infered'] [level] - 2 * self.covariance ['infered'] [level]
        self.variance_diff ['infered'] [level] = numpy.maximum ( 0 , self.variance_diff ['infered'] [level] )

    # report non-available inference modes
    elif self.inference != None:

      helpers.error ('Inference mode \'%s\' is not implemented' % self.inference)

    print 'done.'

  def optimize (self, mcs, indices, L0, forecast=False):

    if self.ocv:
      print
      if forecast:
        print ' :: FORECAST'
      print ' :: Optimizing INDICATORS...',
      sys.stdout.flush ()

    # === OPTIMAL control variate COEFFICIENTS

    # compute optimal control variate coefficients
    if self.ocv:
      if forecast:
        self.coefficients.optimize (self)
      else:
        counts = [ len (indices [level]) for level in self.levels ]
        self.coefficients.optimize (self, samples=counts)

    # re-evaluate distances between indicators for every two consecute levels of each sample for the specified indices
    distances = self.distances (mcs, indices)
    
    # === MEAN DIFF and VARIANCE DIFF level distance indicators
    # (WITH optimal control variate coefficients computed above)
    
    self.mean_diff_opt     = Indicator ('MEAN     DIFF OPT', self.levels, start = self.L0 + 1)
    self.variance_diff_opt = Indicator ('VARIANCE DIFF OPT', self.levels, start = self.L0 + 1)

    # compute optimized level distances (measured values)
    for level in self.levels:
      self.mean_diff_opt     ['measured'] [level] = numpy.mean ( numpy.abs (distances [level]) )
      self.variance_diff_opt ['measured'] [level] = numpy.var  ( distances [level], ddof = 1 ) if len (distances [level]) > 1 else float ('nan')
    
    # compute magnitudes of optimized level distances (infered values)
    # remark: infering optimized differences from measured optimized differences could lead to inconsistencies with other infered indicators
    self.mean_diff_opt     ['infered'] [self.L0] = self.coefficients.values [self.L0]         * self.mean     [self.FINE]   ['infered'] [self.L0]
    self.variance_diff_opt ['infered'] [self.L0] = self.coefficients.values [self.L0]    ** 2 * self.variance [self.FINE]   ['infered'] [self.L0]
    for level in self.levels [ self.L0 + 1 : ]:
      self.mean_diff_opt     ['infered'] [level]  = self.coefficients.values [level    ]      * self.mean     [self.FINE]   ['infered'] [level]
      self.mean_diff_opt     ['infered'] [level] -= self.coefficients.values [level - 1]      * self.mean     [self.COARSE] ['infered'] [level]
      self.mean_diff_opt     ['infered'] [level]  = numpy.abs ( self.mean_diff_opt ['infered'] [level] )
      self.variance_diff_opt ['infered'] [level]  = self.coefficients.values [level    ] ** 2 * self.variance [self.FINE]   ['infered'] [level]
      self.variance_diff_opt ['infered'] [level] += self.coefficients.values [level - 1] ** 2 * self.variance [self.COARSE] ['infered'] [level]
      self.variance_diff_opt ['infered'] [level] -= 2 * self.coefficients.values [level] * self.coefficients.values [level - 1] * self.covariance ['infered'] [level]
      self.variance_diff_opt ['infered'] [level]  = numpy.maximum ( 0, self.variance_diff_opt ['infered'] [level] )

    if self.ocv:
      print 'done.'

    # report only of OCV is enabled and successful
    if self.ocv:

      # === report measured values
      print
      if forecast:
        print ' :: FORECAST'
      print ' :: OPTIMIZED INDICATORS: (normalized to %s)' % helpers.scif (self.normalization)
      print '  :'
      print '  :       LEVEL       : ' + ' '.join ( [ '  ' + helpers.intf (level, table=1)       for level in self.levels ] )
      print '  :---------------------' + '-'.join ( [        helpers.scif (None, table=1, bar=1) for level in self.levels ] )

      # report 'coefficients' and OCV MLMC vs. PLAIN MLMC speedup from coefficient optimization
      print '  : %-18s:' % 'COEFFICIENT',
      for level in self.levels:
        print helpers.scif (self.coefficients.values [level], table=1),
      print

      # report 'mean diff opt'
      self.mean_diff_opt.report ('infered', self.normalization)

      # report 'variance diff opt'
      self.variance_diff_opt.report ('infered', self.normalization ** 2)

      # report optimization performance
      if self.coefficients.optimization != None:
        print
        if forecast:
          print ' :: FORECAST'
        print ' :: OPTIMIZATION (OCV vs. PLAIN): %.2f' % self.coefficients.optimization

  # evaluates indicators for each sample (alternatively, specific indices can also be provided)
  def values (self, mcs, indices=None):

    # container for results
    values = helpers.level_type_list (self.levels)

    # evaluate indicators for all samples on all levels and types
    for level, type in self.levels_types:

      # bugfix when self.L0 != 0
      if level == self.L0 and type == self.COARSE:
        values [level] [type] = numpy.array ( [ float('nan') ] )
        continue

      # evaluate indicators
      if indices == None:
        values [level] [type] = numpy.array ( [ self.indicator (result) for result in mcs [ self.pick [level] [type] ] .results if result != None ] )
      else:
        values [level] [type] = numpy.array ( [ self.indicator (result) for sample, result in enumerate (mcs [ self.pick [level] [type] ] .results) if sample in indices [level] ] )

      # handle unavailable simulations
      if len (values [level] [type]) == 0:
        values [level] [type] = numpy.array ( [ float('nan') ] )
    
    return values

  # evaluates distances between indicators on every two consecute levels for each sample (alternatively, specific indices can also be provided)
  def distances (self, mcs, indices=None):
    
    # container for results
    distances = helpers.level_list (self.levels)

    # evaluate level distances for all samples on all levels
    for level in self.levels:

      # TODO: take into account optimal control variate coefficients!

      # for coarsest level, distance is taken w.r.t. 'None'
      if level == self.L0:
        if indices == None:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * result, None) for result in mcs [ self.pick [level] [self.FINE] ] .results ] )
        else:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * result, None) for sample, result in enumerate (mcs [ self.pick [level] [self.FINE] ] .results) if sample in indices [level] ] )
      
      # for the remaining levels, evaluate distance indicators between every two consecutive levels
      elif level > self.L0:
        zipped = izip (mcs [ self.pick [level] [self.FINE] ] .results, mcs [ self.pick [level] [self.COARSE] ] .results)
        if indices == None:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * fine, self.coefficients.values [level - 1] * coarse) for fine, coarse in zipped ] )
        else:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * fine, self.coefficients.values [level - 1] * coarse) for sample, (fine, coarse) in enumerate (zipped) if sample in indices [level] ] )
      
      # handle unavailable simulations
      if level < self.L0 or len (distances [level]) == 0:
        distances [level] = numpy.array ( [ float('nan') ] )

    return distances
  
  # least squares inference of indicator level values based on the magnitudes of measured level values
  def infer (self, indicator, degree=1, log=0, exp=0, offset=0, factor=1, critical=0, min=None, max=None):

    # check if inference is not enforced
    if not self.enforce:
      
      # proceed only in case some indicators are not available
      if not numpy.isnan (indicator ['measured'] [indicator.start:]) .any ():
      
        # simply copy all values
        indicator ['infered'] = indicator ['measured'] [:]

        # do not proceed with the inference
        return

    # inference will be performed
    self.infered = 1

    # simply copy all values before 'start'
    indicator ['infered'] [:indicator.start] = indicator ['measured'] [:indicator.start]

    # filter out invalid entries
    levels  = numpy.array (self.levels [indicator.start:]) [ ~ numpy.isnan (indicator ['measured'] [indicator.start:]) ]
    values  = numpy.abs  ( indicator ['measured'] [levels] )
    if not numpy.isnan ( indicator ['accuracy'] [levels] ) .any ():
      weights = 1.0 / indicator ['accuracy'] [levels]
    else:
      weights = None

    # add offset, if specified
    values += offset

    # use factor, if specified
    values *= factor

    # check if sufficiently many measurements are available for inference
    if (not exp and len (values) < degree + 1) or (exp and len (values) < 3):
      if critical:
        self.available = 0
      helpers.warning ('Inference of indicator \'%s\' not possible!' % indicator.name)
      return

    '''
    # if only one measurement is available, assign it to all infered level values
    if  len (values) == 1:
      indicator ['infered'] [indicator.start:] = values [0]
      return
    '''
    
    # nonlinear fit for y = a * exp (b * x) + c
    if exp:

      # not yet implemented
      helpers.warning ('Inference of indicator \'%s\' using nonlinear fit not implemented!' % indicator.name)
      return

    # linear fit for y = a * x + b or y = a * exp (b * x)
    else:

      # use log-coordinates, if specified
      if log:
        values = numpy.log (values)

      # fit a linear polynomial to absolute valus in log-scale using linear least squares, weighted by data uncertainties
      #if not numpy.isnan ( indicator ['accuracy'] [levels] ) .any ():
      #  line = numpy.polyfit ( levels, values, degree, w = weights )
      #else:
      line = numpy.polyfit ( levels, values, degree )

      # get infered maximum likelihood values
      infered = numpy.polyval (line, self.levels)

      # transform back to linear coordinates
      if log:
        infered = numpy.exp (infered)

    # use factor, if specified
    infered /= factor

    # subtract offset, if specified
    infered -= offset

    # respect envelope specifications
    if min != None:
      infered = numpy.maximum ( min, infered )
    if max != None:
      infered = numpy.minimum ( max, infered )

    # if inference is enforced, update all indicator values to the infered values
    if self.enforce:
      indicator ['infered'] [indicator.start:] = infered [indicator.start:]

    # otherwise, update only invalid entries
    else:
      indicator ['infered'] [indicator.start:] = indicator ['measured'] [indicator.start:]
      levels = numpy.array (self.levels [indicator.start:]) [ numpy.isnan (indicator ['measured'] [indicator.start:]) ]
      indicator ['infered'] [levels] = infered [levels]
  
  def report (self):

    # === report measured values

    print
    print ' :: MEASURED INDICATORS: (normalized to %s)' % helpers.scif (self.normalization)
    print '  :'
    print '  :       LEVEL       : ' + ' '.join ( [ '  ' + helpers.intf (level, table=1)       for level in self.levels ] )
    print '  :---------------------' + '-'.join ( [        helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'correlation'
    self.correlation.report ('measured')

    # splitter
    print '  :---------------------' + '-'.join ( [ helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'mean (fine)'
    self.mean [self.FINE] .report ('measured', self.normalization)
    
    # report 'mean (coarse)'
    self.mean [self.COARSE] .report ('measured', self.normalization)
    
    # report 'variance (fine)'
    self.variance [self.FINE] .report ('measured', self.normalization ** 2)
    
    # report 'variance (coarse)'
    self.variance [self.COARSE] .report ('measured', self.normalization ** 2)

    # report 'mean diff'
    self.mean_diff.report ('measured', self.normalization)

    # report 'variance diff'
    self.variance_diff.report ('measured', self.normalization ** 2)
    
    # report 'covariance'
    self.covariance.report ('measured', self.normalization ** 2)

    '''
    # splitter
    print '  :---------------------' + '-'.join ( [ helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'coefficients' and OCV MLMC vs. PLAIN MLMC speedup from coefficient optimization
    print '  : %-18s:' % 'COEFFICIENT',
    for level in self.levels:
      print helpers.scif (self.coefficients.values [level], table=1),
    if self.coefficients.optimization != None:
      print '[OPTIMIZATION: %.2f]' % self.coefficients.optimization,
    print
    
    # report 'mean diff opt'
    self.mean_diff_opt.report ('measured', self.normalization)

    # report 'variance diff opt'
    self.variance_diff_opt.report ('measured', self.normalization ** 2)
    '''

    # === report infered values

    if not self.inference:
      print
      print ' :: INFERENCE OF INDICATORS IS DISABLED'
      return

    if not self.infered:
      print
      print ' :: INFERENCE OF INDICATORS IS NOT NECESSARY'
      return
    
    print
    print ' :: INFERED INDICATORS: (w.r.t. \'%s\'%s, normalized to %s)' % ( self.inference, ' [enforced]' if self.enforce else ' [not enforced]', helpers.scif (self.normalization) )
    print '  :'
    print '  :       LEVEL       : ' + ' '.join ( [ '  ' + helpers.intf (level, table=1)       for level in self.levels ] )
    print '  :---------------------' + '-'.join ( [        helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'correlation'
    self.correlation.report ('infered')

    # splitter
    print '  :---------------------' + '-'.join ( [ helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'mean (fine)'
    self.mean [self.FINE] .report ('infered', self.normalization)
    
    # report 'mean (coarse)'
    self.mean [self.COARSE] .report ('infered', self.normalization)
    
    # report 'variance (fine)'
    self.variance [self.FINE] .report ('infered', self.normalization ** 2)
    
    # report 'variance (coarse)'
    self.variance [self.COARSE] .report ('infered', self.normalization ** 2)

    # report 'mean diff'
    self.mean_diff.report ('infered', self.normalization)

    # report 'variance diff'
    self.variance_diff.report ('infered', self.normalization ** 2)
    
    # report 'covariance'
    self.covariance.report ('infered', self.normalization ** 2)
  
  def save (self, iteration):

    origins = ['measured', 'infered']

    # initialize history
    if len (self.history) == 0:
      for origin in origins:
        self.history ['mean_fine_'         + origin] = {}
        self.history ['mean_coarse_'       + origin] = {}
        self.history ['variance_fine_'     + origin] = {}
        self.history ['variance_coarse_'   + origin] = {}
        self.history ['covariance_'        + origin] = {}
        self.history ['correlation_'       + origin] = {}
        self.history ['coefficients_'      + origin] = {}
        self.history ['mean_diff_'         + origin] = {}
        self.history ['variance_diff_'     + origin] = {}
        self.history ['mean_diff_opt_'     + origin] = {}
        self.history ['variance_diff_opt_' + origin] = {}

    # append history
    for origin in origins:
      self.history ['mean_fine_'         + origin] [iteration] = self.mean     [self.FINE]   [origin]
      self.history ['mean_coarse_'       + origin] [iteration] = self.mean     [self.COARSE] [origin]
      self.history ['variance_fine_'     + origin] [iteration] = self.variance [self.FINE]   [origin]
      self.history ['variance_coarse_'   + origin] [iteration] = self.variance [self.COARSE] [origin]
      self.history ['covariance_'        + origin] [iteration] = self.covariance             [origin]
      self.history ['correlation_'       + origin] [iteration] = self.correlation            [origin]
      self.history ['coefficients_'      + origin] [iteration] = self.coefficients.values
      self.history ['mean_diff_'         + origin] [iteration] = self.mean_diff              [origin]
      self.history ['variance_diff_'     + origin] [iteration] = self.variance_diff          [origin]
      self.history ['mean_diff_opt_'     + origin] [iteration] = self.mean_diff_opt          [origin]
      self.history ['variance_diff_opt_' + origin] [iteration] = self.variance_diff_opt      [origin]
    
    # dump history
    helpers.delete (self.indicators_file)
    for variable in self.history:
      for i in range (iteration + 1):
        helpers.dump (self.history [variable] [i], '%f', variable, self.indicators_file, i)

  def load (self, config):

    if config.iteration > 0:

      self.history = {}
      execfile ( os.path.join (config.root, self.indicators_file), globals(), self.history )

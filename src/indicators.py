
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
    self.weights  = numpy.full ( len (levels), float ('nan') )

    # measured values (signed)
    self.measured = numpy.full ( len (levels), float ('nan') )

    # accuracy of estimates
    self.accuracy = numpy.full ( len (levels), float ('nan') )

    # infered values (magnitude)
    self.infered  = numpy.full ( len (levels), float ('nan') )
  
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
  
  def __init__ (self, indicator, distance, levels, levels_types, pick, FINE, COARSE, works, pairworks, recycle, inference = 'diffs', lsqfit = True, enforce = True):
    
    # store configuration 
    vars (self) .update ( locals() )
    
    self.L               = len (self.levels) - 1
    self.indicators_file = 'indicators.dat'
    self.available       = 0
    self.history         = {}
  
  def accuracy (self, values, moment = 1):

    if values.size > moment:
      power = 2 * moment
      return numpy.power ( numpy.mean ( (values - numpy.mean (values)) ** power ) / (values.size - moment), 1.0 / power )
    else:
      return float ('nan')

  def compute (self, mcs, indices):

    print
    print ' :: Computing INDICATORS...',
    sys.stdout.flush ()

    self.available = 1

    # === initialize control variate COEFFICIENTS

    # initialize coefficients
    self.coefficients = Coefficients (self.levels, self.recycle)

    # === VALUES and DISTANCES

    # evaluates indicators for each level, type and sample for the specified indices
    values = self.values (mcs, indices)

    # evaluate distances between indicators for every two consecute levels of each sample for the specified indices
    distances = self.distances (mcs, indices)

    # === MEAN & VARIANCE indicators

    self.mean     = [ Indicator ('MEAN     FINE', self.levels), Indicator ('MEAN     COARSE', self.levels, start = 1) ]
    self.variance = [ Indicator ('VARIANCE FINE', self.levels), Indicator ('VARIANCE COARSE', self.levels, start = 1) ]

    # compute mean and variance for all levels and types
    for level, type in self.levels_types:
      self.mean     [type] ['weights']  [level] = numpy.sqrt ( values [level] [type] .size )
      self.variance [type] ['weights']  [level] = numpy.sqrt ( values [level] [type] .size )
      self.mean     [type] ['measured'] [level] = numpy.mean ( values [level] [type] )
      self.variance [type] ['measured'] [level] = numpy.var  ( values [level] [type], ddof = 1 ) if len (values [level] [type]) > 1 else float ('nan')
    
    # compute accuracy of mean and variance indicators for all levels and types
    for level, type in self.levels_types:
      self.mean     [type] ['accuracy'] [level] = self.accuracy (values [level] [type], moment = 1)
      self.variance [type] ['accuracy'] [level] = self.accuracy (values [level] [type], moment = 2)
    
    # set the normalization
    if numpy.isnan (self.mean [self.FINE] ['measured'] [0]):
      self.normalization = 1
      helpers.warning ('Defaulting \'normalization\' to 1.0 for indicators')
    else:
      self.normalization = numpy.abs (self.mean [self.FINE] ['measured'] [0])
    
    # least squares inference of indicator level values based on the magnitides of measured level values
    self.infer (self.mean     [self.FINE  ], degree=0, log=True, critical = False)
    self.infer (self.mean     [self.COARSE], degree=0, log=True, critical = False)
    self.infer (self.variance [self.FINE  ], degree=0, log=True, critical = True )
    self.infer (self.variance [self.COARSE], degree=0, log=True, critical = True )

    # === MEAN DIFF and VARIANCE DIFF level distance indicators
    # (WITHOUT optimal control variate coefficients computed below)

    self.mean_diff     = Indicator ('MEAN     DIFF', self.levels, start = 1)
    self.variance_diff = Indicator ('VARIANCE DIFF', self.levels, start = 1)
    
    # compute level distances
    for level in self.levels:
      self.mean_diff     ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.variance_diff ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.mean_diff     ['measured'] [level] = numpy.mean ( distances [level] )
      self.variance_diff ['measured'] [level] = numpy.var  ( distances [level], ddof = 1 ) if len (distances [level]) > 1 else float ('nan')
    
    # compute accuracy of mean diff and variance diff indicators for all levels and types
    for level, type in self.levels_types:
      self.mean_diff     ['accuracy'] [level] = self.accuracy (distances [level], moment = 1)
      self.variance_diff ['accuracy'] [level] = self.accuracy (distances [level], moment = 2)

    # least squares inference of indicator level values based on the magnitides of measured level values
    #self.infer (self.mean_diff, log=True, critical = False)
    # compute 'mean diff' from infered 'mean'
    self.mean_diff ['infered'] [ 0   ] = self.mean [self.FINE] ['infered'] [ 0 ]
    self.mean_diff ['infered'] [ 1 : ] = numpy.abs ( self.mean [self.FINE] ['infered'] [ 1 : ] - self.mean [self.COARSE] ['infered'] [ 1 : ] )
    
    # least squares inference of 'variance diff' indicator level values based on the magnitides of measured level values
    if self.inference == 'diffs':
      self.infer (self.variance_diff, degree=1, log=True, critical = True )
      self.variance_diff ['infered'] [0] = self.variance [self.FINE] ['infered'] [0]

    # === COVARIANCES and CORRELATIONS
    
    self.covariance  = Indicator ('COVARIANCE',  self.levels, start = 1)
    self.correlation = Indicator ('CORRELATION', self.levels, start = 1)
    
    # compute covariance and correlation (measured)
    # remark: computing covariances and correlations from 'values' leads to inconsistent estimations and should be avoided
    for level in self.levels [ 1 : ]:
      self.covariance  ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.covariance  ['measured'] [level] = 0.5 * ( self.variance [self.FINE] ['measured'] [level] + self.variance [self.COARSE] ['measured'] [level] - self.variance_diff ['measured'] [level] )
      self.correlation ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.correlation ['measured'] [level] = self.covariance ['measured'] [level] / numpy.sqrt ( self.variance [self.FINE] ['measured'] [level] * self.variance [self.COARSE] ['measured'] [level] )

    # for 'diffs' inference, correlations and covariances are computed from infered 'variance_diff'
    if self.inference == 'diffs':

      # compute covariance and correlation (infered)
      for level in self.levels [ 1 : ]:
        self.covariance  ['infered']  [level] = 0.5 * ( self.variance [self.FINE] ['infered'] [level] + self.variance [self.COARSE] ['infered'] [level] - self.variance_diff ['infered']  [level] )
        self.correlation ['infered']  [level] = self.covariance ['infered'] [level] / numpy.sqrt ( self.variance [self.FINE] ['infered'] [level] * self.variance [self.COARSE] ['infered']  [level] )
    
    # for 'correlations' inference, 'correlations' is infered and variance diffs with covariances and computed from it
    elif:
      
      # least squares inference of indicator level values based on the magnitides of measured level values
      self.infer (self.correlation, degree=1, log=False, critical = True, min = -1.0, max = 1.0)

      # compute covariance and variance diffs (infered)
      for level in self.levels [ 1 : ]:
        self.covariance    ['infered'] [level] = self.correlation ['infered'] [level] * numpy.sqrt ( self.variance [self.FINE] ['infered'] [level] * self.variance [self.COARSE] ['infered'] [level] )
        self.variance_diff ['infered'] [level] = self.variance [self.FINE] ['infered'] [level] + self.variance [self.COARSE] ['infered'] [level] - 2 * self.covariance ['infered'] [level]
      self.variance_diff ['infered'] [0] = self.variance [self.FINE] ['infered'] [0]

    # report non-available inference modes
    else:

      helpers.error ('Inference mode \'%s\' is not implemented' % self.inference)

    
    # === OPTIMAL control variate COEFFICIENTS
    
    # compute optimal control variate coefficients
    self.coefficients.optimize (self)
    
    # re-evaluate distances between indicators for every two consecute levels of each sample for the specified indices
    distances = self.distances (mcs, indices)
    
    # === MEAN DIFF and VARIANCE DIFF level distance indicators
    # (WITH optimal control variate coefficients computed above)
    
    self.mean_diff_opt     = Indicator ('MEAN     DIFF OPT', self.levels)
    self.variance_diff_opt = Indicator ('VARIANCE DIFF OPT', self.levels)

    # compute optimized level distances (measured values)
    for level in self.levels:
      self.mean_diff_opt     ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.variance_diff_opt ['weights']  [level] = numpy.sqrt ( distances [level] .size )
      self.mean_diff_opt     ['measured'] [level] = numpy.mean ( distances [level] )
      self.variance_diff_opt ['measured'] [level] = numpy.var  ( distances [level], ddof = 1 ) if len (distances [level]) > 1 else float ('nan')
    
    # compute magnitudes of optimized level distances (infered values)
    # remark: infering optimized differences from measured optimized differences could lead to inconsistencies with other infered indicators
    self.mean_diff_opt     ['infered'] [0] = self.coefficients.values [0]      * self.mean     [self.FINE] ['infered'] [0]
    self.variance_diff_opt ['infered'] [0] = self.coefficients.values [0] ** 2 * self.variance [self.FINE] ['infered'] [0]
    for level in self.levels [ 1 : ]:
      self.mean_diff_opt     ['infered'] [level]  = self.coefficients.values [level    ]      * self.mean     [self.FINE]   ['infered'] [level]
      self.mean_diff_opt     ['infered'] [level] -= self.coefficients.values [level - 1]      * self.mean     [self.COARSE] ['infered'] [level]
      self.mean_diff_opt     ['infered'] [level]  = numpy.abs ( self.mean_diff_opt ['infered'] [level] )
      self.variance_diff_opt ['infered'] [level]  = self.coefficients.values [level    ] ** 2 * self.variance [self.FINE]   ['infered'] [level]
      self.variance_diff_opt ['infered'] [level] += self.coefficients.values [level - 1] ** 2 * self.variance [self.COARSE] ['infered'] [level]
      self.variance_diff_opt ['infered'] [level] -= 2 * self.coefficients.values [level] * self.coefficients.values [level - 1] * self.covariance ['infered'] [level]
      self.variance_diff_opt ['infered'] [level]  = numpy.abs ( self.variance_diff_opt ['infered'] [level] )
    
    print 'done.'

  # evaluates indicators for each sample (alternatively, specific indices can also be provided)
  def values (self, mcs, indices=None):

    # container for results
    values = helpers.level_type_list (self.levels)

    # evaluate indicators for all samples on all levels and types
    for level, type in self.levels_types:

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
      if level == 0:
        if indices == None:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * result, None) for result in mcs [ self.pick [level] [self.FINE] ] .results ] )
        else:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * result, None) for sample, result in enumerate (mcs [ self.pick [level] [self.FINE] ] .results) if sample in indices [level] ] )

      # for the remaining levels, evaluate distance indicators between every two consecutive levels
      else:
        zipped = izip (mcs [ self.pick [level] [self.FINE] ] .results, mcs [ self.pick [level] [self.COARSE] ] .results)
        if indices == None:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * fine, self.coefficients.values [level - 1] * coarse) for fine, coarse in zipped ] )
        else:
          distances [level] = numpy.array ( [ self.distance (self.coefficients.values [level] * fine, self.coefficients.values [level - 1] * coarse) for sample, (fine, coarse) in enumerate (zipped) if sample in indices [level] ] )

      # handle unavailable simulations
      if len (distances [level]) == 0:
        distances [level] = numpy.array ( [ float('nan') ] )

    return distances
  
  # least squares inference of indicator level values based on the magnitudes of measured level values
  def infer (self, indicator, degree, log, critical, min = None, max = None):

    # check if inference is not enforced
    if not self.enforce:
      
      # proceed only in case some indicators are not available
      if not numpy.isnan (indicator ['measured'] [indicator.start:]) .any ():
      
        # simply copy all values
        indicator ['infered'] = indicator ['measured'] [:]

        # do not proceed with the inference
        return

    # simply copy all values before 'start'
    indicator ['infered'] [:indicator.start] = indicator ['measured'] [:indicator.start]

    # check if sufficiently many measurements are available for inference
    if numpy.isnan (indicator ['measured'] [indicator.start:]) .all ():
      if critical:
        self.available = 0
      helpers.warning ('Inference of indicator \'%s\' not possible!' % indicator.name)
      return
    
    # if only one measurement is available, assign it to all infered level values
    if  numpy.sum ( ~ numpy.isnan (indicator ['measured'] [indicator.start:]) ) == 1:
      indicator ['infered'] [indicator.start:] = numpy.abs ( indicator ['measured'] [ indicator.start + numpy.where ( ~ numpy.isnan (indicator ['measured'] [indicator.start:]) ) [0] ] )
      return
    
    # if inference is disabled, simply copy the values
    if not self.inference:
      indicator ['infered'] [indicator.start:] = indicator ['measured'] [indicator.start:]
      return

    # use log-coordinates, if specified
    if log:
      data = numpy.log ( numpy.abs (indicator ['measured'] [indicator.start:]) )
    else:
      data = numpy.abs (indicator ['measured'] [indicator.start:])

    # fit a linear polynomial to absolute valus in log-scale using linear least squares, weighted by data undertainties
    #line = numpy.polyfit ( self.levels [indicator.start:], data, degree, w = numpy.sqrt (indicator ['weights'] [indicator.start:]) )
    line = numpy.polyfit ( self.levels [indicator.start:], data, degree )

    # update indicator values to the maximum likelihood estimations
    indicator ['infered'] [indicator.start:] = numpy.polyval (line, self.levels [indicator.start:])

    # transform back to linear coordinates
    if log:
      indicator ['infered'] [indicator.start:] = numpy.exp ( indicator ['infered'] [indicator.start:] )

    # respect envelope specifications
    if min != None:
      indicator ['infered'] [indicator.start:] = numpy.maximum ( min, indicator ['infered'] [indicator.start:] )
    if max != None:
      indicator ['infered'] [indicator.start:] = numpy.minimum ( max, indicator ['infered'] [indicator.start:] )
  
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

    # splitter
    print '  :---------------------' + '-'.join ( [ helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'coefficients' and OCV MLMC vs. PLAIN MLMC speedup from coefficient optimization
    print '  : %-18s:' % 'COEFFICIENT',
    for level in self.levels:
      print helpers.scif (self.coefficients.values [level], table=1),
    print '[OPTIMIZATION: %.2f]' % self.coefficients.optimization,
    print
    
    # report 'mean diff opt'
    self.mean_diff_opt.report ('measured', self.normalization)

    # report 'variance diff opt'
    self.variance_diff_opt.report ('measured', self.normalization ** 2)

    # === report infered values

    if not self.inference:
      return

    print
    print ' :: INFERED INDICATORS: (w.r.t. \'%s\'%s, normalized to %s)' % ( self.inference, ' [enforced]' if self.enforce else '', helpers.scif (self.normalization) )
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

    # splitter
    print '  :---------------------' + '-'.join ( [ helpers.scif (None, table=1, bar=1) for level in self.levels ] )

    # report 'coefficients' and OCV MLMC vs. PLAIN MLMC speedup from coefficient optimization
    print '  : %-18s:' % 'COEFFICIENT',
    for level in self.levels:
      print helpers.scif (self.coefficients.values [level], table=1),
    print '[OPTIMIZATION: %.2f]' % self.coefficients.optimization,
    print

    # report 'mean diff opt'
    self.mean_diff_opt.report ('infered', self.normalization)

    # report 'variance diff opt'
    self.variance_diff_opt.report ('infered', self.normalization ** 2)
  
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
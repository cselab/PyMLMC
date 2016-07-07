
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Errors class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers

import os
import numpy

from coefficients import *

class Errors (object):
  
  def __init__ (self, levels, recycle):
    
    # save configuration
    vars (self) .update ( locals() )

    # additional setup
    self.L           = len(levels) - 1
    self.errors_file = 'errors.dat'
    self.available   = 0
    self.history     = {}

  # compute errors
  def compute (self, indicators, counts):
    
    # set the normalization
    self.normalization = indicators.normalization

    # check if indicators are available
    if indicators.available == 1:
      self.available = 1
    else:
      self.available = 0
      return

    # compute relative sampling errors (if only one sample is loaded, use indicator value)
    # REMARK: this is not accurate since variance_diff are not easy to extrapolate correctly (see a commented alternative [not yet properly tested])
    # TODO: add conditional branch, based on whether the indicators were extrapolated or not
    self.relative_error = numpy.sqrt ( indicators.variance_diff / numpy.maximum ( counts.loaded, numpy.ones (len(self.levels)) ) ) / self.normalization
    '''
    self.relative_error = numpy.zeros ( len (self.levels) )
    self.relative_error [0] = indicators.coefficients.values [0] ** 2 * indicators.variance [0] [0] / max (counts.loaded [0], 1)
    for level in self.levels [ 1 : ]:
      self.relative_error [level]  = indicators.coefficients.values [level] ** 2 * indicators.variance [level] [0]
      self.relative_error [level] += indicators.coefficients.values [level - 1] ** 2 * indicators.variance [level - 1] [0]
      self.relative_error [level] -= 2 * indicators.coefficients.values [level] * indicators.coefficients.values [level - 1] * indicators.covariance [level]
      self.relative_error [level] /= max (counts.loaded [level], 1)
      self.relative_error [level]  = max ( self.relative_error [level], 0 )
    self.relative_error = numpy.sqrt (self.relative_error) / self.normalization
    '''

    # compute the cumulative relative sampling error
    self.total_relative_error = numpy.sqrt ( numpy.sum ( self.relative_error ** 2 ) )
    
    # compute the cumulative sampling error
    self.total_error = self.total_relative_error * self.normalization
  
  # report relative sampling errors
  def report (self):

    if not self.available:
      helpers.warning ('ERRORS not available')
      return

    print
    print ' :: ERRORS: (normalized to %s [~%.1e])' % ( helpers.scif (self.normalization), self.normalization )
    
    print '  :'
    print '  :  LEVEL  :' + ' '.join ( [ '  ' + helpers.intf (level, table=1)       for level in self.levels ] )
    print '  :----------' + '-'.join ( [        helpers.scif (None, table=1, bar=1) for level in self.levels ] )
    print '  :  ERROR  :',
    for level in self.levels:
      print helpers.scif (self.relative_error [level], table=1),
    print

    print '  :'
    print '  : Total sampling error : %s [~%.1e]' % ( helpers.scif (self.total_relative_error), self.total_relative_error )

    if numpy.isnan (self.total_relative_error) or numpy.isinf (self.total_relative_error):
      self.available = 0

  # compute and report speedup (MLMC vs MC and OCV vs PLAIN)
  def speedup (self, indicators, works, counts):

    if not self.available or self.total_error == 0:
      helpers.warning ('Speedup can not be estimated since total sampling error is not available')
      return

    # compute MLMC vs. MC speedup
    FINEST       = numpy.max ( [ level for level in self.levels if counts.loaded [level] > 0 ] )
    work_mlmc    = sum ( [ works [level] * counts.loaded [level] for level in self.levels ] )
    variance_mc  = numpy.max ( [ indicators.variance [level] [0] for level in self.levels [0 : FINEST + 1] ] )
    samples_mc   = numpy.ceil ( variance_mc / (self.total_error ** 2) )
    work_mc      = works [FINEST] * samples_mc
    self.speedup = work_mc / work_mlmc

    # avoid round-off errors for pure MC runs
    if len (self.levels) == 1:
      self.speedup = 1.0
    
    # report
    print
    print ' :: SPEEDUP (MLMC vs. MC): %.2f' % self.speedup + (' [finest level: %d]' % FINEST if FINEST != self.L else '')
    print '  : -> MLMC budget: %s CPU hours' % helpers.intf ( numpy.ceil (work_mlmc) )
    print '  : ->   MC budget: %s CPU hours' % helpers.intf ( numpy.ceil (work_mc) )

    # compute OCV MLMC vs. PLAIN MLMC speedup
    total_error_plain = numpy.sqrt ( numpy.sum ( indicators.variance_diff_plain / numpy.maximum ( counts.loaded, numpy.ones (len(self.levels)) ) ) )
    self.ocv_speedup = (total_error_plain ** 2) / (self.total_error ** 2)

    # report
    print
    print ' :: SPEEDUP (OCV vs. PLAIN): %.2f' % self.ocv_speedup + (' [finest level: %d]' % FINEST if FINEST != self.L else '')
    print '  : ->   OCV MLMC error: %1.2e' % self.total_error / self.normalization
    print '  : -> PLAIN MLMC error: %1.2e' % total_error_plain / self.normalization

  def save (self, iteration):

    # init history
    if len (self.history) == 0:
      self.history ['relative_error']       = {}
      self.history ['total_relative_error'] = {}
      self.history ['total_error']          = {}


    # append history
    self.history ['relative_error']       [iteration] = self.relative_error       if self.available else float ('NaN')
    self.history ['total_relative_error'] [iteration] = self.total_relative_error if self.available else float ('NaN')
    self.history ['total_error']          [iteration] = self.total_error          if self.available else float ('NaN')

    # dump history
    helpers.delete (self.errors_file)
    for variable in self.history:
      for i in range (iteration + 1):
        helpers.dump (self.history [variable] [i], '%f', variable, self.errors_file, i)

  def load (self, config):

    if config.iteration > 0:
      self.history = {}
      execfile ( os.path.join (config.root, self.errors_file), globals(), self.history )

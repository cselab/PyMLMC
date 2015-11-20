
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

class Errors (object):
  
  def __init__ (self, levels):
    
    self.levels      = levels
    self.L           = len(levels) - 1
    self.errors_file = 'errors.dat'
    self.available   = 0
    self.history     = {}

  # compute errors
  def compute (self, indicators, counts):
    
    # save configuration
    self.indicators = indicators
    self.counts     = counts
    
    # extrapolate missing indicators
    if indicators.nans:
      helpers.warning ('Missing indicator values are extrapolated!')
      self.indicators.extrapolate ()
    
    # set the normalization
    self.normalization = self.indicators.normalization

    # check if indicators are available
    if not self.indicators.available:
      self.available = 0
      return
    else:
      self.available = 1
    
    # compute relative sampling errors
    self.relative_error = numpy.sqrt ( self.indicators.variance_diff / self.counts.loaded ) / self.normalization
    
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
    print '  :  LEVEL  :' + ' '.join ( [ '   ' + helpers.intf (level, table=1)       for level in self.levels ] )
    print '  :----------' + '-'.join ( [         helpers.scif (None, table=1, bar=1) for level in self.levels ] )
    print '  :  ERROR  :',
    for level in self.levels:
      print helpers.scif (self.relative_error [level], table=1),
    print

    print '  :'
    print '  : Total sampling error : %s [~%.1e]' % ( helpers.scif (self.total_relative_error), self.total_relative_error )

    if numpy.isnan (self.total_relative_error) or numpy.isinf (self.total_relative_error):
      self.available = 0

  # compute and report speedup (MLMC vs MC)
  def speedup (self, works):

    if not self.available or self.total_error == 0:
      helpers.warning ('Speedup can not be estimated since total sampling error is not available')
      return

    work_mlmc    = sum ( [ works [level] * self.counts.loaded [level] for level in self.levels ] )
    variance_mc  = numpy.max ( [ self.indicators.variance [level] [0] for level in self.levels ] )
    samples_mc   = numpy.ceil ( variance_mc / (self.total_error ** 2) )
    work_mc      = works [self.L] * samples_mc
    self.speedup = work_mc / work_mlmc
    
    print
    print ' :: SPEEDUP (MLMC vs. MC): %.1f' % self.speedup
    print '  : -> MLMC budget: %s CPU hours' % helpers.intf ( numpy.ceil(work_mlmc) )
    print '  : ->   MC budget: %s CPU hours' % helpers.intf ( numpy.ceil(work_mc) )
  
  def save (self, iteration):

    # append history
    self.history ['relative_error']       [iteration] = self.relative_error
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

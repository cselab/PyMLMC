
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Errors class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import helpers
import numpy

class Errors (object):
  
  def __init__ (self, levels):
    
    self.levels      = levels
    self.L           = len(levels) - 1
    self.errors_file = 'errors.dat'
    self.available   = 0
  
  def init (self):
    
    # initialize errors file
    with open ( self.errors_file, 'w') as f:
      f.write ( 'relative_error = []\n' )
      f.write ( 'total_relative_error = []\n' )
      f.write ( 'total_error = []\n' )

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
      print
      print ' :: ERRORS: not available since \'indicators\' are not available'
      return

    print
    print ' :: ERRORS: (normalized to %.1e)' % self.normalization

    print '  :'
    print '  :  LEVEL  :' + ''.join ( ['       %d' % level for level in self.levels ] )
    print '  :----------' + (len (self.levels) * '--------')
    print '  :  ERROR  :',
    for level in self.levels:
      print '%.1e' % self.relative_error [level] if not numpy.isnan (self.relative_error [level]) else '    N/A',
    print

    print '  :'
    print '  : Total sampling error : ' + ('%f [%.1e]' % (self.total_relative_error, self.total_relative_error) if not numpy.isnan (self.total_relative_error) else 'N/A')
    if numpy.isnan (self.total_relative_error):
      self.available = 0
    '''
    if tol:
      print '(= %.1f%% of tol=%.1e)' % ( round ( 1000 * self.total_relative_error / tol ) / 10, tol )
    else:
      print
    '''
  
  # compute and report speedup (MLMC vs MC)
  def speedup (self, works):

    if not self.available or self.total_error == 0:
      helpers.warning ('Speedup can not be estimated since total sampling error is not available')
      return

    work_mlmc    = sum ( [ works [level] * self.counts.computed [level] for level in self.levels ] )
    variance_mc  = numpy.max ( [ self.indicators.variance [level] [0] for level in self.levels ] )
    samples_mc   = numpy.ceil ( variance_mc / (self.total_error ** 2) )
    work_mc      = works [self.L] * samples_mc
    self.speedup = work_mc / work_mlmc
    
    print
    print ' :: SPEEDUP (MLMC vs. MC): %.1f' % self.speedup
    print '  : -> MLMC budget: %s CPU hours' % helpers.intf ( numpy.ceil(work_mlmc) )
    print '  : ->   MC budget: %s CPU hours' % helpers.intf ( numpy.ceil(work_mc) )
  
  def save (self):

    if self.available:
      helpers.dump (self.relative_error, '%f', 'relative_error', self.errors_file)
      with open ( self.errors_file, 'a' ) as f:
        f.write ( 'total_relative_error .append ( %f )\n' % self.total_relative_error )
        f.write ( 'total_error .append ( %f )\n' % self.total_error )
    else:
      with open ( self.errors_file, 'a' ) as f:
        f.write ( 'total_relative_error .append ( %f )\n' % float ('NaN') )

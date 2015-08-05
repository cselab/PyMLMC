
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
      self.indicators.extrapolate ()
      print
      print ' :: WARNING: Missing indicator values are extrapolated!'

    # set the normalization
    self.normalization = self.indicators.normalization
    
    # compute relative sampling errors
    self.relative_error = numpy.sqrt ( self.indicators.variance_diff / self.counts.computed ) / self.normalization
    
    # compute the cumulative relative sampling error
    self.total_relative_error = numpy.sqrt ( numpy.sum ( self.relative_error ** 2 ) )
    
    # compute the cumulative sampling error
    self.total_error = self.total_relative_error * self.normalization
  
  # report relative sampling errors
  def report (self, tol):

    print
    print ' :: ERRORS: (normalized to %.1e)' % self.normalization
    
    print '  : Level sampling errors:',
    #print '    ',
    for level in self.levels:
      print '%.1e' % self.relative_error [level],
    print

    print '  : Total sampling error : %f [%.1e]' % (self.total_relative_error, self.total_relative_error),
    if tol:
      print '(= %.1f%% of tol=%.1e)' % ( round ( 1000 * self.total_relative_error / tol ) / 10, tol )
    else:
      print
  
  # compute and report speedup (MLMC vs MC)
  def speedup (self, works):
    
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
    
    helpers.dump (self.relative_error, '%f', 'relative_error', self.errors_file)
    with open ( self.errors_file, 'a' ) as f:
      f.write ( 'total_relative_error .append ( %f )\n' % self.total_relative_error )
      f.write ( 'total_error .append ( %f )\n' % self.total_error )

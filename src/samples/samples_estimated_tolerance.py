
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (estimated number of samples)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from samples import *
import helpers
import numpy

# surpresses invalid division errors and simply returns 'nan' in such cases
numpy.seterr ( divide='ignore', invalid='ignore' )

# this Samples class updates the required number of samples based on the desired tolerance

class Estimated_Tolerance (Samples):
  
  def __init__ (self, tol=1e-1, warmup=1, warmup_finest_level='last', aggression=0.9, proximity=1.1):
    
    # save configuration
    vars (self) .update ( locals() )
  
  def init (self):
    
    # set range for multiple warmup samples
    if   self.warmup_finest_level == 'last': self.warmup_finest_level = self.L
    elif self.warmup_finest_level == 'half': self.warmup_finest_level = ( self.L + 1 ) / 2

    # set warmup samples
    if hasattr ( self.warmup, '__iter__' ):
      counts = numpy.array ( self.warmup [0 : self.L+1] )
    
    # compute warmup samples based on works ensuring that total work does not exceed 2 * warmup * works [self.L]
    else:
      works = self.works if self.recycle else self.pairworks
      counts = numpy.array ( [ self.warmup * numpy.ceil ( float (works [self.L] / works [level]) / (2 ** (self.L - level)) ) for level in self.levels ], dtype=int )
    
    # adjust warmup samples w.r.t. set range for multiple warmup samples
    counts [0 : self.warmup_finest_level+1] = counts [self.L - self.warmup_finest_level : self.L+1]
    counts [self.warmup_finest_level : ]    = counts [self.L]

    self.counts.additional = counts
  
  def finished (self, errors):

    if not erros.available:
      return 0
    
    if numpy.isnan (errors.total_relative_error):
      return 1
    
    else:
      return errors.total_relative_error <= self.tol

  def update (self, errors, indicators):

    # check if errors or indicators contain NaN's
    if not numpy.isnan (errors)     .any() : return
    if not numpy.isnan (indicators) .any() : return

    # compute the required cumulative sampling error
    self.required_error = self.tol * errors.normalization
    
    # take into account desired aggression
    if self.aggression > 1.0 or errors.total_relative_error / self.tol > self.proximity
      self.required_error *= self.aggression
    
    # compute optimal number of samples
    # assuming that no samples were computed so far
    self.counts.optimal = self.optimal ( numpy.ones(len(self.levels)), self.required_error, indicators )
    
    # compute optimal number of samples
    # assuming that self.counts.available() samples are already available on each level
    updated = self.optimal ( self.counts.available(), self.required_error, indicators)
    
    # compute additional number of samples from updated
    self.counts.additional = numpy.maximum ( 0, updated - self.counts.available() )
    
    # update counts [level] = 1 to counts [level] = 2 first, and only afterwards allow counts [level] > 2
    # this prevents assigning wrong number of samples based on _extrapolated_ indicators
    for level in self.levels:
      if self.counts.available() [level] == 1 and self.counts.additional [level] > 1:
        self.counts.additional [level] = 1
    
    # compute overhead
    self.overhead = numpy.sum ( (self.counts.available() + self.counts.additional) * self.pairworks ) / numpy.sum ( self.counts.optimal * self.works ) - 1.0
    
    # compute optimal control variate coefficients
    # TODO: check this
    if self.optimal:
      indicators.coefficients.optimize (indicators, self.counts.available() + self.counts.additional)
    
    # check if the current coarsest level is optimal
    #self.check_optimal_coarsest_level ()
    
    # check if the current finest level is optimal
    #self.check_optimal_finest_level ()

    # samples are now available
    self.available = 1

  def report (self):
    
    print
    print ' :: SAMPLES: (estimated for the specified tolerance tol=%s)' % helpers.scif (self.tol)
    
    # report computed and additional number of samples
    self.counts.report (self.available)
  
  # query for tolerance
  def query (self):

    message = 'specify the required tolerance'
    hint    = 'press ENTER to leave tol=%.1e' % self.tol
    tol = helpers.query (message, hint=hint, type=float, default=self.tol, format='%.1e', exit=0)
    modified = tol != self.tol
    self.tol = tol
    return modified
  
  # computes the optimal number of samples if some samples are already computed
  def optimal (self, computed, required_error, indicators):
    
    from numpy import sqrt, zeros, ceil
    
    updated = numpy.array ( computed, dtype=int, copy=True )
    
    # compute the work-weighted sum of all variances
    variance_work = sqrt (indicators.variance_diff_opt ['infered'] * self.pairworks)

    # perform iterative optimization until valid number of samples is obtained
    optimize  = 1
    available = numpy.ones ( len (self.levels) )
    while optimize:
      
      # for the next step, by default optimization should not be needed
      optimize = 0
      
      # compute the new required number of samples for all levels
      # taking into account that some samples are already computed (unavailable)
      for level in self.levels:
        
        # continue if this level is not available
        if not available [level]:
          continue
        
        # compute new sample number
        updated [level] = math.ceil ( 1.0 / (required_error ** 2) * sqrt ( indicators.variance_diff_opt ['infered'] [level] / self.pairworks [level] ) * numpy.sum (variance_work * available) )
        
        # if the optimal number of samples is smaller than the already computed number of samples,
        # remove this level from the optimization problem (mark unavailable)
        if updated [level] < computed [level]:
          
          # leave the sample number unchanged
          updated [level] = computed [level]
          
          # declare this level as FIXED (no more optimization for this level)
          available [level] = 0
          
          # the remaining number of samples need to be recomputed
          optimize = 1
          
          # update required sampling error
          required_error = sqrt ( (required_error ** 2) - indicators.variance_diff_opt ['infered'] [level] / computed [level] )

          # restart the optimization for all levels
          break
    
    return updated
 

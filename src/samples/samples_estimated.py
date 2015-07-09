
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

class Estimated (Samples):
  
  def __init__ (self, tol=1e-1, warmup=1, aggressive=0, warmup_finest_level='last', evaluation_fraction=0.9, min_evaluation_fraction=0.1, aggression=0.1):
    
    # save configuration
    vars (self) .update ( locals() )
  
  def init (self):
    
    print
    print ' :: SAMPLES: estimated'
    
    # default warmup samples
    if   self.warmup_finest_level == 'last': self.warmup_finest_level = self.L
    elif self.warmup_finest_level == 'half': self.warmup_finest_level = ( self.L + 1 ) / 2
    counts = numpy.array ( [ self.warmup * ( 4 ** max ( 0, self.warmup_finest_level - level) ) for level in self.levels ] )

    self.counts.computed   = numpy.zeros ( len(self.levels), dtype=int )
    self.counts.additional = numpy.array ( counts, copy=True )
    
    # set simulation type (deterministic or stochastic)
    self.deterministic = ( self.warmup == 1 and self.L == 0 )
  
  def finished (self, errors):
    
    return errors.total_relative_error <= self.tol
  
  def update (self, errors, indicators):
    
    # compute the required cumulative sampling error
    if self.aggressive:
      self.required_error = self.tol * errors.normalization * max (0.5, 1.0 - self.aggression)
    else:
      self.required_error = self.tol * errors.normalization
    
    # compute optimal number of samples
    # assuming that no samples were computed so far
    self.counts_optimal = self.optimal ( numpy.ones(len(self.levels)), self.required_error, indicators )
    
    # compute optimal number of samples
    # assuming that self.counts.computed samples are already computed on each level
    self.counts_updated = self.optimal ( self.counts.computed, self.required_error, indicators)
    
    # compute additional number of samples from counts_updated
    self.counts.additional = numpy.zeros ( len(self.levels), dtype=int )
    for level in self.levels:
     if self.counts_updated [level] > self.counts.computed [level]:
       
       # assign all required additional number of samples
       if self.aggressive:
         self.counts.additional [level] = self.counts_updated [level] - self.counts.computed [level]
       
       # compute required additional number of samples according to (min_)evaluation_fraction
       else:
         self.counts.additional [level] = numpy.round ( self.evaluation_fraction * (self.counts_updated [level] - self.counts.computed [level] ) )
         if self.counts.additional [level] < self.min_evaluation_fraction * self.counts_updated [level]:
           self.counts.additional [level] = self.counts_updated [level] - self.counts.computed [level]
    
    # update counts [level] = 1 to counts [level] = 2 first, and only afterwards allow counts [level] > 2
    # this prevents assigning wrong number of samples based on _extrapolated_ indicators
    for level in self.levels:
      if self.counts.computed [level] == 1 and self.counts.additional [level] > 1:
        self.counts.additional [level] = 1;
    
    # compute optimal_work_fraction
    self.optimal_work_fraction = numpy.sum ( (self.counts.computed + self.counts.additional) * self.works ) / numpy.sum ( self.counts_optimal * self.works )
    
    # check if the current coarsest level is optimal
    #self.check_optimal_coarsest_level ()
    
    # check if the current finest level is optimal
    #self.check_optimal_finest_level ()
  
  def report (self):
    
    print
    print ' :: SAMPLES:'
    
    print '    -> Updated number of samples for each level:'
    print '      ',
    for level in self.levels:
      print '%d' % self.counts_updated [level],
    print
    
    fractions = ( numpy.round(100 * self.evaluation_fraction), numpy.round(100 * self.min_evaluation_fraction) )
    '''
    print '    -> Updated number of samples for each level (%d%% of required, at least %d%% of all)' % fractions
    print '      ',
    for level in self.levels:
      print '%d' % ( self.counts.computed [level] + self.counts.additional [level] ),
    print
    '''
    print '    -> Additional number of samples for each level (%d%% of required, at least %d%% of all)' % fractions
    print '      ',
    for level in self.levels:
      print '%d' % self.counts.additional [level],
    print
  
  # query for tolerance
  def query (self):
    
    print
    print ' :: QUERY: specify the required tolerance [press ENTER to leave tol=%.1e]: ' % self.tol
    tol = float ( raw_input ( '  : ' ) or str(self.tol) )
    modified = tol != self.tol
    self.tol = tol
    return modified
  
  # computes the optimal number of samples if some samples are already computed
  def optimal (self, computed, required_error, indicators):
    
    from numpy import sqrt, zeros, ceil
    
    updated = numpy.array ( computed, dtype=int, copy=True )
    
    # compute the work-weighted sum of all variances
    variance_work_sum = sum ( sqrt ( [ indicators.variance_diff [level] * self.works [level] for level in self.levels ] ) )
    
    # perform iterative optimization until valid number of samples is obtained
    optimize = 1
    fixed = zeros (len(self.levels))
    while optimize:
      
      # for the next step, by default optimization should not be needed
      optimize = 0
      
      # compute the new required number of samples for all levels
      # taking into account that some samples are already computed
      for level in self.levels:
        
        # continue if this level is already fixed
        if fixed [level]:
          continue
        
        # compute new sample number
        updated [level] = ceil ( 1.0 / (required_error ** 2) * sqrt ( indicators.variance_diff [level] / self.works [level] ) * variance_work_sum )
        
        # if the new sample number is smaller than the already computed sample number,
        # then remove this level from the optimization problem
        # remark: comparison must include '=' since the upper bound for optimal number of samples is used
        if updated [level] <= computed [level]:
          
          # leave the sample number unchanged
          updated [level] = computed [level]
          
          # declare this level as FIXED (no more optimization for this level)
          fixed [level] = 1
          
          # the remaining number of samples need to be recomputed
          optimize = 1
          
          # update variance_work_sum
          variance_work_sum -= sqrt ( indicators.variance_diff [level] * self.works [level] )
          
          # update required sampling error
          required_error = sqrt ( (required_error ** 2) - indicators.variance_diff [level] / computed [level] )
    
    return updated
 

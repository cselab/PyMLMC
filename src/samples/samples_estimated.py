
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (estimated number of samples)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from samples import Samples
import numpy

class Estimated (Samples):

  def __init__ (self, warmup=None, warmup_factor=1, tol=1e-3, evaluation_fraction=0.9, min_evaluation_fraction=0.1):
    
    # save configuration
    vars (self) .update ( locals() )
  
  def init (self, levels, works):
    
    # save configuration
    self.levels = levels
    self.works  = works
    
    print ' :: SAMPLES: estimated'
    
    # default warmup samples
    if not self.warmup:
      self.warmup = numpy.array ( [ self.warmup_factor * ( 2 ** (len(levels) - 1 - level) ) for level in levels ] )
    
    self.counts  = self.warmup [:]
    self.indices = [ range ( self.warmup [level] ) for level in self.levels ]
  
  def compute_errors (self, indicators):
    
    # save configuration
    self.indicators = indicators
    
    # extrapolate missing indicators
    self.indicators.extrapolate ()
    
    # set the normalization
    self.normalization = self.indicators.mean[0][0]
    
    # compute the required cumulative sampling error
    self.required_error = self.tol * self.normalization
    
    # compute relative sampling errors
    self.relative_error = numpy.sqrt ( self.indicators.variance_diff / self.counts ) / self.normalization
    
    # compute the cumulative relative sampling error
    self.total_relative_error = numpy.sqrt ( numpy.sum ( self.relative_error ** 2 ) )
    
    # compute the cumulative sampling error
    self.total_error = self.total_relative_error * self.normalization
  
  def report_errors (self):
    
    # report relative sampling errors
    print '    -> Relative total sampling error is %.1e' % self.total_relative_error,
    print '(= %.1f%% of rel_tol=%.1e)' % ( round ( 1000 * (self.total_relative_error ** 2) / (self.tol ** 2) ) / 10, self.tol )
    print '       Relative level sampling errors:'
    print '      ',
    for level in self.levels:
      print '%.1e' % self.relative_error [level],
    print
  
  def finished (self):
    
    return self.total_relative_error <= self.tol
  
  def update (self):
    
    # compute optimal number of samples
    # assuming that no samples were computed so far
    self.counts_optimal = self.compute_optimal ( numpy.ones(len(self.levels)), self.required_error )
    
    # compute optimal number of samples
    # assuming that self.counts samples are already computed on each level
    self.counts_updated = self.compute_optimal ( self.counts, self.required_error)
    
    # compute counts_additional from counts_updated, according to (min_)evaluation_fraction
    self.counts_additional = self.counts_updated [:]
    for level in self.levels:
     if self.counts_updated [level] > self.counts [level]:
       self.counts_additional [level] = numpy.max ( 1, numpy.round ( self.evaluation_fraction * (self.counts_updated [level] - self.counts [level] ) ) )
       if self.counts_additional [level] < self.min_evaluation_fraction * self.counts_updated [level]:
         self.counts_additional [level] = self.counts_updated [level] - self.counts [level]
    
    # update counts [-1] = 1 to counts [-1] = 2 first, and only afterwards allow counts [-1] > 2
    if self.counts [-1] == 1 and self.counts_updated [-1] > 1:
      self.counts_additional [-1] = 1;
    
    # update counts using counts_additional
    self.counts += self.counts_additional
    
    # compute optimal_work_fraction
    self.optimal_work_fraction = numpy.sum ( self.counts * self.works ) / numpy.sum ( self.counts_optimal * self.works )
    
    # check if the current coarsest level is optimal
    #self.check_optimal_coarsest_level ()
    
    # check if the current finest level is optimal
    #self.check_optimal_finest_level ()
  
  def report (self):
    
    print '    -> Updated number of samples for each level:'
    print '      ',
    for level in self.levels:
      print '%d' % self.counts_updated [level],
    print
    
    fractions = ( numpy.round(100 * self.evaluation_fraction), numpy.round(100 * self.min_evaluation_fraction) )

    print '       Updated number of samples for each level (%d%% of additional, at least %d%% of all)' % fractions
    print '      ',
    for level in self.levels:
      print '%d' % self.counts [level],
    print
    
    print '       Additional number of samples for each level (%d%% of additional, at least %d%% of all)' % fractions
    print '      ',
    for level in self.levels:
      print '%d' % self.counts_additional [level],
    print
  
  def mask (self, level):
    if level == 0:
      return 0
    elif self.indices [level] > 1:
      return level
    else:
      return mask [level-1]
  
  # computes the optimal number of samples if some samples are already computed
  def compute_optimal (self, computed, required_error):
    
    from numpy import sqrt, zeros, ceil
    
    updated = computed

    # compute the work-weighted sum of all variances
    variance_work_sum = sum ( sqrt ( [ self.indicators.variance_diff [level] * self.works [level] for level in self.levels ] ) )
    
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
        updated [level] = ceil ( 1.0 / (required_error ** 2) * sqrt ( self.indicators.variance_diff [level] / self.works [level] ) * variance_work_sum )
        
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
          variance_work_sum -= sqrt ( self.indicators.variance_diff [level] * self.works [level] )
          
          # update required sampling error
          required_error = sqrt ( (required_error ** 2) - self.indicators.variance_diff [level] / computed [level] )
    
    return updated
 

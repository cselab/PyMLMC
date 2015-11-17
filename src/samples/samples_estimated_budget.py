
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (estimated number of samples for computational budget)
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

class Estimated_Budget (Samples):
  
  def __init__ (self, budget=8, warmup=1, warmup_finest_level='last'):
    
    # save configuration
    vars (self) .update ( locals() )
    self.counts_updated = None
  
  def init (self):

    # set range for multiple warmup samples
    if   self.warmup_finest_level == 'last': self.warmup_finest_level = self.L
    elif self.warmup_finest_level == 'half': self.warmup_finest_level = ( self.L + 1 ) / 2

    # compute warmup samples based on works
    counts = numpy.array ( [ self.warmup * numpy.ceil ( float (self.works [self.L] / self.works [level]) / (2 ** (self.L - level)) ) for level in self.levels ], dtype=int )

    # adjust warmup samples w.r.t. set range for multiple warmup samples
    counts [0 : self.warmup_finest_level+1] = counts [self.L - self.warmup_finest_level : self.L+1]
    counts [self.warmup_finest_level : ]    = counts [self.L]

    self.counts.additional = numpy.array ( counts, copy=True )

  def finished (self, errors):

    work = numpy.sum ( numpy.array(self.works) * numpy.array(self.counts.computed) )
    return work >= 0.9 * self.budget

  def update (self, errors, indicators):

    # compute optimal number of samples
    # assuming that no samples were computed so far
    self.counts_optimal = self.optimal ( numpy.ones(len(self.levels)), self.budget, indicators )
    
    # compute optimal number of samples
    # assuming that self.counts.computed samples are already computed on each level
    self.counts_updated = self.optimal ( self.counts.computed, self.budget, indicators)
    
    # compute additional number of samples from counts_updated
    self.counts.additional = numpy.zeros ( len(self.levels), dtype=int )
    for level in self.levels:
     if self.counts_updated [level] > self.counts.loaded [level]:
        self.counts.additional [level] = self.counts_updated [level] - self.counts.loaded [level]
    
    # compute optimal_work_fraction
    self.optimal_work_fraction = numpy.sum ( (self.counts.loaded + self.counts.additional) * self.works ) / numpy.sum ( self.counts_optimal * self.works )
    
    # check if the current coarsest level is optimal
    #self.check_optimal_coarsest_level ()
    
    # check if the current finest level is optimal
    #self.check_optimal_finest_level ()

    # samples are now available
    self.available = 1

  def report_budget (self):

    print
    print ' :: BUDGET:'

    budget_used = sum ( [ self.works [level] * self.counts.computed [level] for level in self.levels ] )
    budget_left = self.budget - budget_used
    if self.counts.additional != []:
      budget_reqd = sum ( [ self.works [level] * self.counts.additional [level] for level in self.levels ] )

    print '  : -> Specified budget: %s CPU hours' % helpers.intf (numpy.ceil(self.budget), table=1)
    print '  : -> Consumed  budget: %s CPU hours' % helpers.intf (numpy.ceil(budget_used), table=1)
    print '  : -> Remaining budget: %s CPU hours' % helpers.intf (numpy.ceil(budget_left), table=1)
    if self.counts.additional != []:
      print '  : -> Requested budget: %s CPU hours' % helpers.intf (numpy.ceil(budget_reqd), table=1)

  def report (self):

    print
    print ' :: SAMPLES: (estimated for the specified budget)'

    print '    -> Computed number of samples for each level:'
    print '      ',
    for level in self.levels:
      print '%d' % self.counts.computed [level],
    print

    if self.counts_updated != None:
      print '    -> Updated number of samples for each level:'
      print '      ',
      for level in self.levels:
        print '%d' % self.counts_updated [level],
      print

    if self.counts.additional != []:
      print '    -> Pending number of samples for each level'
      print '      ',
      for level in self.levels:
        print '%d' % self.counts.additional [level],
      print

    # report budget status
    self.report_budget()

  # query for budget
  def query (self):

    message = 'specify the required computational budget'
    hint    = 'press ENTER to leave %s CPU hours' % helpers.intf (self.budget)
    default = self.budget
    budget = helpers.query (message, hint=hint, type=float, default=default, format='intf', exit=0)
    modified = budget != self.budget
    self.budget = budget
    return modified
  
  # computes the optimal number of samples if some samples are already computed
  def optimal (self, computed, budget, indicators):
    
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
        updated [level] = ceil ( sqrt ( indicators.variance_diff [level] / self.works [level] ) * budget / variance_work_sum )

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

          # update budget
          budget -= self.works [level] * updated [level]
    
    return updated

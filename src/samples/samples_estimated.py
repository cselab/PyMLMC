
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (estimated number of samples)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Estimated (object):

  def __init__ (self, levels, work, tol=1e-3, warmup=None, indicators):
    
    # save configuration
    self.levels = levels
    self.work = work
    self.tol = tol
    self.warmup = warmup
    self.indicators = indicators
    
    # default warmup samples
    if self.warmup == None:
      self.warmup = [ 2 ** (len(levels) - level) for level in levels ]
  
  def init (self):
    print ' :: SAMPLES: estimated'
    self.indices = [ range ( self.warmup [level] ) for level in self.levels ]
  
  def update (self):
   
   
  def mask (self, level):
    if level == 0:
      return 0
    elif self.indices [level] > 1:
      return level
    else:
      return mask [level-1]

  # computes the optimal number of samples if some samples are already computed
  def optimal (self, computed, error_required):
    
    from numpy import sqrt, zeros, ceil
    
    updated = computed

    # compute the work-weighted sum of all variances
    variance_work_sum = sum ( sqrt ( [ indicators.variance_diff [level] * work [level] for level in self.levels ] ) )
    
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
        updated [level] = ceil ( 1.0 / (error_required ** 2) * sqrt ( self.variance_diff [ mask(level) ] / work [level] ) * variance_work_sum )
        
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
          variance_work_sum -= sqrt ( self.variance_diff [ mask(level) ] * work [level] )
          
          # update required sampling error
          error_required = sqrt ( (error_required ** 2) - self.variance_diff [ mask(level) ] / computed [level] )
 

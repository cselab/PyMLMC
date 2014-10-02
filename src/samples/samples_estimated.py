
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Samples class (estimated number of samples)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Estimated (object):

  def __init__ (self, warmup=None, warmup_factor=1, tol=1e-3):
    
    # save configuration
    self.tol = tol
    self.warmup = warmup
    self.warmup_factor = warmup_factor
  
  def init (self, levels):
    
    self.levels = levels
    print ' :: SAMPLES: estimated'
    
    # default warmup samples
    if not self.warmup:
      self.warmup = [ self.warmup_factor * ( 2 ** (len(levels) - 1 - level) ) for level in levels ]
    
    self.counts  = self.warmup [:]
    self.indices = [ range ( self.warmup [level] ) for level in self.levels ]
  
  def update (self, levels, works, indicators):
    
    # save configuration
    self.levels     = levels
    self.works      = works
    self.indicators = indicators
    
    print ' :: Updating number of samples:'
    self.compute ()
    
    # check if the current coarsest level is optimal
    #self.check_optimal_coarsest_level ()
    
    # check if the current finest level is optimal
    #self.check_optimal_finest_level ()
  
  def report (self):
    
    print ' :: WARNING: samples report not yet implemented.'
    '''
    std::cout << "    -> Updated number of samples for each level:" << std::endl;
    std::cout << "      ";
    for (int samples_level=L; samples_level>=0; samples_level--)
      std::cout << " " << NM_UPDATED [samples_level];
    std::cout << std::endl;
    
    std::cout << "       Updated number of samples for each level (" << round(100 * EVALUATION_FRACTION) << "\% of additional, at least " << round(100 * MIN_EVALUATION_FRACTION) << "\% of all)" << std::endl;
    std::cout << "      ";
    for (int samples_level=L; samples_level>=0; samples_level--)
      std::cout << " " << NM [samples_level];
    std::cout << std::endl;
    
    std::cout << "       Additional number of samples for each level (" << round(100 * EVALUATION_FRACTION) << "\% of additional, at least " << round(100 * MIN_EVALUATION_FRACTION) << "\% of all)" << std::endl;
    std::cout << "      ";
    for (int samples_level=L; samples_level>=0; samples_level--)
      std::cout << " " << NM_ADDITIONAL [samples_level];
    std::cout << std::endl;
    '''
  
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
        updated [level] = ceil ( 1.0 / (error_required ** 2) * sqrt ( self.indicators.variance_diff [ mask(level) ] / self.works [level] ) * variance_work_sum )
        
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
          variance_work_sum -= sqrt ( self.indicators.variance_diff [ mask(level) ] * self.works [level] )
          
          # update required sampling error
          error_required = sqrt ( (error_required ** 2) - self.indicators.variance_diff [ mask(level) ] / computed [level] )
 


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
  
  def compute (self):
    
    # set the normalization
    self.normalization = self.indicators.mean[0][0]
    
    # compute the required cumulative sampling error
    required_error = self.tol * self.normalization
    
    # compute relative sampling errors
    relative_error = numpy.sqrt ( self.indicators.variance_diff / self.counts ) / self.normalization
    
    # compute the cumulative relative sampling error
    total_relative_error = 0;
    for (int samples_level=L; samples_level>=0; samples_level--)
      total_relative_error_s += sqr ( relative_error_s [samples_level] );
    total_relative_error_s = sqrt (total_relative_error_s);
  
  // compute the cumulative sampling error
  total_error_s = total_relative_error_s * NORMALIZATION;
  
  // report relative sampling errors
  std::ostringstream sampling_error;
  sampling_error << std::setprecision(1) << std::scientific;
  sampling_error << "    -> Relative total sampling error is " << total_relative_error_s << " ( = ";
  sampling_error << std::fixed;
  sampling_error << round ( 1000 * sqr(total_relative_error_s) / sqr(TOL) ) / 10;
  sampling_error << std::scientific;
  sampling_error << "% of REL_TOL=" << TOL << ")" << std::endl;
  sampling_error << "       Relative level sampling errors:" << std::endl;
  sampling_error << "      ";
  for (int samples_level=L; samples_level>=0; samples_level--)
    sampling_error << " " << relative_error_s [samples_level];
  sampling_error << std::endl;
  std::cout << sampling_error.str().c_str();
  
  #if ITERATIVE_OCV
  
  // report relative sampling error if optimal control variates ARE NOT used
  std::ostringstream output_error_ocv;
  output_error_ocv << std::setprecision(1) << std::scientific;
  output_error_ocv << "    -> Relative total sampling error (no OCV) is ";
  real error = 0;
  for (int samples_level=0; samples_level<=L; samples_level++)
    error += get_variance (samples_level) / NM [samples_level];
  output_error_ocv << sqrt(error) / NORMALIZATION;
  output_error_ocv << " ( = " << std::fixed;
  output_error_ocv << round ( 1000 * error / sqr(NORMALIZATION) / sqr(TOL) ) / 10 << "% of REL_TOL=" << std::scientific << TOL << ")"  << std::endl;
  output_error_ocv << "       Relative level sampling errors (no OCV):" << std::endl;
  output_error_ocv << "      ";
  for (int samples_level=L; samples_level>=0; samples_level--)
    output_error_ocv << " " << sqrt ( get_variance (samples_level) / NM [samples_level] ) / NORMALIZATION;
  output_error_ocv << std::endl;
  std::cout << output_error_ocv.str().c_str();
  
  #else
  
  // report relative sampling error if optimal control variates ARE used
  std::ostringstream output_error_ocv;
  output_error_ocv << std::setprecision(1) << std::scientific;
  output_error_ocv << "    -> Relative total sampling error (with OCV) is ";
  real error = 0;
  for (int samples_level=0; samples_level<=L; samples_level++)
    error += get_variance_ocv (samples_level) / NM [samples_level];
  output_error_ocv << sqrt(error) / NORMALIZATION;
  output_error_ocv << " ( = " << std::fixed;
  output_error_ocv << round ( 1000 * error / sqr(NORMALIZATION) / sqr(TOL) ) / 10 << "% of REL_TOL=" << std::scientific << TOL << ")"  << std::endl;
  output_error_ocv << "       Relative level sampling errors (with OCV):" << std::endl;
  output_error_ocv << "      ";
  for (int samples_level=L; samples_level>=0; samples_level--)
    output_error_ocv << " " << sqrt ( get_variance_ocv (samples_level) / NM [samples_level] ) / NORMALIZATION;
  output_error_ocv << std::endl;
  std::cout << output_error_ocv.str().c_str();
  
  #endif

  // return if the required sampling error is reached
  if ( total_relative_error_s * NORMALIZATION <= required_error_s ) {
    
    // report tolerance status
    std::ostringstream tot_error;
    tot_error << std::setprecision(1) << std::scientific;
    #if ESTIMATE_DETERMINISTIC_ERROR
    real total_error = sqrt( sqr(total_relative_error_s) + sqr(relative_error_d) );
    #else
    real total_error = total_relative_error_s;
    #endif
    tot_error << "    -> Required relative tolerance is reached:" << std::endl;
    tot_error << "       total relative error is " << total_error;
    tot_error << std::fixed;
    tot_error << " ( = ";
    tot_error << round ( 1000 * sqr(total_error) / sqr(TOL) ) / 10;
    tot_error << std::scientific;
    tot_error << "% of REL_TOL=" << TOL << ")" << std::endl;
    std::cout << tot_error.str().c_str();
    
    // no additional samples need to be computed
    ADDITIONAL_SAMPLES_NEEDED = 0;
  }
  
  // otherwise, additional samples are needed
  else
    ADDITIONAL_SAMPLES_NEEDED = 1;
  
  // compute optimal number of samples
  // assuming that no samples were computed so far
  long_int NM_MIN1 [L+1];
  for (int samples_level=L; samples_level>=0; samples_level--)
    NM_MIN1 [samples_level] = 1;
  mlmc_samples_get_optimal (& NM_MIN1 [0], & NM_OPTIMAL [0], required_error_s);
  
  // compute optimal number of samples
  // assuming that NM [*] samples are already computed on each level
  mlmc_samples_get_optimal (& NM [0], & NM_UPDATED [0], required_error_s);
  
  // update NM [*] from NM_UPDATED [*], according to EVALUATION_FRACTION and MIN_EVALUATION_FRACTION
  if ( ADDITIONAL_SAMPLES_NEEDED ) {
    
    // update NM [L] = 1 to NM [L] = 2 first, and only afterwards allow NM [L] > 2
    if (NM [L] == 1 && NM_UPDATED [L] > 1)
      NM [L] = 2;
    else if ( NM_UPDATED [L] > NM [L] ) {
      NM_ADDITIONAL [L] = max (1, round ( EVALUATION_FRACTION * (NM_UPDATED [L] - NM [L]) ) );
      NM [L] += NM_ADDITIONAL [L];
    }
    
    // update the remaining NM [*] as usual
    for (int samples_level=L-1; samples_level>=0; samples_level--)
      if ( NM_UPDATED [samples_level] > NM [samples_level] ) {
        NM_ADDITIONAL [samples_level] = max (1, round ( EVALUATION_FRACTION * (NM_UPDATED [samples_level] - NM [samples_level]) ) );
        if (NM_ADDITIONAL [samples_level] < MIN_EVALUATION_FRACTION * NM_UPDATED [samples_level])
          NM_ADDITIONAL [samples_level] = NM_UPDATED [samples_level] - NM [samples_level];
        NM [samples_level] += NM_ADDITIONAL [samples_level];
      }
  }
  
  // compute optimal_work_fraction
  real total_work = 0;
  for (int samples_level = 0; samples_level <= L; samples_level++)
    total_work += NM [samples_level] * work [samples_level];
  real optimal_work = 0;
  for (int samples_level = 0; samples_level <= L; samples_level++)
    optimal_work += NM_OPTIMAL [samples_level] * work [samples_level];
  optimal_work_fraction = total_work / optimal_work;


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
 


# # # # # # # # # # # # # # # # # # # # # # # # # #
# General statistics classes                      #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import copy
import numpy
import helpers

class Stat (object):
  
  # containers for results
  estimate = None

  # whether statistic is available
  available = 0
  
  # special clipping
  clip = None

  # alpha by default is disabled
  alpha = 0

  # evalaute statistics for all qois
  def evaluate (self, samples, indices=None, qois=None):

    # statistic is initially not available
    self.available = 0
    
    # compute indices, if not explicitely specified
    if indices == None:
      indices = [ index for index, sample in enumerate (samples) if sample != None ]

    # check if at least one sample is available
    if len (indices) == 0:
      print '       %-30s[%s]' % (self.name, 'unavailable')
      return
    
    # check if sufficiently many samples are available
    if len (indices) < self.limit:
      print '       %-30s[%s]' % (self.name, 'insufficient')
      return
    
    # statistic will be available
    self.available = 1

    # copy data class from the first valid sample
    self.estimate = copy.deepcopy ( samples [ indices [0] ] )

    # resize estimate according to statistics size
    if not self.online:
      self.estimate.resize (self.size)
    
    # quantities of interest to be assembled
    if qois == None:
      names   = self.estimate.qois
      extents = [ None for name in names ]
    else:
      names   = qois.keys()
      extents = qois.values()

    # use progress indicator, report current statistic each time
    prefix = '       %-30s' % self.name
    steps = len (names) * len (indices)
    progress = helpers.Progress (prefix=prefix, steps=steps, length=20)
    progress.init ()
    failed = []
    
    # compute sample statistics for each qoi
    for i, (qoi, extent) in enumerate (zip (names, extents)):

      # check if qoi is available
      if qoi not in self.estimate.data:
        failed.append (qoi)
        progress.update ( (i + 1) * len (indices) )
        continue
      
      # templated online estimation is supported by statistic
      if self.online:

        # initialize statistics
        self.init ()

        # process all samples
        for index in indices:

          # update estimate with a sample
          self.update (samples [index] [qoi], extent)

          # update progress
          progress.update (i * len (indices) + index + 1)
        
        # store estimated statistic
        self.estimate [qoi] = self.result ()

      # templated online estimation is NOT supported by statistic
      else:

        # compute sample statistics for each element in a flattened array
        for element in xrange ( len ( self.estimate.serialize (qoi) ) ):

          # create an ensemble of sample values
          ensemble = [ sample.serialize (qoi) [element] for index, sample in enumerate (samples) if index in indices ]
          
          # compute statistic
          self.estimate.serialize (qoi) [element] = self.compute (ensemble, extent)
          
        # update progress
        progress.update ( (i + 1) * len (indices) )
      
    # finalize progress indicator
    progress.finalize()

    # report missing qois
    if failed != []:
      helpers.warning ('Missing QoIs: %s' % ' '.join (failed) )

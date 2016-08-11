
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

  # special clipping
  clip = 1

  # return empty result in case no samples are available
  def empty (self):

    return numpy.full ( self.size, float ('nan') )

  # TODO: implement serialize() method for DataClass and generalize this
  def steps (self, samples, indices=None, qois=None):

    # check if sufficiently many samples are provided
    if len (samples) == 0 or (indices and len (indices) == 0):
      return None

    # copy data class from the first valid sample
    for sample in samples:
      if sample != None:
        self.estimate = copy.deepcopy (sample)
        self.estimate.resize (self.size)
        break
    
    # check if at least one sample is available
    if self.estimate == None:
      print '       %-30s[%s]' % (self.name, 'unavailable')
      return None

    # quantities of interest to be assembled
    if qois == None:
      names   = stats.data.keys()
      extents = [ None for name in names ]
    else:
      names   = qois.keys()
      extents = qois.values()

    # use progress indicator, report current statistic each time
    prefix = '       %-30s' % self.name
    progress = helpers.Progress (prefix=prefix, steps=len(names), length=20)
    
    # compute sample statistics for each qoi
    for i, (name, extent) in enumerate (zip (names, extents)):

      # check if qoi is available
      if name not in sample.data:
        #helpers.warning ('QoI \'%s\' not found in loaded data.' % name)
        progress.update (i + 1)
        continue
      
      # compute sample statistics for each step
      for step in xrange ( len ( self.estimate.data [name] ) ):

        # if spedific indices are required, take this into account
        if indices != None:
          ensemble = [ sample.data [name] [step] for index, sample in enumerate (samples) if index in indices and not numpy.isnan (sample.data [name] [step]) ]
        else:
          ensemble = [ sample.data [name] [step] for sample in samples if not numpy.isnan (sample.data [name] [step]) ]
        
        # compute statistic
        if len (ensemble) > 0:
          self.estimate.data [name] [step] = self.compute (ensemble, extent)
        else:
          self.estimate.data [name] [step] = self.empty ()
      
      # update progress
      progress.update (i + 1)
      
    # finalize progress indicator
    progress.finalize()

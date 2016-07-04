
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
from helpers import Progress

class Stat (object):
  
  # return empty result in case no samples are available
  def empty (self):

    return numpy.full ( self.size, float ('nan') )

  # TODO: implement serialize() method for DataClass and generalize this
  def steps (self, samples, indices=None, check=0, qois=None):

    # check if sufficiently many samples are provided
    if len (samples) == 0 or (indices and len (indices) == 0):
      return None

    # copy data class from the first valid sample
    stats = None
    for sample in samples:
      if sample != None:
        stats = copy.deepcopy (sample)
        stats.resize (self.size)
        break
    
    # check if at least one sample is available
    if stats == None:
      print '       %-30s[%s]' % (self.name, 'unavailable')
      return None

    # quantities of interest to be assembled
    if qois == None:
      names   = stats.data.keys()
      extents = [ None for name in names ]
    else:
      names, extents = qois.iteritems()

    # use progress indicator, report current statistic each time
    prefix = '       %-30s' % self.name
    progress = Progress (prefix=prefix, steps=len(keys), length=20)

    # compute sample statistics
    for i, (name, extent) in enumerate (zip (names, extents)):
      for step in xrange ( len ( stats.data [name] ) ):

        # check for unavailable samples
        if check:

          # if spedific indices are required, take this into account
          if indices != None:
            ensemble = [ sample.data [name] [step] for index, sample in enumerate (samples) if sample != None and index in indices and not numpy.isnan (sample.data [name] [step]) ]
          else:
            ensemble = [ sample.data [name] [step] for sample in samples if sample != None and not numpy.isnan (sample.data [name] [step]) ]

        # assume all samples are available
        else:

          # if spedific indices are required, take this into account
          if indices != None:
            ensemble = [ sample.data [name] [step] for index, sample in enumerate (samples) if index in indices and not numpy.isnan (sample.data [name] [step]) ]
          else:
            ensemble = [ sample.data [name] [step] for sample in samples if not numpy.isnan (sample.data [name] [step]) ]
        
        # compute statistic
        if len (ensemble) > 0:
          stats.data [name] [step] = self.compute (ensemble, extent)
        else:
          stats.data [name] [step] = self.empty ()
      
      # update progress
      progress.update (i + 1)
      
    # finalize progress indicator
    progress.finalize()

    return stats

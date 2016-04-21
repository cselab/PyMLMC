
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
  
  # TODO: implement serialize() method for DataClass and generalize this
  def compute_all (self, samples, indices=None, check=0, qois='all'):

    # check if sufficiently many samples are provided
    if len (samples) == 0 or (indices and len (indices) == 0):
      return None

    # copy data class from the first valid sample
    stats = None
    for sample in samples:
      if sample != None:
        stats = copy.deepcopy (sample)
        break

    # check if at least one sample is available
    if stats == None:
      print '       %-30s[%s]' % (self.name, 'unavailable')
      return None

    # quantities of interest to be assembled
    if qois == 'all':
      keys = stats.data.keys()
    else:
      keys = qois

    # use progress indicator, report current statistic each time
    prefix = '       %-30s' % self.name
    progress = Progress (prefix=prefix, steps=len(keys), length=20)

    # compute sample statistics
    for i, key in enumerate (keys):
      for step in xrange ( len ( stats.data [key] ) ):

        # check for unavailable samples
        if check:

          # if spedific indices are required, take this into account
          if indices != None:
            ensemble = [ sample.data [key] [step] for index, sample in enumerate (samples) if sample != None and index in indices and not numpy.isnan (sample.data [key] [step]) ]
          else:
            ensemble = [ sample.data [key] [step] for sample in samples if sample != None and not numpy.isnan (sample.data [key] [step]) ]

        # assume all samples are available
        else:

          # if spedific indices are required, take this into account
          if indices != None:
            ensemble = [ sample.data [key] [step] for index, sample in enumerate (samples) if index in indices and not numpy.isnan (sample.data [key] [step]) ]
          else:
            ensemble = [ sample.data [key] [step] for sample in samples if not numpy.isnan (sample.data [key] [step]) ]

        # remove NaN's
        #ensemble = [ element for element in ensemble if not numpy.isnan (element) ]

        # compute statistic
        if len (ensemble) > 0:
          stats.data [key] [step] = self.compute (ensemble)
        else:
          stats.data [key] [step] = float ('nan')
      
      # update progress
      progress.update (i + 1)
      
    # finalize progress indicator
    progress.finalize()

    return stats

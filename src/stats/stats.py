
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
  def compute_all (self, samples, indices=None, check=0):
    
    # copy data class from the first valid sample
    for sample in samples:
      if sample != None:
        stats = copy.deepcopy (sample)
        break

    # use progress indicator, report current statistic each time
    prefix = '       %s: ' % self.name
    progress = Progress (prefix=prefix, steps=len(stats.data.keys()), length=20)

    # compute sample statistics
    for i, key in enumerate (stats.data.keys()):
      for step in xrange ( len ( stats.data [key] ) ):

        # check for unavailable samples
        if check:

          # if spedific indices are required, take this into account
          if indices != None:
            series = [ sample.data [key] [step] for index, sample in enumerate (samples) if sample != None and index in indices ]
          else:
            series = [ sample.data [key] [step] for sample in samples if sample != None ]

        # assume all samples are available
        else:

          # if spedific indices are required, take this into account
          if indices != None:
            series = [ sample.data [key] [step] for index, sample in enumerate (samples) if index in indices ]
          else:
            series = [ sample.data [key] [step] for sample in samples ]

        # remove NaN's
        series = [ value for value in series if not numpy.isnan (value) ]

        # compute statistic
        if len (series) > 0:
          stats.data [key] [step] = self.compute (series)
        else:
          stats.data [key] [step] = float ('nan')
      
      # update progress
      progress.update (i + 1)

    # finalize progress indicator
    progress.finalize()

    return stats

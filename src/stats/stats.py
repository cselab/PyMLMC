
# # # # # # # # # # # # # # # # # # # # # # # # # #
# General statistics classes                      #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import copy

class Stat (object):
  
  # TODO: implement serialize() method for DataClass and generalize this
  def compute_all (self, samples):
    
    # copy data class from the first valid sample
    for sample in samples:
      if sample != None:
        stats = copy.deepcopy (sample)
        break
    
    # compute sample statistics
    for key in stats.data.keys():
      for step in xrange ( len ( stats.data [key] ) ):
        series = [ sample.data [key] [step] for sample in samples if sample != None ]
        stats.data [key] [step] = self.compute (series)
    
    return stats


# # # # # # # # # # # # # # # # # # # # # # # # # #
# General statistics classes                      #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from solver import Results

class Stat (object):
  
  # TODO: implement serialize() method for DataClass and generalize this
  def compute_all (self, samples):
    
    stats = Results ()
    
    # copy metadata from the first sample
    stats.meta = samples [0] .meta
    
    # copy keys from the first sample
    keys = samples [0] .data.keys()
    
    # compute sample statistics
    for key in keys:
      stats.data [key] = []
      for step in xrange ( len ( samples [0] .data [key] ) ):
        stats.data [key] .append ( self.compute ( [ sample.data [key] [step] for sample in samples ] ) )
    
    return stats

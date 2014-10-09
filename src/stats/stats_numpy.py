
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Stats class for general statistics from NumPy
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy

class NumPy_Stat (object):
  
  def __init__ (self, stat, name=None):
    self.stat = getattr ( numpy, stat )
    if name:
      self.name = name
    else:
      self.name = stat
  
  #TODO: parts of this should be moved out to stats.py general object, only the actual statistics for an array should be computed here
  def compute (self, samples):
    
    stats = Results ()
    
    # copy metadata from the first sample
    stats.meta = samples [0] .meta
    
    # copy keys from the first sample
    keys = samples [0] .data.keys()
    
    # compute sample statistics
    for key in keys:
      stats.data [key] = []
      for step in xrange ( len ( samples [0] .data [key] ) ):
        stats.data [key] .append ( self.stat ( [ sample.data [key] [step] for sample in samples ] ) )
    
    return stats

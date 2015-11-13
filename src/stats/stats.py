
# # # # # # # # # # # # # # # # # # # # # # # # # #
# General statistics classes                      #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Stat (object):
  
  # TODO: implement serialize() method for DataClass and generalize this
  def compute_all (self, samples):
    
    # copy data class from the first sample
    stats = samples [0]
    
    # compute sample statistics
    for key in stats.data.keys():
      stats.data [key] = []
      for step in xrange ( len ( samples [0] .data [key] ) ):
        series = [ sample.data [key] [step] for sample in samples if sample != None ]
        stats.data [key] .append ( self.compute ( series ) )
    
    return stats


# # # # # # # # # # # # # # # # # # # # # # # # # #
# General samples classes                        #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Samples (object):
  
  def validate (self):
    
    for level in self.levels:
      if self.counts [level] == 0:
        Exception (" :: ERROR: Encountered a level with no samples: counts[%d] = 0" % level )

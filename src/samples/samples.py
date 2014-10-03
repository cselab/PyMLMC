
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
    # TODO: fix this
    for level in range(self.params.L+1):
      if self.M [level] == 0:
        Exception (" :: ERROR: Encountered a level with no samples: M[%d] = 0" % self.M [samples_level] )

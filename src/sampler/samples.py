
# # # # # # # # # # # # # # # # # # # # # # # # # #
# General samples classes                        #
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Samples (object):

  def __init__ (self, params):
    
    self.L = params.L + 1
    
    self.M            = range (params.L+1)
    self.M_ADDITIONAL = range (params.L+1)
    self.M_UPDATED    = range (params.L+1)
    
  def validate (self):
    for samples_level in range(self.params.L+1):
      if self.M [samples_level] == 0:
        Exception (" :: ERROR: Encountered a level with no samples: M[%d] = 0" % self.M [samples_level] )

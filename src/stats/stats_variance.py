
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Stats class for variance 
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Variance (object):
  
  def __init__ (self):
    self.name  = 'variance'
    self.style = 'r--'
  
  def compute (self, samples):
    Exception ( " :: ERROR: Variance stat is not implemented." )

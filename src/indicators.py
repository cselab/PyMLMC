
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Error indicators class
# TODO: add paper, description and link
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import numpy

# === local imports


# === classes

class Indicators (object):
  
  def __init__ (self, indicator):
    
    # store configuration 
    self.indicator = indicator
  
  def compute (self, levels, mcs):
    
    # list of results
    self.error_relative = [ None ] * len ( levels )
    self.error_total    = [ None ] * len ( levels )
    self.error = 0


    
  def report (self):
    
    print ' :: WARNING: indicator report() not yet implemented.'

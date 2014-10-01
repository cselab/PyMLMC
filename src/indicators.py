
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Error indicators classes
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
    
    # list of results
    self.error_relative = [ None ] * len ( self.samples )
    self.error_total    = [ None ] * len ( self.samples )
  
  def compute (self):
    
    
  def report (self):
    
    

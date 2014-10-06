
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base Solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Solver (object):
  
  # return the name of a particular run
  def name (self, level, type, sample, id):
    return 'level=%d_type=%d_sample=%d_id=%d' % (level, type, sample, id)
  
  # return the seed for the simulation
  def seed (self, level, sample, id):
    return self.pair ( self.pair (level, sample), id )
  
  # pair two seeds into one
  def pair (self, a, b):
    return a ** 2 + a + b if a >= b else a + b ** 2

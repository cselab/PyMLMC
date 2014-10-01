
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base Solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

class Example_Solver (Solver):
  
  # return the name of a particular run
  def name (self, level, type, sample, run_id):
    return 'level=%d_type=%d_sample=%d_run_id=%d' % (level, type, sample, run_id)
  

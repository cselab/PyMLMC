
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Solver class (example)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from solver import Solver
import os, subprocess

class Example_Solver (Solver):
  
  def __init__ (self):
    self.cmd  = ['echo', '$RANDOM']
    self.filename = 'output_%(name)s'
    self.indicator = lambda x : x
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    return 1
  
  def run (self, level, type, sample, id, discretization, params):
    args = {}
    args ['name'] = self.name (level, type, sample, id)
    outputf = open (self.filename % args, 'w')
    subprocess.check_call ( self.cmd, stdout=outputf, stderr=subprocess.STDOUT )
  
  def finished (self, level, type, sample, id):
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    return os.path.exists ( filename )
  
  def load (self, level, type, sample, id):
    if not self.finished (level, type, sample, id):
      Exception ( ' :: ERROR: sample %d form level %d of type %d could not be loaded (id is %d) !' % (level, type, sample, id) )
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    f = open ( filename, 'r' )
    return 1 

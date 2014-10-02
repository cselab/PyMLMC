
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Solver class (example)
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

from solver import Solver
import subprocess, numpy, os

class Example_Solver (Solver):
  
  def __init__ (self):
    self.cmd  = 'echo $RANDOM'
    self.filename = 'output_%(name)s'
    self.argsf = '>> output_%(name)s'
    self.indicator = lambda x : x
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    return 1
  
  def run (self, level, type, sample, id, discretization, params):
    args = {}
    args ['name'] = self.name (level, type, sample, id)
    print self.cmd, self.argsf % args
    #subprocess.call ( [self.cmd, self.argsf % args] )
    os.system ( self.cmd + self.argsf % args )
  
  def finished (self, level, type, sample, id):
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    return os.path.exists ( filename )
  
  def load (self, level, type, sample, id):
    if not self.finished (level, type, sample, id):
      Exception ( ' :: ERROR: sample %d form level %d of type %d could not be loaded (id is %d) !' % (level, type, sample, id) )
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    f = open ( filename, 'r' )
    #return numpy.read_from_file(f)
    return 1 

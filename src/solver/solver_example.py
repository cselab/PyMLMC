
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Example solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === Discretization format:
# discretization = {'NX' : ?, 'NY' : ?, 'NZ' : ?}

from solver import Solver
import os, subprocess

class Example_Solver (Solver):
  
  def __init__ (self):
    
    self.cmd  = 'echo $RANDOM'
    self.filename = 'output_%(name)s'
    self.indicator = lambda x : x

    # prefix for the labels
    self.prefix = 'mpcf'
    
    # set datatype
    self.DataClass = float
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ']
  
  # return the approproate ratio of the number of cores between two discretizations
  def ratio (self, d1, d2):
    
    return d1 ['NX'] / d2 ['NX'] * d1 ['NY'] / d2 ['NY'] * d1 ['NZ'] / d2 ['NZ']
  
  def validate (self, discretization, parallelization):
    
    return 1
  
  def run (self, level, type, sample, id, seed, discretization, params, paralellization):
    
    args = {}
    args ['name'] = self.name (level, type, sample, id)
    outputf = open (self.filename % args, 'w')
    subprocess.check_call ( self.cmd, stdout=outputf, stderr=subprocess.STDOUT, shell=True, env=os.inviron.copy() )
    #subprocess.check_call ( self.cmd, stdout=outputf, stderr=subprocess.STDOUT, env=os.inviron.copy() )
  
  def finished (self, level, type, sample, id):
    
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    return os.path.exists ( filename )
  
  def load (self, level, type, sample, id):
    
    filename = self.filename % { 'name' : self.name (level, type, sample, id) }
    f = open ( filename, 'r' )
    f.close()
    
    from numpy.random import seed, randn
    from helpers import pair
    seed ( pair ( pair (level, sample), id ) )
    return randn() / ( 2 ** level )


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Example solver class
# TODO: add paper, description and link           #
#                                                 #
# Jonas Sukys                                     #
# CSE Lab, ETH Zurich, Switzerland                #
# sukys.jonas@gmail.com                           #
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === SHORT INTRODUCTION
# for each deterministic run, specified by parameters (level, type, sample, id),
# a directory is created and the run (together with input and output) is restricted to that directory.
#
# Discretization format:
# discretization = {'NX' : ?, 'NY' : ?, 'NZ' : ?}
#

from solver import Solver
import local
import os, subprocess

class Float (float):
  
  def zero (self):
    self = 0

class Example_Solver (Solver):
  
  # constructor for the example solver
  # 'options'       options for the solver
  # 'inputfiles'    list of required input files that will be copied to subdirectories
  # 'path'          path to the executable; if local.cluster = 1 and path != None, a local copy of the executable is created
  # 'init'          function to execute before starting each simulation; format: 'init (seed)'
  def __init__ (self, options='', inputfiles=[], path=None, init=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # command to be executed in terminal
    self.cmd  = 'echo $RANDOM'
    
    # set path from the environment variable
    # if not path: self.path = self.env('ENV_VARIABLE_FOR_PATH')
    
    # name of the relevant output file
    self.outputfile = 'output.dat'
    
    # indicator function: given the results of the output file,
    # picks out (or computes) the required quantity of interest
    self.indicator = lambda x : x
    
    # name of this solver (used as prefix for the job names)
    self.name = 'example'
    
    # set datatype that function self.load(...) returns
    self.DataClass = Float
    
    # enable shared memory (i.e. 1 MPI-rank per node)
    # self.sharedmem = 1
  
  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ['NX'] * d ['NY'] * d ['NZ']
  
  # return the prefered ratio of the number of cores between two discretizations
  def ratio (self, d1, d2):
    
    return d1 ['NX'] / d2 ['NX'] * d1 ['NY'] / d2 ['NY'] * d1 ['NZ'] / d2 ['NZ']
  
  # validate the proposed parallelization for the specified discretization
  def validate (self, discretization, parallelization):
    
    return 1
  
  # run the specified deterministic simulation (level, type, sample)
  def run (self, level, type, sample, seed, discretization, params, paralellization):
    
    # initialize arguments for the specified parallelization
    #TODO: move this to Scheduler base class?
    args = self.args (parallelization)
    
    # inspect args - uncomment this for first time use!
    # print args
    
    # here, args can be modified and additional args can be added
    # args ['parameter'] = value
    # args ['seed'] = seed
    
    # execute/submit job
    self.launch (args, parallelization, level, type, sample)
  
  # check if the job is finished
  # (required only for non-interactive sessions on clusters)
  def finished (self, level, type, sample):
    
    # get directory
    directory = self.directory ( level, type, sample )
    
    # check if the output file exists
    return os.path.exists ( os.path.join (self.directory, self.outputfile) )
  
  # open output file and read results
  def load (self, level, type, sample):
    
    outputfile = open ( os.path.join (self.directory (level, type, sample), self.outputfile), 'r' )
    lines = outputfile .readlines ()
    outputfile.close()
    return [ float ( lines[0] .strip() ) ]

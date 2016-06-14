
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Example solver class
# Performs integration of a two-dimensional random function using rectangle rule
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
# discretization = N
#

from solver import Solver
import local
import os, subprocess

class Integral2D (Solver):
  
  # constructor for the example solver, all arguments are optional
  # 'options'       additional options for the solver
  # 'path'          path to the executable; if local.cluster = 1 and path != None, a local copy of the executable is created
  # 'name'          name of this solver (used as prefix for the job names, so better keep it short, ~4-6 characters)
  # 'workunit'      estimated workunit (in core hours), such that runtime = workunit * solver.work (resolution)
  # 'init'          function to execute before starting each simulation; format: 'init (seed)'
  def __init__ (self, options='', path=None, name='int2d', workunit=None, init=None):
    
    # save configuration
    vars (self) .update ( locals() )
    
    # command to be executed in terminal
    # see available list of dynamic arguments in '/doc' directory, others can be set in 'self.run()'
    self.cmd  = 'python -c "from numpy import *; f = lambda x, y, t, u : u**2 * x**2 * cos(y) * sqrt(t); random.seed (%(seed)d); u = random.uniform(); g = linspace (0, 2, %(N)d); x,y = meshgrid (g,g); I = [1.0 / %(N)d ** 2 * sum (f(x,y,t,u)) for t in arange (10)]; print I; f = open (\'output.dat\', \'w\'); f.write (str(I)); f.close()"'

    # set path from the environment variable
    #if not path: self.path = self.env ('ENV_VARIABLE_FOR_PATH')

    # default workunit
    if not workunit: workunit = 1

    # name of the relevant output file
    self.outputfile = 'output.dat'
    
    # indicator function: given the results of the output file,
    # picks out (or computes) the required quantity of interest
    self.indicator = lambda x : x

    # distance function: given the results of two output files,
    # picks out and computes the required distance in quantity of interest
    self.distance = lambda f, c : abs ( f - c if c != None else f )
    
    # shared memory support (i.e. 1 MPI-rank per node)
    self.sharedmem = 0

  # return string representing the resolution of a give discretization 'd'
  def resolution_string (self, d):
    from helpers import intf
    return intf (d)

  # return amount of work needed for a given discretization 'd'
  def work (self, d):
    
    return d ** 2
  
  # return the prefered ratio of the number of cores between two discretizations
  def ratio (self, d1, d2):
    
    return self.work (d1) / self.work (d2)
  
  # validate the proposed parallelization for the specified discretization
  def validate (self, discretization, parallelization):
    
    # TODO: parallelization can not be larger than 1?
    return 1
  
  # run the specified deterministic simulation (level, type, sample)
  # note, that current contents of the 'input' directory (if exists) will be copied to the working directory
  def run (self, level, type, sample, seed, discretization, params, paralellization):
    
    # get parallelization args
    args = parallelization.args()
    
    # inspect args - uncomment this for first time use!
    # print args
    
    # here, args can be modified and additional args can be added
    args ['N']    = discretization
    args ['seed'] = seed
    
    # execute/submit job
    self.launch (args, parallelization, level, type, sample)
  
  # open output file and read results
  def load (self, level, type, sample):
    
    outputfile = open ( os.path.join (self.directory (level, type, sample), self.outputfile), 'r' )
    lines = outputfile .readlines ()
    outputfile.close()
    return { 't' : [0:10], 'I' : [ float ( lines[0] .strip() ) ] }

  # report progress of a pending simulation
  def progress (self, results):

    return None

  # report efficiency
  def efficiency (self, level=0, type=0, sample=0, file=None):

    return None
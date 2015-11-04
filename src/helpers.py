
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Helpers
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import os
import sys
import subprocess
import argparse

# === functions

# parse command line arguments
def parse ():
  parser = argparse.ArgumentParser()
  parser.add_argument ('-r', '--restart',       action = "count", default = 0,  help = 'restart the simulation')
  parser.add_argument ('-i', '--interactive',   action = "count", default = 0,  help = 'after launch of each update, wait for jobs to finish instead of exiting')
  parser.add_argument ('-q', '--query',         action = "store", default = 1,  help = 'query user for the modification of the tolerance after each update', type=int)
  parser.add_argument ('-o', '--xopts',         action = "store", default = '', help = 'additional options for the job scheduling system', type=str)
  parser.add_argument ('-v', '--verbose',       action = "store", default = 0,  help = 'additional options for the solver', type=int)
  parser.add_argument ('-s', '--simulate',      action = "count", default = 0,  help = 'simulate run only - no actual execution')
  parser.add_argument ('-p', '--proceed',       action = "count", default = 0,  help = 'proceed with simulations (can override existing files)')
  parser.add_argument ('-b', '--batch',         action = "store", default = 1,  help = 'group small jobs of the same level and type into a single batch job', type=int)
#  parser.add_argument ('-d', '--deterministic', action = "count", default = deterministic,  help = 'deterministic simulation - no subdirectories are created')
  return parser.parse_args()

# creates an empty nested list iterating over levels and types
def level_type_list (levels):
  return [ [None, None] for level in levels ]

# generates hierarchical grids by specifying the coarsest grid and the additional number of levels L
def grids (N0, L=0):
  return [ N0 * (2 ** level) for level in range (L+1) ]

# generates hierarchical sponge widths by specifying the coarsest sponge width, the additional number of levels L and the block size
def spongewidths (S0, L=0, bs=32):
  return [ min ( bs, S0 * (2 ** level) ) for level in range (L+1) ]

# generates 1D grids with specified numbers of cells N
def grids_1d (N):
  return [ { 'NX' : n } for n in N ]

# generates 1D grids with specified numbers of cells N and time steps NS
def grids_1d_t (N, NS):
  return [ { 'NX' : n, 'NS' : n } for n in N ]

# generates 2D grids with specified numbers of cells N
def grids_2d (N):
  return [ { 'NX' : n, 'NY' : n } for n in N ]

# generates 2D grids with specified numbers of cells N and time steps NS
def grids_2d_t (N, NS):
  return [ { 'NX' : n, 'NY' : n, 'NS' : n } for n in N ]

# generates 3D grids with specified numbers of cells N
def grids_3d (N):
  return [ { 'NX' : n, 'NY' : n, 'NZ' : n } for n in N ]

# generates 3D grids with specified numbers of cells N and sponge widths SW
def grids_3d (N, S = None):
  if S == None:
    S = spongewidths (32, L=len(N)-1)
  return [ { 'NX' : n, 'NY' : n, 'NZ' : n, 'spongewidth' : s } for n, s in zip (N, S) ]

# generates 3D grids with specified numbers of cells N and time steps NS
def grids_3d_t (N, NS):
  return [ { 'NX' : n, 'NY' : n, 'NZ' : n, 'NS' : n } for n in N ]

# integer format with multipliers K, M, etc.
def intf (number, table=0):
  if table:
    template = '%3d%1s'
  else:
    template = '%d%s'
  if number == 0:
    return template % ( 0, '' )
  from math import log, floor
  base = 1000
  magnitude = int ( floor ( log ( number, base ) ) )
  number    = int ( floor ( number / ( base ** magnitude ) ) )
  return template % ( number, ['', 'K', 'M', 'G', 'T', 'P', 'E'] [magnitude] )

# pair two seeds into one
def pair (a, b):
  return a ** 2 + a + b if a >= b else a + b ** 2

# dump list to file
def dump (listvar, listformat, listname, filename):
  with open ( filename, 'a') as f:
    line = listname + ' = [ '
    for var in listvar:
      line += listformat % var + ', '
    f.write ( line + ']\n' )

# load MLMC simulation from a different directory
def load (dir):
  print
  print ' :: LOADING simulation from'
  print '  : %s' % dir
  list = {}
  path = os.path.join (os.getcwd(), dir )
  execfile ( os.path.join (path, 'script.py'), globals(), list )
  list ['mlmc'] .chroot (dir)
  list ['mlmc'] .load ()
  print
  return list

# query for user decision
def query (question):
  print ' :: QUERY: %s [enter \'y\' or press ENTER]' % question
  input = raw_input ( '  : ' ) or 'y'
  if input != 'y':
    print '  : EXIT'
    print
    sys.exit()
  else:
    print '  : CONTINUE'
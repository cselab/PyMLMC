
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Helpers
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import sys
import subprocess
import argparse

# === functions

# parse command line arguments
def parse ():
  parser = argparse.ArgumentParser()
  parser.add_argument ('-r', '--restart',     action = "count", default = 0,  help = 'restart the simulation')
  parser.add_argument ('-i', '--interactive', action = "count", default = 0,  help = 'if set tonot s')
  parser.add_argument ('-q', '--query',       action = "count", default = 1,  help = 'query user for the modification of the tolerance after each update')
  #parser.add_argument ('-o', '--options',     action = "store", default = '', help = 'additional options for the solver')
  return parser.parse_args()

# creates an empty nested list iterating over levels and types
def level_type_list (levels):
  return [ [None, None] for level in levels ]

# generates hierarchical grids specifying the coarsest grid and the additional number of levels L
def grids (N0, L):
  return [ N0 * (2 ** level) for level in range (L+1) ]

# generates 1D grids with specified numbers of cells N
def grids_1d (N):
  return [ { 'NX' : N[l] } for l in range(len(N)) ]

# generates 1D grids with specified numbers of cells N and time steps NS
def grids_1d_t (N, NS):
  return [ { 'NX' : N[l], 'NS' : NS[l] } for l in range(len(N)) ]

# generates 2D grids with specified numbers of cells N
def grids_2d (N):
  return [ { 'NX' : N[l], 'NY': N[l] } for l in range(len(N)) ]

# generates 2D grids with specified numbers of cells N and time steps NS
def grids_2d_t (N, NS):
  return [ { 'NX' : N[l], 'NY' : N[l], 'NS' : NS[l] } for l in range(len(N)) ]
 
# generates 3D grids with specified numbers of cells N
def grids_3d (N):
  return [ { 'NX' : N[l], 'NY' : N[l], 'NZ' : N[l] } for l in range(len(N)) ]

# generates 3D grids with specified numbers of cells N and time steps NS
def grids_3d_t (N, NS):
  return [ { 'NX' : N[l], 'NY' : N[l], 'NZ' : N[l], 'NS' : NS[l] } for l in range(len(N)) ]

# integer format with multipliers K, M, etc.
def intf (number):
  if number == 0:
    return '%3d%s' % ( 0, ' ' )
  from math import log, floor
  base = 1000
  magnitude = int ( floor ( log ( number, base ) ) )
  number    = int ( floor ( number / ( base ** magnitude ) ) )
  return '%3d%s' % ( number, [' ', 'K', 'M', 'G', 'T', 'P', 'E'] [magnitude] )

# pair two seeds into one
def pair (self, a, b):
  return a ** 2 + a + b if a >= b else a + b ** 2

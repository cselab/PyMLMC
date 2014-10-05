
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
  parser.add_argument ('-r', '--restart',     action = "count", default = 0, help = 'restart the simulation')
  parser.add_argument ('-i', '--interactive', action = "count", default = 0, help = 'if set tonot s')
  parser.add_argument ('-q', '--query',       action = "count", default = 1, help = 'query user for the modification of the tolerance after each update')
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
  from math import log
  magnitude = int ( round ( log ( 1000, number ) ) )
  number    = int ( round ( number / ( 1000 ** magnitude ) ) )
  return '%3d%s' % ( number, ['', 'K', 'M', 'G', 'T', 'P', 'E'] [magnitude] )

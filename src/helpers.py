
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
import collections

params = None

# === functions

# parse command line arguments
def parse ():
  parser = argparse.ArgumentParser()
  parser.add_argument ('-r', '--restart',       action = "count", default = 0,  help = 'restart the simulation')
  parser.add_argument ('-i', '--interactive',   action = "count", default = 0,  help = 'after launch of each update, wait for jobs to finish instead of exiting')
  parser.add_argument ('-q', '--query',         action = "count", default = 1,  help = 'query user for the modification of the tolerance or budget after each update')
  parser.add_argument ('-a', '--auto',          action = "count", default = 0,  help = 'automatically continue in all queries')
  parser.add_argument ('-o', '--xopts',         action = "store", default = '', help = 'additional options for the job scheduling system', type=str)
  parser.add_argument ('-v', '--verbose',       action = "store", default = 0,  help = 'additional options for the solver', type=int)
  parser.add_argument ('-s', '--simulate',      action = "count", default = 0,  help = 'simulate run only - no actual execution')
  parser.add_argument ('-p', '--proceed',       action = "count", default = 0,  help = 'proceed with simulations (might override existing files)')
  parser.add_argument ('-o', '--override',      action = "count", default = 0,  help = 'override configurations')
  parser.add_argument ('-b', '--batch',         action = "store", default = 1,  help = 'group small jobs of the same level and type into a single batch job', type=int)

  global params
  params = parser.parse_args()

  return params

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
def intf (number, table=0, empty=0):
  if table:
    template = '%3d%1s'
  else:
    template = '%d%s'
  if number == 0:
    if empty:
      if table:
        return '    '
      else:
        return ''
    else:
      return template % ( 0, '' )
  from math import log, floor
  sign = -1 if number < 0 else 1
  number = abs (number)
  base = 1000
  magnitude = int ( floor ( log ( number, base ) ) )
  number    = int ( floor ( number / ( base ** magnitude ) ) )
  return template % ( sign * number, ['', 'K', 'M', 'G', 'T', 'P', 'E'] [magnitude] )

# pair two seeds into one
def pair (a, b):
  return a ** 2 + a + b if a >= b else a + b ** 2

# delete file
def delete (filename):
  os.remove (filename)

# dump variable or list (iterable object) to a file
def dump (var, format, name, filename, iteration):

  # write header for the first iteration
  if iteration == 0:
    with open ( filename, 'a') as f:
      f.write ( '%s = {}\n' % name )
  
  # write data
  with open ( filename, 'a') as f:
    if not isinstance (var, collections.Iterable):
      line = name + ' [%d]' % iteration + ' = ' + format % var
    else:
      line = name + ' [%d]' % iteration + ' = [ '
      for item in var:
        if str(item) == 'nan':
          line += 'float(\'nan\')' + ', '
        else:
          line += format % item + ', '
      line += ']'
    f.write ( line + '\n' )

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

# provides an update'able progress bar for the command line
class Progress (object):

  def __init__ (self, prefix, steps, length=20):

    self.prefix  = prefix
    self.length  = length
    self.steps   = steps
    self.percent = None

    from sys import stdout
    self.stdout = stdout
    
    self.update (0)

  def update (self, step):
    fraction = float(step) / self.steps
    percent = int(round(100*fraction))
    if percent == self.percent:
      return
    self.percent = percent
    text  = '\r' + self.prefix
    text += '[' + '#' * int(round(fraction*self.length)) + ' ' * int((self.length-round(fraction*self.length))) + ']'
    text += ' ' + str (percent) + '%'
    self.stdout.write (text)
    self.stdout.flush ()

  def reset (self):
    self.stdout.write('\r')
    length = len (self.prefix) + 8 + self.length
    self.stdout.write(' ' * length)
    self.stdout.flush()
    self.stdout.write('\r')
    self.stdout.flush()

# info
def info (message, details=None, advice=None):
  print
  print ' :: INFO: %s' % message
  if details != None:
    print '  : %s' % details
  if advice != None:
    print '  : -> %s' % advice

# query
def query (message, hint='enter \'y\' or press ENTER', type=str, default='y', warning=None, exit=1, format=None):

  print
  if warning != None:
    print ' :: WARNING: %s' % warning
  print ' :: QUERY: %s [%s]' % (message, hint)

  # in auto mode, continue with the default value
  if params.auto:
    print '  : AUTO CONTINUE [%s]' % str (default)
    input = default

  # otherwise, query for user input
  else:
    input = raw_input ( '  : ' )

    # format accordingly
    if not format:
      input = type (input) or default
    elif format == 'intf':
      factor = 1
      if 'K' in input:
        factor = 1e3
        input = input.replace ('K', '')
      if 'M' in input:
        factor = 1e6
        input = input.replace ('M', '')
      if 'G' in input:
        factor = 1e9
        input = input.replace ('G', '')
      try:
        input = type (input) * factor
      except:
        input = default

    # handle process flow
    if exit:
      if input != default:
        print '  : EXIT'
        print
        sys.exit()

    # report the parsed input
    if format == 'intf':
      print '  : %s' % intf (input)
    elif format:
      print '  : %s' % (format % input)
    else:
      print '  : %s' % str  (input)
    
    return input

# error
def error (message, details=None, advice=None):
  print
  print ' :: ERROR: %s -> exiting...' % message
  if details != None:
    print '  : %s' % details
  if advice != None:
    print '  : -> %s' % advice
  print
  sys.exit()

# warning
def warning (message, details=None, advice=None):
  print
  print ' :: WARNING: %s' % message
  if details != None:
    print '  : %s' % details
  if advice != None:
    print '  : -> %s' % advice
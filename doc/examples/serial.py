
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Simple serial code exhibiting the main idea of a single-stage MLMC algorithm
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy

# === configuration

N0    = 8 # coarsest resolution
L     = 6 # finest level (levels = 0, ..., L)
times = numpy.linspace (0, 1, 10)

# === deterministic application

def Integral2D (N, seed):

  f = lambda x, y, t, u : 1 + u ** 2 * x ** 2 * numpy.cos (y) * numpy.sqrt (t)
  numpy.random.seed (seed)
  u = 1 + 0.1 * numpy.random.uniform ()
  g = numpy.linspace (0, 2, N)
  x,y = numpy.meshgrid (g,g)
  I = [1.0 / N ** 2 * numpy.sum (f(x,y,t,u)) for t in times]
  return I

# === helpers

def pair (a, b):
  return a ** 2 + a + b if a >= b else a + b ** 2

# === MLMC simulation

levels  = numpy.arange (L + 1)
samples = 4 * 2 ** (L - levels)
N       = N0 * 2 ** levels

results = [ numpy.empty ( (samples [level], len (times)), dtype=float ) for level in levels ]

for level in levels:
  for sample in range ( samples [level] ):
    results [level] [sample, :] = Integral2D ( N [level], pair (level, sample) )

# === statistics assembly

mean = numpy.zeros ( len (times) )
var  = numpy.zeros ( len (times) )

for level in levels:
  for snapshot, time in enumerate (times):

    if level == 0:
      mean [snapshot] = numpy.mean ( results [level] [:, snapshot] )
      var  [snapshot] = numpy.var  ( results [level] [:, snapshot] )

    else:
      mean [snapshot] += numpy.mean ( results [level] [:, snapshot] - results [level - 1] [ : samples [level], snapshot ] )
      var  [snapshot] += numpy.var  ( results [level] [:, snapshot] - results [level - 1] [ : samples [level], snapshot ] )

# === output

print mean
print var

# === plotting

import pylab
lower = mean - numpy.sqrt (var)
upper = mean + numpy.sqrt (var)
pylab.plot (times, mean, linewidth=3, label='mean')
color = 'red'
pylab.fill_between (times, lower, upper, facecolor=color, edgecolor=color, linewidth=3)
pylab.plot ([], [], color=color, linewidth=10, label='mean +/- std. dev.')

pylab.title  ( 'MLMC statistics' )
pylab.xlabel ( 'time' )
pylab.ylabel ( 'quantity of interest' )
pylab.legend ( loc='best' )
pylab.show   ()

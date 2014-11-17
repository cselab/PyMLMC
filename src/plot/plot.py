
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Plotting routines for stats generated by PyMLMC
# TODO: add paper, description and link
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# === global imports

import pylab
import numpy

import matplotlib
matplotlib.rcParams['font.size'] = 16
matplotlib.rcParams['legend.fontsize'] = 14

styles = {}
styles ['mean']             = 'b-'
styles ['std. deviation']   = 'r--'
styles ['percentile']       = 'g--'

# plot each stat
def plot_stats (qoi, stats):
  
  for name, stat in stats.iteritems():
    
    ts = numpy.array ( stat.meta ['t_i'] )
    vs = numpy.array ( stat.data [qoi]  )
    
    style = styles [name] if name in styles else ''
    
    # stat-specific plotting
    if name == 'std. deviation' and 'mean' in stats:
      ms = numpy.array ( stats ['mean'] .data [qoi] )
      pylab.plot (ts, ms + vs, style, label='mean +/- std. dev.')
      pylab.plot (ts, ms - vs, style)
    
    # general plotting
    else:  
      pylab.plot (ts, vs, style, label=name)
  
  pylab.legend (loc='best')

def plot_infolines (mlmc):
  
  #TODO
  print ' :: ERROR: plot_infolines() not implemented.'

def generateTexTable (mlmc):
  
  #TODO
  print ' :: ERROR: generateTexTable() not implemented.'

# plot computed MC statistics
def plot_mc (mlmc, qoi=None, infolines=False, save=None):
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  levels = (len(mlmc.mcs) + 1) / 2
  
  if infolines:
    pylab.figure(figsize=(levels*8,2*6))
  else:
    pylab.figure(figsize=(levels*8,5+6))
  
  for mc in mlmc.mcs:
    
    pylab.subplot ( 2, levels, mc.config.level + 1 + (mc.config.type == 1) * levels )
    pylab.title ( 'estimated statistics for %s (level %d, type %d)' % (qoi, mc.config.level, mc.config.type) )
    plot_stats ( qoi, mc.stats )
  
  if infolines: plot_infolines (self)
  if save:
    pylab.savefig    (save)
    pylab.savefig    (save[:-3] + 'eps')
    generateTexTable (save)
  pylab.show ()

# plot computed MLMC statistics
def plot_mlmc (mlmc, qoi=None, infolines=False, save=None):
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  if infolines:
    pylab.figure(figsize=(8,6))
  else:
    pylab.figure(figsize=(8,5))
  
  pylab.title ( 'estimated statistics for %s' % qoi )
  plot_stats (qoi, mlmc.stats)
  
  if infolines: plot_infolines (self)
  if save:
    pylab.savefig    (save)
    pylab.savefig    (save[:-3] + 'eps')
    generateTexTable (save)
  pylab.show ()

# plot indicators
def plot_indicators (mlmc, exact=None, infolines=False, save=None):
  
  # === load all required data
  
  '''
  try:
    data = {}
    execfile(mlmc.estimatorsf, globals(), data)
  except:
    raise Exception ("ERROR: Estimators datafile " + mlmc.estimatorsf + " is not available!")
  '''
  
  EPSILON       = mlmc.indicators.mean_diff
  SIGMA         = mlmc.indicators.variance_diff
  TOL           = mlmc.config.samples.tol
  NORMALIZATION = mlmc.errors.normalization
  levels        = mlmc.levels
  qoi           = mlmc.config.solver.qoi
  
  # === compute error using the exact solution mean_exact
  
  if exact:
    
    # TODO: this needs to be reviewed
    error = numpy.abs ( exact - mlmc.stats [ qoi ] ) / NORMALIZATION
  
  # === plot
  
  if infolines:
    pylab.figure(figsize=(2*8,6))
  else:
    pylab.figure(figsize=(2*8,5))
  
  # plot EPSILON
  
  pylab.subplot(121)
  pylab.semilogy (levels, [e / NORMALIZATION for e in EPSILON],        color='b', linestyle='-',  linewidth=2, marker='x', markeredgewidth=2, markersize=8, label='relative level means')
  if exact:
    pylab.axhline (y=error, xmin=levels[0], xmax=levels[-1],           color='k', linestyle='-',  linewidth=2, alpha=0.3, label='MLMC error (%1.1e) for K = 1' % error)
  pylab.axhline   (y=TOL,   xmin=levels[0], xmax=levels[-1],           color='m', linestyle='--', linewidth=2, label='TOL = %1.1e' % TOL)
  pylab.title  ('Estimated relative level means for Q = %s' % qoi)
  pylab.ylabel (r'mean of relative $Q_\ell - Q_{\ell-1}$')
  pylab.xlabel ('mesh level')
  pylab.legend (loc='upper right')
  
  # plot SIGMA
  
  pylab.subplot(122)
  pylab.semilogy (levels, numpy.sqrt(SIGMA) / NORMALIZATION,        color='b', linestyle='-',  linewidth=2, marker='x', markeredgewidth=2, markersize=8, label='rel. level standard deviations')
  pylab.axhline (y=TOL, xmin=levels[0], xmax=levels[-1],            color='m', linestyle='--', linewidth=2, label='TOL = %1.1e' % TOL)
  pylab.title  ('Estimated rel. level standard deviations for Q = %s' % qoi)
  pylab.ylabel (r'standard deviation of rel. $Q_\ell - Q_{\ell-1}$')
  pylab.xlabel ('mesh level')
  pylab.legend (loc='best')
  
  pylab.subplots_adjust(top=0.94)
  pylab.subplots_adjust(right=0.95)
  pylab.subplots_adjust(left=0.07)
  
  if infolines:
    plot_infolines (self)
    pylab.subplots_adjust(bottom=0.28)
  else:
    pylab.subplots_adjust(bottom=0.15)
  
  if save:
    pylab.savefig    (save)
    pylab.savefig    (save[:-3] + 'eps')
    generateTexTable (save)
  
  pylab.show()

# plot samples
def plot_samples (mlmc, infolines=False, warmup=True, optimal=True, save=None):
  
  # === load all required data
  
  '''
  try:
    data = {}
    execfile(mlmc.samplesf, globals(), data)
  except:
    raise Exception ("ERROR: Samples datafile " + mlmc.samplesf + " is not available!")
  '''
  
  warmup_samples   = mlmc.config.samples.warmup
  samples          = mlmc.config.samples.counts.computed
  #counts_optimal   = mlmc.config.samples.counts_optimal
  #optimal_fraction = mlmc.config.samples.optimal_fraction
  TOL              = mlmc.config.samples.tol
  levels           = mlmc.levels
  
  # === plot
  
  if infolines:
    pylab.figure(figsize=(8,6))
  else:
    pylab.figure(figsize=(8,5))
  
  # plot number of samples
  
  #if warmup:
  #  pylab.semilogy (levels, warmup_samples, color='r', linestyle='--', linewidth=2, marker='+', markeredgewidth=2, markersize=12, label='warmup')
  pylab.semilogy (levels, samples, color='b', linestyle='-', linewidth=2, marker='x', markeredgewidth=2, markersize=8, label='estimated for TOL=%1.1e' % TOL)
  #if optimal:
  #  pylab.semilogy (levels, counts_optimal, color='g', linestyle='--', linewidth=2, marker='|', markeredgewidth=2, markersize=12, label='optimal (~%d%% less work)' % (100 * (1 - 1/optimal_fraction)))
  pylab.title  ('Estimated number of samples')
  pylab.ylabel ('number of samples')
  pylab.xlabel ('mesh level')
  pylab.ylim   (ymin=0.7)
  #TODO: add light gray lines at y = 1, 2, 4
  pylab.legend (loc='upper right')
  
  pylab.subplots_adjust(top=0.94)
  pylab.subplots_adjust(right=0.95)
  pylab.subplots_adjust(left=0.07)
  
  if infolines:
    show_info(self)
    pylab.subplots_adjust(bottom=0.28)
  else:
    pylab.subplots_adjust(bottom=0.15)
  
  if save:
    pylab.savefig    (save)
    pylab.savefig    (save[:-3] + 'eps')
    generateTexTable (save)
  
  pylab.show()

# plot errors
def plot_errors (mlmc, infolines=False, save=None):
  
  # === load all required data
  
  '''
  try:
    data = {}
    execfile(mlmc.estimatorsf, globals(), data)
  except:
    raise Exception ("ERROR: Estimators datafile " + mlmc.estimatorsf + " is not available!")
  '''
  
  relative_error   = mlmc.errors.relative_error
  TOL              = mlmc.config.samples.tol
  levels           = mlmc.levels
  qoi              = mlmc.config.solver.qoi
  
  # === plot
  
  if infolines:
    pylab.figure(figsize=(8,6))
  else:
    pylab.figure(figsize=(8,5))
  
  # plot relative sampling error
  
  pylab.semilogy (levels, relative_error, color='b', linestyle='-', linewidth=2, marker='x', markeredgewidth=2, markersize=8, label='relative sampling errors')
  pylab.axhline  (y=TOL, xmin=levels[0], xmax=levels[-1], color='m', linestyle='--', linewidth=2, label='required sampling tolerance' )
  pylab.title  ('Estimated relative sampling errors for Q = %s' % qoi)
  pylab.ylabel (r'relative error $\sqrt{\operatorname{Var} ( Q_\ell - Q_{\ell-1} ) / M_\ell}$')
  pylab.xlabel ('mesh level')
  pylab.ylim   (ymax=1.5*TOL)
  pylab.legend (loc='lower left')
  
  pylab.subplots_adjust(top=0.94)
  pylab.subplots_adjust(right=0.95)
  pylab.subplots_adjust(left=0.07)
  
  if infolines:
    show_info(self)
    pylab.subplots_adjust(bottom=0.28)
  else:
    pylab.subplots_adjust(bottom=0.15)
  
  if save:
    pylab.savefig    (save)
    pylab.savefig    (save[:-3] + 'eps')
    generateTexTable (save)
  
  pylab.show()

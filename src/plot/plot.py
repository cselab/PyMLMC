
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

import matplotlib

# for pylab.tight_layout()
#matplotlib.use('Agg')

import pylab
import numpy

# font configuration
matplotlib.rcParams ['font.size']       = 16
matplotlib.rcParams ['legend.fontsize'] = 14
matplotlib.rcParams ['lines.linewidth'] = 3
# TODO: increase label sizes

# additional colors
matplotlib.colors.ColorConverter.colors['a'] = (38/256.0,135/256.0,203/256.0)
matplotlib.colors.ColorConverter.colors['i'] = (251/256.0,124/256.0,42/256.0)
matplotlib.colors.ColorConverter.colors['j'] = (182/256.0,212/256.0,43/256.0)

# default color cycle
matplotlib.rcParams ['axes.color_cycle'] = ['a', 'i', 'j', 'c', 'y', 'm', 'g', 'r', 'burlywood', 'chartreuse', 'b', 'k']

styles = {}
styles ['mean']             = 'a-'
styles ['std. deviation']   = 'i--'
styles ['percentile']       = 'j--'

styles ['rp_integrated']    = 'k-'
styles ['rp_approximated']  = 'k--'

styles ['Req']              = 'a-'
styles ['p_max']            = 'i-'
styles ['ke']               = 'j-'
styles ['mach_max']         = 'c-'

# show plots
def show ():
  pylab.show()

# plot each stat
def plot_stats (qoi, stats, extent):
  
  for name, stat in stats.iteritems():
    
    ts = numpy.array ( stat.meta ['t'] )
    vs = numpy.array ( stat.data [qoi]  )
    
    style = styles [name] if name in styles else ''
    if 'percentile' in name: style = styles ['percentile']
    
    # stat-specific plotting
    if name == 'std. deviation' and 'mean' in stats:
      ms = numpy.array ( stats ['mean'] .data [qoi] )
      pylab.plot (ts, ms + vs, style, label='mean +/- std. dev.')
      pylab.plot (ts, ms - vs, style)
    
    # general plotting
    else:  
      pylab.plot (ts, vs, style, label=name)
  
  if extent:
    pylab.ylim (*extent)
  
  pylab.legend (loc='best')

def plot_infolines (mlmc):
  
  #TODO
  print ' :: ERROR: plot_infolines() not implemented.'

def generateTexTable (mlmc, save):
  
  #TODO
  print ' :: ERROR: generateTexTable() not implemented.'

# generate figure name using the format 'figpath/pwd_suffix.extension'
def figname (suffix, extension='pdf'):
  import os
  figpath = 'fig'
  if not os.path.exists (figpath):
    os.mkdir (figpath)
  runpath, rundir = os.path.split (os.getcwd())
  return os.path.join (figpath, rundir + '_' + suffix + '.' + extension)

def figure (infolines=False):
  if infolines:
    pylab.figure(figsize=(8,6))
  else:
    pylab.figure(figsize=(8,5))

def saveall (mlmc, save):
  pylab.savefig    (save)
  pylab.savefig    (save[:-3] + 'eps')
  pylab.savefig    (save[:-3] + 'png')
  generateTexTable (mlmc, save)

def draw (mlmc, save, legend=False, loc='best'):
  if legend:
    pylab.legend (loc = loc)
  if save:
    saveall (mlmc, save)
  pylab.draw ()

# plot computed MC statistics
def plot_mc (mlmc, qoi=None, infolines=False, extent=None, frame=False, save=None):
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  levels = (len(mlmc.mcs) + 1) / 2
  
  if infolines:
    pylab.figure (figsize=(levels*8, 2*6))
  else:
    pylab.figure (figsize=(levels*8, 5+6))
  
  for mc in mlmc.mcs:
    
    pylab.subplot ( 2, levels, mc.config.level + 1 + (mc.config.type == 1) * levels )
    pylab.title ( 'estimated statistics for %s (level %d, type %d)' % (qoi, mc.config.level, mc.config.type) )
    plot_stats ( qoi, mc.stats, extent )
  
  if infolines:
    plot_infolines (self)
  
  if not frame:
    draw (mlmc, save)

# plot computed MLMC statistics
def plot_mlmc (mlmc, qoi=None, infolines=False, extent=None, frame=False, save=None):
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  if infolines:
    pylab.figure(figsize=(8,6))
  else:
    pylab.figure(figsize=(8,5))
  
  pylab.title ( 'estimated statistics for %s' % qoi )
  plot_stats (qoi, mlmc.stats, extent)
  
  if infolines:
    plot_infolines (self)

  if not frame:
    draw (mlmc, save)

# plot results of one sample of the specified level and type
def plot_sample (mlmc, level, type=0, sample=0, qoi=None, infolines=False, extent=None, frame=False, save=None):
  
  # some dynamic values
  if level  == 'finest':   level  = mlmc.L
  if level  == 'coarsest': level  = 0
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  results = mlmc.config.solver.load ( level, type, sample )
  
  ts = numpy.array ( results.meta ['t'] )
  vs = numpy.array ( results.data [qoi]  )
  
  if not frame:
    if infolines:
      pylab.figure(figsize=(8,6))
    else:
      pylab.figure(figsize=(8,5))
  
  if qoi in styles:
    style = styles [qoi]
  else:
    style = styles ['mean']

  pylab.plot  (ts, vs, style, label=qoi)
  
  if not mlmc.params.deterministic:
    pylab.title ( 'sample %d of %s at level %d of type %d' % (sample, qoi, level, type) )

  if extent:
    pylab.ylim(*extent)

  if infolines: plot_infolines (self)
  #pylab.tight_layout()

  if not frame:
    draw (mlmc, save, legend=True, loc='best')

# plot the first sample of the finest level and type 0
# used mainly for deterministic runs
def plot (mlmc, qoi=None, infolines=False, extent=None, frame=False, save=None):
  level  = 'finest'
  type   = 0
  sample = 0
  plot_sample (mlmc, level, type, sample, qoi, infolines, extent, frame, save)

# plot results of all samples (ensemble) of the specified level and type 
def plot_ensemble (mlmc, level, type=0, qoi=None, infolines=False, extent=None, legend=4, save=None):
  
  # some dynamic values
  if level  == 'finest':   level  = mlmc.L
  if level  == 'coarsest': level  = 0
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  if infolines:
    pylab.figure(figsize=(8,6))
  else:
    pylab.figure(figsize=(8,5))
  
  for sample in range(mlmc.config.samples.counts.computed[level]):
    
    results = mlmc.config.solver.load ( level, type, sample )
    
    ts = numpy.array ( results.meta ['t'] )
    vs = numpy.array ( results.data [qoi]  )
    
    pylab.plot  (ts, vs, label=str(sample), linewidth=1)
  
  pylab.title ( 'samples of %s at level %d of type %d' % (qoi, level, type) )
  
  if extent:
    pylab.ylim(*extent)

  if mlmc.config.samples.counts.computed[level] <= legend:
    pylab.legend (loc='best')

  if infolines: plot_infolines (self)
  draw (mlmc, save)

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
  
  draw (mlmc, save)

# plot samples
def plot_samples (mlmc, infolines=False, warmup=True, optimal=True, frame=False, save=None):
  
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
  if not frame:
    pylab.legend (loc='upper right')
  
  pylab.subplots_adjust(top=0.94)
  pylab.subplots_adjust(right=0.95)
  pylab.subplots_adjust(left=0.07)
  
  if infolines:
    show_info(self)
    pylab.subplots_adjust(bottom=0.28)
  else:
    pylab.subplots_adjust(bottom=0.15)

  if not frame:
    draw (mlmc, save)

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
  
  draw (mlmc, save)

def rp_approximated (r, p1=100, p2=0.0234, rho=1000):
  tc = 0.914681 * r * numpy.sqrt ( rho / (p1 - p2) )
  print ' Collapse time: %f' % tc
  rp = lambda t : r * numpy.power (tc ** 2 - t ** 2, 2.0/5.0) / numpy.power (tc ** 2, 2.0/5.0)
  ts = numpy.linspace (0, tc, 10000)
  rs = rp(ts)
  return ts, rs

def rp_integrated (r, p1=100, p2=0.0234, rho=1000, tend=None, mu=0, S=0):
  import rp
  dr0 = 0
  [ts, rs, ps, drs] = rp.integrate (r, p1, p2, rho, tend, dr0, mu, S)
  return ts, rs, ps, drs

# plot Rayleigh Plesset
def plot_rp (mlmc, r, p1=100, p2=0.0234, rho=1000, mu=0, S=0, approximation=False, frame=False, save=None):
  
  # determine tend
  results = mlmc.config.solver.load ( mlmc.L, 0, 0 )
  ts = numpy.array ( results.meta ['t'] )
  tend = ts [-1]
  
  if approximation:
    ts, rs = rp_approximated (r, p1, p2, rho)
    label = 'Rayleigh-Plesset (approx.)'
    style = styles ['rp_approximated']
  else:
    ts, rs, ps, drs = rp_integrated (r, p1, p2, rho, tend, mu, S)
    label = 'Rayleigh-Plesset'
    if mu:
      label += ' + dissipation'
    style = styles ['rp_integrated']
  
  pylab.plot (ts, rs, style, alpha=0.5, label=label)

  if not frame:
    pylab.label (loc='best')
    draw (mlmc, save, legend=True, loc='best')
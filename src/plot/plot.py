
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
import sys

# figure configuration
matplotlib.rcParams ['figure.max_open_warning'] = 100
matplotlib.rcParams ['savefig.dpi']             = 300

# font configuration
matplotlib.rcParams ['font.size']             = 16
matplotlib.rcParams ['legend.fontsize']       = 14
matplotlib.rcParams ['lines.linewidth']       = 3
matplotlib.rcParams ['lines.markeredgewidth'] = 3
matplotlib.rcParams ['lines.markersize']      = 10

# additional colors
matplotlib.colors.ColorConverter.colors['custom_blue'] = (38/256.0,135/256.0,203/256.0)
matplotlib.colors.ColorConverter.colors['custom_orange'] = (251/256.0,124/256.0,42/256.0)
matplotlib.colors.ColorConverter.colors['custom_green'] = (182/256.0,212/256.0,43/256.0)

# default color cycle
matplotlib.rcParams ['axes.color_cycle'] = ['custom_blue', 'custom_orange', 'custom_green'] + list (matplotlib.colors.cnames.keys())

# === parser for base qoi

def base (qoi):
  
  if qoi in colors.keys() or qoi == None:
    return qoi
  elif len (qoi) > 3 and qoi [2] == '_' and qoi [:2] in colors.keys():
    return qoi [:2]
  elif len (qoi) > 2 and qoi [1] == '_' and qoi [0] in colors.keys():
    return qoi [0]
  else:
    return qoi

# === colors (specified by the stat, param or qoi)

# statistical estimators

colors_stats = {}

colors_stats ['default']          = 'custom_blue'

colors_stats ['mean']             = 'custom_blue'
colors_stats ['percentile']       = 'custom_orange'
colors_stats ['std. deviation']   = 'custom_green'

def color_stats (name):
  color = colors_stats [name] if name in colors_stats else colors_stats ['default']
  if 'percentile' in name: color = colors_stats ['percentile']
  return color

# MLMC parameters

colors_params = {}

colors_params ['default'] = 'custom_blue'

colors_params ['epsilon'] = 'custom_blue'
colors_params ['sigma']   = 'custom_orange'
colors_params ['samples'] = 'custom_green'
colors_params ['warmup']  = 'saddlebrown'
colors_params ['optimal'] = 'yellowgreen'
colors_params ['errors']  = 'coral'
colors_params ['error']   = 'lightskyblue'
colors_params ['tol']     = 'darkorchid'

def color_params (name):
  color = colors_params [name] if name in colors_params else colors_params ['default']
  return color

# quantities of interest from simulation

colors = {}

colors ['default'] = 'custom_blue'
colors ['pos'] = 'lightgrey'
colors ['trendline'] = 'darkorange'
colors ['t'] = 'grey'

colors ['r']   = 'saddlebrown'
colors ['r2']  = 'burlywood'
colors ['u']   = 'red'
colors ['v']   = 'green'
colors ['w']   = 'blue'
colors ['m']   = 'darkgoldenrod'
colors ['ke']  = 'mediumseagreen'
colors ['e']   = 'cyan'
colors ['W']   = 'darkorchid'
colors ['p']   = 'custom_orange'
colors ['pw']  = 'orangered'
colors ['c']   = 'forestgreen'
colors ['M']   = 'darkturquoise'
colors ['V2']  = 'custom_blue'
colors ['Req'] = 'custom_blue'
colors ['Vc']  = 'lightskyblue'

# other

colors ['rp_integrated']    = 'black'
colors ['rp_approximated']  = 'black'

def color (qoi):
  if '_pos' in qoi:
    return colors ['pos']
  if '_time' in qoi:
    return colors ['t']
  base_qoi = base (qoi)
  if base_qoi in colors.keys():
    return colors [base_qoi]
  else:
    return colors ['default']

# === styles (specified by the run)

#styles = ['-', '--', ':', '-.']
styles = ['-', '-', '-', '-']

def style (run):
  if (run - 1) < len (styles):
    return styles [run-1]
  else:
    return '-'

# === alphas (specified by the run)

alphas = [1.0, 0.6, 0.3, 0.1]

def alpha (run):
  if (run - 1) < len (alphas):
    return alphas [run-1]
  else:
    return '-'

# === units

units = {}

units ['t']   = r'$\mu s$'
units ['pos'] = r'$mm$'

units ['r']   = r'$kg/m^3$'
units ['r2']  = r'$kg/m^3$'
units ['u']   = r'$mm/\mu s$'
units ['v']   = r'$mm/\mu s$'
units ['w']   = r'$mm/\mu s$'
units ['m']   = r'$mm/\mu s$'
units ['ke']  = r'$J$' # check
units ['W']   = r'$\mu s^{-1}$'
units ['e']   = r'$J$' # check
units ['p']   = r'$bar$'
units ['pw']  = r'$bar$'
units ['c']   = r'$mm/\mu s$'
units ['M']   = r'$-$'
units ['V2']  = r'$mm^3$'
units ['Req'] = r'$mm$'
units ['Vc']  = r'$mm^3$'

def unit (qoi):
  if '_pos' in qoi:
    return units ['pos']
  if '_time' in qoi:
    return units ['t']
  base_qoi = base (qoi)
  if base_qoi in units.keys():
    return units [base_qoi]
  else:
    return r'$???$'

# === names

names = {}

names ['t']   = 'time'
names ['r']   = 'density'
names ['r2']  = 'gas density'
names ['u']   = 'x-velocity'
names ['v']   = 'y-velocity'
names ['w']   = 'z-velocity'
names ['m']   = 'velocity magnitude'
names ['ke']  = 'kinetic energy'
names ['W']   = 'vorticity magnitude'
names ['e']   = 'total energy'
names ['p']   = 'pressure'
names ['pw']  = 'wall pressure'
names ['c']   = 'speed of sound'
names ['M']   = 'Mach number'
names ['V2']  = 'gas volume'
names ['Req'] = 'equivalent radius'
names ['Vc']  = 'cloud volume'

def name (qoi, short=False):
  
  base_qoi = base (qoi)
  
  if not short and base_qoi in names.keys():
    name_ = names [base_qoi]
  else:
    name_ = base_qoi

  if '_avg' in qoi:
    name_ = 'avg ' + name_
  if '_min' in qoi:
    name_ = 'min ' + name_
  if '_max' in qoi:
    name_ = 'max ' + name_
  if '_time' in qoi:
    name_ = 'time of ' + name_
  if short and '_pos' in qoi:
    name_ = name_ + ' pos'
  else:
    if '_pos_x' in qoi:
      name_ = 'x-pos. of ' + name_
    if '_pos_y' in qoi:
      name_ = 'y-pos. of ' + name_
    if '_pos_z' in qoi:
      name_ = 'z-pos. of ' + name_
    if '_pos_d' in qoi:
      if not '_pos_d_x' in qoi and not '_pos_d_y' in qoi and not '_pos_d_z' in qoi:
        name_ = 'dist. of ' + name_
    if '_pos_d_x' in qoi:
      name_ = 'x-dist. of ' + name_
    if '_pos_d_y' in qoi:
      name_ = 'y-dist. of ' + name_
    if '_pos_d_z' in qoi:
      name_ = 'z-dist. of ' + name_

  return name_

# === helper routines

# set levels extent
def levels_extent (levels):
  pylab.xlim ( [ -0.2, levels[-1]+0.2 ] )
  pylab.xticks (levels)

# generate figure name using the format 'figpath/pwd_suffix.extension'
def figname (suffix='', extension='pdf'):
  import os
  figpath = 'fig'
  if not os.path.exists (figpath):
    os.mkdir (figpath)
  runpath, rundir = os.path.split (os.getcwd())
  if suffix == '':
    return os.path.join (figpath, rundir + '.' + extension)
  else:
    return os.path.join (figpath, rundir + '_' + suffix + '.' + extension)

def figure (infolines=False, subplots=1):
  if infolines:
    pylab.figure(figsize=(subplots*8,6))
  else:
    pylab.figure(figsize=(subplots*8,5))

# adjust subplot margins
def adjust (infolines, subplots=1):

  pylab.subplots_adjust (top=0.92)

  if infolines:
    pylab.subplots_adjust (bottom=0.28)
  else:
    pylab.subplots_adjust (bottom=0.15)

  left = max (0.05, 0.16/subplots)
  pylab.subplots_adjust (left=left)

  right = 0.95
  pylab.subplots_adjust (right=right)

# compute parameters needed for the generation of the TexTable
def getTexTableConfig (mlmc):
  
  # config
  
  keys     =  ['grid_size', 'cores', 'runtime', 'cluster']
  captions =  ['grid size', 'cores', 'runtime', 'cluster']
  
  # aggregation of information
  
  import time
  
  values               = {}
  values ['grid_size'] = 'x'.join ( [ str(parameter) for parameter in mlmc.config.discretizations [mlmc.config.L] .values() ] )
  values ['cores']     = mlmc.status.list ['parallelization']
  values ['cluster']   = mlmc.status.list ['cluster']
  
  if mlmc.finished:
    values ['runtime'] = time.strftime ( '%H:%M:%S', time.gmtime ( mlmc.mcs[mlmc.config.L].timer (mlmc.config.scheduler.batch) ) )
  else:
    values ['runtime'] = mlmc.status.list ['walltimes'] [-1] [0]
  
  # number of levels

  if mlmc.config.L != 0:
    keys = ['L'] + keys
    captions = [r'$L$'] + captions
    values ['L'] = mlmc.config.L
  
  return [keys, captions, values]

# generate TeX code with the table including information about the simulation
def generateTexTable (mlmc, base):
  
  # check for valid mlmc simulation
  if mlmc == None:
    return
  
  # get the config
  
  [keys, captions, opts] = getTexTableConfig (mlmc)
  
  # TeX code generation
  
  columns =  '|' + 'c|' * len(keys)
  
  text =  '\n'
  text += r'\begin{tabular}{%s}' % columns + '\n'
  
  text += r'\hline' + '\n'
  text += (r'%s & ' * len(captions))[0:-2] % tuple(captions) + r'\\' + '\n'
  text += r'\hline' + '\n'
  text += (r'%s & ' * len(keys))[0:-2] % tuple([opts[key] for key in keys]) + r'\\' + '\n'
  text += r'\hline' + '\n'
  
  text += r'\end{tabular}' + '\n'
  
  # saving
  f = open (base + '.tex', 'w')
  f.write (text)
  f.close ()

# plot infolines with information about the simulation
def plot_infolines (mlmc):
  
  '''
  # text formatter
  def format_text (text, subplots):
    if not subplots and len(text) > 65:
      cut_pos = len(text)/2
      cut_pos = text.find(' ', cut_pos)
      text = text[:cut_pos] + '\n' + ' ' * 9 + text[cut_pos:]
    return text
  
  # CONF
  text  = prefix + format_text('CONF:' + ???, subplots) + '\n'
  
  # OPTS
  text += prefix + format_text('OPTS: ' + mlmc.options, subplots) + '\n'
  
  # INFO
  [keys, captions, values] = getTexTableConfig (mlmc)
  
  string_info  = ' CLUSTER: ' + config ['cluster']
  string_info += ', cores: ' + str(helpers.intf(int(config ['cores'])))
  string_info += ', runtime: ' + config ['runtime']

  text += prefix + format_text('INFO:' + string_info, subplots)
  
  # SAMPLES
  samples_available = self.samples and (self.i.L != 0 or self.i.ML != 1 or self.i.READ_NUMBER_OF_SAMPLES_FROM_FILE)
  if samples_available:
    text += '\n' + prefix + 'SAMPLES: ' + str(self.samples[::-1])[1:-1]
  
  # MESH_LEVEL and TYPE
  if level != None:
    text += ' (only the %d-sample MC estimate from MESH_LEVEL=%d and TYPE=%d is displayed)' % (self.samples[level+type], level, type)
  
  # default parallelization
  if self.default_parallelization:
    if samples_available:
      text += ' | '
    else:
      text += '\n'
    text += 'PARALLELIZATION:'
    for level in range(len(self.default_parallelization)):
      text += ' ' + str(self.default_parallelization[level][3]) + 'x(' + str(self.default_parallelization[level][0])
      if self.i.NY > 1: text += 'x' + str(self.default_parallelization[level][1])
      if self.i.NZ > 1: text += 'x' + str(self.default_parallelization[level][2])
      text += ')'
  
  return text
  '''
  return None

def saveall (mlmc, save, qoi=None):
  base_name = save[:-4]
  if qoi != None:
    base_name += '_' + qoi
  # bug workaround
  if base (qoi) == 'm' or base (qoi) == 'w':
    base_name += '_'
  pylab.savefig    (base_name + '.' + save[-3:])
  pylab.savefig    (base_name + '.' + 'eps')
  pylab.savefig    (base_name + '.' + 'png')
  pylab.savefig    (base_name + '.' + 'pdf')
  generateTexTable (mlmc, base_name)

#def draw (mlmc, save, qoi=None, legend=False, loc='best', extent=None, xorigin=True, yorigin=True):
def draw (mlmc, save, qoi=None, legend=False, loc='best'):
  
  #adjust_axes (qoi, extent, xorigin, yorigin)
  
  # reset xend_max
  global xend_max
  xend_max = None
  
  if legend or (qoi != None and '_pos' in qoi):
    pylab.legend (loc = loc)
  if save:
    saveall (mlmc, save, qoi)
  pylab.draw ()

# show plots
def show ():
  pylab.show()

# === domain related constants

extent_x = 'N/A'
extent_y = 'N/A'
extent_z = 'N/A'
surface  = 'N/A'
xend_max = None

def set_extent (e_x, e_y=None, e_z=None):
  global extent_x
  global extent_y
  global extent_z
  extent_x = e_x
  extent_y = e_y if e_y != None else extent_x
  extent_z = e_z if e_z != None else extent_x

def set_surface (s):
  global surface
  surface = s

# === plotting routines

# filter
def filter (vs, width):
  if width % 2 != 0:
    width += 1
  vs_ext = numpy.r_ [ vs [width-1:0:-1], vs, vs [-1:-width:-1] ]
  window = numpy.hanning (width)
  window /= window.sum()
  vs_cnv = numpy.convolve (window, vs_ext, mode='valid')
  return vs_cnv [width / 2 - 1 : len (vs_cnv) - width / 2]

# plot a line indicating position
def plot_helper_lines (qoi, run=1):
  
  if qoi == None:
    return
  
  if '_pos_d' in qoi:
    if surface == 'N/A':
      print
      print
      print ' :: ERROR: \'pymlmc.plot.surface\' not set.'
      print
      sys.exit()
    if surface != None:
      pylab.axhline (y=surface, color='maroon', linestyle='--', alpha=alpha(run), label='cloud surface')

# adjust axes
def adjust_axes (qoi, extent, xorigin, yorigin, xend=None, yend=None):
  
  # fit all existing data first
  pylab.gca().axis ('auto')
  
  # adjust x-axis
  if xorigin:
    pylab.gca().set_xlim (left = 0)
  if xend != None:
    global xend_max
    if xend_max == None:
      xend_max = xend
    else:
      xend_max = max (xend, xend_max)
    pylab.gca().set_xlim (right = xend_max)

  # if extent is specified, use that
  if extent:
    pylab.ylim (*extent)

  # otherwise perform some automatic axes modifications based on parameters
  else:
    
    if yorigin:
      pylab.gca().set_ylim (bottom = 0)
    
    if yend:
      pylab.gca().set_ylim (top = yend)
    
    if qoi == None:
      return
  
    # this should be perfomed _only_ if data is too close
    #pylab.gca().set_ylim (top = 1.05 * pylab.ylim() [1])
    
    ylim = pylab.ylim() [1]

    if '_pos_d' in qoi and surface != None:
      pylab.gca().set_ylim (top = max (1.05 * surface, ylim))

    if '_pos_x' in qoi and extent_x != None:
      pylab.gca().set_ylim (top = max (extent_x, ylim))
    if '_pos_y' in qoi and extent_y != None:
      pylab.gca().set_ylim (top = max (extent_y, ylim))
    if '_pos_z' in qoi and extent_z != None:
      pylab.gca().set_ylim (top = max (extent_z, ylim))

# plot each stat
def plot_stats (qoi, stats, extent, xorigin, yorigin, xlabel, run=1, legend=True):
  
  percentiles = []

  for stat_name, stat in stats.iteritems():
    
    ts = numpy.array ( stat.meta ['t'] )
    vs = numpy.array ( stat.data [qoi] )
    
    # exclude first data point, if we are dealing with positions
    if '_pos' in qoi:
      ts = ts [1:]
      vs = vs [1:]
    
    color = color_stats (stat_name)
    
    # stat-specific plotting: std. deviation
    if stat_name == 'std. deviation' and 'mean' in stats:
      ms = numpy.array ( stats ['mean'] .data [qoi] )
      color = color_stats ('std. deviation')
      pylab.fill_between (ts, ms - vs, ms + vs, facecolor=color, alpha=0.2, label='mean +/- std. dev.')
    
    # collect percentiles for later fill
    elif 'percentile' in stat_name:
      percentiles.append ( { 'ts' : ts, 'vs' : vs, 'level' : float ( stat_name.split(' ') [0] ) } )
    
    # general plotting
    else:
      pylab.plot (ts, vs, color=color, linestyle=style(run), alpha=alpha(run), label=stat_name)
  
  # plot percentiles
  if percentiles != []:

    if len (percentiles) != 2:
      print
      print ' :: ERROR: Only two percentiles can be plotted at a time.'
      print
      print sys.exit()
    
    lower  = percentiles [0] ['vs']
    upper  = percentiles [1] ['vs']
    ts     = percentiles [0] ['ts']
    label  = 'confidence %.2f - %.2f' % ( percentiles [0] ['level'], percentiles [1] ['level'] )
    color  = color_stats ('percentile')
    
    pylab.fill_between (ts, lower, upper, facecolor=color, alpha=0.5, label=label)
  
  adjust_axes (qoi, extent, xorigin, yorigin, xend=numpy.max(ts))
  
  pylab.xlabel (xlabel)
  pylab.ylabel ('%s [%s]' % (name(qoi), unit(qoi)))
  
  plot_helper_lines (qoi, run)
  
  if legend:
    pylab.legend (loc='best')

# plot computed MC estimators of statistics
def plot_mc (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, run=1, frame=False, save=None):

  print ' :: INFO: Plotting MC estimates...',

  if not qoi: qoi = mlmc.config.solver.qoi

  levels = len (mlmc.config.levels)

  if not frame:
    figure (infolines, subplots=levels)

  xlabel = '%s [%s]' % (name('t'), unit('t'))

  for mc in mlmc.mcs:

    if mc.config.type != mlmc.config.FINE:
      continue

    pylab.subplot ( 1, levels, mc.config.level + 1 )
    pylab.title ( 'level %d' % mc.config.level )
    plot_stats ( qoi, mc.stats, extent, xorigin, yorigin, xlabel, run )

  if infolines:
    plot_infolines (self)

  adjust (infolines, subplots='table')

  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot computed MC estimators of statistics for both types
def plot_mc_both (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, run=1, frame=False, save=None):
  
  print ' :: INFO: Plotting MC estimates...',
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  levels = len (mlmc.config.levels)
  
  if not frame:
    if infolines:
      pylab.figure (figsize=(levels*6, 4+5))
    else:
      pylab.figure (figsize=(levels*6, 2*4))
  
  xlabel = '%s [%s]' % (name('t'), unit('t'))
  
  for mc in mlmc.mcs:
    
    typestr = ['fine', 'coarse'] [mc.config.type]
    pylab.subplot ( 2, levels, mc.config.level + 1 + (mc.config.type == 1) * levels )
    pylab.title ( 'level %d %s' % (mc.config.level, typestr) )
    plot_stats ( qoi, mc.stats, extent, xorigin, yorigin, xlabel, run, legend=False )
  
  handles, labels = pylab.gcf().gca().get_legend_handles_labels()
  pylab.subplot (2, levels, 1 + levels)
  pylab.legend (handles, labels, loc='center')
  pylab.axis('off')

  '''
  pylab.subplots_adjust (top=0.95)
  pylab.subplots_adjust (right=0.97)
  pylab.subplots_adjust (left=0.05)

  if infolines:
  plot_infolines (self)
  pylab.subplots_adjust (bottom=0.10)
  else:
  pylab.subplots_adjust (bottom=0.05)
  '''

  if infolines:
    plot_infolines (self)

  adjust (infolines, subplots='table')

  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot computed differences of MC estimators
def plot_diffs (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=False, run=1, frame=False, save=None):

  print ' :: INFO: Plotting differences of MC estimates...',

  if not qoi: qoi = mlmc.config.solver.qoi

  if not frame:
    figure (infolines, subplots=mlmc.config.L)

  xlabel = '%s [%s]' % (name('t'), unit('t'))

  extent_range = extent [1] - extent [0]
  extent_diff = ( extent [0] - extent_range / 2.0, extent [1] - extent_range / 2.0 )

  for level, diff in enumerate (mlmc.diffs [1:]):

    pylab.subplot ( 1, mlmc.config.L, level)
    pylab.title ( 'level %d - level %d' % (level, level - 1) )
    plot_stats ( qoi, diff, extent_diff, xorigin, yorigin, xlabel, run )

  '''
  handles, labels = pylab.gcf().gca().get_legend_handles_labels()
  pylab.subplot (2, levels, 1 + levels)
  pylab.legend (handles, labels, loc='center')
  pylab.axis('off')
  '''

  '''
  pylab.subplots_adjust (top=0.95)
  pylab.subplots_adjust (right=0.97)
  pylab.subplots_adjust (left=0.05)

  if infolines:
    plot_infolines (self)
    pylab.subplots_adjust (bottom=0.10)
  else:
    pylab.subplots_adjust (bottom=0.05)
  '''

  if infolines:
    plot_infolines (self)

  adjust (infolines, subplots=mlmc.config.L)

  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot computed MC estimators and their differences
def plot_mc_and_diffs (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, run=1, frame=False, save=None):

  print ' :: INFO: Plotting MC estimates AND differences...',

  if not qoi: qoi = mlmc.config.solver.qoi

  levels = len (mlmc.config.levels)

  if not frame:
    if infolines:
      pylab.figure (figsize=(levels*6, 4+5))
    else:
      pylab.figure (figsize=(levels*6, 2*4))

  xlabel = '%s [%s]' % (name('t'), unit('t'))

  # MC estimates for each level (only type = 0)
  for mc in mlmc.mcs:

    if mc.config.type != 0:
      continue

    pylab.subplot ( 2, levels, mc.config.level + 1 )
    pylab.title ( 'level %d' % mc.config.level )
    plot_stats ( qoi, mc.stats, extent, xorigin, yorigin, xlabel, run, legend=False )

  extent_range = extent [1] - extent [0]
  extent_diff = ( extent [0] - extent_range / 2.0, extent [1] - extent_range / 2.0 )

  # differences of MC estimates
  for level, diff in enumerate (mlmc.diffs):

    if level == 0:
      continue

    pylab.subplot ( 2, levels, level + 1 + levels )
    pylab.title ( 'level %d - level %d' % (level, level - 1) )
    plot_stats ( qoi, diff, extent_diff, xorigin, yorigin, xlabel, run )

  handles, labels = pylab.gcf().gca().get_legend_handles_labels()
  pylab.subplot (2, levels, 1 + levels)
  pylab.legend (handles, labels, loc='center')
  pylab.axis('off')

  '''
  pylab.subplots_adjust (top=0.95)
  pylab.subplots_adjust (right=0.97)
  pylab.subplots_adjust (left=0.05)

  if infolines:
    plot_infolines (self)
    pylab.subplots_adjust (bottom=0.10)
  else:
    pylab.subplots_adjust (bottom=0.05)
  '''

  if infolines:
    plot_infolines (self)

  adjust (infolines, subplots='table')

  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot computed MLMC statistics
def plot_mlmc (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, run=1, frame=False, save=None):
  
  print ' :: INFO: Plotting MLMC estimates...',
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  if not frame:
    figure (infolines, subplots=1)
  
  xlabel = '%s [%s]' % (name('t'), unit('t'))
  #pylab.title ( 'estimated statistics for %s' % qoi )
  plot_stats (qoi, mlmc.stats, extent, xorigin, yorigin, xlabel, run)

  if infolines:
    plot_infolines (self)

  adjust (infolines)

  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot results of one sample of the specified level and type
def plot_sample (mlmc, level, type=0, sample=0, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, run=1, trendline=None, smoothen=41, label=None, frame=False, save=None):
  
  # some dynamic values
  if level  == 'finest':   level = mlmc.config.L
  if level  == 'coarsest': level = 0
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  if trendline == None:
    if '_pos' in qoi:
      trendline = 1
    else:
      trendline = 0

  results = mlmc.config.solver.load ( level, type, sample )
  
  ts = numpy.array ( results.meta ['t'] )
  vs = numpy.array ( results.data [qoi] )
  
  # energy filter
  if base (qoi) == 'e':
    positions = []
    if '_pos_d_x' in qoi:
      max_d_x = 0.5 * numpy.sqrt (extent_y ** 2 + extent_z ** 2)
      positions = numpy.argwhere (vs > 0.9 * max_d_x)
    elif '_pos_d_y' in qoi:
      max_d_y = 0.5 * numpy.sqrt (extent_x ** 2 + extent_z ** 2)
      positions = numpy.argwhere (vs > 0.9 * max_d_y)
    elif '_pos_d_z' in qoi:
      max_d_z = 0.5 * numpy.sqrt (extent_x ** 2 + extent_y ** 2)
      positions = numpy.argwhere (vs > 0.9 * max_d_z)
    elif '_pos_d' in qoi:
      max_d = 0.5 * numpy.sqrt (extent_x ** 2 + extent_y ** 2 + extent_z ** 2)
      positions = numpy.argwhere (vs > 0.9 * max_d)
    ts = numpy.delete (ts, positions)
    vs = numpy.delete (vs, positions)
  
  # exclude first data point, if we are dealing with positions or vorticities
  if '_pos' in qoi or base (qoi) == 'W':
    ts = ts [1:]
    vs = vs [1:]

  # exclude more first data points for positions of densities
  if '_pos' in qoi and base (qoi) == 'r':
    ts = ts [3:]
    vs = vs [3:]
  
  if not frame:
    figure (infolines, subplots=1)

  if label == None:
    if '_pos' in qoi:
      label = 'distance'
    elif not frame:
      label = None
    elif not label:
      label = name (qoi)

  if not (trendline and frame):
    pylab.plot  (ts, vs, color=color(qoi), linestyle=style(run), alpha=alpha(run), label=label)

  # add trendline (if specified or if dealing with positions)
  if trendline:
    ls = filter (vs, width=smoothen)
    if not frame:
      label = 'trendline'
    if len (ls) == len (ts):
      pylab.plot  (ts, ls, color=color('trendline'), linestyle=style(run), alpha=alpha(run), label=label)
    else:
      print
      print ' :: WARNING: computing trendline failed (NaN\'s present? Too short?)'

  if not mlmc.config.deterministic:
    pylab.title ( 'sample %d of %s at level %d of type %d' % (sample, qoi, level, type) )

  pylab.xlabel ('%s [%s]' % (name('t'), unit('t')))
  pylab.ylabel ('%s [%s]' % (name(qoi), unit(qoi)))
  
  plot_helper_lines (qoi, run)
  
  adjust_axes (qoi, extent, xorigin, yorigin, xend=numpy.max(ts))
  
  if infolines:
    plot_infolines (self)
  
  adjust (infolines)
  
  if not frame:
    draw (mlmc, save, qoi)

# plot the first sample of the finest level and type 0
# used mainly for deterministic runs
def plot (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, run=1, trendline=None, smoothen=41, label=None, frame=False, save=None):
  
  print ' :: INFO: Plotting %s...' % qoi,
  
  level  = 'finest'
  type   = 0
  sample = 0
  
  plot_sample (mlmc, level, type, sample, qoi, infolines, extent, xorigin, yorigin, run, trendline, smoothen, label, frame, save)
  
  print ' done.'

# plot results of all samples (ensemble) of the specified level and type 
def plot_ensemble (mlmc, level, type=0, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, legend=4, limit=128, save=None):
  
  print ' :: INFO: Plotting ensemble for level %d (type %d)...' % (level, type),
  
  # some dynamic values
  if level  == 'finest':   level  = mlmc.config.L
  if level  == 'coarsest': level  = 0
  
  if not qoi: qoi = mlmc.config.solver.qoi
  
  figure (infolines, subplots=1)
  
  for sample in range ( min (limit, mlmc.config.samples.counts.computed[level]) ):
    
    results = mlmc.config.solver.load ( level, type, sample )
    
    ts = numpy.array ( results.meta ['t'] )
    vs = numpy.array ( results.data [qoi]  )
    
    # exclude first data point, if we are dealing with positions
    if '_pos' in qoi:
      ts = ts [1:]
      vs = vs [1:]
    
    pylab.plot  (ts, vs, label=str(sample), linewidth=1)
  
  pylab.title ( 'samples of %s at level %d of type %d' % (qoi, level, type) )
  
  pylab.xlabel ('%s [%s]' % (name('t'), unit('t')))
  pylab.ylabel ('%s [%s]' % (name(qoi), unit(qoi)))
  
  plot_helper_lines (qoi)
  
  adjust_axes (qoi, extent, xorigin, yorigin)
  
  if mlmc.config.samples.counts.computed[level] <= legend:
    pylab.legend (loc='best')
  
  if infolines:
    plot_infolines (self)
  
  adjust (infolines)
  
  draw (mlmc, save, qoi)
  
  print ' done.'

# plot results of all samples (ensemble) of all levels
def plot_ensembles (mlmc, qoi=None, infolines=False, extent=None, xorigin=True, yorigin=True, limit=1024, save=None):

  print ' :: INFO: Plotting ensembles for all levels...'

  if not qoi: qoi = mlmc.config.solver.qoi

  levels = len (mlmc.config.levels)

  figure (infolines, subplots=levels)

  for level in mlmc.config.levels:

    pylab.subplot ( 1, levels, level + 1 )
    pylab.title ( 'samples of level %d' % level )

    types = [mlmc.config.FINE, mlmc.config.COARSE] if level > 0 else [mlmc.config.FINE]

    for sample in range ( min (limit, mlmc.config.samples.counts.computed[level]) ):

      for type in types:

        results = mlmc.config.solver.load ( level, type, sample )

        ts = numpy.array ( results.meta ['t'] )
        vs = numpy.array ( results.data [qoi]  )

        # exclude first data point, if we are dealing with positions
        if '_pos' in qoi:
          ts = ts [1:]
          vs = vs [1:]

        if type == mlmc.config.FINE:
          line = pylab.plot  (ts, vs, linewidth=1 )
        else:
          pylab.plot  (ts, vs, linewidth=1, alpha=0.6, color=line.get_color() )

    pylab.xlabel ('%s [%s]' % (name('t'), unit('t')))
    pylab.ylabel ('%s [%s]' % (name(qoi), unit(qoi)))

    plot_helper_lines (qoi)

    adjust_axes (qoi, extent, xorigin, yorigin)

    pylab.legend (loc='best')

  if infolines:
    plot_infolines (self)

  adjust (infolines, subplots=levels)

  draw (mlmc, save, qoi)

  print ' done.'

def plot_diagram (solver, params, param_name, param_unit, outputfilenames, qoi=None, ref_file=None, ref_label=None, infolines=False, extent=None, xorigin=True, yorigin=True, logx=False, run=1, label=None, frame=False, save=None):
  
  if not qoi: qoi = solver.qoi
  
  vs = []
  for outputfilename in outputfilenames:
    results = solver.load (file=outputfilename)
    if '_time' in qoi:
      vs.append ( results.meta ['t'] [ numpy.argmax (results.data [qoi[:-5]]) ] )
    else:
      vs.append ( numpy.max ( results.data [qoi] ) )

  if not frame:
    figure (infolines, subplots=1)
  
  if label == None:
    label = name (qoi)
  
  if logx:
    pylab.semilogx (params, vs, color=color(qoi), linestyle=style(run), marker='o', markerfacecolor='w', markeredgecolor=color(qoi), alpha=alpha(run), label=label)
  else:
    pylab.plot (params, vs, color=color(qoi), linestyle=style(run), marker='o', markerfacecolor='w', markeredgecolor=color(qoi), alpha=alpha(run), label=label)
  
  if ref_file:
    results = solver.load (file=ref_file)
    if '_time' in qoi:
      v_ref = results.meta ['t'] [ numpy.argmax (results.data [qoi[:-5]]) ]
    else:
      v_ref = numpy.max ( results.data [qoi] )
    pylab.axhline (y=v_ref, xmin=params[0], xmax=params[-1], color=color(qoi), linestyle=style(run), alpha=0.5, label=ref_label)
  
  pylab.xlabel ('%s [%s]' % (param_name, param_unit))
  pylab.ylabel ('%s [%s]' % (name(qoi), unit(qoi)))
  
  plot_helper_lines (qoi, run)

  yend = 1.05 * numpy.max (vs)
  adjust_axes (qoi, extent, xorigin, yorigin, yend=yend)
  
  if infolines:
    plot_infolines (self)
  
  adjust (infolines)
  
  if not frame:
    draw (None, save, qoi, legend=True)

# plot indicators
def plot_indicators (mlmc, exact=None, infolines=False, run=1, frame=False, tol=False, save=None):
  
  print ' :: INFO: Plotting indicators...',
  
  # === load all required data
  
  EPSILON       = mlmc.indicators.mean_diff
  SIGMA         = mlmc.indicators.variance_diff
  TOL           = mlmc.config.samples.tol
  NORMALIZATION = mlmc.errors.normalization
  levels        = mlmc.config.levels
  qoi           = mlmc.config.solver.qoi
  
  # === compute error using the exact solution mean_exact
  
  if exact:
    
    # TODO: this needs to be reviewed
    error = numpy.abs ( exact - mlmc.stats [ qoi ] ) / NORMALIZATION
  
  # === plot
  
  if not frame:
    figure (infolines, subplots=2)
  
  # plot EPSILON
  
  pylab.subplot(121)
  pylab.semilogy (levels, [e / NORMALIZATION for e in EPSILON], color=color_params('epsilon'), linestyle=style(run), alpha=alpha(run), marker='x', label='relative level means')
  if run == 1:
    if exact:
      pylab.axhline (y=error, xmin=levels[0], xmax=levels[-1], color=color_params('error'), linestyle=style(run), alpha=0.3, label='MLMC error (%1.1e) for K = 1' % error)
    pylab.axhline   (y=TOL,   xmin=levels[0], xmax=levels[-1], color=color_params('tol'),   linestyle=style(run), alpha=0.6, label='TOL = %1.1e' % TOL)
  pylab.title  ('Rel. level means for Q = %s' % qoi)
  pylab.ylabel (r'mean of relative $Q_\ell - Q_{\ell-1}$')
  pylab.xlabel ('mesh level')
  levels_extent (levels)
  pylab.legend (loc='upper right')
  
  # plot SIGMA
  
  pylab.subplot(122)
  pylab.semilogy (levels, numpy.sqrt(SIGMA) / NORMALIZATION, color=color_params('sigma'), linestyle=style(run), alpha=alpha(run), marker='x', label='rel. level standard deviations')
  if run == 1:
    pylab.axhline (y=TOL, xmin=levels[0], xmax=levels[-1], color=color_params('tol'), linestyle=style(run), alpha=0.6, label='TOL = %1.1e' % TOL)
  pylab.title  ('Rel. level standard deviations for Q = %s' % qoi)
  pylab.ylabel (r'standard deviation of rel. $Q_\ell - Q_{\ell-1}$')
  pylab.xlabel ('mesh level')
  levels_extent (levels)
  pylab.legend (loc='best')
  
  adjust (infolines, subplots=2)
  
  if infolines:
    show_info(self)
  
  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot samples
def plot_samples (mlmc, infolines=False, warmup=True, optimal=True, run=1, frame=False, save=None):
  
  print ' :: INFO: Plotting samples...',
  
  # === load all required data
  
  warmup           = mlmc.config.samples.warmup
  samples          = mlmc.config.samples.counts.computed
  #optimal          = mlmc.config.samples.counts_optimal
  #optimal_fraction = mlmc.config.samples.optimal_fraction
  TOL              = mlmc.config.samples.tol
  levels           = mlmc.config.levels
  qoi              = mlmc.config.solver.qoi
  
  # === plot
  
  if not frame:
    figure (infolines, subplots=1)
  
  # plot number of samples
  
  #if warmup:
  #  pylab.semilogy (levels, warmup, color=color_params('warmup'), linestyle=style(run), marker='+', label='warmup')
  pylab.semilogy (levels, samples, color=color_params('samples'), linestyle=style(run), alpha=alpha(run), marker='x', label='estimated for TOL=%1.1e' % TOL)
  #if optimal:
  #  pylab.semilogy (levels, optimal, color=color_params('optimal'), linestyle=style(run), marker='|', label='optimal (~%d%% less work)' % (100 * (1 - 1/optimal_fraction)))
  pylab.title  ('Estimated number of samples')
  pylab.ylabel ('number of samples')
  pylab.xlabel ('mesh level')
  levels_extent (levels)
  pylab.ylim   (ymin=0.7)
  #TODO: add light gray lines at y = 1, 2, 4 (OR: label data points)
  #OR: change to barplot, labeling data points
  if not frame:
    pylab.legend (loc='upper right')
  
  adjust (infolines)
  
  if infolines:
    show_info(self)

  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

# plot errors
def plot_errors (mlmc, infolines=False, run=1, frame=False, save=None):
  
  print ' :: INFO: Plotting errors...',
  
  # === load all required data
  
  relative_error   = mlmc.errors.relative_error
  TOL              = mlmc.config.samples.tol
  levels           = mlmc.config.levels
  qoi              = mlmc.config.solver.qoi
  
  # === plot
  
  if not frame:
    figure (infolines, subplots=1)
  
  # plot relative sampling error
  
  pylab.semilogy (levels, relative_error, color=color_params('errors'), linestyle=style(run), alpha=alpha(run), marker='x', label='relative sampling errors')
  if run == 1:
    pylab.axhline  (y=TOL, xmin=levels[0], xmax=levels[-1], color=color_params('tol'), linestyle=style(run), alpha=0.6, label='required TOL = %1.1e' % TOL )
  pylab.title  ('Relative sampling errors for Q = %s' % qoi)
  pylab.ylabel (r'relative error $\sqrt{\operatorname{Var} ( Q_\ell - Q_{\ell-1} ) / M_\ell}$')
  pylab.xlabel ('mesh level')
  levels_extent (levels)
  pylab.ylim   (ymax=1.5*TOL)
  pylab.legend (loc='lower left')
  
  adjust (infolines)
  
  if infolines:
    show_info(self)
  
  if not frame:
    draw (mlmc, save, qoi)

  print ' done.'

import rp

def rp_approximated (r, p0_l=100, p0_g=0.0234, rho_l=1000):
  tc = 0.914681 * r * numpy.sqrt ( rho_l / (p0_l - p0_g) )
  rh = lambda t : r * numpy.power (tc ** 2 - t ** 2, 2.0/5.0) / numpy.power (tc ** 2, 2.0/5.0)
  return tc, rh

def rp_integrated (r, p0_l=100, p0_g=0.0234, rho_l=1000, rho0_g=1, gamma=1.4, tend=None, mu=0, S=0, model=rp.OptPL2()):
  dr0 = 0
  [ts, rs, ps, drs, name] = rp.integrate (r, p0_l, p0_g, rho_l, rho0_g, gamma, tend, dr0, mu, S, model)
  return numpy.array(ts), numpy.array(rs), numpy.array(ps), numpy.array(drs), name

# plot Rayleigh Plesset
def plot_rp (mlmc, r, p0_l=100, p0_g=0.0234, rho_l=1000, rho0_g=1, gamma=1.4, mu=0, S=0, count=1, color=None, approximation=False, model='OptPL2', run=1, frame=False, save=None):
  
  if r == None:
    r = numpy.array ( mlmc.config.solver.load ( mlmc.config.L, 0, 0 ) .data ['Req'] ) [0]
    if count != 1:
      r /= count ** (1.0/3.0)
  
  if not frame:
    figure (infolines=False, subplots=1)
  
  if approximation:
    tc, rh = rp_approximated (r, p0_l, p0_g, rho_l)
    ts = numpy.linspace (0, tc, 10000)
    rs = rp(ts)
    label = 'Rayleigh-Plesset (approx.)'
    if color == None:
      color = color_params('rp_approximated')
  else:
    results = mlmc.config.solver.load ( mlmc.config.L, 0, 0 )
    tend = numpy.array ( results.meta ['t'] ) [-1]
    model_class = getattr (rp, model)
    ts, rs, ps, drs, model_name = rp_integrated (r, p0_l, p0_g, rho_l, rho0_g, gamma, tend, mu, S, model_class() )
    label = model_name
    if mu:
      label += ' + dissipation'
    if color == None:
      color = color_params('rp_integrated')

  # report approximate collapse time
  print
  if count != 1:
    print ' :: Approximated (Rayleigh-Plesset) collapse time (for count = %d): %f' % (count, rp.approximate_collapse_time (r, p0_l, p0_g, rho_l) )
  else:
    print ' :: Approximated (Rayleigh-Plesset) collapse time: %f' % rp.approximate_collapse_time (r, p0_l, p0_g, rho_l)

  # report maximum pressure
  if not approximation:
    print
    if count != 1:
      print ' :: Approximated (%s) maximum pressure (for count = %d): %f' % ( model, count, numpy.max(ps) )
    else:
      print ' :: Approximated (%s) maximum pressure: %f' % ( model, numpy.max(ps) )
    print '  : -> Amplification factor \'p_max / p0_l\' is: %.1f' % (numpy.max(ps) / p0_l)
  
  # compute equivalent radius of simultaneously collapsing multiple bubbles
  if count != 1:
    label += ' (%d)' % count
    rs *= count ** (1.0 / 3.0)

  pylab.plot (ts, rs, color=color, linestyle=style(run), alpha=alpha(run), label=label)
  
  pylab.xlabel ('%s [%s]' % (name('t'),   unit('t')))
  pylab.ylabel ('%s [%s]' % (name('Req'), unit('Req')))
  
  if not frame:
    pylab.label (loc='best')
    draw (mlmc, save, legend=True, loc='best')

# plot hinton diagram
# source: http://matplotlib.org/examples/specialty_plots/hinton_demo.html
def plot_hinton (matrix, scale=0.95):
  
  ax = pylab.gca ()
  
  ax.patch.set_facecolor ('gray')
  ax.set_aspect ('equal', 'box')
  ax.xaxis.set_major_locator (pylab.NullLocator())
  ax.yaxis.set_major_locator (pylab.NullLocator())
  
  for (x, y), w in numpy.ndenumerate (matrix):
    color = 'white' if w > 0 else 'black'
    if x == y:
      color = 'gray'
    size = scale * numpy.sqrt (numpy.abs(w))
    #size = scale * numpy.abs(w)
    rect = pylab.Rectangle ([x - size / 2, y - size / 2], size, size, facecolor=color, edgecolor=color)
    ax.add_patch (rect)
  
  ax.autoscale_view ()
  ax.invert_yaxis ()

# plot correlations between different qois
def plot_correlations (mlmc, qois=None, hinton=True, infolines=False, save=None):
  
  if qois == None: qois = [ mlmc.config.solver.qoi ]
  
  level  = 'finest'
  type   = 0
  sample = 0
  
  results = mlmc.config.solver.load ( level, type, sample )
  
  data = numpy.zeros ( (len (qois), len (results.meta ['t']) - 1) )
  for i, qoi in enumerate (qois):
    # exclude first data point, because some channels needs to
    data [i, :] = numpy.array ( results.data [qoi] ) [1:]
  
  # mask unavailable data
  data = numpy.ma.masked_array ( data, numpy.isnan (data) )
  
  # compute correlation matrix
  R = numpy.ma.corrcoef (data)
  
  pylab.figure ( figsize = (8, 8) )
  
  # plot Hinton diagram
  if hinton:
    plot_hinton (R)
    pylab.minorticks_off()
    pylab.gca().tick_params ( labelleft='on', labelright='off', labelbottom='off',labeltop='on' )
    pylab.gca().set_xticks ( numpy.arange ( len (qois) ) )
    pylab.gca().set_yticks ( numpy.arange ( len (qois) ) )
    pylab.gca().set_xticklabels ( [' ' + name (qoi, short=True) for qoi in qois], rotation='vertical')
    pylab.gca().set_yticklabels ( [name (qoi, short=True) + ' ' for qoi in qois] )

  # plot conventional correlation matrix
  else:
    pylab.pcolor (R)
    pylab.axis ('equal')
    pylab.xlim ( [0, len (qois)] )
    pylab.ylim ( [0, len (qois)] )
    pylab.xticks ( 0.5 + numpy.arange ( len (qois) ), qois )
    pylab.yticks ( 0.5 + numpy.arange ( len (qois) ), qois )
    pylab.colorbar ()
  
  if infolines:
    plot_infolines (self)

  pylab.subplots_adjust (bottom=0.05)
  pylab.subplots_adjust (right=0.95)
  pylab.subplots_adjust (left=0.20)
  pylab.subplots_adjust (top=0.80)
  
  draw (mlmc, save)
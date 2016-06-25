
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Piz Daint cluster
# Cray XC30 @ Swiss Supercomputing Center (CSCS), Switzerland
# More information: http://www.cscs.ch/computers/piz_daint/index.html
#                   http://user.cscs.ch/computing_resources/piz_daint/index.html
# SLURM job scheduling system
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'CSCS Piz Daint (Cray XC30)'

# Piz Daint is a cluster
cluster = 1

# default configuration
cores     = 8    # per node
threads   = 1    # per core
walltime  = 1    # hours
memory    = 4096 # GB per core

# constraints

bootup       = 5  # minutes
min_cores    = cores
max_cores    = 5272 * cores

def min_walltime (cores): # hours
  return 0

def max_walltime (cores): # hours
  return 24

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# core performance metric (normalized w.r.t. IBM BG/Q)
performance = 1

# scratch path
scratch = '/scratch/daint/sukysj/pymlmc'

# ensemble support
ensembles = 0

# boot
boot = 0

# default environment variables
envs = ''

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads)d; %(envs)s %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; %(envs)s srun -n %(ranks)d -N %(tasks)d -d %(threads)d %(cmd)s %(options)s'

# submission script template
script = '''#!/bin/bash
#SBATCH --job-name=%(label)s
#SBATCH --nodes=%(nodes)d
#SBATCH --ntasks=%(ranks)d
#SBATCH --ntasks-per-node=%(tasks)d
#SBATCH --cpus-per-task=%(threads)d
#SBATCH --time=%(hours).2d:%(minutes).2d:00
#SBATCH --mem=%(memory)d
#SBATCH --output=%(reportfile)s
#SBATCH --account=s659
%(xopts)s
ulimit -c 0
%(job)s
'''

# submit command
submit = 'sbatch %(scriptfile)s'

# timer
timer = '(time -p (%(job)s)) 2>&1 | tee %(timerfile)s'

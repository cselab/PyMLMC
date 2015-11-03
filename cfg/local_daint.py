
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
min_walltime = 0  # hours
max_walltime = 24 # hours
min_cores    = cores

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# scratch path
scratch = '/scratch/daint/sukysj/pymlmc'

# default environment variables
envs = ''

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads)d; %(envs)s %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; %(envs)s aprun -n %(ranks)d -N %(tasks)d -d %(threads)d %(cmd)s %(options)s'

# submission script template
script = '''#!/bin/bash
#SBATCH --job-name=%(label)s
#SBATCH --nodes=%(nodes)d
#SBATCH --ntasks=%(ranks)d
#SBATCH --ntasks-per-node=%(tasks)d
#SBATCH --cpus-per-task=%(threads)d
#SBATCH --time=%(hours).2d:%(minutes).2d:00
#SBATCH --mem=%(memory)d
#SBATCH --output=report.%(label)s
#SBATCH --account=s500
%(xopts)s
ulimit -c 0
%(job)s
'''

# submit command
submit = 'sbatch %(scriptfile)s'

# timer
#timer = 'date; time --portability --output=%(timerfile)s --append (%(job)s)'
timer = 'date; (time -p (%(job)s)) 2>&1 | tee %(timerfile)s; touch %(statusfile)s'

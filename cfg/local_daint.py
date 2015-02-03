
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Piz Daint cluster
# Cray XC30 @ Swiss Supercomputing Center (CSCS)
# More information: http://www.cscs.ch/computers/piz_daint/index.html
#                   http://user.cscs.ch/computing_resources/piz_daint/index.html
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
cores     = 8
threads   = 8
walltime  = 1
memory    = 4096

# constraints
bootup = 5

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
#SBATCH --time=%(hours)d:%(minutes)d:00
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
timer = 'time'

# timer is disabled (for non-batch jobs)
#timer       = 0
#timer_start = 'START="$(/bin/date +%s)"'
#timer_stop  = 'TIME="$(($(/bin/date +%s)-START))"; echo Total time: "$TIME" seconds'

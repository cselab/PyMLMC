
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
walltime_min = 5

# scratch path
scratch = '/scratch/daint/sukysj/pymlmc'

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads); %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; aprun -n %(ranks)d -N %(tasks)d -d %(threads)d %(cmd)s %(options)s'

# batch run command
batch_job = '%(batch)s'

# submit command
submit = '''echo "#!/bin/bash
#SBATCH --job-name=%(label)s
#SBATCH --ntasks=%(ranks)d
#SBATCH --ntasks-per-node=%(tasks)d
#SBATCH --cpus-per-task=%(threads)d
#SBATCH --time=%(hours)d:%(minutes)d:00
#SBATCH --output=report.%(label)s
#SBATCH --account=s500
ulimit -c 0
%(xopts)s
%(job)s" | sbatch
'''

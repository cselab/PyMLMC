
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

# contraints
walltime_min = 5

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads); %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; aprun -n %(cores)d -N %(threads)d -d %(threads)d %(cmd)s %(options)s'

# batch run command
batch_job = '%(batch)s'

# submit command
submit = '''echo "#!/bin/bash
#SBATCH --job-name=%(label)s
#SBATCH --ntasks=%(cores)d
#SBATCH --ntasks-per-node=%(tasks)d
#SBATCH --cpus-per-ntask=%(threads)d
#SBATCH --time=%(hours)d:%(minutes)d:00
#SBATCH --mem=%(memory)d
#SBATCH --output=report.%(label)s
#SBATCH --account=s500
ulimit -c 0
%(xopts)s
%(job)s" | sbatch
'''

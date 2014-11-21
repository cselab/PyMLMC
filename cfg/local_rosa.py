
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Monte Rosa cluster (CSCS)
# More information: http://www.cscs.ch/computers/monte_rosa/index.html
#                   http://user.cscs.ch/computing_resources/monte_rosa/index.html
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'CSCS Monte Rosa (Cray XE6)'

# Piz Daint is a cluster
cluster = 1

# default configuration
cores     = 32
threads   = 32
walltime  = 1
memory    = 1024

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads); %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; aprun -n %(cores)d -N %(threads)d -d %(threads)d %(cmd)s %(options)s'

# batch script command
# TODO
batch_job = '%(script)s'

# submit command
# TODO: memory
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


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Monte Rosa cluster
# Cray XE6 @ Swiss Supercomputing Center (CSCS)
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

# Rosa is a cluster
cluster = 1

# default configuration
cores     = 32
threads   = 32
walltime  = 1
memory    = 1024

# constraints
bootup = 5

# scratch path
scratch = '/scratch/rosa/sukysj/pymlmc'

# simple run command
simple_job = 'export OMP_NUM_THREADS=%(threads)d; %(cmd)s %(options)s'

# MPI run command
mpi_job = 'export OMP_NUM_THREADS=%(threads)d; aprun -n %(ranks)d -N %(tasks)d -d %(threads)d %(cmd)s %(options)s'

# batch run command
batch_job = '%(batch)s'

# submit command
submit = '''echo "#!/bin/bash
#SBATCH --job-name=%(label)s
#SBATCH --ntasks=%(ranks)d
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

# timer is disabled (for non-batch jobs)
timer       = 0
timer_start = 'START=$(/bin/date +%s)'
timer_stop  = 'TIME=$(($(/bin/date +%s)-START)); echo Total time: $TIME seconds'

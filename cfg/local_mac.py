
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Mac
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Mac + GCC'

# Mac is (usually) not a cluster
cluster = 0

# default configuration
cores    = 2
threads  = 2
walltime = None

# run command
job = 'export OMP_NUM_THREADS=%(threads)d; %(cmd)s %(options)s'

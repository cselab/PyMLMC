
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Cetus cluster
# IBM BlueGene/Q @ Argonne National Laboratory, United States
# More information: http://www.alcf.anl.gov/user-guides/blue-geneq-versus-blue-genep
# Cobalt job scheduling system
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Argonne Cetus (IBM BlueGene/Q) [OUTDATED!!!]'

# Cetus is a cluster
cluster = 1

# default configuration
cores     = 16   # per node
threads   = 4    # per core
walltime  = 1    # h
memory    = 1024 # GB per core
rack      = 1024 # nodes

# constraints

bootup       = 5   # minutes
min_cores    = 512 * cores
max_cores    = 49152 * cores

def min_walltime (cores): # hours
  return 0.5

def max_walltime (cores): # hours
  if cores == 'default':
    return '12/24'
  if cores <= 16 * 4096:
    return 12
  else:
    return 24

# theoretical performance figures per node
peakflops = 0.0 # TFLOP/s
bandwidth = 0.0 # GB/s

# core performance metric (normalized w.r.t. IBM BG/Q)
performance = 1

# scratch path
scratch = '/projects/CloudPredict/sukysj/pymlmc'

# ensemble support
ensembles = 1

# default environment variables
envs = '''  --envs PAMI_DEVICE=B \
  --envs BG_MEMSIZE=16384 \
  --envs BG_THREADLAYOUT=2 \
  --envs OMP_STACKSIZE=4M \
  --envs OMP_SCHEDULE="dynamic,1" \
  --envs PAMID_COLLECTIVES=1 \
  --envs PAMI_MEMORY_OPTIMIZED=1 \
  --envs BG_SHAREDMEMSIZE=512 \
  --envs BG_MAPCOMMONHEAP=0 \
  --envs BG_SMP_FAST_WAKEUP=YES \
  --envs L1P_POLICY="dcbt" \
  --envs L1P_DEPTH=2 \
  --envs PAMID_THREAD_MULTIPLE=1 \
  --envs PAMID_VERBOSE=1 \
  --envs PAMID_MAX_COMMTHREADS=1 \
  --envs OMP_WAIT_POLICY=PASSIVE \
  --envs OMP_PROC_BIND=FALSE \
  --envs USEMAXTHREADS=0 \
  --envs MYROUNDS=1 \
  --envs DARSHAN_DISABLE=1 \
  '''

#  --envs PAMID_ASYNC_PROGRESS=1 \
#  --mapping TABCDE \

# simple run command
simple_job = '''ulimit -c 0; runjob \
  --np %(ranks)d \
  --ranks-per-node %(tasks)d \
  --cwd $PWD \
  --envs OMP_NUM_THREADS=%(threads)d \
  --envs XLSMPOPTS=parthds=%(threads)d \
  --block BATCH_JOB_BLOCK_HOOK \
  %(envs)s \
  : %(cmd)s
  '''

# MPI run command
mpi_job = '''ulimit -c 0; runjob \
  --np %(ranks)d \
  --ranks-per-node %(tasks)d \
  --cwd $PWD \
  --envs OMP_NUM_THREADS=%(threads)d \
  --envs XLSMPOPTS=parthds=%(threads)d \
  --block BATCH_JOB_BLOCK_HOOK \
  %(envs)s \
  : %(cmd)s
  '''

# batch job block hook
BATCH_JOB_BLOCK_HOOK = '${BLOCKS[%(batch_id)d]}'

# submission script template (required for support of batch job ensembles)
script = '''#!/bin/bash

  # get blocks for each batch job in the ensemble
  BLOCKS=`get-bootable-blocks --size %(nodes)d $COBALT_PARTNAME`

  # split string of blocks into array elements
  read -r -a BLOCKS <<< $BLOCKS

  # print info about blocks
  echo
  echo 'Obtained blocks:'
  for BLOCK in ${BLOCKS[@]}
  do
  echo $BLOCK
  done
  echo

  for BLOCK in ${BLOCKS[@]}
  do
  boot-block --block $BLOCK &
  done
  wait

  %(job)s

  wait

  for BLOCK in ${BLOCKS[@]}
  do
  boot-block --block $BLOCK --free &
  done
  wait
  '''

# submit command
submit = 'qsub --project CloudPredict --nodecount %(nodes)d --time %(hours).2d:%(minutes).2d:00 --outputprefix report.%(label)s --notify %(email)s --disable_preboot %(xopts)s --mode script %(scriptfile)s'

# timer
timer = '(time -p (%(job)s)) 2>&1 | tee %(timerfile)s'

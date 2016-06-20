
# # # # # # # # # # # # # # # # # # # # # # # # # #
# Local configuration for Mira cluster
# IBM BlueGene/Q @ Argonne National Laboratory
# More information: http://www.alcf.anl.gov/user-guides/blue-geneq-versus-blue-genep
# For a detailed description of string mapping keys refer to documentation in 'cfg/local.txt'
#
# Jonas Sukys
# CSE Lab, ETH Zurich, Switzerland
# sukys.jonas@gmail.com
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# name
name = 'Argonne Mira (IBM BlueGene/Q)'

# Mira is a cluster
cluster = 1

# default configuration
cores     = 16   # per node
threads   = 4    # per core
walltime  = 1    # h
memory    = 1024 # MB per core
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
  if cores < 16 * 8192:
    return 6
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
envs = '''\
--envs PAMI_DEVICE=B \
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

#  --block $COBALT_PARTNAME ${COBALT_CORNER:+--corner} $COBALT_CORNER ${COBALT_SHAPE:+--shape} $COBALT_SHAPE \
#  --envs PAMID_ASYNC_PROGRESS=1 \
#  --mapping TABCDE \

# simple run command
simple_job = '''ulimit -c 0
runjob \
--np %(ranks)d \
--ranks-per-node %(tasks)d \
--block ${BLOCKS[%(block)d]} \
--corner ${CORNERS[%(corner)d]} \
--shape %(shape)s \
--cwd $PWD \
--envs OMP_NUM_THREADS=%(threads)d \
--envs XLSMPOPTS=parthds=%(threads)d \
%(envs)s \
: %(cmd)s %(options)s
'''

# MPI run command
mpi_job = '''ulimit -c 0
runjob \
--np %(ranks)d \
--ranks-per-node %(tasks)d \
--block ${BLOCKS[%(block)d]} \
--corner ${CORNERS[%(corner)d]} \
--shape %(shape)s \
--cwd $PWD \
--envs OMP_NUM_THREADS=%(threads)d \
--envs XLSMPOPTS=parthds=%(threads)d \
%(envs)s \
: %(cmd)s %(options)s
'''

# block boot
boot = 'boot-block --block ${BLOCKS[%(block)d]}'

'''
# boot blocks (3 attempts are recommended)
for BLOCK in ${BLOCKS[@]}
do
  boot-block --block $BLOCK &
  boot-block --block $BLOCK &
  boot-block --block $BLOCK &
done
wait
'''

# get shape from number of nodes
def shape (nodes):
  if nodes >= 512:
    return '$COBALT_SHAPE'
  shape = [1, 1, 1, 1, 1]
  index = 0
  while nodes != 1:
    shape [index] *= 2
    nodes /= 2
    index = (index + 1) % 5
  return '%dx%dx%dx%dx%d' % tuple (shape)

# get corners for sub-blocks
corners = '''
# get corners of subblocks for each batch job in the ensemble
CORNERS=`/soft/cobalt/bgq_hardware_mapper/get-corners.py ${BLOCKS[%(block)d]} %(shape)s`

# if 512 or more nodes are needed, return default corner
if (( %(nodes)d >= 512 ))
then
  CORNERS=$COBALT_CORNER
fi

# split string of subblocks into array elements
read -r -a CORNERS <<< $CORNERS

# print info about all corners of subblocks
echo
echo 'Obtained corners:'
for CORNER in ${CORNERS[@]}
do
  echo $CORNER
done
echo
'''

# block free
free = 'boot-block --block ${BLOCKS[%(block)d]} --free'

# batch job corner hook
#CORNER_HOOK = '${CORNERS[%(corner)d]}'

# batch job shape hook
#SHAPE_HOOK = '%(shape)s'

# submission script template (required for support of batch jobs ensembles)
script = '''#!/bin/bash

# get blocks for each batch job in the ensemble
BLOCKS=`get-bootable-blocks --size $((%(nodes)d/%(merge)d)) $COBALT_PARTNAME`

# split string of blocks into array elements
read -r -a BLOCKS <<< $BLOCKS

# sort array by length (longest to shortest)
# sorting is required since sometimes 2 versions of the _same_ block are provided - need to choose longer version
BLOCKS=($(for i in ${BLOCKS[@]} ; do echo ${#i}$'\\t'${i}; done | sort -n -r | cut -f 2-))

# print info about all blocks
echo
echo 'Obtained blocks (sorted by name length):'
for BLOCK in ${BLOCKS[@]}
do
  echo $BLOCK
done
echo

# truncate array to the required number of blocks
BLOCKS=($(for ((i=0; i<%(merge)d; i++)); do echo ${BLOCKS[$i]}; done))

# print info about selected blocks
echo
echo 'First %(merge)d selected block(s):'
for BLOCK in ${BLOCKS[@]}
do
  echo $BLOCK
done
echo

# get default subblock
CORNERS=$COBALT_CORNER

# print default subblock
echo $CORNERS

# split string of subblocks into array elements
read -r -a CORNERS <<< $CORNERS

%(job)s

wait
'''

# submit command
submit = 'qsub --project CloudPredict --nodecount %(nodes)d --time %(hours).2d:%(minutes).2d:00 --outputprefix %(reportfile)s --jobname %(label)s --notify %(email)s --disable_preboot %(xopts)s --mode script /soft/debuggers/scripts/bin/nofail ./%(scriptfile)s'

# timer
#timer = 'time --portability --output=%(timerfile)s --append (%(job)s)'
timer = '(time -p (%(job)s)) 2>&1 | tee %(timerfile)s'

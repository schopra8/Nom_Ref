#!/bin/bash
#
#all commands that start with SBATCH contain commands that are just used by SLURM for scheduling
#################
#set a job name
#SBATCH --job-name=alexnet
#################
#a file for job output, you can check job progress
#SBATCH --output=alexnet.out
#################
# a file for errors from the job
#SBATCH --error=alexnet.err
#################
#time you think you need; default is one hour; max is 48 hours
#SBATCH --time=3:00:00
#################
#quality of service; think of it as job priority (set --qos=long to submit a job for > 2 days & < 7 days)
#SBATCH --qos=normal
#################
#SBATCH -p gpu 
#number of nodes you are requesting (this will usually be 1)
#SBATCH --nodes=1
#################
#memory per node; default is 4000 MB per CPU
#SBATCH --mem=4000
#you could use --mem-per-cpu; they mean what we are calling cores
#################
#tasks to run per node; a "task" is usually mapped to a MPI processes.
# for local parallelism (OpenMP or threads), use "--ntasks-per-node=1 --cpus-per-task=16" instead
#SBATCH --ntasks-per-node=1
################# 

#now run normal batch commands                                                                                 
python myalexnet_forward.py $SLURM_ARRAY_TASK_ID
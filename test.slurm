#!/bin/bash
#SBATCH --job-name=32node-training
#SBATCH --nodes=2                  # 总物理节点数
#SBATCH --ntasks-per-node=8         # 每个节点8张GPU（假设每节点配置8*A100）
#SBATCH --gres=gpu:8                # 每个节点申请8卡
#SBATCH --cpus-per-task=12          # 每个GPU分配12 CPU核心
#SBATCH --time=72:00:00
#SBATCH --partition=ai-cluster
#SBATCH --exclusive                 # 独占节点资源

# NCCL优化参数
export NCCL_ALGO=Tree
export NCCL_SOCKET_IFNAME=ib0       # 使用InfiniBand
export NCCL_IB_DISABLE=0
export NCCL_IB_HCA=mlx5_0:1         # 指定Mellanox网卡

source ~/miniconda3/bin/activate
conda activate 

# 自动获取主节点IP
export MASTER_ADDR=$(scontrol show hostname $SLURM_JOB_NODELIST | head -n1)
export MASTER_PORT=29500

srun --cpu_bind=none \
     --mpi=pmi2 \
     python -u scripts/train.py \
     configs/tmp.yaml --save_overwrite

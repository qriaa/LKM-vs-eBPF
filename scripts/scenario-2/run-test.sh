#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_DATA_DIR="$SCRIPT_DIR/../../results/scenario-2/perf-data/"

mkdir -p $PERF_DATA_DIR

echo "Testing no syscall counting..."
$SCRIPT_DIR/control-syscalls-counter.sh

echo "Testing LKM syscall counting..."
$SCRIPT_DIR/lkm-syscalls-counter.sh

echo "Testing eBPF syscall counting..."
$SCRIPT_DIR/ebpf-syscalls-counter.sh

echo "Testing eBPF no JIT syscall counting..."
$SCRIPT_DIR/ebpf-nojit-syscalls-counter.sh

sudo chmod 777 -R $PERF_DATA_DIR

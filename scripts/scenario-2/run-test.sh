#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

mkdir -p $SCRIPT_DIR/../../results/scenario-2/perf-data/

echo "Testing no syscall counting..."
$SCRIPT_DIR/control-syscalls-counter.sh

echo "Testing LKM syscall counting..."
$SCRIPT_DIR/lkm-syscalls-counter.sh

echo "Testing eBPF syscall counting..."
$SCRIPT_DIR/ebpf-syscalls-counter.sh

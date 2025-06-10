#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

PERF_DATA_DIR="$SCRIPT_DIR/../../results/scenario-1/perf-data/"

mkdir -p $PERF_DATA_DIR

echo "Testing no firewall..."
$SCRIPT_DIR/control-firewall.sh

echo "Testing LKM Netfilter firewall..."
$SCRIPT_DIR/lkm-firewall.sh

echo "Testing eBPF no JIT Netfilter firewall..."
$SCRIPT_DIR/ebpf-nojit-nf-firewall.sh

echo "Testing eBPF no JIT XDP firewall..."
$SCRIPT_DIR/ebpf-nojit-xdp-firewall.sh

echo "Testing eBPF Netfilter firewall..."
$SCRIPT_DIR/ebpf-nf-firewall.sh

echo "Testing eBPF XDP firewall..."
$SCRIPT_DIR/ebpf-xdp-firewall.sh

sudo chmod 777 -R $PERF_DATA_DIR

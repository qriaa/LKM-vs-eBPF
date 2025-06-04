#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

mkdir -p $SCRIPT_DIR/../../results/scenario-1/perf-data/

echo "Testing eBPF Netfilter firewall..."
$SCRIPT_DIR/ebpf-nf-firewall.sh

echo "Testing LKM Netfilter firewall..."
$SCRIPT_DIR/lkm-firewall.sh

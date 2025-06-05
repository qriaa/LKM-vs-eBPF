#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")

. $SCRIPT_DIR/../utils.sh

ensure_sudo

. .env

NET_IF="enp38s0"
ADDRESSES=(
    "192.168.0.100"
    "192.168.0.101"
)
TESTS=(
    "lkm-firewall"
    "ebpf-nf-firewall"
    "xdp-firewall"
)

for RUNNING_TEST in "${TESTS[@]}"; do
    echo "Running test for $RUNNING_TEST"
    for SRC_ADDR in "${ADDRESSES[@]}"; do
        echo "Running test from $SRC_ADDR"
        ip addr add "$SRC_ADDR/24" dev "$NET_IF"
        iperf3 -u -4 -A 15 -b 1G -k 500000 -B "$SRC_ADDR" -c "$REMOTE_ADDR"
        ip addr del "$SRC_ADDR/24" dev "$NET_IF"
        sleep 1 # We need to wait for the server to run another iperf3 before continuing
    done
    sleep 5
done


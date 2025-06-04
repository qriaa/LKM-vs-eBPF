#!/usr/bin/env bash

# Ensure sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

. .env

NET_IF="enp38s0"
ADDRESSES=(
    "192.168.0.100"
    "192.168.0.101"
)

for SRC_ADDR in "${ADDRESSES[@]}"; do
    ip addr add "$SRC_ADDR/24" dev "$NET_IF"
    iperf3 -u -4 -A 15 -b 1G -k 500000 -B "$SRC_ADDR" -c "$REMOTE_ADDR"
    ip addr del "$SRC_ADDR/24" dev "$NET_IF"
    sleep 1 # We need to wait for the server to run another iperf3 before continuing
done

